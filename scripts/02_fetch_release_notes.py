#!/usr/bin/env python3
"""
Stage 2: Fetch Release Notes
Fetch and parse release notes for modules discovered in Stage 1.

Usage:
    python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json
    python scripts/02_fetch_release_notes.py --input data/march_2026_modules_discovered.json --output data/march_2026_release_notes_raw.json

Output:
    - data/{month}_{year}_release_notes_raw.json
    - data/raw_html/{module}_{version}.html (raw HTML snapshots for reproducibility)

Behavior:
    - For Forge-backed modules, all releases in the target month are rolled up together.
    - Top-level version/release_date represent the latest release in that month.
    - releases_in_month lists each monthly version and its parsed bullets.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from urllib.parse import urldefrag
import yaml

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: requests and beautifulsoup4 required. Install with:", file=sys.stderr)
    print("    pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


class ReleaseNotesFetcher:
    """Fetch and parse release notes from Forge and external sources."""
    
    FORGE_BASE_URL = "https://forge.puppet.com"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'puppetlabs-roundup-bot/1.0'})
        # Cache of PR URL -> author login (or None) so we hit the GitHub API at
        # most once per PR. GitHub's unauthenticated API is rate limited to 60
        # requests/hour per IP, so we only look up PRs that lack attribution.
        self._pr_author_cache: Dict[str, Optional[str]] = {}
        self.config = {}
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
    
    def fetch_from_forge(
        self,
        module_slug: str,
        version: str,
        source_url: Optional[str] = None,
        target_month: Optional[int] = None,
        target_year: Optional[int] = None,
        fallback_release_date: str = '',
    ) -> Optional[Dict]:
        """
        Fetch release notes from Puppet Forge changelog tab.
        
        Returns:
            Dict with version, release_date, source, source_url, raw_html_path, parsed_bullets
            or None if fetch fails.
        """
        # Construct Forge changelog URL
        changelog_url = source_url or f"{self.FORGE_BASE_URL}/modules/{module_slug}/releases"
        
        print(f"Fetching Forge changelog for {module_slug} v{version} from {changelog_url}", file=sys.stderr)
        
        try:
            response = self.session.get(changelog_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch {changelog_url}: {e}", file=sys.stderr)
            return None
        
        html_content = response.text
        
        # Parse HTML to extract bullets for this version/month
        monthly_rollup = self._parse_forge_monthly_changelog(
            html=html_content,
            latest_version=version,
            target_month=target_month,
            target_year=target_year,
            fallback_release_date=fallback_release_date,
        )

        bullets = monthly_rollup.get('parsed_bullets', [])
        
        return {
            'source': 'forge_changelog',
            'source_url': changelog_url,
            'html_snapshot_path': None,  # Will be set by caller
            'parsed_bullets': bullets if bullets else ['See release notes on Puppet Forge'],
            'releases_in_month': monthly_rollup.get('releases_in_month', []),
            'latest_monthly_version': monthly_rollup.get('latest_version') or version,
            'latest_monthly_release_date': monthly_rollup.get('latest_release_date') or fallback_release_date,
            'raw_html': html_content,
        }

    def _parse_forge_monthly_changelog(
        self,
        html: str,
        latest_version: str,
        target_month: Optional[int],
        target_year: Optional[int],
        fallback_release_date: str,
    ) -> Dict:
        """Parse Forge changelog and roll up all releases that match the target month/year."""
        soup = BeautifulSoup(html, 'html.parser')
        changelog = self._extract_forge_markdown_changelog(soup)

        if not changelog:
            bullets = self._parse_forge_changelog(html, latest_version)
            return {
                'parsed_bullets': bullets,
                'releases_in_month': [
                    {
                        'version': latest_version,
                        'release_date': fallback_release_date,
                        'parsed_bullets': bullets,
                    }
                ] if bullets else [],
                'latest_version': latest_version,
                'latest_release_date': fallback_release_date,
            }

        all_sections = self._extract_markdown_release_sections(changelog)
        monthly_sections = self._filter_sections_by_month(all_sections, target_month, target_year)

        if not monthly_sections:
            # Fall back to the specific latest version for backwards compatibility.
            bullets = self._extract_markdown_bullets_for_version(changelog, latest_version)
            return {
                'parsed_bullets': bullets,
                'releases_in_month': [
                    {
                        'version': latest_version,
                        'release_date': fallback_release_date,
                        'parsed_bullets': bullets,
                    }
                ] if bullets else [],
                'latest_version': latest_version,
                'latest_release_date': fallback_release_date,
            }

        rolled_up_bullets: List[str] = []
        releases_in_month: List[Dict] = []

        for section in monthly_sections:
            section_bullets = self._dedupe_and_limit(section.get('bullets', []), limit=None)
            releases_in_month.append(
                {
                    'version': section.get('version', ''),
                    'release_date': section.get('release_date', ''),
                    'parsed_bullets': section_bullets,
                }
            )
            rolled_up_bullets.extend(section_bullets)

        latest = monthly_sections[0]
        return {
            'parsed_bullets': self._dedupe_and_limit(rolled_up_bullets, limit=None),
            'releases_in_month': releases_in_month,
            'latest_version': latest.get('version') or latest_version,
            'latest_release_date': fallback_release_date or latest.get('release_date') or '',
        }

    def _extract_forge_markdown_changelog(self, soup: BeautifulSoup) -> str:
        """Extract markdown changelog from Forge Next.js payload when available."""
        next_data = soup.find('script', id='__NEXT_DATA__')
        if not next_data or not next_data.string:
            return ''

        try:
            payload = json.loads(next_data.string)
        except (json.JSONDecodeError, TypeError):
            return ''

        changelog = (
            payload.get('props', {})
            .get('pageProps', {})
            .get('release', {})
            .get('changelog')
        )
        if isinstance(changelog, str):
            return changelog
        return ''

    def _extract_markdown_release_sections(self, changelog: str) -> List[Dict]:
        """Extract version/date scoped sections from markdown changelog."""
        lines = changelog.splitlines()
        sections: List[Dict] = []
        current_heading = ''
        current_lines: List[str] = []

        for line in lines:
            if line.startswith('## '):
                if current_heading:
                    section = self._build_release_section(current_heading, current_lines)
                    if section:
                        sections.append(section)
                current_heading = line.strip()
                current_lines = []
                continue

            if current_heading:
                current_lines.append(line)

        if current_heading:
            section = self._build_release_section(current_heading, current_lines)
            if section:
                sections.append(section)

        # Sort most recent first by release_date, with unknown dates last.
        sections.sort(key=lambda s: s.get('release_date') or '', reverse=True)
        return sections

    def _build_release_section(self, heading: str, section_lines: List[str]) -> Optional[Dict]:
        """Build a release section record from a markdown heading and body lines."""
        version_match = re.search(r'\b(?:v)?(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9._-]+)?)\b', heading)
        if not version_match:
            return None

        release_date_match = re.search(r'\b(20\d{2}-\d{2}-\d{2})\b', heading)
        release_date = release_date_match.group(1) if release_date_match else ''

        bullets = self._bullets_from_lines(section_lines)

        return {
            'version': version_match.group(1),
            'release_date': release_date,
            'bullets': self._dedupe_and_limit(bullets, limit=None),
        }

    def _filter_sections_by_month(
        self,
        sections: List[Dict],
        target_month: Optional[int],
        target_year: Optional[int],
    ) -> List[Dict]:
        """Filter release sections by target month/year."""
        if not target_month or not target_year:
            return sections

        filtered: List[Dict] = []
        for section in sections:
            release_date = section.get('release_date', '')
            if not release_date:
                continue

            try:
                parsed = datetime.strptime(release_date, '%Y-%m-%d')
            except ValueError:
                continue

            if parsed.month == target_month and parsed.year == target_year:
                filtered.append(section)

        return filtered
    
    def fetch_from_external_docs(self, module_name: str, version: str, docs_url: str, parser_type: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch release notes from external docs (help.puppet.com).
        
        Args:
            module_name: Name of the module
            version: Version number
            docs_url: URL to fetch from
            parser_type: Type of parser to use ('madcap_flare', 'help_puppet_html', etc.)
        
        Returns:
            Dict with version, release_date, source, source_url, raw_html_path, parsed_bullets
            or None if fetch fails.
        """
        print(f"Fetching external docs for {module_name} v{version} from {docs_url}", file=sys.stderr)
        fetch_url, anchor = urldefrag(docs_url)
        
        try:
            response = self.session.get(fetch_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch {fetch_url}: {e}", file=sys.stderr)
            return None
        
        html_content = response.text
        
        # Parse HTML to extract bullets based on parser type
        if parser_type == 'madcap_flare':
            full_bullets = self._parse_madcap_flare(
                html_content,
                anchor=anchor,
                version=version,
                module_name=module_name,
                limit=None,
            )
        else:
            full_bullets = self._parse_external_docs(html_content, limit=None)

        bullets = self._dedupe_and_limit(full_bullets, limit=5)
        
        return {
            'source': 'external_docs',
            'source_url': docs_url,
            'html_snapshot_path': None,
            'parsed_bullets': bullets if bullets else ['See release notes on help.puppet.com'],
            'parsed_bullets_full': full_bullets,
            'raw_html': html_content,
        }
    
    def _parse_forge_changelog(self, html: str, version: str) -> List[str]:
        """
        Parse Forge changelog HTML for a specific version.
        
        Returns first 5 bullets as list of strings.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Preferred path: parse release changelog markdown from Next.js payload.
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data and next_data.string:
            try:
                payload = json.loads(next_data.string)
                changelog = (
                    payload.get('props', {})
                    .get('pageProps', {})
                    .get('release', {})
                    .get('changelog')
                )
                if isinstance(changelog, str) and changelog.strip():
                    markdown_bullets = self._extract_markdown_bullets_for_version(changelog, version)
                    if markdown_bullets:
                        return markdown_bullets
            except (json.JSONDecodeError, TypeError):
                pass
        
        bullets: List[str] = []

        # Try to find the release heading that contains the target version.
        heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        version_heading = None
        version_pattern = re.compile(rf'\b{re.escape(version)}\b')

        for heading in soup.find_all(heading_tags):
            heading_text = heading.get_text(' ', strip=True)
            if version_pattern.search(heading_text):
                version_heading = heading
                break

        if version_heading is not None:
            node = version_heading.find_next_sibling()
            while node is not None and getattr(node, 'name', None) not in heading_tags:
                for li in node.find_all('li'):
                    text = self._clean_text(li.get_text(' ', strip=True))
                    if text:
                        bullets.append(text)
                node = node.find_next_sibling()

        # Fallback: take meaningful list items from the page.
        if not bullets:
            for li in soup.find_all('li'):
                text = self._clean_text(li.get_text(' ', strip=True))
                if text:
                    bullets.append(text)

        return self._dedupe_and_limit(bullets, limit=5)

    def _extract_markdown_bullets_for_version(self, changelog: str, version: str) -> List[str]:
        """Extract bullets from the markdown section for the requested version."""
        lines = changelog.splitlines()
        section_lines: List[str] = []
        section_pattern = re.compile(rf'^##\s+.*\b(?:v)?{re.escape(version)}\b', re.IGNORECASE)

        in_section = False
        for line in lines:
            if line.startswith('## '):
                if in_section:
                    break
                if section_pattern.search(line):
                    in_section = True
                    continue

            if in_section:
                section_lines.append(line)

        bullets = self._bullets_from_lines(section_lines)
        return self._dedupe_and_limit(bullets, limit=5)
    
    def _parse_external_docs(self, html: str, limit: Optional[int] = 5) -> List[str]:
        """
        Parse external docs (help.puppet.com) HTML for release notes.
        
        TODO: Extract bullet points from help.puppet.com layout.
        Returns first 5 bullets as list of strings.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        bullets: List[str] = []

        # Prefer semantic content containers if present.
        content_root = (
            soup.find('main')
            or soup.find('article')
            or soup.find('div', attrs={'role': 'main'})
            or soup
        )

        for li in content_root.find_all('li'):
            text = self._clean_text(li.get_text(' ', strip=True))
            if text:
                bullets.append(text)

        return self._dedupe_and_limit(bullets, limit=limit)

    def _parse_madcap_flare(
        self,
        html: str,
        anchor: str = '',
        version: str = '',
        module_name: str = '',
        limit: Optional[int] = 5,
    ) -> List[str]:
        """
        Parse MadCap Flare HTML (help.puppet.com) for release notes.
        
        MadCap Flare pages have:
        - Navigation TOC with version links
        - Main content in div[data-mc-content-body="True"]
        - Real content as <li><p> or <li> with descriptions
        
        Strategy:
        1. Find main content container
        2. Extract <li> elements with actual content (have <p> tags or substantial text)
        3. Filter out pure navigation items (version selectors, breadcrumbs)
        4. Return up to 5 items
        """
        soup = BeautifulSoup(html, 'html.parser')
        bullets: List[str] = []
        
        # Try to find main content container specific to MadCap Flare
        content_container = soup.find('div', attrs={'data-mc-content-body': 'True'})
        if not content_container:
            # Fallback to common content containers
            content_container = (
                soup.find('main')
                or soup.find('article')
                or soup.find('div', attrs={'role': 'main'})
                or soup
            )
        
        search_root = self._find_anchor_section_root(content_container, anchor)
        if not anchor:
            search_root = self._find_version_section_root(search_root, version, module_name)

        # Find actual content lists (skip TOC-style lists with just links)
        for li in search_root.find_all('li'):
            text = self._clean_madcap_text(li)
            if text and self._is_content_item(text):
                bullets.append(text)
        
        return self._dedupe_and_limit(bullets, limit=limit)

    def _find_version_section_root(self, content_container, version: str, module_name: str = ''):
        """Scope parsing to the section matching the target version when possible."""
        if not version:
            return content_container

        version_pattern = re.compile(rf'\b{re.escape(version)}\b')
        heading_tags = ['h1', 'h2', 'h3', 'h4']
        version_heading = None

        for heading in content_container.find_all(heading_tags):
            heading_text = self._clean_text(heading.get_text(' ', strip=True))
            if version_pattern.search(heading_text):
                version_heading = heading
                break

        if not version_heading:
            return content_container

        section_nodes = [version_heading]
        node = version_heading.find_next_sibling()
        while node is not None:
            if getattr(node, 'name', None) == version_heading.name:
                node_text = self._clean_text(node.get_text(' ', strip=True))
                if re.search(r'\b\d+\.\d+\.\d+\b', node_text):
                    break

            section_nodes.append(node)
            node = node.find_next_sibling()

        scoped_soup = BeautifulSoup('', 'html.parser')
        wrapper = scoped_soup.new_tag('div')
        for section_node in section_nodes:
            wrapper.append(section_node)
        scoped_soup.append(wrapper)
        return scoped_soup

    def _find_anchor_section_root(self, content_container, anchor: str):
        """Return a scoped root for an anchor section when available."""
        if not anchor:
            return content_container

        anchor_target = (
            content_container.find(attrs={'id': anchor})
            or content_container.find('a', attrs={'name': anchor})
        )
        if not anchor_target:
            return content_container

        section_nodes = []
        heading_tags = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

        node = anchor_target
        while node is not None:
            section_nodes.append(node)
            node = node.find_next_sibling()
            if node is not None and getattr(node, 'name', None) in heading_tags:
                break

        if len(section_nodes) <= 1:
            parent_block = anchor_target.find_parent(['section', 'article', 'div'])
            return parent_block or content_container

        scoped_soup = BeautifulSoup('', 'html.parser')
        wrapper = scoped_soup.new_tag('div')
        for section_node in section_nodes:
            wrapper.append(section_node)
        scoped_soup.append(wrapper)
        return scoped_soup

    def _clean_madcap_text(self, li_element) -> str:
        """
        Extract and clean text from a MadCap Flare <li> element.

        Handles <li><p>text</p></li>, <li>text</li>, nested markup, etc.
        Preserves <b> tags as **markdown bold** so titles stay readable.
        """
        # Try to get text from nested <p> first (most common in MadCap)
        p_tag = li_element.find('p')
        el = p_tag if p_tag else li_element

        parts = []
        for child in el.children:
            if hasattr(child, 'name'):
                if child.name == 'b':
                    inner = child.get_text(' ', strip=True)
                    if inner:
                        parts.append(f'**{inner}**')
                else:
                    inner = child.get_text(' ', strip=True)
                    if inner:
                        parts.append(inner)
            else:
                # NavigableString
                raw = str(child)
                stripped = raw.strip()
                if stripped:
                    parts.append(stripped)

        text = ' '.join(parts)
        # Remove bold markdown wrapping lone punctuation (MadCap artifact: <b>.</b>)
        text = re.sub(r'\*\*([.,:;!?])\*\*', r'\1', text)
        # Remove space before sentence-ending punctuation that was previously a separate element
        text = re.sub(r'\s+([.,:;!?])', r'\1', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text or '').strip()

        return text
    
    def _is_content_item(self, text: str) -> bool:
        """
        Determine if text is actual release note content vs navigation.
        
        Filters out:
        - Concatenated versions: "Version 3.7.1 Version 3.7.0..."
        - Single version numbers
        - Pure product/module names
        - Navigation headers
        - Release notes TOC pages (product name repeated with versions)
        - Very short items
        """
        if len(text) < 10:
            return False
        
        # Concatenated versions anywhere in text: "Version X.Y.Z"
        if re.search(r'Version\s+\d+\.\d+\.\d+', text):
            # But only if it's mostly versions (allow some description before)
            version_count = len(re.findall(r'Version\s+\d+\.\d+\.\d+', text))
            if version_count > 1 or (version_count == 1 and text.strip().startswith('Version')):
                return False
        
        # Single version number
        if re.match(r'^(?:Version\s+)?\d+\.\d+(?:\.\d+)?$', text):
            return False
        
        # Pure product/module names (common navigation items)
        nav_items = [
            'Security Compliance Management',
            'Continuous Delivery',
            'release notes',
        ]
        for item in nav_items:
            # Match if it's the item by itself or item followed by just a version
            if re.match(rf'^{re.escape(item)}(?:\s+\d+\.\d+(?:\.\d+)?)?$', text):
                return False
        
        # Patterns that are clearly navigation (all versions/product names)
        if re.match(r'^(?:Security Compliance Management|Continuous Delivery)\s+\d+\.\d+', text):
            return False
        
        # Release notes TOC: "ProductName release notes ProductName X.Y ProductName X.Y..."
        # Check if it starts with product name + "release notes" then repeats product+version
        if re.search(r'(Security Compliance Management|Continuous Delivery)\s+release\s+notes', text):
            # This is a TOC/nav page
            if re.search(r'(Security Compliance Management|Continuous Delivery)\s+\d+\.\d+', text):
                return False
        
        return True

    # Matches a PR reference such as "[#25](https://github.com/org/repo/pull/25)",
    # optionally wrapped in parentheses ("([#25](...))") as older changelogs do.
    _PR_LINK_RE = re.compile(
        r'(?P<lp>\(?)\[#(?P<num>\d+)\]\((?P<url>https://github\.com/[^/]+/[^/]+/pull/\d+)\)(?P<rp>\)?)'
    )
    # Matches an author profile credit such as "([smortex](https://github.com/smortex))".
    # The profile URL has no further path segment, which distinguishes it from a PR link.
    _AUTHOR_CREDIT_RE = re.compile(r'\(\[[^\]]+\]\(https://github\.com/[^/)]+\)\)')

    def _bullets_from_lines(self, section_lines: List[str]) -> List[str]:
        """Turn markdown changelog lines into bullet strings.

        A list item (``- ``/``* ``) may wrap onto indented continuation lines —
        older puppetlabs changelogs put the PR reference on the line *after* the
        title, e.g.::

            * **Allow ruby_task_helper 1.x**
              ([#25](https://github.com/puppetlabs/puppetlabs-aws_inventory/pull/25))

        Continuation lines are merged into the current bullet until a blank line,
        a heading, or the next list item ends it. This keeps the PR reference that
        the previous line-by-line parser silently dropped.
        """
        bullets: List[str] = []
        current: Optional[List[str]] = None

        for line in section_lines:
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                self._flush_bullet(bullets, current)
                current = [re.sub(r'^[-*]\s+', '', stripped)]
            elif not stripped or stripped.startswith('#'):
                # Blank line or heading terminates the current bullet.
                self._flush_bullet(bullets, current)
                current = None
            elif current is not None:
                # Indented/continuation text belonging to the current bullet.
                current.append(stripped)

        self._flush_bullet(bullets, current)
        return bullets

    def _flush_bullet(self, bullets: List[str], parts: Optional[List[str]]) -> None:
        """Finalize an accumulated bullet: join, clean, enrich attribution, append."""
        if not parts:
            return
        cleaned = self._clean_text(' '.join(parts))
        if cleaned:
            bullets.append(self._enrich_bullet_attribution(cleaned))

    def _enrich_bullet_attribution(self, bullet: str) -> str:
        """Append community attribution to a bullet that references a PR but has none.

        If the bullet already credits an author (newer changelog style), it is
        returned unchanged. Otherwise the PR author is looked up via the public
        GitHub API and rendered to match the existing style:
        ``... [#N](url) ([login](https://github.com/login))``.
        """
        if self._AUTHOR_CREDIT_RE.search(bullet):
            return bullet

        match = self._PR_LINK_RE.search(bullet)
        if not match:
            return bullet

        author = self._lookup_pr_author(match.group('url'))
        if not author:
            return bullet

        pr_link = f"[#{match.group('num')}]({match.group('url')})"
        credit = f"([{author}](https://github.com/{author}))"
        # Replace the matched PR reference (dropping any wrapping parens) with the
        # normalized "PR link + author credit" form.
        return bullet[:match.start()] + f"{pr_link} {credit}" + bullet[match.end():]

    def _lookup_pr_author(self, pr_url: str) -> Optional[str]:
        """Look up a PR author's GitHub login via the public API (no token needed).

        Results (including failures) are cached per URL. Network errors and rate
        limiting are non-fatal: attribution is simply skipped for that bullet.
        """
        if pr_url in self._pr_author_cache:
            return self._pr_author_cache[pr_url]

        match = re.match(r'https://github\.com/([^/]+)/([^/]+)/pull/(\d+)', pr_url)
        if not match:
            self._pr_author_cache[pr_url] = None
            return None

        owner, repo, number = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
        author: Optional[str] = None
        try:
            response = self.session.get(
                api_url,
                timeout=10,
                headers={'Accept': 'application/vnd.github+json'},
            )
            if response.status_code == 200:
                author = (response.json().get('user') or {}).get('login')
            elif response.status_code in (403, 429):
                print(
                    f"WARNING: GitHub API rate limit hit looking up {api_url}; "
                    "skipping author attribution for this PR",
                    file=sys.stderr,
                )
            else:
                print(
                    f"WARNING: GitHub API returned {response.status_code} for {api_url}",
                    file=sys.stderr,
                )
        except requests.RequestException as e:
            print(f"WARNING: Failed to look up PR author {api_url}: {e}", file=sys.stderr)

        self._pr_author_cache[pr_url] = author
        return author

    def _clean_text(self, text: str) -> str:
        """Normalize extracted list item text."""
        cleaned = re.sub(r'\s+', ' ', text or '').strip()
        if len(cleaned) < 8:
            return ''
        if cleaned.lower().startswith('version '):
            return ''
        return cleaned

    def _dedupe_and_limit(self, items: List[str], limit: Optional[int] = 5) -> List[str]:
        """Deduplicate while preserving order, then limit list size."""
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
    
    def save_html_snapshot(self, module_name: str, version: str, html_content: str, snapshot_dir: Path) -> Path:
        """Save raw HTML snapshot for audit trail."""
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_name = module_name.replace('-', '_').replace('/', '_')
        safe_version = version.replace('.', '_')
        
        snapshot_path = snapshot_dir / f"{safe_name}_{safe_version}.html"
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return snapshot_path


def infer_target_month_year(discovered: Dict, input_path: Path) -> Tuple[Optional[int], Optional[int]]:
    """Infer target month/year from discovery metadata, with filename fallback."""
    metadata = discovered.get('metadata', {})
    target_month_value = metadata.get('target_month')
    target_year_value = metadata.get('target_year')

    if isinstance(target_month_value, str) and target_month_value and target_year_value:
        try:
            month_num = datetime.strptime(target_month_value.capitalize(), '%B').month
            return month_num, int(target_year_value)
        except (ValueError, TypeError):
            pass

    match = re.search(r'([a-zA-Z]+)_(\d{4})_modules_discovered', input_path.name)
    if match:
        month_name = match.group(1).capitalize()
        try:
            month_num = datetime.strptime(month_name, '%B').month
            return month_num, int(match.group(2))
        except ValueError:
            return None, None

    return None, None


def main():
    parser = argparse.ArgumentParser(
        description='Fetch and parse release notes for modules from Stage 1 discovery'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to modules_discovered.json from Stage 1'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: input filename with suffix _release_notes_raw.json)'
    )
    parser.add_argument(
        '--snapshot-dir',
        default='data/raw_html',
        help='Directory to store raw HTML snapshots'
    )
    parser.add_argument(
        '--config',
        default='config/release_notes_sources.yaml',
        help='Path to release notes configuration file'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load discovered modules
    with open(input_path, 'r') as f:
        discovered = json.load(f)

    target_month_num, target_year = infer_target_month_year(discovered, input_path)
    
    modules = discovered.get('modules', [])
    print(f"Fetching release notes for {len(modules)} modules...", file=sys.stderr)
    
    # Create fetcher with config
    config_path = Path(args.config)
    fetcher = ReleaseNotesFetcher(config_path)
    
    release_notes = []
    snapshot_dir = Path(args.snapshot_dir)
    
    for module_info in modules:
        module_name = module_info.get('name', '')
        module_slug = module_info.get('slug', '')
        version = module_info.get('latest_version', '')
        release_date = module_info.get('release_date', '')
        source = module_info.get('release_notes_source', 'forge_changelog')
        source_url = module_info.get('release_notes_url')
        
        print(f"\nProcessing {module_name} v{version}...", file=sys.stderr)
        
        # Fetch based on source type
        if source == 'external_docs':
            if not source_url:
                print(f"WARNING: Missing external docs URL for {module_name}; skipping", file=sys.stderr)
                continue
            # Get parser type from config
            parser_type = None
            external_docs_config = fetcher.config.get('external_docs', {})
            module_config = external_docs_config.get(module_name, {})
            if module_config:
                parser_type = module_config.get('parser_type')
            release_info = fetcher.fetch_from_external_docs(module_name, version, source_url, parser_type=parser_type)
        elif source == 'manual_review':
            release_info = {
                'source': 'manual_review',
                'source_url': None,
                'html_snapshot_path': None,
                'parsed_bullets': ['Manual curator review required for this module.'],
                'raw_html': None,
            }
        else:
            release_info = fetcher.fetch_from_forge(
                module_slug,
                version,
                source_url=source_url,
                target_month=target_month_num,
                target_year=target_year,
                fallback_release_date=release_date,
            )
        
        if release_info:
            raw_html = release_info.pop('raw_html', None)
            html_snapshot_path = None
            if raw_html:
                snapshot_path = fetcher.save_html_snapshot(module_name, version, raw_html, snapshot_dir)
                html_snapshot_path = str(snapshot_path)

            effective_version = release_info.pop('latest_monthly_version', version)
            effective_release_date = release_info.pop('latest_monthly_release_date', release_date)

            # Add module metadata
            entry = {
                'name': module_name,
                'slug': module_slug,
                'version': effective_version,
                'release_date': effective_release_date,
                **release_info,
                'html_snapshot_path': html_snapshot_path,
            }
            release_notes.append(entry)
    
    # Prepare output
    output_data = {
        'metadata': {
            'fetched_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'source_discovery_file': str(input_path),
            'modules_processed': len(release_notes)
        },
        'release_notes': release_notes
    }
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Replace 'modules_discovered' with 'release_notes_raw'
        output_path = input_path.parent / input_path.name.replace(
            'modules_discovered', 'release_notes_raw'
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save output
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nFetched release notes for {len(release_notes)} modules", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
