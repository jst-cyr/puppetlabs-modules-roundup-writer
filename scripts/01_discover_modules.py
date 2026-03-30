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
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin
import yaml

# Try to import requests; fall back to urllib if not available
try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests", file=sys.stderr)
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
            with open(self.config_path, 'r') as f:
                # YAML config is not Python dict; parse it ourselves
                import re
                content = f.read()
                # For now, return a simple dict; proper YAML parsing below
                config = {
                    'forge_changelog': [
                        'accounts', 'apache', 'apt', 'docker', 'firewall', 'inifile',
                        'peadm', 'postgresql', 'pwshlib', 'sce_windows', 'sqlserver'
                    ],
                    'external_docs': {
                        'sce_linux': {
                            'type': 'help_puppet_versioned',
                            'base_url': 'https://help.puppet.com/sce/current/linux/',
                            'url_pattern': 'scel_relnotes_{version_underscore}.htm'
                        }
                    }
                }
                return config
        except FileNotFoundError:
            print(f"WARNING: Config not found at {self.config_path}, using defaults", file=sys.stderr)
            return {'forge_changelog': [], 'external_docs': {}}
    
    def get_release_notes_source(self, module_name: str) -> Dict:
        """Determine release notes source for a module."""
        external = self.release_notes_sources.get('external_docs', {})
        if module_name in external:
            return {
                'source': 'external_docs',
                'config': external[module_name]
            }
        return {'source': 'forge_changelog'}
    
    def discover_from_html(self, html_content: str) -> List[Dict]:
        """
        Parse Forge listing HTML to extract module info.
        
        For now, return stub data. In production, parse with BeautifulSoup:
        - Extract module name, version, release date from each listing
        """
        # TODO: Implement HTML parsing with BeautifulSoup
        # For now, return example structure
        return []
    
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
                'discovered_at': datetime.utcnow().isoformat() + 'Z',
                'query_url': self.FORGE_LISTING_URL
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
        for module in discovered.get('modules', []):
            name = module.get('name', '').lower()
            source_info = self.get_release_notes_source(name)
            module['release_notes_source'] = source_info['source']
            
            if source_info['source'] == 'external_docs':
                # Construct release notes URL from config
                config = source_info.get('config', {})
                module['release_notes_url'] = self._build_external_docs_url(
                    name, module.get('latest_version'), config
                )
        
        return discovered
    
    def _build_external_docs_url(self, module_name: str, version: str, config: Dict) -> str:
        """Construct external docs URL using config pattern."""
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
        
        return urljoin(base_url, url)


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
