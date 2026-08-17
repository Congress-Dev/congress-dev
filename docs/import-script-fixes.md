# import.sh fix plan

Findings from a manual run of `import.sh` on the `parser` host (10.0.0.171) on
2026-08-16. The script ran to completion, but with real failures.

## 1. Sponsors import failed with `API_KEY_MISSING` — likely a test-run artifact, not a dead key

Every request to `api.congress.gov` during the `billparser.importers.sponsors`
step failed:

```
"code": "API_KEY_MISSING", "message": "No api_key was supplied. Get one at https://api.congress.gov:443"
Failed to fetch data. Status code: 403
```

**Correction:** the manual run this was observed in was started as plain
`bash import.sh`, without the `CONGRESS_API_KEY=...` prefix that the crontab
entry normally supplies. The deployed script's `bills` step has the key
hardcoded directly (so it isn't affected), but `sponsors`/`actions` only ever
read `${CONGRESS_API_KEY}` from the environment — which was empty for that
manual run. So this failure is most likely explained by the test invocation,
not an actually-revoked key. Treat "the key is dead" as unconfirmed until a
run with the env var properly set (e.g. the real cron run, or a manual
`CONGRESS_API_KEY=<value> bash scripts/import.sh`) is checked.

**Fix:**
- Confirm on the next real cron run (or a manual run with the key set)
  whether sponsors actually succeeds now that `scripts/import.sh` no longer
  hardcodes the key on the `bills` step and uses `${CONGRESS_API_KEY}`
  consistently everywhere (see accompanying script change).
- If it's still failing with a properly-set key, then it needs replacing —
  get a working `api.congress.gov` key.
- Regardless, get the key out of plaintext in the crontab entry (still
  hardcoded there) into a proper secrets store / `.env` file that
  `import.sh` sources, rather than an inline cron env assignment.
- Add a check after the sponsors step that fails loudly (non-zero exit /
  explicit log line) if every request 403s, instead of silently continuing.

## 2. `docker run --name congress-bill-parser` container-name collisions skip steps — FIXED

**Status: fixed in `scripts/import.sh`** on this branch — see commit history.

`import.sh` only calls `docker rm congress-bill-parser` between *some* of the
importer steps, not all of them. Missing cleanup between:

- `prompts` → `bioguide`
- `sponsors` → `releases`

When the previous step's container is still present, the next
`docker run --name congress-bill-parser ...` fails immediately with:

```
docker: Error response from daemon: Conflict. The container name
"/congress-bill-parser" is already in use by container "<id>". You have to
remove (or rename) that container to be able to reuse that name.
```

Because the script has no `set -e`, this failure is silently swallowed and
the step (in this run, `releases`) never actually executes — the new US Code
release point does not get imported that cycle.

**Fix:**
- [x] Added `--rm` to every `docker run --name congress-bill-parser` /
  `congress-bill-cleanup` invocation, so containers are always cleaned up
  automatically regardless of exit status. Removed the now-redundant manual
  `docker rm ... && true` calls between steps, keeping a single
  `docker rm congress-bill-parser || true` pre-flight check at the top as a
  safety net for a container left over from a previous crashed run.
- [x] Also fixed the `bills` step to use `${CONGRESS_API_KEY}` /
  `${DISCORD_WEBHOOK}` consistently instead of a hardcoded literal, matching
  the other steps.
- [ ] Not done: `set -e` (or explicit exit-code checks per step). Left out of
  this pass since several steps in the script are expected to tolerate
  partial failures; adding it needs a closer look at which failures should
  actually stop the run vs. just get logged.

## 3. High volume of action-parsing errors during the `actions` step

Dozens of distinct bills produced tracebacks in
`billparser/actions/parser.py` while applying legislative actions to the US
Code tree, e.g.:

```
IndexError: list index out of range          (insert_subsection_end)
TypeError: 'NoneType' object is not subscriptable   (replace_section)
AssertionError: Should be singular child      (insert_subsection_after)
```

**Fix:**
- Needs triage: sample a handful of the affected
  `legislation_version_id`/`legislation_content_id` pairs from the log and
  determine whether these are expected parser misses (regex/action-type
  edge cases) or a regression. Track the failure rate over time; if it's
  climbing, that points at a change in incoming bill-text patterns rather
  than one-off inputs. Not blocking a re-run, but worth a scoped follow-up.

## 4. Outbound cron-failure email is broken

Cron output to `MAILTO=admin@congress.dev` has been bouncing since at least
2026-03-20 with `Network is unreachable` connecting to
`mx1.improvmx.com` over IPv6 — this is why the (previously daily, then
disabled) cron job's failures went unnoticed. The cron line has now been
re-enabled (2026-08-16) after this manual run, but failure visibility is
still broken.

**Fix:**
- Fix outbound SMTP/IPv6 routing on the `parser` host, or switch `MAILTO` to
  something reachable (or point cron output at the existing Discord webhook
  the script already posts to, so failures show up somewhere that's actually
  monitored).

## Suggested order of work

1. ~~Fix the `docker rm` gaps (#2)~~ — done, see `scripts/import.sh` on this
   branch.
2. Confirm whether the `CONGRESS_API_KEY` sponsors failure (#1) reproduces
   with the key actually supplied; only rotate it if it does. Either way, get
   it out of plaintext in the crontab entry.
3. Fix cron failure notifications (#4) so future regressions are visible.
4. Triage the action-parser error volume (#3) as a separate follow-up.
