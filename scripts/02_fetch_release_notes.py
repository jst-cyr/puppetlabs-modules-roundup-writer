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
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin
import re

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
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'puppetlabs-roundup-bot/1.0'})
    
    def fetch_from_forge(self, module_slug: str, version: str) -> Optional[Dict]:
        """
        Fetch release notes from Puppet Forge changelog tab.
        
        Returns:
            Dict with version, release_date, source, source_url, raw_html_path, parsed_bullets
            or None if fetch fails.
        """
        # Construct Forge changelog URL
        changelog_url = f"{self.FORGE_BASE_URL}/modules/{module_slug}/releases"
        
        print(f"Fetching Forge changelog for {module_slug} v{version} from {changelog_url}", file=sys.stderr)
        
        try:
            response = self.session.get(changelog_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch {changelog_url}: {e}", file=sys.stderr)
            return None
        
        html_content = response.text
        
        # Parse HTML to extract bullets for this version
        bullets = self._parse_forge_changelog(html_content, version)
        
        return {
            'source': 'forge_changelog',
            'source_url': changelog_url,
            'html_snapshot_path': None,  # Will be set by caller
            'parsed_bullets': bullets if bullets else ['See release notes on Puppet Forge']
        }
    
    def fetch_from_external_docs(self, module_name: str, version: str, config: Dict) -> Optional[Dict]:
        """
        Fetch release notes from external docs (help.puppet.com).
        
        Returns:
            Dict with version, release_date, source, source_url, raw_html_path, parsed_bullets
            or None if fetch fails.
        """
        url_pattern = config.get('url_pattern', '')
        base_url = config.get('base_url', '')
        
        # Build version parameter for URL
        # e.g., "2.6.0" -> "260", or with version_transform "v221"
        version_underscore = version.replace('.', '')
        if 'version_transform' in config:
            version_underscore = config['version_transform'] + version_underscore
        
        # Replace placeholder
        relative_url = url_pattern.replace('{version_underscore}', version_underscore)
        docs_url = urljoin(base_url, relative_url)
        
        print(f"Fetching external docs for {module_name} v{version} from {docs_url}", file=sys.stderr)
        
        try:
            response = self.session.get(docs_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch {docs_url}: {e}", file=sys.stderr)
            return None
        
        html_content = response.text
        
        # Parse HTML to extract bullets (varies by doc layout)
        bullets = self._parse_external_docs(html_content)
        
        return {
            'source': 'external_docs',
            'source_url': docs_url,
            'html_snapshot_path': None,
            'parsed_bullets': bullets if bullets else ['See release notes on help.puppet.com']
        }
    
    def _parse_forge_changelog(self, html: str, version: str) -> List[str]:
        """
        Parse Forge changelog HTML for a specific version.
        
        TODO: Extract bullet points for the given version from the changelog.
        Returns first 5 bullets as list of strings.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Placeholder: in production, find version section and extract <li> items
        bullets = []
        
        # Look for any <li> items in the page (rough approximation)
        list_items = soup.find_all('li')
        for item in list_items[:5]:  # Take first 5
            text = item.get_text(strip=True)
            if text and len(text) > 5:  # Filter out empty/tiny items
                bullets.append(text)
        
        return bullets
    
    def _parse_external_docs(self, html: str) -> List[str]:
        """
        Parse external docs (help.puppet.com) HTML for release notes.
        
        TODO: Extract bullet points from help.puppet.com layout.
        Returns first 5 bullets as list of strings.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Placeholder: in production, find release notes section and extract bullets
        bullets = []
        
        # Look for <li> items in main content area
        list_items = soup.find_all('li')
        for item in list_items[:5]:
            text = item.get_text(strip=True)
            if text and len(text) > 5:
                bullets.append(text)
        
        return bullets
    
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
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load discovered modules
    with open(input_path, 'r') as f:
        discovered = json.load(f)
    
    modules = discovered.get('modules', [])
    print(f"Fetching release notes for {len(modules)} modules...", file=sys.stderr)
    
    # Fetch release notes for each module
    fetcher = ReleaseNotesFetcher()
    release_notes = []
    
    for module_info in modules:
        module_name = module_info.get('name', '')
        module_slug = module_info.get('slug', '')
        version = module_info.get('latest_version', '')
        release_date = module_info.get('release_date', '')
        source = module_info.get('release_notes_source', 'forge_changelog')
        
        print(f"\nProcessing {module_name} v{version}...", file=sys.stderr)
        
        # Fetch based on source type
        if source == 'external_docs':
            # TODO: Load config to get external docs info
            release_info = fetcher.fetch_from_external_docs(
                module_name, version, {'base_url': '', 'url_pattern': ''}
            )
        else:
            release_info = fetcher.fetch_from_forge(module_slug, version)
        
        if release_info:
            # Add module metadata
            entry = {
                'name': module_name,
                'slug': module_slug,
                'version': version,
                'release_date': release_date,
                **release_info
            }
            release_notes.append(entry)
    
    # Prepare output
    output_data = {
        'metadata': {
            'fetched_at': datetime.utcnow().isoformat() + 'Z',
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
