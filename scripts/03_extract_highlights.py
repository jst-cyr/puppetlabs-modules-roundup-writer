#!/usr/bin/env python3
"""
Stage 3: Extract Highlights Candidates
Analyze release notes to identify themes, breaking changes, features, and security updates.
Output candidates as YAML for human curation.

Usage:
    python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json
    python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --output data/march_2026_highlights_candidates.yaml

Output:
    - data/{month}_{year}_highlights_candidates.yaml (for curator to edit)
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import re

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class HighlightsExtractor:
    """Detect themes, breaking changes, and notable features from release notes."""
    
    # Keywords for categorizing release notes
    BREAKING_KEYWORDS = {'removed', 'breaking', 'deprecated', 'breaking change', 'incompatible', 'no longer'}
    FEATURE_KEYWORDS = {'added', 'added support', 'now supports', 'support for', 'new', 'introduces'}
    SECURITY_KEYWORDS = {'security', 'cve', 'vulnerability', 'patch', 'fixes security'}
    
    # Phrases to extract as themes (appear 2+ times)
    THEME_MIN_FREQUENCY = 2
    
    # Common words to exclude from theme detection
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'is', 'are', 'was', 'were', 'been', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'to', 'of', 'in', 'for', 'by', 'with', 'on', 'at', 'from', 'that', 'this',
        'it', 'as', 'bug', 'fix', 'fixes', 'fixed', 'fixed', 'update', 'improved'
    }
    
    def __init__(self):
        self.themes = Counter()
        self.breaking_changes = []
        self.major_features = []
        self.security_updates = []
        self.single_important = []
    
    def extract_all(self, release_notes_data: Dict) -> Dict:
        """
        Extract all highlights from release notes.
        
        Returns:
            Dict with themes, breaking_changes, major_features, security_updates
        """
        all_bullets = []
        module_map = {}  # Map theme/feature to list of modules
        
        # Collect all bullets and categorize
        for entry in release_notes_data.get('release_notes', []):
            module_name = entry.get('name', '')
            bullets = entry.get('parsed_bullets', [])
            
            for bullet in bullets:
                all_bullets.append((module_name, bullet))
                
                # Categorize
                if self._is_breaking(bullet):
                    self.breaking_changes.append({
                        'module': module_name,
                        'bullet': bullet
                    })
                elif self._is_security(bullet):
                    self.security_updates.append({
                        'module': module_name,
                        'bullet': bullet
                    })
                elif self._is_feature(bullet):
                    self.major_features.append({
                        'module': module_name,
                        'bullet': bullet
                    })
                
                # Extract themes
                self._extract_themes(bullet, module_name, module_map)
        
        # Build highlights dict
        highlights = {
            'metadata': {
                'extracted_at': datetime.utcnow().isoformat() + 'Z',
                'total_bullets_analyzed': len(all_bullets),
                'note': 'Curator: review and delete rows you do not want in final roundup'
            },
            'themes': self._format_themes(),
            'breaking_changes': self.breaking_changes[:10],  # Top 10
            'major_features': self.major_features[:10],
            'security_updates': self.security_updates[:10],
            'single_important_updates': self.single_important[:5]
        }
        
        return highlights
    
    def _is_breaking(self, bullet: str) -> bool:
        """Check if bullet describes a breaking change."""
        bullet_lower = bullet.lower()
        return any(keyword in bullet_lower for keyword in self.BREAKING_KEYWORDS)
    
    def _is_security(self, bullet: str) -> bool:
        """Check if bullet describes a security update."""
        bullet_lower = bullet.lower()
        return any(keyword in bullet_lower for keyword in self.SECURITY_KEYWORDS)
    
    def _is_feature(self, bullet: str) -> bool:
        """Check if bullet describes a new feature."""
        bullet_lower = bullet.lower()
        return any(keyword in bullet_lower for keyword in self.FEATURE_KEYWORDS)
    
    def _extract_themes(self, bullet: str, module_name: str, module_map: Dict):
        """Extract repeating phrases/themes from bullets."""
        # Simple phrase extraction: capitalized phrases 2-5 words
        # This is a rough heuristic; in production use NLP
        
        # Find phrases like "Puppet 7 support", "Windows Server 2025", etc.
        words = bullet.split()
        
        for i in range(len(words)):
            # Look for capitalized phrases (2-4 words)
            phrase_parts = []
            for j in range(i, min(i + 4, len(words))):
                word = words[j]
                if word[0].isupper() or word.isdigit():
                    phrase_parts.append(word)
                else:
                    break
            
            if len(phrase_parts) >= 2:
                phrase = ' '.join(phrase_parts)
                if phrase not in self.STOP_WORDS:
                    self.themes[phrase] += 1
                    
                    # Track which modules have this theme
                    if phrase not in module_map:
                        module_map[phrase] = set()
                    module_map[phrase].add(module_name)
        
        return module_map
    
    def _format_themes(self) -> List[Dict]:
        """Format themes for YAML output."""
        themes_list = []
        
        for phrase, count in self.themes.most_common():
            if count >= self.THEME_MIN_FREQUENCY:
                themes_list.append({
                    'phrase': phrase,
                    'frequency': count,
                    'description': f'{phrase} mentioned in {count} release notes'
                })
        
        return themes_list[:15]  # Top 15 themes


def main():
    parser = argparse.ArgumentParser(
        description='Extract highlights candidates from release notes'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to release_notes_raw.json from Stage 2'
    )
    parser.add_argument(
        '--output',
        help='Output YAML path (default: input filename with suffix _highlights_candidates.yaml)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load release notes
    with open(input_path, 'r') as f:
        release_notes_data = json.load(f)
    
    print(f"Extracting highlights from {len(release_notes_data.get('release_notes', []))} modules...", file=sys.stderr)
    
    # Extract highlights
    extractor = HighlightsExtractor()
    highlights = extractor.extract_all(release_notes_data)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Replace 'release_notes_raw' with 'highlights_candidates'
        output_path = input_path.parent / input_path.name.replace(
            'release_notes_raw', 'highlights_candidates'
        ).replace('.json', '.yaml')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save output as YAML
    with open(output_path, 'w') as f:
        yaml.dump(highlights, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\nExtracted highlights:", file=sys.stderr)
    print(f"  - {len(highlights['themes'])} themes", file=sys.stderr)
    print(f"  - {len(highlights['breaking_changes'])} breaking changes", file=sys.stderr)
    print(f"  - {len(highlights['major_features'])} major features", file=sys.stderr)
    print(f"  - {len(highlights['security_updates'])} security updates", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)
    print(f"\n⚠️  CURATOR: Review {output_path} and delete rows you don't want to highlight", file=sys.stderr)


if __name__ == '__main__':
    main()
