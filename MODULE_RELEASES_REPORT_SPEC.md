# Module Releases Report — Implementation Spec (for review)

Status: **draft, not yet implemented.** Design for a new `/module-releases-report` command.
Nothing here has been built yet.

Revision note: this is the third revision. Rev 2 added per-release change/contribution counts.
Rev 3 (this one) incorporates a review pass in which several rev-2 assumptions were tested
against the live Forge API and turned out to be wrong — see
[Verified findings](#verified-findings-rev-3-review) for what changed and why. The cost model,
the `external_docs` handling, and the CSV columns all changed as a result.

## Goal

A CSV report of every `puppetlabs` module released on the Forge between a start and end date,
one row per release.

| Column | Example | Notes |
|---|---|---|
| `module_name` | `stdlib` | from Forge |
| `version` | `10.0.2` | from Forge |
| `release_date` | `2026-08-06` | **UTC** date of `created_at` (see [Date basis](#date-basis)) |
| `num_changes` | `4` | top-level changelog bullets for that version; blank if no bullets could be sourced |
| `num_community_contributions` | `1` | bullets credited to a handle in the `community` list |
| `num_unknown_contributions` | `0` | bullets credited to a handle in **neither** list in `config/internal_contributors.yaml` |

**On `num_unknown_contributions`:** this uses the meaning `05_count_contributions.py` already
established — a GitHub handle *was* resolved for the bullet, but it isn't classified yet in
[config/internal_contributors.yaml](config/internal_contributors.yaml), so it needs a human to
file it as internal or community. It is a **to-do counter**, and a nonzero value means
`num_community_contributions` may be undercounting until the config is updated.

Note this deliberately does *not* count bullets that carry no attribution at all (measured:
23 of 245 bullets in the default window have no PR link — pure-maintenance entries with nobody
to credit). Those are counted in `num_changes` only. Consequence: the columns don't sum —
`num_changes` ≥ community + unknown, with the remainder being internal-authored plus
unattributed changes. If you'd rather `num_unknown_contributions` also absorb the
no-attribution bullets, or want internal/unattributed as their own columns, say so and it's a
one-line change.

Other behavior:

- Command: `/module-releases-report [start-date] [end-date]`
- Either date may be omitted; the **script** computes defaults from the real clock, never the skill:
  - **Start default**: January 1st of the current calendar year
  - **End default**: today
- Range is **inclusive** on both ends.
- Module scope matches `01_discover_modules.py`: `module_groups=base+pe_only`, owner
  `puppetlabs`, `hide_deprecated=true`, `hide_contribution=true`.
- Output: CSV in the existing gitignored `data/` folder, e.g.
  `data/module_releases_report_20260101_20260817.csv`.

### Expected output size

Measured for the default window (2026-01-01 → 2026-08-17): **96 rows across 54 modules.**
Multi-release modules in that window include peadm (5), cd4peadm (4), sce_linux (4),
windows_eventlog (4), inifile (4). Useful as a smoke-test baseline.

## Verified findings (rev-3 review)

Everything below was checked against the live Forge API, not assumed.

**1. The whole report costs 2 HTTP requests, not ~56.** Rev 2 claimed one changelog fetch per
module. Wrong: the `v3/modules` listing payload **already embeds every module's complete
`CHANGELOG.md`** in `current_release.changelog` (stdlib 98,401 chars; apache 179,600). Since
the module list is 108 modules over 2 pages at `limit=100`, two requests yield every release
date *and* every changelog. No per-module fetches. (`exclude_fields` does not shrink the
payload — each page is ~19 MB, which is still less total transfer than 54 individual changelog
pages would have been.)

**2. `comply` and `complyadm` have real structured changelogs**, despite being configured as
`external_docs`: comply has 64 versioned sections and 258 inline attributions, complyadm 13 and
41. Only three modules are genuine stubs whose entire changelog is a pointer to the docs site:

| Module | Changelog content |
|---|---|
| `cd4peadm` | 109 chars — "For details on changes, see https://www.puppet.com/docs/continuous-delivery/…" |
| `sce_linux` | 151 chars — "The changelog for SCE for Linux lives on the official documentation site…" |
| `sce_windows` | 155 chars — same, for Windows |

This is why source selection is now **data-driven rather than list-driven** (see below).

**3. `premium` / `login_required` cannot identify the "private module" set.** comply is
`premium=False, login_required=False`; sce_linux/sce_windows are `premium=True`;
cd4peadm/complyadm are `login_required=True`. No flag or combination isolates them, so those
fields are not used for source selection.

**4. GitHub API load is negligible.** Across the default window's 245 changelog bullets: **213
already carry inline author credit**, only **9 lack it but have a PR link** (9 unique PRs), and
23 have no PR link at all. The posts cache resolves 4 of those 9, leaving **5 live GitHub calls
for a full year-to-date run** — far under the unauthenticated 60/hour limit. Rev 2 treated rate
limiting as a headline risk; it isn't. `GITHUB_TOKEN` support is therefore dropped as
unnecessary complexity.

**5. 48 of 2,523 releases carry a non-null `deleted_at`** (withdrawn/yanked). Rev 2 never
filtered these. Now excluded.

**6. Timezone choice moves 22% of dates.** `created_at` is Pacific (`-0700`); **21 of the 96**
in-range releases fall on a different calendar day in UTC — e.g. cd4peadm 5.16.0 is
`2026-07-28 17:58:35 -0700` = **2026-07-29** UTC, and the July post publishes `2026-07-29`.
See [Date basis](#date-basis).

**7. Version matching is reliable but not perfect.** Matching Forge versions to changelog
sections (after normalizing the `v` prefix) succeeded for **81 of 82** non-external in-range
releases. The one miss — `pe_event_forwarding 2.3.0` — has no matching section at all, and one
matched section parsed to zero bullets. Both cases need distinct handling (see
[Blank vs. zero](#blank-vs-zero)).

**8. Historical external-docs URLs all still resolve** (HTTP 200) for every in-range version of
sce_linux (2.8.0, 2.7.0, 2.6.1, 2.6.0), sce_windows (2.2.1), and cd4peadm — so those rows are
populatable, not 404 gambles. Note cd4peadm's four in-range releases **all live on one fixed
page** differentiated only by anchor, so it must be fetched once and reused, not four times.

## Design decisions

### Date basis

`release_date` is the **UTC** date of `created_at`. This matches
`01_discover_modules.py`'s existing `.astimezone(timezone.utc)` convention and therefore matches
the dates already published in `posts/`. Confirmed decision.

Caveat worth knowing: for **month-aligned** windows this shifts releases across the boundary
(a release at `2026-07-31 18:00 -0700` is an August release under UTC). The default YTD window
happens to have zero such flips, but that's a property of this window, not a general guarantee.

### Source selection is data-driven, not list-driven

Rather than trusting `config/release_notes_sources.yaml`'s `external_docs` membership to mean
"no changelog" (finding 2 shows it doesn't), bullets are sourced per release by this rule:

1. **Embedded changelog** — if the module's `current_release.changelog` contains a `## ` section
   matching this release's version, parse bullets from it. Populate all three count columns.
2. **External docs** — else, if the module has an `external_docs` entry in the config, build its
   URL via `release_sources.build_external_docs_url()` and parse bullets from there. Populate
   `num_changes`; leave `num_community_contributions` and `num_unknown_contributions` **blank**,
   since prose release notes carry no PR/attribution structure to count.
3. **Nothing available** — else (`manual_review`, or no section and no external config): emit
   the row with all three count columns blank and name the module in the run summary.

This self-maintains: comply/complyadm automatically get real counts because their sections
exist; cd4peadm/sce_* automatically fall through to their docs pages because theirs don't; and
a future module that gains or loses a real changelog needs no config edit.

### Blank vs. zero

These are different facts and must not collapse:

- **Blank** = not knowable from the available source (no changelog section found; external-docs
  or `manual_review` sourcing for the contribution columns).
- **`0`** = knowable and genuinely zero (a changelog section exists and parsed fine; it simply
  had no community-credited bullets — or, for `num_changes`, a section that exists with no
  bullets in it).

### Row visibility

Every in-range release always gets a row. This is a releases report first; a release never
disappears because a derived count wasn't obtainable. Confirmed decision.

### Deleted releases

Releases with a non-null `deleted_at` are excluded entirely. Confirmed decision.

## Proposed file layout

```
scripts/
  lib/
    __init__.py
    http_common.py               # NEW — shared session/User-Agent
    date_utils.py                # NEW — default_date_range(), resolve_date_range()
    forge_api.py                 # NEW — paged v3/modules client
    release_sources.py           # NEW — extracted from 01_discover_modules.py
    changelog_parse.py           # NEW — extracted parsing half of 02_fetch_release_notes.py
    external_docs.py             # NEW — extracted MadCap/generic docs parsing from 02
    contributor_classification.py # NEW — extracted from 05_count_contributions.py
    posts_attribution_cache.py   # NEW — mines posts/*.md for resolved PR→author credits
  01_discover_modules.py         # refactored to use lib/release_sources.py (behavior-preserving)
  02_fetch_release_notes.py      # refactored to use lib/changelog_parse.py + lib/external_docs.py
  05_count_contributions.py      # refactored to use lib/contributor_classification.py
  report_module_releases.py      # NEW — the report script
.claude/
  commands/
    module-releases-report.md    # NEW
  skills/
    module-releases-report/
      SKILL.md                   # NEW
```

**Naming:** deliberately *not* `06_…`. The `NN_` prefix in this repo means "stage N of the
roundup pipeline," and this report is a standalone tool, not a sixth stage. Easy to rename if
you'd rather it sort alongside the others.

**Reduced refactor surface:** because of finding 1, no shared *fetching* of changelogs is
needed — only shared *parsing*. That's a smaller and safer extraction than rev 2 proposed.

### `scripts/lib/date_utils.py`

```python
def default_date_range(today: Optional[date] = None) -> Tuple[date, date]:
    """(Jan 1 of today.year, today). `today` is for testability only;
    production resolves it from datetime.now()."""

def resolve_date_range(start_str, end_str, today=None) -> Tuple[date, date]:
    """Parse YYYY-MM-DD where given, else fall back to default_date_range()
    for the missing side. Raises ValueError if start > end."""
```

Satisfies "the script calculates dates, not the skill." The script always prints the resolved
range to stderr so nothing is silently assumed.

### `scripts/lib/forge_api.py`

```python
def iter_puppetlabs_modules(session) -> Iterator[dict]:
    """Page v3/modules (limit=100, follow pagination.next) with the same filters
    01_discover_modules.py uses. Yields full module dicts including the embedded
    `releases` history and `current_release.changelog`."""
```

### `scripts/lib/changelog_parse.py`

Extracted from `ReleaseNotesFetcher`. The key generalization: today's
`_filter_sections_by_month(sections, month, year)` becomes
`filter_sections_by_range(sections, start, end)` — a strict generalization, since a month is a
range from its 1st to its last day.

```python
def extract_release_sections(changelog_md) -> List[dict]   # {version, release_date, bullets}
def filter_sections_by_range(sections, start_date, end_date) -> List[dict]
def normalize_version(v) -> str                            # strips leading v/V
def bullets_from_lines(lines, top_level_only=True) -> List[str]
def enrich_bullet_attribution(bullet, session, pr_author_cache) -> str
```

`02_fetch_release_notes.py` becomes a thin wrapper that computes the target month's first/last
day and calls `filter_sections_by_range`, instead of holding its own month filter.

**Three implementation constraints carried over from the review** — each is a live trap in the
code being reused:

1. **Never inherit the 5-bullet cap.** `_dedupe_and_limit(..., limit=5)` is applied by the
   external-docs path and by `_parse_forge_changelog`. Counting must use `limit=None`, or
   `num_changes` silently maxes out at 5.
2. **Never use the `<li>` scraping fallback for counting.** When no markdown changelog exists,
   `_parse_forge_changelog` falls back to harvesting every `<li>` on the page, which would count
   navigation chrome as changes. For this report, "no markdown section" means blank, full stop.
3. **`num_changes` counts top-level bullets only** (`top_level_only=True`). The existing parser
   flattens indented continuation lines and nested sub-bullets into the same list; for a
   "number of changes" metric a nested bullet is elaboration on its parent, not a separate
   change. PR-link and attribution detection still scan the full bullet text including
   continuation lines, so nothing is lost for attribution. Flagging this as a documented
   assumption — it's the one place `num_changes` is a judgment call rather than a fact.

### `scripts/lib/contributor_classification.py`

Extracted from `05_count_contributions.py`, behavior unchanged:

```python
ATTRIBUTION_RE = re.compile(r"\[([A-Za-z0-9_-]+)\]\(https://github\.com/([A-Za-z0-9_-]+)\)")
def load_classification(config_path) -> Tuple[set, set]
def classify_handle(handle, internal_set, community_set) -> str  # internal|community|unknown
```

`05` keeps its post-scanning loop and imports these instead of defining them locally.

**Bot accounts:** `ATTRIBUTION_RE`'s `[A-Za-z0-9_-]+` cannot match `dependabot[bot]` (brackets),
so bot PRs are invisible to attribution today. That's arguably correct for a *community
contribution* count and requires no change — noting it so the behavior is intentional rather
than accidental.

### `scripts/lib/posts_attribution_cache.py`

```python
def build_pr_author_cache(posts_dir=Path("posts")) -> Dict[str, str]:
    """Scan posts/*.md for '[#N](pull-url) ([login](...))' pairs → {pr_url: login}.
    No network calls."""
```

**Measured value, stated honestly:** mines 115 PR→author pairs from the existing posts, which
covers 4 of the 9 lookups a default run needs — reducing live GitHub calls from 9 to 5. That's
a real but small win. It's ~15 lines and removes a network dependency, so it's worth keeping,
but it is not the load-bearing optimization rev 2 made it out to be. Cut it if you'd prefer
fewer moving parts.

### `scripts/report_module_releases.py`

```
Usage:
    python scripts/report_module_releases.py
    python scripts/report_module_releases.py --start-date 2026-01-01 --end-date 2026-08-17
    python scripts/report_module_releases.py --start-date 2026-03-01      # end defaults to today
    python scripts/report_module_releases.py --output data/custom.csv
    python scripts/report_module_releases.py --no-github-lookups          # fully offline
```

1. Resolve `(start, end)`; print `Resolved range: <start> to <end>` to stderr.
2. Page `v3/modules` via `forge_api.iter_puppetlabs_modules()` — 2 requests, and the only
   network cost for the Forge side.
3. For each module, walk the embedded `releases` array; keep releases where `deleted_at` is null
   and the **UTC** date of `created_at` is within `[start, end]`.
4. Build the posts PR-author cache once.
5. For each kept release, source bullets per the [source-selection rule](#source-selection-is-data-driven-not-list-driven).
   Cache external-docs fetches **by URL** so cd4peadm's shared page is fetched once.
6. Count: `num_changes` = top-level bullets. For each bullet, resolve a handle via
   (a) inline credit, (b) posts cache, then (c) a live GitHub lookup — then classify via
   `classify_handle()`. `community` increments `num_community_contributions`; `unknown`
   increments `num_unknown_contributions`.
   - **Circuit breaker**: on the first 403/429, stop live lookups for the rest of the run, log
     once, and leave remaining bullets unresolved. Retained as cheap insurance even though
     measured load is 5 calls.
   - `--no-github-lookups` skips step (c) entirely for a fully offline run.
7. Write CSV sorted by `release_date` asc, then `module_name`, then `version` desc.
   UTF-8 **with BOM** (`utf-8-sig`) and `newline=''` so Excel on Windows opens it cleanly.
   Always write the header row, even when there are no rows.
8. Print a summary: resolved range, row count, distinct module count, sums of each count column,
   attribution resolution breakdown (inline / posts cache / live / unresolved), any `unknown`
   handles to classify in `config/internal_contributors.yaml`, and any releases that produced
   blank counts and why.

### `.claude/commands/module-releases-report.md`

```
---
description: Generate a CSV report of puppetlabs module releases between two dates
argument-hint: [start-date] [end-date] — e.g. "2026-01-01 2026-08-17"; omit either for defaults
---

Run the module-releases-report skill for: **$ARGUMENTS**

If no dates were given, do not compute "today" or "January 1st" yourself — offer to run the
script with defaults (it resolves and reports the exact range) or ask for a custom range.
```

### `.claude/skills/module-releases-report/SKILL.md`

1. **Resolve inputs.** Normalize supplied dates to `YYYY-MM-DD` (turning "March 2026" into
   `2026-03-01` is text parsing, fine). If either is missing, use `AskUserQuestion` to offer the
   script's computed year-to-date default or a custom range — don't silently guess.
2. **Run the script**, omitting whichever flag should default.
   ```powershell
   .venv\Scripts\python.exe scripts\report_module_releases.py --start-date <start> --end-date <end>
   ```
3. **Read the resolved range back from stderr** and quote exactly that — never restate a
   self-computed date.
4. **Report**: CSV path, row count, distinct modules, totals per count column, any unknown
   handles to classify, and any blank-count releases.

## Documentation to update (part of this change)

Rev 2 omitted these; the repo documents this pipeline by convention:

- [CLAUDE.md](CLAUDE.md) — add the command to the command table and `report_module_releases.py`
  to Key Files; note it's a standalone report, not a pipeline stage.
- [scripts/README.md](scripts/README.md) — per-script section matching the existing style.
- [data/SCHEMA.md](data/SCHEMA.md) — document the CSV schema and the blank-vs-zero rule.

## Verification plan

The refactor touches three working scripts with no test suite, so:

1. Before refactoring, snapshot current outputs for a known month (July 2026): Stage 1 JSON,
   Stage 2 JSON, Stage 5 stdout.
2. After refactoring, re-run and diff — ignoring only the `discovered_at` / `fetched_at`
   timestamps. Any other delta is a regression to fix, not to accept.
3. For the new report, assert the default-window baseline from
   [Expected output size](#expected-output-size) (96 rows / 54 modules), and spot-check
   `haproxy 9.1.0` and `haproxy 9.0.0` as separate rows against the July post, which documents
   both releases.

## Remaining open question

**`num_unknown_contributions` semantics** — implemented as "handle found but unclassified" (the
`05_count_contributions.py` sense), which leaves the 23 no-attribution bullets counted only in
`num_changes`. Flagged in the Goal section above; say the word if you want unattributed folded
in or split into its own column.

## Extension: `--all-publishers` (implemented 2026-08)

Management asked to compare puppetlabs against other Forge publishers, specifically Vox Pupuli
(Forge owner slug `puppet`, confirmed live via `v3/users/puppet`) and a rollup of everyone else.

**Design decisions:**

- The Forge API query drops `owner=puppetlabs` entirely rather than querying per-publisher; the
  full catalog is ~1,501 modules (vs. 108 for puppetlabs alone) across ~16 paged requests and
  took ~18s end to end in testing — cheap enough not to need a narrower default.
- The CSV's new `publisher` column holds the **raw Forge owner slug** per row (`puppetlabs`,
  `puppet`, or an individual maintainer's username) rather than a pre-bucketed value — more
  flexible for downstream pivoting than baking in the puppetlabs/puppet/other split. The script's
  own run summary does bucket into those three groups for a quick terminal read.
- `num_community_contributions`/`num_unknown_contributions` are computed **only** for
  `publisher == 'puppetlabs'` rows, always blank otherwise. Two reasons, both structural rather
  than effort-driven: `config/internal_contributors.yaml` is curated against Puppet/Perforce
  staff and has no meaning for a Vox Pupuli or independent maintainer's contributors; and
  resolving attribution for the whole catalog's changelog bullets would need far more live
  GitHub lookups than the unauthenticated 60/hour limit tolerates (measured: still only 5 live
  lookups for a full YTD `--all-publishers` run, because that's exactly the count that already
  applied to the puppetlabs-only report — attribution resolution never runs for the ~1,393
  non-puppetlabs modules in scope).
- Default off, opt-in via `--all-publishers`, to leave the existing puppetlabs-only report's
  behavior and cost profile unchanged when not requested.
- `manual_review_modules` / blank-`num_changes` name lists in the run summary are capped at 25
  names (falling back to a count) since the full catalog has hundreds of modules using changelog
  formats the parser doesn't recognize — dumping them all into a terminal isn't useful; the CSV
  has the full detail.

## Not in scope

- No behavior change to `01`/`02`/`05` — the refactor moves logic only, verified by diff.
- No highlight curation or post generation; this report only counts.
- **Noted for later, deliberately not done here:** finding 1 means `02_fetch_release_notes.py`
  could drop its per-module changelog fetches too, and finding 1 + full release history means
  `01_discover_modules.py`'s `recover_overshot_releases()` HTML-scraping workaround is no longer
  necessary. Both are real simplifications, but they change working pipeline code for no gain to
  this feature, so they stay out.
