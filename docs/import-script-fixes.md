# import.sh fix plan

Findings from a manual run of `import.sh` on the `parser` host (10.0.0.171) on
2026-08-16. The script ran to completion, but with real failures.

## 1. Sponsors import is fully broken (invalid `CONGRESS_API_KEY`)

Every request to `api.congress.gov` during the `billparser.importers.sponsors`
step failed:

```
"code": "API_KEY_MISSING", "message": "No api_key was supplied. Get one at https://api.congress.gov:443"
Failed to fetch data. Status code: 403
```

This repeated for the entire step — no sponsor data was updated in this run.

**Fix:**
- Obtain/verify a working `api.congress.gov` API key.
- Rotate the key out of the crontab entry and `import.sh` (both currently
  hardcode `CONGRESS_API_KEY` in plaintext) into a proper secrets store /
  `.env` file that `import.sh` sources, not committed to the repo or crontab.
- Add a check after the sponsors step that fails loudly (non-zero exit /
  explicit log line) if every request 403s, instead of silently continuing.

## 2. `docker run --name congress-bill-parser` container-name collisions skip steps

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
- Add `docker rm congress-bill-parser && true` (or switch every `docker run`
  to use `--rm`) before *every* `docker run --name congress-bill-parser`
  invocation, not just some of them.
- Prefer `--rm` on the `docker run` calls generally, so containers are always
  cleaned up automatically regardless of exit status, removing the need to
  track manual `docker rm` calls between every pair of steps.
- Add `set -e` (or explicit exit-code checks per step) so a genuine failure
  stops the script / surfaces clearly instead of continuing silently into
  later steps.

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

1. Fix the `docker rm` gaps (#2) — cheap, mechanical, and currently causing a
   real release-import step to be skipped every run.
2. Rotate/fix the `CONGRESS_API_KEY` (#1) and get it out of plaintext in the
   crontab/script.
3. Fix cron failure notifications (#4) so future regressions are visible.
4. Triage the action-parser error volume (#3) as a separate follow-up.
