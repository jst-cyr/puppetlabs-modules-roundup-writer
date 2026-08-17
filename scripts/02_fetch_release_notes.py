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
import calendar
import json
import sys
from datetime import date, datetime, timezone
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

from lib import http_common, changelog_parse, external_docs


def _month_bounds(year: int, month: int) -> Tuple[date, date]:
    """First and last calendar day of the given month."""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


class ReleaseNotesFetcher:
    """Fetch and parse release notes from Forge and external sources."""

    FORGE_BASE_URL = "https://forge.puppet.com"

    def __init__(self, config_path: Optional[Path] = None):
        self.session = http_common.make_session()
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

        # `bullet_transform` reproduces the original inline enrich-then-dedupe
        # order (each bullet was enriched with PR attribution as it was
        # flushed, *before* the section's dedupe/limit pass ran).
        enrich = lambda bullet: changelog_parse.enrich_bullet_attribution(
            bullet, self.session, self._pr_author_cache
        )
        all_sections = changelog_parse.extract_release_sections(changelog, bullet_transform=enrich)

        if target_month and target_year:
            start, end = _month_bounds(target_year, target_month)
            monthly_sections = changelog_parse.filter_sections_by_range(all_sections, start, end)
        else:
            monthly_sections = all_sections

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
            section_bullets = changelog_parse.dedupe_and_limit(section.get('bullets', []), limit=None)
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
            'parsed_bullets': changelog_parse.dedupe_and_limit(rolled_up_bullets, limit=None),
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
            full_bullets = external_docs.parse_madcap_flare(
                html_content,
                anchor=anchor,
                version=version,
                module_name=module_name,
                limit=None,
            )
        else:
            full_bullets = external_docs.parse_external_docs(html_content, limit=None)

        bullets = changelog_parse.dedupe_and_limit(full_bullets, limit=5)
        
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
                    text = changelog_parse.clean_text(li.get_text(' ', strip=True))
                    if text:
                        bullets.append(text)
                node = node.find_next_sibling()

        # Fallback: take meaningful list items from the page.
        if not bullets:
            for li in soup.find_all('li'):
                text = changelog_parse.clean_text(li.get_text(' ', strip=True))
                if text:
                    bullets.append(text)

        return changelog_parse.dedupe_and_limit(bullets, limit=5)

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

        bullets = changelog_parse.bullets_from_lines(section_lines)
        bullets = [
            changelog_parse.enrich_bullet_attribution(b, self.session, self._pr_author_cache)
            for b in bullets
        ]
        return changelog_parse.dedupe_and_limit(bullets, limit=5)

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
