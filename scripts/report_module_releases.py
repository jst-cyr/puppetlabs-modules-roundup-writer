#!/usr/bin/env python3
"""
Module Releases Report

Generates a CSV report of every puppetlabs module released on the Forge
between a start and end date, one row per release. This is a standalone
report, not a stage of the monthly-roundup pipeline -- it reuses that
pipeline's parsing/classification logic (via scripts/lib/) but has its own
data flow: it talks to Forge's v3/modules JSON API directly rather than
scraping HTML, since that API already returns every module's full release
history (and, for Forge-hosted changelogs, the full changelog markdown)
inline. See MODULE_RELEASES_REPORT_SPEC.md for the full design rationale.

--all-publishers extends the same report to every Forge publisher, for
comparing puppetlabs against Vox Pupuli (owner slug `puppet`) and everyone
else -- see that flag's help text for what is and isn't computed for
non-puppetlabs releases.

Usage:
    python scripts/report_module_releases.py
    python scripts/report_module_releases.py --start-date 2026-01-01 --end-date 2026-08-17
    python scripts/report_module_releases.py --start-date 2026-03-01   # end defaults to today
    python scripts/report_module_releases.py --output data/custom.csv
    python scripts/report_module_releases.py --no-github-lookups       # fully offline
    python scripts/report_module_releases.py --all-publishers          # every Forge publisher

Output:
    data/module_releases_report_<start>_<end>.csv (or --output)
    data/module_releases_report_all_publishers_<start>_<end>.csv (with --all-publishers)

CSV columns:
    publisher, module_name, version, release_date, num_changes,
    num_community_contributions, num_unknown_contributions

Blank vs. zero in the count columns is meaningful, not incidental:
  - blank = not knowable from the available source (no changelog section
    found for this release; or the module's release notes carry no
    attribution structure at all, e.g. sce_linux/sce_windows/cd4peadm) --
    OR, for the two contribution columns, this release's publisher isn't
    puppetlabs (see --all-publishers below).
  - 0 = knowable and genuinely zero.
A release always gets a row, even when every count is blank -- this is a
releases report first, and that data is more important than the derived
counts. See "Blank vs. zero" / "Row visibility" in the spec.

--all-publishers reports every Forge publisher, not just puppetlabs (the
default). `publisher` is always the raw Forge owner slug (e.g. puppetlabs,
puppet for Vox Pupuli, or an individual maintainer's username) -- pivot/
bucket it downstream as needed. Contribution counts (community/unknown) are
only ever computed for puppetlabs releases: config/internal_contributors.yaml
is curated against Puppet/Perforce staff and doesn't generalize to other
publishers' contributors, and resolving attribution for the whole catalog's
changelog bullets would need far more live GitHub lookups than the
unauthenticated 60/hour limit allows. Those two columns are always blank for
non-puppetlabs rows, regardless of whether the underlying changelog has
attribution structure.
"""

import argparse
import csv
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urldefrag

import yaml

try:
    import requests
except ImportError:
    print("ERROR: requests required. Install with: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from lib import (
    changelog_parse,
    contributor_classification,
    date_utils,
    external_docs,
    forge_api,
    http_common,
    posts_attribution_cache,
    release_sources,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RELEASE_SOURCES_CONFIG = REPO_ROOT / "config" / "release_notes_sources.yaml"
DEFAULT_CONTRIBUTORS_CONFIG = REPO_ROOT / "config" / "internal_contributors.yaml"
DEFAULT_POSTS_DIR = REPO_ROOT / "posts"
DEFAULT_DATA_DIR = REPO_ROOT / "data"


def load_release_sources_config(path: Path) -> Dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"WARNING: {path} not found; every module will be treated as forge_changelog/default", file=sys.stderr)
        config = {}
    config.setdefault('forge_changelog', [])
    config.setdefault('external_docs', {})
    config.setdefault('manual_review', [])
    config.setdefault('default_source', 'forge_changelog')
    return config


def _parse_utc_date(created_at: str) -> date:
    """Forge's created_at is Pacific-offset; normalize to the UTC calendar
    date, matching 01_discover_modules.py's existing convention (and what's
    already published in posts/)."""
    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S %z')
    return dt.astimezone(timezone.utc).date()


def _version_sort_key(version: str):
    """Best-effort numeric-aware version key for the version-desc tie-break."""
    parts = re.split(r'[.\-+]', version or '')
    key = []
    for p in parts:
        if p.isdigit():
            key.append((0, int(p)))
        else:
            key.append((1, p))
    return tuple(key)


class ReleaseRow:
    __slots__ = (
        'publisher', 'module_name', 'version', 'release_date',
        'num_changes', 'num_community_contributions', 'num_unknown_contributions',
    )

    def __init__(self, publisher: str, module_name: str, version: str, release_date: date):
        self.publisher = publisher
        self.module_name = module_name
        self.version = version
        self.release_date = release_date
        self.num_changes: Optional[int] = None
        self.num_community_contributions: Optional[int] = None
        self.num_unknown_contributions: Optional[int] = None


class AttributionResolver:
    """Resolves a changelog bullet to a classified contribution.

    Resolution order: inline credit already in the bullet -> the posts/*.md
    attribution cache -> a live GitHub lookup (unless the circuit breaker has
    tripped or live lookups are disabled). Tracks resolution-source stats and
    unknown handles for the run summary.
    """

    def __init__(
        self,
        session: requests.Session,
        posts_cache: Dict[str, str],
        internal_set: set,
        community_set: set,
        allow_live_lookups: bool = True,
    ):
        self.session = session
        self.posts_cache = posts_cache
        self.internal_set = internal_set
        self.community_set = community_set
        self.allow_live_lookups = allow_live_lookups
        self.breaker_tripped = False
        self._live_cache: Dict[str, Optional[str]] = {}
        self.stats = {'inline': 0, 'posts_cache': 0, 'live': 0, 'unresolved': 0}
        self.unknown_handles: set = set()

    def resolve(self, bullet: str) -> Optional[str]:
        """Returns 'community' | 'internal' | 'unknown', or None if no
        attribution is possible/resolvable for this bullet at all."""
        handle = None

        inline_match = contributor_classification.ATTRIBUTION_RE.search(bullet)
        if inline_match and inline_match.group(1).lower() == inline_match.group(2).lower():
            handle = inline_match.group(2)
            self.stats['inline'] += 1
        else:
            pr_match = changelog_parse.PR_LINK_RE.search(bullet)
            if not pr_match:
                return None  # no PR reference at all -- unattributable, not "unresolved"

            pr_url = pr_match.group('url')
            if pr_url in self.posts_cache:
                handle = self.posts_cache[pr_url]
                self.stats['posts_cache'] += 1
            elif self.allow_live_lookups and not self.breaker_tripped:
                try:
                    handle = changelog_parse.lookup_pr_author(pr_url, self.session, self._live_cache)
                except changelog_parse.GitHubRateLimitError:
                    print(
                        "WARNING: GitHub API rate limit hit; disabling further live "
                        "lookups for the rest of this run",
                        file=sys.stderr,
                    )
                    self.breaker_tripped = True
                    self.stats['unresolved'] += 1
                    return None
                if handle:
                    self.stats['live'] += 1
                else:
                    self.stats['unresolved'] += 1
                    return None
            else:
                self.stats['unresolved'] += 1
                return None

        if handle is None:
            return None

        result = contributor_classification.classify_handle(handle, self.internal_set, self.community_set)
        if result == 'unknown':
            self.unknown_handles.add(handle)
        return result


def _get_external_docs_html(session, html_cache: Dict[str, Optional[str]], fetch_url: str, module_name: str) -> Optional[str]:
    """Fetch (and cache by URL) an external-docs page's HTML.

    Cached by the de-fragmented URL so a module whose in-range releases all
    share one page differentiated only by anchor (e.g. cd4peadm) is fetched
    once, not once per release.
    """
    if fetch_url in html_cache:
        return html_cache[fetch_url]

    try:
        response = session.get(fetch_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"WARNING: Failed to fetch external docs for {module_name} ({fetch_url}): {e}", file=sys.stderr)
        html_cache[fetch_url] = None
        return None

    html_cache[fetch_url] = response.text
    return response.text


def build_rows(
    session: requests.Session,
    start_date: date,
    end_date: date,
    release_sources_config: Dict,
    resolver: AttributionResolver,
    owner: Optional[str] = None,
) -> Tuple[List[ReleaseRow], set]:
    """Fetch the module list (scoped to `owner`, or every publisher if None)
    and build one ReleaseRow per in-range release."""
    rows: List[ReleaseRow] = []
    manual_review_modules: set = set()
    external_docs_html_cache: Dict[str, Optional[str]] = {}

    if owner:
        print(f"Fetching {owner} module list from Forge...", file=sys.stderr)
    else:
        print("Fetching full Forge module catalog (all publishers)...", file=sys.stderr)
    modules = list(forge_api.iter_forge_modules(session, owner=owner))
    print(f"Discovered {len(modules)} modules", file=sys.stderr)

    for module in modules:
        name = module.get('name', '')
        publisher = (module.get('owner') or {}).get('slug', '')
        # Contribution classification is curated against Puppet/Perforce
        # staff (config/internal_contributors.yaml) and doesn't generalize
        # to other publishers' contributors, so it's only ever computed for
        # puppetlabs releases -- see the --all-publishers module docstring.
        classify_attribution = publisher == 'puppetlabs'
        current_release = module.get('current_release') or {}
        changelog_md = current_release.get('changelog') or ''

        in_range: List[Tuple[str, date]] = []
        for release in module.get('releases') or []:
            created_at = release.get('created_at')
            if not created_at or release.get('deleted_at'):
                continue
            try:
                release_date = _parse_utc_date(created_at)
            except ValueError:
                continue
            if start_date <= release_date <= end_date:
                in_range.append((release.get('version', ''), release_date))

        if not in_range:
            continue

        sections_by_version = {}
        if changelog_md.strip():
            sections = changelog_parse.extract_release_sections(changelog_md, top_level_only=True)
            for section in sections:
                sections_by_version[changelog_parse.normalize_version(section['version'])] = section

        for version, release_date in in_range:
            row = ReleaseRow(publisher, name, version, release_date)
            norm_version = changelog_parse.normalize_version(version)
            section = sections_by_version.get(norm_version)

            if section is not None:
                bullets = section['bullets']
                row.num_changes = len(bullets)
                if classify_attribution:
                    community = unknown = 0
                    for bullet in bullets:
                        result = resolver.resolve(bullet)
                        if result == 'community':
                            community += 1
                        elif result == 'unknown':
                            unknown += 1
                    row.num_community_contributions = community
                    row.num_unknown_contributions = unknown
                # else: contribution columns stay blank by design (not
                # "unknowable from source" -- just out of scope for this
                # publisher).
            else:
                source_info = release_sources.get_release_notes_source(name.lower(), release_sources_config)
                if source_info['source'] == 'external_docs':
                    ext_config = source_info['config']
                    url = release_sources.build_external_docs_url(name, version, ext_config)
                    fetch_url, anchor = urldefrag(url)
                    html = _get_external_docs_html(session, external_docs_html_cache, fetch_url, name)
                    if html is not None:
                        parser_type = ext_config.get('parser_type')
                        if parser_type == 'madcap_flare':
                            bullets = external_docs.parse_madcap_flare(
                                html, anchor=anchor, version=version, module_name=name, limit=None,
                            )
                        else:
                            bullets = external_docs.parse_external_docs(html, limit=None)
                        row.num_changes = len(bullets)
                    # num_community_contributions / num_unknown_contributions stay
                    # blank: prose release notes have no attribution structure.
                else:
                    manual_review_modules.add(name)
                    # everything stays blank: no automated bullet source at all.

            rows.append(row)

    return rows, manual_review_modules


def write_csv(rows: List[ReleaseRow], output_path: Path) -> None:
    # Stable multi-pass sort: version desc within a (publisher, release_date,
    # module_name) tie, publisher/release_date/module_name asc otherwise.
    # publisher is constant across all rows in a puppetlabs-only run, so this
    # doesn't change that mode's existing ordering.
    rows.sort(key=lambda r: _version_sort_key(r.version), reverse=True)
    rows.sort(key=lambda r: (r.publisher, r.release_date, r.module_name))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig (BOM) + newline='' so Excel on Windows opens this cleanly.
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            'publisher', 'module_name', 'version', 'release_date',
            'num_changes', 'num_community_contributions', 'num_unknown_contributions',
        ])
        for row in rows:
            writer.writerow([
                row.publisher,
                row.module_name,
                row.version,
                row.release_date.isoformat(),
                row.num_changes if row.num_changes is not None else '',
                row.num_community_contributions if row.num_community_contributions is not None else '',
                row.num_unknown_contributions if row.num_unknown_contributions is not None else '',
            ])


def _publisher_bucket(publisher: str) -> str:
    if publisher == 'puppetlabs':
        return 'puppetlabs'
    if publisher == 'puppet':
        return 'puppet (Vox Pupuli)'
    return 'other'


_NAME_LIST_PRINT_LIMIT = 25


def _print_name_list(label: str, names) -> None:
    """Print a sorted name list inline if short, else just the count -- a
    full-catalog run can turn these into hundreds of names, which isn't
    useful to dump into a terminal."""
    names = sorted(names)
    if not names:
        return
    if len(names) <= _NAME_LIST_PRINT_LIMIT:
        print(f"{label}: {', '.join(names)}")
    else:
        print(f"{label}: {len(names)} (see CSV; too many to list here)")


def print_summary(
    rows: List[ReleaseRow],
    output_path: Path,
    start_date: date,
    end_date: date,
    resolver: AttributionResolver,
    manual_review_modules: set,
) -> None:
    def total(attr, subset=rows):
        return sum(getattr(r, attr) for r in subset if getattr(r, attr) is not None)

    distinct_modules = {r.module_name for r in rows}
    distinct_publishers = {r.publisher for r in rows}
    blank_change_rows = [r for r in rows if r.num_changes is None]

    print(f"\nModule releases report: {output_path}")
    print(f"Resolved range: {start_date.isoformat()} to {end_date.isoformat()}")
    print(f"Releases (rows): {len(rows)}")
    print(f"Distinct modules: {len(distinct_modules)}")
    print(f"Total changes: {total('num_changes')}")
    print(f"Total community contributions: {total('num_community_contributions')}")
    print(f"Total unknown-handle contributions: {total('num_unknown_contributions')}")
    print(
        "Attribution resolution: "
        f"inline={resolver.stats['inline']} "
        f"posts_cache={resolver.stats['posts_cache']} "
        f"live={resolver.stats['live']} "
        f"unresolved={resolver.stats['unresolved']}"
    )
    if resolver.breaker_tripped:
        print("NOTE: GitHub rate limit was hit; some contributions may be undercounted.")
    if resolver.unknown_handles:
        _print_name_list("Unknown handles (add to config/internal_contributors.yaml)", resolver.unknown_handles)

    if len(distinct_publishers) > 1:
        print("\nBy publisher:")
        buckets: Dict[str, List[ReleaseRow]] = {}
        for row in rows:
            buckets.setdefault(_publisher_bucket(row.publisher), []).append(row)
        for bucket_name in ('puppetlabs', 'puppet (Vox Pupuli)', 'other'):
            bucket_rows = buckets.get(bucket_name)
            if not bucket_rows:
                continue
            bucket_modules = {r.module_name for r in bucket_rows}
            line = (
                f"  {bucket_name}: {len(bucket_rows)} releases, {len(bucket_modules)} modules, "
                f"{total('num_changes', bucket_rows)} changes"
            )
            if bucket_name == 'puppetlabs':
                line += f", {total('num_community_contributions', bucket_rows)} community contributions"
            else:
                line += " (contribution counts not computed for non-puppetlabs publishers)"
            if bucket_name == 'other':
                distinct_others = {r.publisher for r in bucket_rows}
                line += f" -- {len(distinct_others)} distinct publishers"
            print(line)

    if manual_review_modules:
        _print_name_list("\nModules with no automated bullet source (blank counts)", manual_review_modules)
    if blank_change_rows:
        names = [f"{r.publisher}/{r.module_name} {r.version}" for r in blank_change_rows]
        if len(names) <= _NAME_LIST_PRINT_LIMIT:
            print(
                "Releases with blank num_changes (no matching changelog/docs source found): "
                + ", ".join(names)
            )
        else:
            print(
                f"Releases with blank num_changes (no matching changelog/docs source found): "
                f"{len(names)} (see CSV; too many to list here)"
            )


def main():
    parser = argparse.ArgumentParser(
        description='Generate a CSV report of puppetlabs module releases between two dates'
    )
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD); defaults to Jan 1 of the current year')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD); defaults to today')
    parser.add_argument(
        '--output',
        help='Output CSV path (default: data/module_releases_report_<start>_<end>.csv)',
    )
    parser.add_argument(
        '--config',
        default=str(DEFAULT_RELEASE_SOURCES_CONFIG),
        help='Path to release_notes_sources.yaml',
    )
    parser.add_argument(
        '--contributors-config',
        default=str(DEFAULT_CONTRIBUTORS_CONFIG),
        help='Path to internal_contributors.yaml',
    )
    parser.add_argument(
        '--posts-dir',
        default=str(DEFAULT_POSTS_DIR),
        help='Path to posts/ directory used to seed the PR-author attribution cache',
    )
    parser.add_argument(
        '--no-github-lookups',
        action='store_true',
        help='Disable live GitHub API lookups entirely; unresolved PR credits are left unattributed',
    )
    parser.add_argument(
        '--all-publishers',
        action='store_true',
        help=(
            'Report releases across every Forge publisher, not just puppetlabs. '
            'Adds a publisher column (raw Forge owner slug); contribution counts '
            '(community/unknown) are still only computed for puppetlabs releases.'
        ),
    )
    args = parser.parse_args()

    try:
        start_date, end_date = date_utils.resolve_date_range(args.start_date, args.end_date)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Resolved range: {start_date.isoformat()} to {end_date.isoformat()}", file=sys.stderr)

    release_sources_config = load_release_sources_config(Path(args.config))
    internal_set, community_set = contributor_classification.load_classification(Path(args.contributors_config))

    posts_cache = posts_attribution_cache.build_pr_author_cache(Path(args.posts_dir))
    print(f"Mined {len(posts_cache)} PR->author credits from {args.posts_dir}", file=sys.stderr)

    session = http_common.make_session()
    resolver = AttributionResolver(
        session, posts_cache, internal_set, community_set,
        allow_live_lookups=not args.no_github_lookups,
    )

    owner = None if args.all_publishers else 'puppetlabs'
    rows, manual_review_modules = build_rows(
        session, start_date, end_date, release_sources_config, resolver, owner=owner,
    )

    if args.output:
        output_path = Path(args.output)
    else:
        suffix = '_all_publishers' if args.all_publishers else ''
        output_path = DEFAULT_DATA_DIR / f"module_releases_report{suffix}_{start_date:%Y%m%d}_{end_date:%Y%m%d}.csv"

    write_csv(rows, output_path)
    print_summary(rows, output_path, start_date, end_date, resolver, manual_review_modules)


if __name__ == '__main__':
    main()
