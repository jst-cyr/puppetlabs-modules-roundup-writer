# Module Releases Report — Implementation Spec (for review)

Status: **draft, not yet implemented**. This document describes the proposed design for a new
`/module-releases-report` command. Nothing in this spec has been built yet — it's here for
sign-off before writing code.

Revision note: this supersedes an earlier draft. The CSV requirements grew to include per-release
change/contribution counts, which changes the architecture significantly (see "What changed
since the first draft" below) — it's no longer just a version/date listing.

## Goal

A new skill/command that produces a CSV report of every `puppetlabs` module released on the
Forge between a start date and an end date, with one row per release:

| Column | Example | Source |
|---|---|---|
| `module_name` | `stdlib` | Forge |
| `version` | `10.0.2` | Forge |
| `release_date` | `2026-08-06` | Forge |
| `num_changes` | `4` | count of changelog bullets for that version; blank only if no bullets could be sourced at all |
| `num_community_contributions` | `1` | subset of those bullets attributed to a non-Puppet/Perforce GitHub handle; blank (not `0`) when this module's release notes carry no attribution data at all |

- Command: `/module-releases-report [start-date] [end-date]`
- If either date is omitted, the skill offers to continue with computed defaults instead of
  asking the user to do date arithmetic:
  - **Start default**: January 1st of the current calendar year
  - **End default**: today
- The *script*, not the skill, computes these defaults from the real clock. The skill never
  invents or calculates "today" or "Jan 1" itself — it either passes explicit dates through, or
  leaves them off and lets the script fill the gap and report back what it used.
- Module scope matches `01_discover_modules.py`: `module_groups=base+pe_only`, owner
  `puppetlabs`, deprecated modules excluded.
- Output: a CSV in the existing (gitignored) `data/` folder, e.g.
  `data/module_releases_report_20260101_20260817.csv`.

## What changed since the first draft

The first draft only needed module/version/date, which Forge's `v3/modules` JSON API returns
inline for every module in ~2 requests total (confirmed empirically last round). Counting
**changes** and **community contributions** per release needs actual changelog bullet text,
which that API does not provide — so this now needs the same kind of changelog-parsing the
pipeline already does in Stage 2, generalized from "one target month" to "an arbitrary date
range," plus the same contributor classification Stage 5 already does, applied per-release
instead of per-post.

I re-verified two things live before finalizing this design:

1. **One HTTP fetch per module is enough, regardless of range length.** Forge's
   `/modules/puppetlabs/{slug}/releases` page embeds the module's *entire* markdown
   `CHANGELOG.md` in its Next.js payload — not just the latest version. For `stdlib` this came
   back with **99** `## `-headed version sections spanning 2011 to 2026-08-06. So a full
   year-to-date (or even multi-year) report still costs one request per module for changelog
   content, same as the existing single-month pipeline does today.
2. **The bullet attribution format matches `05_count_contributions.py`'s regex exactly.** e.g.:
   ```
   - fix(stdlib::manage) parser fails `$type` resources [#1477](.../pull/1477) ([jcpunk](https://github.com/jcpunk))
   ```
   `ATTRIBUTION_RE` in `05_count_contributions.py` already extracts `jcpunk` from that pattern.
   The same regex, applied to individual bullets instead of a whole rendered post, is exactly
   the "is this change a community contribution" check this report needs.

Net effect: this report is best understood as **Stage 1 (module discovery) + Stage 2
(changelog fetch/parse) + Stage 5 (contributor classification), all generalized from
"one target month" to "an arbitrary date range,"** rather than a lightweight new script. That
generalization is exactly the kind of shared-logic extraction the project asked for, so the
plan below pulls the reusable engines out of `01`/`02`/`05` into `scripts/lib/` rather than
copy-pasting or reimplementing them.

One more piece landed after checking an actual post: rather than hitting GitHub's API to
resolve PR authorship for bullets that lack inline credit, the already-published `posts/*.md`
files are themselves a free, durable cache of exactly those resolutions (see
`posts_attribution_cache.py` below) — since each post baked in the result of that same lookup
when it was originally generated. That cache is checked **first**, so it absorbs almost all of
the load; live GitHub lookups remain the default fallback for whatever the cache doesn't cover,
since accuracy matters more here than avoiding network calls. A run-level circuit breaker (see
"Risk / accuracy caveats" below) stops making live calls for the rest of that run if GitHub
starts rate-limiting, rather than grinding through 60+ more failed requests.

## Proposed file layout

```
scripts/
  lib/
    __init__.py
    http_common.py              # NEW — shared requests.Session/User-Agent/error handling
    date_utils.py                # NEW — default_date_range(), resolve_date_range()
    release_sources.py           # NEW — extracted from ModuleDiscovery in 01_discover_modules.py
    forge_changelog.py           # NEW — extracted from ReleaseNotesFetcher in 02_fetch_release_notes.py
    contributor_classification.py # NEW — extracted from 05_count_contributions.py
    posts_attribution_cache.py   # NEW — mines posts/*.md for already-resolved PR-author credits
  01_discover_modules.py         # refactored to call lib/release_sources.py (behavior-preserving)
  02_fetch_release_notes.py      # refactored to call lib/forge_changelog.py (behavior-preserving)
  05_count_contributions.py      # refactored to call lib/contributor_classification.py (behavior-preserving)
  06_module_releases_report.py   # NEW — the report script
.claude/
  commands/
    module-releases-report.md    # NEW
  skills/
    module-releases-report/
      SKILL.md                  # NEW
```

Each existing script keeps its current CLI and output — the refactor moves logic, it doesn't
change behavior. I'd verify that with a regression check (re-run a recent month's Stage 1/2/5
before and after the refactor and diff the outputs) before considering it done.

### `scripts/lib/http_common.py`

```python
USER_AGENT = "puppetlabs-roundup-bot/1.0"

def make_session() -> requests.Session: ...
```

Removes the copy-pasted `session.headers.update({'User-Agent': ...})` currently duplicated in
`ModuleDiscovery` and `ReleaseNotesFetcher`.

### `scripts/lib/date_utils.py`

```python
def default_date_range(today: Optional[date] = None) -> Tuple[date, date]:
    """(Jan 1 of today.year, today). `today` exists only for testability —
    production calls always resolve it from datetime.now()."""

def resolve_date_range(
    start_str: Optional[str], end_str: Optional[str], today: Optional[date] = None
) -> Tuple[date, date]:
    """Parse YYYY-MM-DD strings where given; fall back to default_date_range()
    for whichever side is missing. Raises ValueError if start > end."""
```

This is the piece that directly satisfies "the script calculates dates, not the skill." The
skill can omit `--start-date`/`--end-date` entirely; the script always prints the resolved
range to stderr so nothing is silently assumed.

### `scripts/lib/release_sources.py`

Extracted from `ModuleDiscovery.get_release_notes_source()` / `_build_external_docs_url()` in
`01_discover_modules.py`, unchanged in behavior:

```python
def get_release_notes_source(module_slug: str, config: dict) -> dict: ...
def build_external_docs_url(module_name: str, version: str, config: dict) -> str: ...
```

`01_discover_modules.py`'s `ModuleDiscovery` calls these instead of defining them inline.
`06_module_releases_report.py` uses the same functions to decide, per module, whether to parse
a Forge changelog or an external (help.puppet.com) doc for a given release.

### `scripts/lib/forge_changelog.py`

Extracted from `ReleaseNotesFetcher` in `02_fetch_release_notes.py`. The key generalization:
today's `_filter_sections_by_month(sections, target_month, target_year)` becomes
`filter_sections_by_range(sections, start_date, end_date)` — a strict generalization, since a
month is just a range from its 1st to its last day. Everything else moves over unchanged:

```python
def fetch_changelog_markdown(session, module_slug) -> Optional[str]: ...      # one GET, full history
def extract_release_sections(changelog_markdown) -> List[dict]:               # {version, release_date, bullets}
def filter_sections_by_range(sections, start_date, end_date) -> List[dict]: ...
def fetch_external_docs_bullets(session, url, parser_type) -> List[str]: ...  # madcap_flare / generic
def enrich_bullet_attribution(bullet, session, pr_author_cache) -> str: ...   # GitHub PR-author lookup
```

`02_fetch_release_notes.py` becomes a thin wrapper: it computes the target month's first/last
day and calls `filter_sections_by_range` with that, instead of duplicating the parsing engine.

**Version-string matching note:** older changelog headings are inconsistent about a leading
`v` (`## [v10.0.2](...)` vs `## [0.1.5](...)`), while the canonical version field from Forge's
module-listing API is always bare (`10.0.2`). Matching a release (found via listing/API data)
to its changelog section needs a `v`-stripping normalization on both sides — noting this
explicitly since it's an easy off-by-a-character-prefix bug.

### `scripts/lib/contributor_classification.py`

Extracted from `05_count_contributions.py`, unchanged in behavior:

```python
ATTRIBUTION_RE = re.compile(r"\[([A-Za-z0-9_-]+)\]\(https://github\.com/([A-Za-z0-9_-]+)\)")

def load_classification(config_path) -> Tuple[set, set]: ...          # (internal, community) lowercased handles
def classify_handle(handle, internal_set, community_set) -> str: ...  # "internal" | "community" | "unknown"
```

`05_count_contributions.py` keeps its own post-scanning loop (that part is specific to scanning
a whole rendered post) but imports the regex/classification helpers from here instead of
defining them locally. `06_module_releases_report.py` applies the same regex/classification
per-bullet instead of per-post.

### `scripts/lib/posts_attribution_cache.py`

**This replaces the "hit the GitHub API" plan from the first draft.** Every already-published
post in `posts/` was generated by a pipeline run that already did the expensive part — looking
up, via GitHub's API, which login authored a PR that a changelog bullet didn't already credit
inline — and baked the result into the post as `[#N](pull url) ([login](https://github.com/login))`.
That's a durable, free, local record of PR → author resolutions we can reuse instead of asking
GitHub again for the same PR.

```python
def build_pr_author_cache(posts_dir: Path = Path("posts")) -> Dict[str, str]:
    """Scan every posts/*.md for '[#N](pull url) ([login](...))' credit pairs
    (reusing forge_changelog's existing _PR_LINK_RE / _AUTHOR_CREDIT_RE patterns)
    and return {pull_request_url: login}. Mined once per report run, from files
    already tracked in git — no network calls."""
```

`06_module_releases_report.py` builds this cache once at startup and passes it as the *seed*
for `forge_changelog.enrich_bullet_attribution()`'s author cache. Any PR already credited in a
past roundup resolves for free; only a PR that (a) lacks inline credit in the raw changelog
**and** (b) was never mentioned in any published post needs a live lookup — see below for how
that's handled by default.

Since the pipeline has published a post for essentially every month from December 2025 through
July 2026 (see `posts/`), this cache alone covers almost the entire *default* report window
(Jan 1 → today) already — the only real gap is whatever has released in the current,
not-yet-rounded-up month.

### `scripts/06_module_releases_report.py`

```
Usage:
    python scripts/06_module_releases_report.py
    python scripts/06_module_releases_report.py --start-date 2026-01-01 --end-date 2026-08-17
    python scripts/06_module_releases_report.py --start-date 2026-03-01   # end defaults to today
    python scripts/06_module_releases_report.py --output data/custom_name.csv
```

Behavior:

1. Resolve `(start, end)` via `date_utils.resolve_date_range(...)`. Print the resolved range to
   stderr, e.g. `Resolved range: 2026-01-01 to 2026-08-17`.
2. Discover the full puppetlabs module list, same scope as `01_discover_modules.py`
   (`module_groups=base+pe_only`, owner `puppetlabs`, deprecated excluded), paging Forge's
   `v3/modules` API (`limit=100`, follow `pagination.next` until null — puppetlabs currently
   has 108 modules under this filter, so 2 pages). Each module's response includes its full
   `releases` array (`{version, created_at, ...}`) inline — this is the authoritative source
   for "does this module have a release inside `[start, end]`," no extra request needed.
3. Keep only `{module, version, release_date}` entries whose `created_at` date falls in
   `[start, end]` inclusive.
4. For every module with at least one in-range release, look up its `release_notes_source` via
   `release_sources.get_release_notes_source()` and fetch bullets:
   - **`forge_changelog`** (the default, and the overwhelming majority of modules): one GET for
     the module's full changelog history, `extract_release_sections()` + version-string match
     (normalizing the `v` prefix) against the in-range versions from step 3. Both `num_changes`
     and `num_community_contributions` are populated — these changelogs are the GitHub-hosted
     `CHANGELOG.md` for a public repo, so a real (possibly zero) contribution count is knowable.
   - **`external_docs`** (currently `sce_linux`, `sce_windows`, `cd4peadm`, `comply`,
     `complyadm` — the Puppet Enterprise / premium modules whose docs live on
     help.puppet.com instead of a public GitHub repo): one GET **per in-range version**, since
     these docs are versioned by URL rather than rolled up into one page. `num_changes` is
     populated from the parsed bullets, but `num_community_contributions` is left **blank**,
     not `0` — these are prose release notes with no GitHub PR/attribution structure at all
     (confirmed against the July post: `cd4peadm`, `comply`, and `sce_linux` entries have zero
     attribution links in any bullet), so "how many were community contributions" isn't a
     question this source can answer, and reporting `0` would misrepresent "unknown" as "known
     to be zero."
   - **`manual_review`**: no automated bullet source at all. Emit the row with both
     `num_changes` and `num_community_contributions` left blank, and flag it in the run summary
     — mirrors how the existing pipeline already surfaces `manual_review` as a human follow-up.
     (The config currently has zero modules in this bucket, so this is a defensive path, not a
     live one.) The row is always emitted, never omitted — see "Row visibility" below.
5. Before scoring any bullets, build the PR-author cache from `posts/*.md` via
   `posts_attribution_cache.build_pr_author_cache()` — one-time, no network calls.
6. For each matched release: `num_changes` = bullet count. For `num_community_contributions`,
   each bullet resolves a GitHub handle in one of three ways, in order, **live lookups on by
   default**:
   1. Inline credit already in the bullet (`ATTRIBUTION_RE` matches directly) — free.
   2. No inline credit, but the bullet's PR URL is in the posts-mined cache — free.
   3. No inline credit and not in the cache — live lookup via
      `forge_changelog.enrich_bullet_attribution()` (the same GitHub API call
      `02_fetch_release_notes.py` already makes), **unless the run's circuit breaker has
      already tripped** (see below), in which case it's skipped like path 3 in the earlier
      draft. A `--no-github-lookups` flag disables live lookups entirely up front, for a
      fully offline run when you already know you want to trade accuracy for zero network use
      (e.g. you know you're rate-limited from other work).
   - **Circuit breaker**: the first time a live lookup gets a 403/429 (rate-limited) response,
     stop attempting further live lookups for the rest of this run — log it once, and treat
     every remaining unresolved bullet as path-3-skipped rather than retrying into the same
     wall. This is the "we'll turn off if we're hitting limits" behavior, automatic and
     per-run rather than something you have to notice and Ctrl-C for.
   - Optionally honors a `GITHUB_TOKEN` env var, if set, to authenticate lookups (5000/hour
     instead of 60/hour) — opt-in, so "no API keys required" still holds for the default path.

   Once a handle is resolved (by whichever path), it's classified `internal`/`community`/
   `unknown` via `contributor_classification.classify_handle()` against
   `config/internal_contributors.yaml`; only `community` counts toward
   `num_community_contributions`. `unknown` handles are collected and reported in the run
   summary instead of guessed, same as `05` does today.
7. Write CSV rows sorted by `release_date` ascending, then `module_name`, to
   `data/module_releases_report_{start:%Y%m%d}_{end:%Y%m%d}.csv` (or `--output`).
8. Print a summary to stdout: resolved range, total release rows, sum of `num_changes`, sum of
   `num_community_contributions`, how many bullets were resolved from inline credit / the posts
   cache / a live lookup / left unresolved (circuit breaker tripped or `--no-github-lookups`),
   any `unknown` handles encountered (reminder to update `config/internal_contributors.yaml`),
   and any modules that hit `manual_review`.

### `.claude/commands/module-releases-report.md`

```
---
description: Generate a CSV report of puppetlabs module releases between two dates
argument-hint: [start-date] [end-date] — e.g. "2026-01-01 2026-08-17"; omit either or both for defaults
---

Run the module-releases-report skill for: **$ARGUMENTS**

If no dates were given above, do not compute "today" or "January 1st" yourself — offer to run
the script with defaults (it will resolve and report the exact range) or ask the user for a
custom range.
```

### `.claude/skills/module-releases-report/SKILL.md`

Mirrors `monthly-roundup`'s structure at a much smaller scale:

1. **Resolve inputs.** If the user supplied both dates in `$ARGUMENTS`, normalize to
   `YYYY-MM-DD` (natural phrasing like "March 2026" → `2026-03-01` is fine to normalize here —
   that's text parsing, not date-math invention). If one or both are missing, ask
   (`AskUserQuestion`) whether to continue with the script's computed default (year-to-date) or
   supply a custom range — don't silently guess.
2. **Run the script** with whatever flags are known; leave the rest for the script to default.
   ```powershell
   .venv\Scripts\python.exe scripts\06_module_releases_report.py --start-date <start> --end-date <end>
   ```
   (Omit either flag if the user chose defaults for that side.)
3. **Read back the resolved range** from the script's stderr output and use exactly that
   string when reporting to the user — never restate a self-computed date.
4. **Report**: CSV path, total release rows, total changes, total community contributions, any
   unknown handles the user should classify, and the resolved date range.

## Risk / accuracy caveats to flag now

1. **GitHub API rate limiting is still possible, just cheaper to hit.** The posts cache absorbs
   most of the load (everything already covered by a published roundup), so live calls should
   be rare in the common case — but a report range that includes the current in-progress month,
   or a first-ever run against a wide historical range, can still generate enough live lookups
   to hit the unauthenticated 60/hour limit. The circuit breaker (above) makes that a clean,
   bounded degradation — remaining bullets in that run are left unresolved rather than the run
   spending minutes failing the same call repeatedly — but it does mean
   `num_community_contributions` can still undercount for whatever's left unresolved when the
   breaker trips. That's the accuracy/reliability tradeoff being made explicit, not hidden.
2. **Version-string normalization** between the listing API (bare `10.0.2`) and changelog
   headings (mixed `v10.0.2` / `0.1.5` style) — called out above, needs explicit handling on
   both sides of the match.
3. **`manual_review` row handling — open decision**, see below.

## Confirmed decisions (from your last message)

1. **Row granularity**: one row per release. Confirmed — matches the "see all releases" intent
   behind the change/contribution columns.
2. **Module scope**: same as `01_discover_modules.py` (`base+pe_only`, no deprecated).
   Confirmed.
3. **Output location**: existing `data/` folder. Confirmed.
4. **Attribution accuracy**: fall back to a live GitHub API call by default (not skip-by-default);
   a per-run circuit breaker backs off automatically if the API starts rate-limiting. Confirmed.
5. **Row visibility**: every release in range always gets a CSV row — this is a releases report
   first, and that data is more important than the derived counts. `manual_review` releases
   (currently none exist) get the row with both count columns blank. `external_docs` releases
   (the PE/premium modules with no public GitHub source — `sce_linux`, `sce_windows`,
   `cd4peadm`, `comply`, `complyadm`) get the row with `num_changes` populated but
   `num_community_contributions` left blank, since that source has no attribution data to
   report, known-zero or otherwise. A release never disappears from the CSV just because part
   of its data isn't derivable.

## Not in scope for this change

- No change to what `01`/`02`/`05` output — the refactor is purely moving logic into `lib/`,
  not changing behavior. Regression-check against real output before calling it done.
- No changelog authoring, highlight curation, or post generation — this report only counts.
