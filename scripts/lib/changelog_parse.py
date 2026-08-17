"""Forge markdown-changelog parsing and PR-attribution enrichment.

Extracted from ReleaseNotesFetcher in 02_fetch_release_notes.py. The key
generalization versus the original: `_filter_sections_by_month(sections,
month, year)` becomes `filter_sections_by_range(sections, start, end)` -- a
month is just a range from its 1st to its last day, so this is a strict
generalization, not a behavior change for 02's month-based calls.

Bullet enrichment (attaching a GitHub PR-author credit when one is missing)
is intentionally *not* automatic inside bullet parsing here, unlike the
original code where it happened inline as each bullet was flushed. Callers
that want that exact original behavior pass a `bullet_transform` callback
(see 02_fetch_release_notes.py); report_module_releases.py instead resolves
attribution itself per-bullet, with its own cache/circuit-breaker policy.
"""

import re
import sys
from datetime import datetime, date
from typing import Callable, Dict, List, Optional

import requests

# Matches a PR reference such as "[#25](https://github.com/org/repo/pull/25)",
# optionally wrapped in parentheses, as older changelogs do.
PR_LINK_RE = re.compile(
    r'(?P<lp>\(?)\[#(?P<num>\d+)\]\((?P<url>https://github\.com/[^/]+/[^/]+/pull/\d+)\)(?P<rp>\)?)'
)
# Matches an author profile credit such as "([smortex](https://github.com/smortex))".
AUTHOR_CREDIT_RE = re.compile(r'\(\[[^\]]+\]\(https://github\.com/[^/)]+\)\)')

_HEADING_VERSION_RE = re.compile(r'\b(?:v)?(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9._-]+)?)\b')
_HEADING_DATE_RE = re.compile(r'\b(20\d{2}-\d{2}-\d{2})\b')


class GitHubRateLimitError(Exception):
    """Raised when a live PR-author lookup is rate-limited (403/429)."""

    def __init__(self, api_url: str):
        super().__init__(f"GitHub API rate limit hit looking up {api_url}")
        self.api_url = api_url


def normalize_version(version: str) -> str:
    """Strip a leading v/V so listing-API versions and changelog-heading
    versions compare equal (e.g. 'v10.0.2' / '10.0.2')."""
    return (version or '').strip().lstrip('vV').strip()


def clean_text(text: str) -> str:
    """Normalize extracted list item text."""
    cleaned = re.sub(r'\s+', ' ', text or '').strip()
    if len(cleaned) < 8:
        return ''
    if cleaned.lower().startswith('version '):
        return ''
    return cleaned


def dedupe_and_limit(items: List[str], limit: Optional[int] = 5) -> List[str]:
    """Deduplicate (case-insensitive) while preserving order, then limit list size."""
    seen = set()
    result: List[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
        if limit is not None and len(result) >= limit:
            break
    return result


def bullets_from_lines(section_lines: List[str], top_level_only: bool = False) -> List[str]:
    """Turn markdown changelog lines into bullet strings.

    A list item (``- ``/``* ``) may wrap onto indented continuation lines --
    those are merged into the current bullet until a blank line, a heading,
    or the next list item ends it.

    When `top_level_only` is False (the default, matching the original
    parser's behavior exactly), indentation is ignored entirely: any line
    starting with a list marker begins a new bullet, regardless of how far
    it's indented. When True, a marker line indented deeper than this
    section's shallowest marker is treated as a *nested* sub-bullet -- its
    text is folded into the current top-level bullet (so it's still visible
    to attribution scanning) rather than counted as a separate bullet.
    """
    def is_marker(stripped: str) -> bool:
        return stripped.startswith('- ') or stripped.startswith('* ')

    base_indent = None
    if top_level_only:
        indents = [
            len(line) - len(line.lstrip())
            for line in section_lines
            if is_marker(line.strip())
        ]
        if indents:
            base_indent = min(indents)

    marker_re = re.compile(r'^[-*]\s+')
    bullets: List[str] = []
    current: Optional[List[str]] = None

    def flush():
        nonlocal current
        if current:
            cleaned = clean_text(' '.join(current))
            if cleaned:
                bullets.append(cleaned)
        current = None

    for line in section_lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if is_marker(stripped):
            nested = top_level_only and base_indent is not None and indent > base_indent
            if nested:
                if current is not None:
                    current.append(marker_re.sub('', stripped))
                continue
            flush()
            current = [marker_re.sub('', stripped)]
        elif not stripped or stripped.startswith('#'):
            flush()
        elif current is not None:
            current.append(stripped)

    flush()
    return bullets


def extract_release_sections(
    changelog_markdown: str,
    top_level_only: bool = False,
    bullet_transform: Optional[Callable[[str], str]] = None,
) -> List[Dict]:
    """Parse a full markdown changelog into per-version release sections.

    Returns a list of {version, release_date, bullets}, most recent first.
    `bullet_transform`, if given, is applied to each raw bullet *before*
    deduping -- this is the hook 02_fetch_release_notes.py uses to enrich
    bullets with PR-author attribution in the same order the original inline
    implementation did, so its output stays identical.
    """
    lines = changelog_markdown.splitlines()
    sections: List[Dict] = []
    current_heading = ''
    current_lines: List[str] = []

    def build(heading: str, section_lines: List[str]) -> Optional[Dict]:
        version_match = _HEADING_VERSION_RE.search(heading)
        if not version_match:
            return None

        release_date_match = _HEADING_DATE_RE.search(heading)
        release_date = release_date_match.group(1) if release_date_match else ''

        bullets = bullets_from_lines(section_lines, top_level_only=top_level_only)
        if bullet_transform is not None:
            bullets = [bullet_transform(b) for b in bullets]
        bullets = dedupe_and_limit(bullets, limit=None)

        return {
            'version': version_match.group(1),
            'release_date': release_date,
            'bullets': bullets,
        }

    for line in lines:
        if line.startswith('## '):
            if current_heading:
                section = build(current_heading, current_lines)
                if section:
                    sections.append(section)
            current_heading = line.strip()
            current_lines = []
            continue

        if current_heading:
            current_lines.append(line)

    if current_heading:
        section = build(current_heading, current_lines)
        if section:
            sections.append(section)

    sections.sort(key=lambda s: s.get('release_date') or '', reverse=True)
    return sections


def filter_sections_by_range(
    sections: List[Dict],
    start_date: Optional[date],
    end_date: Optional[date],
) -> List[Dict]:
    """Keep only sections whose release_date falls within [start_date, end_date]."""
    if start_date is None or end_date is None:
        return sections

    filtered: List[Dict] = []
    for section in sections:
        release_date = section.get('release_date', '')
        if not release_date:
            continue
        try:
            parsed = datetime.strptime(release_date, '%Y-%m-%d').date()
        except ValueError:
            continue
        if start_date <= parsed <= end_date:
            filtered.append(section)

    return filtered


def lookup_pr_author(pr_url: str, session: requests.Session, cache: Dict[str, Optional[str]]) -> Optional[str]:
    """Look up a PR author's GitHub login via the public API (no token needed).

    Results (including "not found") are cached per URL in `cache`, which the
    caller owns -- callers that want lookups to survive across many bullets
    in one run should pass the same dict every time.

    Raises GitHubRateLimitError on a 403/429 response instead of the
    original's "log and treat as unresolved" -- callers that want the
    original non-fatal behavior should use enrich_bullet_attribution(),
    which catches it; callers that want to react to rate limiting (e.g. a
    circuit breaker) can catch it themselves.
    """
    if pr_url in cache:
        return cache[pr_url]

    match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
    if not match:
        cache[pr_url] = None
        return None

    owner, repo, number = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    author: Optional[str] = None
    try:
        response = session.get(
            api_url,
            timeout=10,
            headers={'Accept': 'application/vnd.github+json'},
        )
        if response.status_code == 200:
            author = (response.json().get('user') or {}).get('login')
        elif response.status_code in (403, 429):
            raise GitHubRateLimitError(api_url)
        else:
            print(
                f"WARNING: GitHub API returned {response.status_code} for {api_url}",
                file=sys.stderr,
            )
    except requests.RequestException as e:
        print(f"WARNING: Failed to look up PR author {api_url}: {e}", file=sys.stderr)

    cache[pr_url] = author
    return author


def enrich_bullet_attribution(bullet: str, session: requests.Session, pr_author_cache: Dict[str, Optional[str]]) -> str:
    """Append community attribution to a bullet that references a PR but has none.

    If the bullet already credits an author, it's returned unchanged.
    Non-fatal: any lookup failure (including rate limiting) leaves the
    bullet unchanged rather than raising, matching 02_fetch_release_notes.py's
    original behavior.
    """
    if AUTHOR_CREDIT_RE.search(bullet):
        return bullet

    match = PR_LINK_RE.search(bullet)
    if not match:
        return bullet

    try:
        author = lookup_pr_author(match.group('url'), session, pr_author_cache)
    except GitHubRateLimitError as e:
        print(f"WARNING: {e}; skipping author attribution for this PR", file=sys.stderr)
        return bullet

    if not author:
        return bullet

    pr_link = f"[#{match.group('num')}]({match.group('url')})"
    credit = f"([{author}](https://github.com/{author}))"
    return bullet[:match.start()] + f"{pr_link} {credit}" + bullet[match.end():]
