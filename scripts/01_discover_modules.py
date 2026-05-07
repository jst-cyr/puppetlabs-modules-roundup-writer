#!/usr/bin/env python3
"""
Stage 1: Module Discovery
Discover all puppetlabs modules from Forge listing and identify which were released in target month.

Usage:
    python scripts/01_discover_modules.py --month March --year 2026
    python scripts/01_discover_modules.py --month march --year 2026 --output data/march_2026_modules.json

Output:
    - data/{month}_{year}_modules_discovered.json
"""

import argparse
import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from urllib.parse import urljoin
import yaml

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: requests and beautifulsoup4 required. Install with: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


class ModuleDiscovery:
    """Discover modules from Puppet Forge listing."""
    
    FORGE_OWNER_URL = "https://forge.puppet.com/modules/puppetlabs"
    FORGE_LISTING_URL = "https://forge.puppet.com/modules/puppetlabs?limit=50&sort_by=latest_release&module_groups=base%20pe_only"
    
    def __init__(self, config_path: Path):
        """Initialize discovery with release notes source config."""
        self.config_path = config_path
        self.release_notes_sources = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load release_notes_sources.yaml config."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                config.setdefault('forge_changelog', [])
                config.setdefault('external_docs', {})
                config.setdefault('manual_review', [])
                config.setdefault('default_source', 'forge_changelog')
                return config
        except FileNotFoundError:
            print(f"WARNING: Config not found at {self.config_path}, using defaults", file=sys.stderr)
            return {
                'forge_changelog': [],
                'external_docs': {},
                'manual_review': [],
                'default_source': 'forge_changelog'
            }
    
    def get_release_notes_source(self, module_name: str) -> Dict:
        """Determine release notes source for a module."""
        manual_review = set(self.release_notes_sources.get('manual_review', []))
        external = self.release_notes_sources.get('external_docs', {})

        if module_name in manual_review:
            return {'source': 'manual_review'}

        if module_name in external:
            return {
                'source': 'external_docs',
                'config': external[module_name]
            }

        return {'source': self.release_notes_sources.get('default_source', 'forge_changelog')}
    
    def discover_from_html(self, html_content: str) -> List[Dict]:
        """
        Parse Forge listing HTML to extract module info.
        Primary source is Next.js page data in __NEXT_DATA__.
        Falls back to card scraping if needed.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Preferred extraction path: parse embedded Next.js payload.
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data and next_data.string:
            try:
                payload = json.loads(next_data.string)
                results = (
                    payload.get('props', {})
                    .get('pageProps', {})
                    .get('initialData', {})
                    .get('results', [])
                )
                modules = []
                for item in results:
                    owner_slug = item.get('owner', {}).get('slug', '')
                    raw_slug = item.get('slug', '')
                    if owner_slug != 'puppetlabs' or not raw_slug:
                        continue

                    short_slug = raw_slug.replace('puppetlabs-', '', 1)
                    release = item.get('current_release', {})
                    version = release.get('version', '')
                    created_at = release.get('created_at', '')

                    if not version or not created_at:
                        continue

                    try:
                        release_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S %z').strftime('%Y-%m-%d')
                    except ValueError:
                        continue

                    modules.append({
                        'name': item.get('name', short_slug),
                        'slug': short_slug,
                        'forge_url': f"https://forge.puppet.com/modules/puppetlabs/{short_slug}",
                        'latest_version': version,
                        'release_date': release_date,
                        'released_in_target_month': False,
                    })

                if modules:
                    return modules
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback extraction from rendered card markup.
        modules = []
        seen_slugs = set()

        module_link_pattern = re.compile(r'^/modules/puppetlabs/[a-z0-9_]+$')
        release_pattern = re.compile(
            r'Version\s+([0-9A-Za-z.\-]+)\s*\|\s*Released\s+([A-Za-z]{3}\s+\d{1,2}(?:st|nd|rd|th)\s+\d{4})'
        )

        for link in soup.find_all('a', href=module_link_pattern):
            href_value = link.get('href', '')
            if isinstance(href_value, list):
                href = href_value[0] if href_value else ''
            else:
                href = href_value or ''

            slug = href.rsplit('/', 1)[-1]
            if not slug or slug in seen_slugs:
                continue

            # Climb card containers until release metadata is found.
            container = link
            card_text = ''
            for _ in range(6):
                if container is None:
                    break
                card_text = container.get_text(' ', strip=True)
                if 'Version' in card_text and 'Released' in card_text:
                    break
                container = container.parent

            match = release_pattern.search(card_text)
            if not match:
                continue

            version = match.group(1)
            release_date_raw = match.group(2)
            release_date_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', release_date_raw)

            try:
                release_date = datetime.strptime(release_date_clean, '%b %d %Y').strftime('%Y-%m-%d')
            except ValueError:
                continue

            name_text = link.get_text(strip=True)
            name = name_text if name_text else slug

            modules.append({
                'name': name,
                'slug': slug,
                'forge_url': f"https://forge.puppet.com/modules/puppetlabs/{slug}",
                'latest_version': version,
                'release_date': release_date,
                'released_in_target_month': False,
            })
            seen_slugs.add(slug)

        return modules
    
    def discover_modules(self) -> Dict:
        """
        Discover all puppetlabs modules from Forge listing.
        
        Returns:
            Dict with metadata and list of modules.
        """
        print(f"Fetching Forge listing from: {self.FORGE_LISTING_URL}", file=sys.stderr)
        
        try:
            response = requests.get(
                self.FORGE_LISTING_URL,
                timeout=10,
                headers={'User-Agent': 'puppetlabs-roundup-bot/1.0'}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"ERROR: Failed to fetch Forge listing: {e}", file=sys.stderr)
            return {'metadata': {}, 'modules': []}
        
        # Parse HTML to extract modules
        modules = self.discover_from_html(response.text)
        
        return {
            'metadata': {
                'discovered_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'query_url': self.FORGE_LISTING_URL,
                'modules_seen_on_page': len(modules),
            },
            'modules': modules
        }
    
    def filter_by_month(self, discovered: Dict, target_month: int, target_year: int) -> Dict:
        """Filter modules to only those released in target month/year."""
        filtered_modules = []
        
        for module in discovered.get('modules', []):
            release_date = module.get('release_date')
            if not release_date:
                continue
            
            # Parse release_date (format: YYYY-MM-DD)
            try:
                rel_date = datetime.strptime(release_date, '%Y-%m-%d').date()
            except ValueError:
                continue
            
            # Check if in target month
            if rel_date.year == target_year and rel_date.month == target_month:
                module['released_in_target_month'] = True
                filtered_modules.append(module)
        
        discovered['modules'] = filtered_modules
        return discovered
    
    def enrich_with_sources(self, discovered: Dict) -> Dict:
        """Add release_notes_source info to each module."""
        source_counts: Dict[str, int] = {}

        for module in discovered.get('modules', []):
            name = module.get('slug', module.get('name', '')).lower()
            source_info = self.get_release_notes_source(name)
            assigned_source = source_info['source']
            module['release_notes_source'] = assigned_source
            source_counts[assigned_source] = source_counts.get(assigned_source, 0) + 1
            
            if assigned_source == 'external_docs':
                # Construct release notes URL from config
                config = source_info.get('config', {})
                module['release_notes_url'] = self._build_external_docs_url(
                    name, module.get('latest_version'), config
                )
            elif assigned_source == 'forge_changelog':
                module['release_notes_url'] = f"https://forge.puppet.com/modules/puppetlabs/{module.get('slug')}/releases"
            else:
                module['release_notes_url'] = None

        discovered.setdefault('metadata', {})['source_summary'] = source_counts
        
        return discovered
    
    def _build_external_docs_url(self, module_name: str, version: str, config: Dict) -> str:
        """Construct external docs URL using config pattern."""
        if not version:
            return ''

        url_pattern = config.get('url_pattern', '')
        base_url = config.get('base_url', '')
        
        # Replace version placeholder: {version_underscore}
        # e.g., "2.6.0" -> "260"
        version_underscore = version.replace('.', '')
        url = url_pattern.replace('{version_underscore}', version_underscore)
        
        # Check for version_transform (e.g., prepend 'v')
        if 'version_transform' in config:
            transform = config['version_transform']
            url = url_pattern.replace('{version_underscore}', transform + version_underscore)
        
        full_url = urljoin(base_url, url)
        
        # Check for version_anchor flag to append anchor to URL
        # e.g., 5.15.0 -> #Version5150
        if config.get('version_anchor', False):
            version_anchor = f"Version{version_underscore}"
            full_url = f"{full_url}#{version_anchor}"
        
        return full_url


def main():
    parser = argparse.ArgumentParser(
        description='Discover puppetlabs modules updated in target month from Forge listing'
    )
    parser.add_argument('--month', required=True, help='Target month name (e.g., March, march)')
    parser.add_argument('--year', required=True, type=int, help='Target year (e.g., 2026)')
    parser.add_argument(
        '--output',
        help='Output file path (default: data/{month_lower}_{year}_modules_discovered.json)'
    )
    parser.add_argument(
        '--config',
        default='config/release_notes_sources.yaml',
        help='Path to release_notes_sources.yaml config'
    )
    
    args = parser.parse_args()
    
    # Normalize month name
    month_name = args.month.capitalize()
    month_num = datetime.strptime(month_name, '%B').month
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"data/{args.month.lower()}_{args.year}_modules_discovered.json")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run discovery
    print(f"Discovering modules updated in {month_name} {args.year}...", file=sys.stderr)
    
    discovery = ModuleDiscovery(Path(args.config))
    discovered = discovery.discover_modules()
    discovered = discovery.filter_by_month(discovered, month_num, args.year)
    discovered = discovery.enrich_with_sources(discovered)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(discovered, f, indent=2)
    
    print(f"Discovered {len(discovered['modules'])} modules released in {month_name} {args.year}", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)
    print(json.dumps(discovered, indent=2))


if __name__ == '__main__':
    main()
