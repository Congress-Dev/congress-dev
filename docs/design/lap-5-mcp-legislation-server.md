# MCP Server for Legislation & US Code — Design Doc

Linear: [LAP-5](https://linear.app/mustyoshi/issue/LAP-5/design-mcp-server-for-reading-legislation-and-us-code-from-the)

Status: Draft for discussion. This is a design-only deliverable — no server code ships
with this doc. Section 7 breaks the work into implementation tickets.

## 1. Schema audit — what exists today vs. what the tools need

Source: `backend/congress_db/models.py` (SQLAlchemy, source of truth) and
`hillstack/prisma/schema.prisma` (generated mirror via `prisma db pull`, 1:1 with the
Postgres schema, no independent drift beyond Prisma naming conventions).

### 1.1 Bills / legislation

| Need | Status |
|---|---|
| Bill identity (congress, chamber, type, number, title) | **Have.** `Legislation` (congress_id, chamber, legislation_type, number, title), unique on `(chamber, number, legislation_type, congress_id)`. |
| Lookup by natural key (e.g. "119th HR 1234") | **Partial.** The unique constraint covers it, but there's no FastAPI endpoint for it today — only internal `legislation_id` lookups. Needs a new handler, not a new column. |
| Sponsors / cosponsors | **Have.** `LegislationSponsorship` (one row per legislator per bill, `cosponsor`/`original` flags, dates). No denormalized "primary sponsor" column on `Legislation` — derived by filtering `original=True`. Fine as-is for a `get_bill_cosponsors` tool. |
| Bill status | **Gap.** No `status` column or table anywhere. Status must be inferred from the latest `LegislationAction`/`LegislationVersion` rows. `search_bills(status=...)` as drafted in the ticket isn't directly queryable today — needs either a derived view or a computed status enum stored on write. |
| Actions (floor votes, referrals, etc.) | **Have.** `LegislationAction`. |
| Versions (ih, rh, enr, etc.) | **Have.** `LegislationVersion`, enum `LegislationVersionEnum`. |
| Related bills (companion bills) | **Gap.** No table. `get_related_bills` as scoped in the ticket has nothing to query — out of v1 unless we add a table and a GovInfo/congress.gov ingestion step to populate it. |
| Amendments to a bill | **Gap.** No first-class amendment object in FastAPI/`congress_db`. The legacy Flask API has `get_bill_version_amdts` — worth checking what it actually reads before assuming the data doesn't exist at all; if it's live, the data model backing it needs to be ported into `congress_db` before `get_amendments` can be a FastAPI/MCP tool. |
| Full bill text, section-addressable | **Have, and it's good.** `LegislationContent` is a `parent_id` adjacency tree, one row per XML structural node (section/subsection/paragraph), tagged with `content_type` (XML tag) and `lc_ident` (stable ID across versions). This is exactly the shape `get_bill_text`/`get_bill_sections` need — no schema change required to address a slice. |

### 1.2 US Code

| Need | Status |
|---|---|
| Title/chapter/section hierarchy | **Have.** `USCChapter` → `USCSection` (self-referencing `parent_id`, ON DELETE CASCADE) → `USCContent` (self-referencing `parent_id` within a section). `usc_ident` is the USLM path (`/us/usc/t42/s1395`); composite index `(usc_ident, version_id)` is the primary lookup path. No ltree/closure table — ancestry is walked via `parent_id` recursion, which is adequate at this scale (a CTE recursive query, not a schema gap). |
| Fetch by title + section | **Have**, via `usc_ident` + `version_id`. `get_usc_section` needs no new column, just a handler that composes the ident string from `(title, section)` inputs. |
| As-of-date / release-point versioning | **Partial.** `USCRelease` has a real `effective_date`. But `USCContent`/`USCSection` don't carry their own effective date — they're scoped to a `version_id` that, via the generic `Version.base_id` self-reference, indirectly points back to the release that was current when a bill was parsed. There's no direct "give me title 42 as it stood on 2023-06-01" query path without first resolving a date to a `USCRelease.version_id`. That resolution logic doesn't exist yet as a service function — small gap, not a schema change. |
| Which bills cite/amend a given section (`get_usc_citations_to`, `get_usc_amending_bills`) | **Gap as a direct query, but the data exists.** See 1.3 — this is answerable today only by joining through `USCContentDiff`, not via a dedicated reverse index. |

### 1.3 Cross-reference (the high-value part)

This is more built than the ticket assumed, just not shaped as an explicit edge table:

- `congress_parser/actions/parser.py::determine_action()` classifies each `LegislationContent` clause into an `ActionType` (STRIKE_TEXT, INSERT_END, REPEAL, REPLACE_SECTION, ...) and `parse_text_for_cite()` extracts the USC citation the clause targets. Both are stored as JSONB on `LegislationActionParse.actions` / `.citations` — informal, not relational.
- `apply_action()` then executes the predicted edit and writes a `USCContentDiff` row carrying `legislation_content_id` → `usc_content_id` / `usc_section_id`. **This is a real, working, section-level "bill clause amends USC node" edge** — it's just modeled as a diff-output table, not a semantic `bill_section -> usc_section (relationship_type)` table as the ticket proposes.

Gap: there's no index that makes "which bills touch USC section X" or "what does bill Y amend" a cheap direct query — today you'd query `USCContentDiff` filtered by `usc_section_id` or by `legislation_content_id`'s ancestor bill, with no composite index for either direction. `compare_bill_to_law` is also already half-built: `congress_fastapi/handlers/legislation_version.py::get_legislation_version_diff_metadata_fastapi` (backing `GET /legislation_version/{id}/diffs`) already returns per-section diff metadata (heading, section number, repealed flag). It needs reshaping for MCP output, not new computation.

**Recommendation**: don't build a new `bill_section -> usc_section` edge table from scratch. Add a thin, explicitly-named view/table that materializes the relationship type already implied by `ActionType` + `USCContentDiff`, with indexes on both `usc_section_id` and the bill-side key. This gets `get_usc_citations_to` / `get_usc_amending_bills` to be index lookups instead of recursive joins, without re-deriving data the parser already computed once.

### 1.4 Full-text / semantic search

- No Postgres FTS anywhere (`tsvector`/GIN/`pg_trgm`) — confirmed by grep across the whole repo. Prisma's schema has `previewFeatures = ["fullTextSearchPostgres"]` turned on but unused — looks like FTS was planned and never finished.
- ChromaDB is real and working, but **only for US Code** (`congress_parser/importers/chroma_uscode.py` ingests embeddings into a `uscode` collection; `congress_fastapi/handlers/uscode.py::search_chroma` backs `POST /uscode/search`). There is no equivalent embedding collection for bill text.
- `search_bills` as drafted needs filtered SQL (congress, chamber, sponsor, status, date range, policy area — all of which have columns/arrays today except status) plus either Postgres FTS or a new Chroma collection for free text. Given Chroma is already running and already the pattern for USC, the pragmatic v1 choice is Postgres `tsvector` for bill search (cheaper to stand up, no new infra, good enough for keyword search on bill titles/actions) and defer bill-text semantic search to a later Chroma collection if agents need it.

### 1.5 Token/size metadata

No char/token-count column exists on `LegislationContent` or `USCContent`. Needed for the MCP server's pagination/truncation story (section 4) — this is a real, small schema addition (a nullable `char_count`/`token_count` int, backfilled once, computed going forward in the importer).

### 1.6 Indexes

`Legislation`'s natural key is covered only by its unique constraint, not a query-optimized index for partial lookups (e.g. "all HR bills in congress 119" without a number) — fine for v1 since `get_bill` always has the full key. USC's `(usc_ident, version_id)` index is solid. Sponsor/cosponsor lookups are already indexed via `LegislationSponsorship` FKs. Status has no index because it has no column (see 1.1).

## 2. Proposed tool / resource / prompt spec

Grouped by the MVP vs. later rollout split used in Section 7. Each tool below: inputs,
output shape, and backing query.

### MVP tools

**`get_bill(congress, bill_type, number)`**
→ `{ legislation_id, congress, chamber, type, number, title, sponsor, cosponsor_count, introduced_date, latest_action, available_versions: [version_code] }`
Backed by `Legislation` + `LegislationSponsorship` (original=True) + `LegislationVersion`. New handler needed (no natural-key lookup exists in FastAPI today — see 1.1).

**`get_bill_text(congress, bill_type, number, version, section?, cursor?)`**
→ `{ version, sections: [{ lc_ident, section_display, heading, content_str }], next_cursor | null }`
Backed by `LegislationContent` tree walk, scoped by `legislation_version_id`. Reuses the existing text-reconstruction logic behind `GET /legislation/{id}/latest/text`, but needs a section-level entry point (fetch one `lc_ident` subtree) rather than always reconstructing the whole bill — that's new, not a schema change.

**`get_bill_sections(congress, bill_type, number, version)`**
→ outline only: `{ lc_ident, section_display, heading, content_type, depth }[]`, no body text. Same tree, projected without `content_str` — cheap, good for an agent to decide what to fetch next.

**`get_usc_section(title, section, as_of?)`**
→ `{ usc_ident, heading, content, children: [...], effective_date }`
Backed by `USCContent`/`USCSection` keyed on `usc_ident`; `as_of` resolves to a `USCRelease.version_id` (new small resolver function, no schema change — see 1.2 gap).

**`search_bills(query?, congress?, chamber?, sponsor?, policy_area?, date_range?, cursor?)`**
→ paginated list of bill summaries. Needs Postgres `tsvector` on title (+ maybe action text) for the free-text part; everything else is existing filterable columns. `status` filter deferred until a status is actually materialized (1.1).

**`search_usc(query, title?, cursor?)`**
→ reuses the existing Chroma-backed `search_chroma`/`POST /uscode/search`, reshaped as an MCP tool with pagination added (today's endpoint doesn't paginate).

### Second-wave tools (need the cross-reference table from 1.3)

**`get_bill_usc_references(congress, bill_type, number, version?)`** → sections a bill amends/repeals/cites, with relationship type.
**`get_usc_amending_bills(title, section)`** → reverse lookup, bills touching a section.
**`get_usc_citations_to(title, section)`** → narrower alias of the above, citation-only (not amendment) hits — depends on whether `parse_text_for_cite` output distinguishes "cites" from "amends" cleanly enough to split; needs a look at `ActionType`'s full enum before committing to two separate tools vs. one tool with a `relationship_type` filter.
**`compare_bill_to_law(congress, bill_type, number, version?)`** → reshapes `get_legislation_version_diff_metadata_fastapi`'s output for MCP; mostly plumbing, minimal new logic.

### Deferred (data doesn't exist yet)

**`get_bill_actions`**, **`get_bill_cosponsors`** — trivial once `get_bill` ships (same tables), can ship alongside it, not actually blocked.
**`get_related_bills`**, **`get_amendments`** — blocked on new data (1.1): no related-bills table, and the amendments data model needs to be confirmed/ported from the legacy Flask `get_bill_version_amdts` path before this is buildable. Flag as a follow-up data-audit ticket rather than committing to a timeline here.
**`get_usc_structure`** — browse title/chapter/subchapter hierarchy without a specific section. Easy (same `USCSection` tree, no leaf content), just not in the MVP cut.

### MCP resources

Stable URIs per the ticket's draft, resolved by the same handlers as the tools above:
`bill://{congress}/{bill_type}/{number}/versions/{version}`, `bill://{congress}/{bill_type}/{number}/versions/{version}/sections/{lc_ident}`, `usc://{title}/{section}`, `usc://{title}/{section}?as_of={date}`.
Resources should be read-only views of the same query path `get_bill_text`/`get_usc_section` use — no separate implementation, just an MCP `resources/read` handler that parses the URI into the same parameters.

### MCP prompts (optional, v1.1+)

"Summarize bill `{uri}`" and "What law does `{uri}` change" — thin prompt templates that chain `get_bill_text` + `get_bill_usc_references`/`compare_bill_to_law`. Not needed for MVP; worth a follow-up ticket once the underlying tools are stable, since prompt quality depends on tool output shape settling first.

## 3. Schema change proposal

1. **Cross-reference materialization** (new): a view (preferred over a new table, to avoid a second write path diverging from the parser's actual output) over `USCContentDiff` joined to `LegislationActionParse`/`LegislationContent`, exposing `(usc_section_id, legislation_content_id, relationship_type, bill's legislation_id)`. Add indexes on `usc_section_id` and on the bill-side key to support both lookup directions. If query performance on a view over the diff table is poor, fall back to a materialized view refreshed after each parser run, not a hand-maintained table.
2. **Token/size metadata**: add `char_count`/`token_count` nullable columns to `LegislationContent` and `USCContent`, computed in the importer going forward, backfilled once via a one-off script. Needed for the pagination/truncation story in Section 4.
3. **Bill status**: either (a) a computed column maintained by the parser pipeline whenever it writes a new `LegislationAction`/`LegislationVersion`, or (b) a view deriving status from the latest action/version at query time. Prefer (b) first — avoids a new write path and the risk of it drifting from the actions it's derived from — and only promote to a stored column if the derivation proves too slow for `search_bills` filtering.
4. **Full-text search**: add a `tsvector` generated column on `Legislation` (title, and optionally concatenated recent `LegislationAction.text`) with a GIN index, migrated via Alembic. This is additive and backward-compatible — no existing query path changes.
5. **As-of resolver**: no schema change, but add a service function (`resolve_usc_version_for_date(date) -> version_id`) backed by `USCRelease.effective_date`, used by both `get_usc_section` and any future "law as of X" tooling. Document it once, reuse everywhere, rather than letting each caller re-derive the join.

Migrations should land as four independent Alembic revisions (cross-ref view, size columns, status view, FTS column) so each can be reviewed and rolled back separately, and so the MVP tools (which only need the existing schema) aren't blocked on all four landing together.

## 4. API / service layer

**Decision: shared service layer, not direct DB access from the MCP process.**

`congress_fastapi/handlers/*` already separates query logic from route definitions (`routes` → `handlers` → `db` per the existing `congress_fastapi` convention documented in `CLAUDE.md`). The MCP server should import and call these handlers directly (same Python process or same deployable, not a new DB connection with its own ORM session management) rather than either (a) re-implementing the same SQLAlchemy queries a second time, or (b) going over HTTP to the FastAPI service and paying a second serialization hop for data that's about to be re-serialized as an MCP tool result. Direct-DB-from-a-second-codebase was rejected because it's exactly the duplicated-query-logic problem the ticket calls out wanting to avoid, and three FastAPI routes are already tagged `MCP` in their OpenAPI tags — a strong signal the original intent was always "FastAPI handlers, exposed twice" rather than two independent read paths to Postgres.

Concretely: new package `backend/congress_mcp/`, depending on `congress_fastapi.handlers` (import, not HTTP) and `congress_db` directly for anything with no handler yet (e.g. the natural-key bill lookup). Where a handler doesn't exist yet (natural-key lookup, section-scoped `get_bill_text`, cross-reference queries), add it to `congress_fastapi/handlers/` first so the REST API and the MCP server share it — this also means the new handlers get test coverage and a REST surface for free, even if nothing currently calls them over HTTP.

**Pagination/truncation**: cursor-based, keyed on `lc_ident`/`usc_ident` ordering (not offset-based — these trees are stable-ordered by `order_number`, so a cursor is just "last `lc_ident` returned"). Every text-bearing tool response carries `{ ..., truncated: bool, next_cursor: string | null }`. A tool call has a max-token budget (configurable, default ~4000 tokens of content per call) computed from the new `token_count` column (Section 3.2) — when a requested slice would exceed it, return as much as fits plus `next_cursor`, never silently truncate mid-node.

**Citation parser/normalizer endpoint**: `congress_parser/actions/__init__.py`'s citation parsing (used by `parse_text_for_cite`) already does free-text → structured-cite extraction for bill clauses. Expose it as `congress_fastapi/handlers/citations.py::normalize_citation(text) -> {title, section} | ambiguous | not_found`, reused by an MCP tool (`normalize_citation`, not in the ticket's draft list but implied by "Citation parser/normalizer endpoint" under API/service layer) and by `get_usc_section`'s free-text input path if we want to accept `"42 USC 1983"` as well as structured `(title=42, section=1983)`.

## 5. Response-size and pagination strategy

Covered inline in Section 4. Summary of the rules every tool follows:
- Outline-only tools (`get_bill_sections`, `get_usc_structure`) never include `content_str` — they're always cheap.
- Content tools (`get_bill_text`, `get_usc_section`) accept an optional `section`/`lc_ident`/`usc_ident` to scope the request, and a `cursor` for the next page within that scope.
- Every truncated response says so explicitly (`truncated: true`, `next_cursor`) — no tool silently drops content.
- Size budget is enforced server-side using the new token-count metadata, not client-guessed.

## 6. Server concerns

- **Transport**: stdio for local agent dev (matches how Claude Code and similar clients run MCP servers locally); streamable HTTP for the hosted/production case (agents running against `api.congress.dev`-adjacent infra). Both transports share the same tool implementations — transport is just the outer layer, per the MCP SDK's normal separation.
- **Language/framework**: Python, using the official `mcp` SDK (FastMCP). The entire backend (`congress_api`, `congress_fastapi`, `congress_parser`, `congress_db`) is Python; a TypeScript server would mean re-implementing the handler layer in a second language for no benefit, given Section 4's decision to share handlers in-process.
- **Auth / rate limiting / DB role**: MCP tools are read-only by scope (ticket explicitly excludes write access), so the DB role used by `congress_mcp` should be a dedicated read-only Postgres role, separate from the read-write role `congress_fastapi` uses for authenticated write endpoints (favorites, LLM query logging) — least-privilege, and it makes "this server cannot write" a DB-enforced guarantee, not just an application-level convention. Rate limiting should reuse whatever `congress_fastapi` already does for its one rate-limited endpoint (`POST /legislation_version/{id}/llm`, 5/5min) as the pattern — same approach (presumably Redis-backed), not a new mechanism.
- **Caching**: cache fully-reconstructed bill/USC text server-side (the recursive tree walk is the expensive part, not the final payload), keyed on `(legislation_version_id, cursor)` / `(usc_ident, version_id, cursor)`. Reuse whatever cache backend FastAPI already has available in its deployment (check `.docker/docker-compose.yml` for an existing Redis/memcached service before introducing a new one).
- **Error model**: not-found → MCP tool error with a clear "no bill matches congress=X type=Y number=Z" message (not a bare 404-shaped object); ambiguous citation (e.g. free-text citation parse matches multiple sections) → a distinct error/result shape that lists the candidates, so an agent can disambiguate rather than silently picking one. This matters most for the citation normalizer (Section 4) and for any free-text entry points.
- **Observability**: log tool name, input params (redacted of nothing — this is all public legislative data), latency, and response byte/token size per call. This is cheap to add from day one and is exactly what the ticket's eval-set testing (Section 7) needs data from.
- **Testing**: fixture bills + USC sections (small, stable, checked into `backend/congress_parser/tests/` alongside existing parser fixtures) and an eval set of agent-shaped questions (e.g. "what does HR 1234 do to 42 USC 1983") run against the live tool surface — not just unit tests of the handlers, since the thing actually being validated is whether an agent gets a useful answer within the token budget.

## 7. Rollout plan — implementation tickets

1. **Schema: cross-reference view + size columns** — the two additive migrations from Section 3 (#1, #2) that the second-wave tools and pagination both depend on. No MVP tool blocks on this; land it in parallel.
2. **Handler layer gaps** — add the missing `congress_fastapi/handlers` functions identified in Section 4: natural-key bill lookup, section-scoped bill text fetch, `as_of` USC version resolver, citation normalizer. These are REST-usable too, not MCP-only.
3. **MCP server skeleton (`backend/congress_mcp/`)** — stdio transport, tool registration scaffolding, read-only DB role wiring, observability (tool-call logging) from the start.
4. **MVP tools**: `get_bill`, `get_bill_text`, `get_bill_sections`, `get_bill_actions`, `get_bill_cosponsors`, `get_usc_section`, `search_usc` (wraps existing Chroma search), `search_bills` (needs the FTS migration — Section 3.4 — as a sub-task of this ticket or a precursor).
5. **MCP resources** — URI scheme + `resources/read` wiring over the MVP tools' handlers.
6. **Second-wave cross-reference tools**: `get_bill_usc_references`, `get_usc_amending_bills`, `get_usc_citations_to`, `compare_bill_to_law` — depends on ticket 1.
7. **Streamable HTTP transport + hosted deployment** — once stdio works locally, add the production transport and deployment wiring (`.docker/docker-compose.yml` entry, following the existing compose pattern for `congress_fastapi`).
8. **Status derivation + bill status filter on `search_bills`** — Section 3.3, deferred because it's the one genuinely open design question (view vs. stored column) worth revisiting once real query-latency data exists.
9. **Data-audit follow-up (not implementation)**: confirm whether the legacy Flask `get_bill_version_amdts` endpoint has live data behind it, and scope a `related bills` ingestion source (congress.gov API has this) before committing `get_amendments`/`get_related_bills` to a ticket.
10. **MCP prompts** (`summarize bill`, `what law does this change`) — after tickets 4–6 are stable, since prompt design depends on finalized tool output shapes.

## Open questions (answered or flagged, per the ticket)

- **US Code source**: OLRC/House USLM XML (`uscode.house.gov`), not GovInfo. Bill source is GovInfo bulk bill XML. Confirmed in `congress_parser/importers/releases.py` and `importers/bills.py`.
- **Bill text parsing format**: already parsed into a structured `parent_id` tree (`LegislationContent`), not kept as raw XML or plain text. No work needed here — the ticket's "Hierarchical structure for text" schema candidate is already in place for both bills and USC.
- **Semantic search for v1**: USC already has it (Chroma). Bill search does not. Recommend Postgres FTS for bill search in v1 (cheaper, matches what's missing) and leave bill-text semantic search as a later extension if agents need conceptual (not keyword) bill search.
- **Cross-reference extraction**: already rule-based (`determine_action`/`parse_text_for_cite` in `congress_parser/actions/`), not LLM-assisted, and it's already running in production (it's what populates `USCContentDiff`). No need to decide this — it's decided and working; the open task is exposing it, not building it.
