#!/usr/bin/env python3
"""
Stage 4: Generate Roundup Markdown
Write final roundup post from curated highlights and release notes.

Usage:
    python scripts/04_generate_roundup.py --highlights data/march_2026_highlights_candidates.yaml --release-notes data/march_2026_release_notes_raw.json
    python scripts/04_generate_roundup.py --highlights data/march_2026_highlights_candidates.yaml --release-notes data/march_2026_release_notes_raw.json --output "posts/2026-03 March 2026 Puppetlabs Modules Roundup.md"

Output:
    - posts/YYYY-MM Month Year Puppetlabs Modules Roundup.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class RoundupGenerator:
    """Generate final roundup markdown from curated highlights and release notes."""
    
    # Template for each module entry
    MODULE_TEMPLATE = """### {name} [{version}](https://forge.puppet.com/modules/{slug})

Released {release_date}

{bullets}
"""
    
    def __init__(self, template_path: Optional[Path] = None):
        """Initialize generator with optional template file."""
        self.template_path = template_path or Path('MONTHLY_ROUNDUP_TEMPLATE.md')
        self.template_content = None
        
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                self.template_content = f.read()
    
    def generate(
        self,
        highlights_data: Dict,
        release_notes_data: Dict,
        month_name: str,
        year: int
    ) -> str:
        """
        Generate final roundup markdown.
        
        Args:
            highlights_data: Curated highlights from Stage 3 (with deletions)
            release_notes_data: Release notes from Stage 2
            month_name: Month name (e.g., "March")
            year: Year (e.g., 2026)
        
        Returns:
            Complete markdown content for roundup post
        """
        if not self.template_content:
            return self._generate_without_template(highlights_data, release_notes_data, month_name, year)
        
        # Fill template placeholders
        markdown = self.template_content
        
        # Title and intro
        title = f"Puppetlabs Modules Roundup – {month_name} {year}"
        markdown = markdown.replace('{{TITLE}}', title)
        markdown = markdown.replace('{{MONTH}}', month_name)
        markdown = markdown.replace('{{YEAR}}', str(year))
        
        # Highlighted updates section
        highlighted_updates = self._format_highlights(highlights_data)
        markdown = markdown.replace('{{HIGHLIGHTED_UPDATES}}', highlighted_updates)
        
        # Module entries (alphabetical order)
        module_entries = self._format_module_entries(release_notes_data)
        markdown = markdown.replace('{{MODULES}}', module_entries)
        
        # Validate no placeholders remain
        remaining_placeholders = re.findall(r'\{\{[A-Z_]+\}\}', markdown)
        if remaining_placeholders:
            print(f"WARNING: Unresolved placeholders found: {remaining_placeholders}", file=sys.stderr)
        
        return markdown
    
    def _format_highlights(self, highlights_data: Dict) -> str:
        """Format highlighted updates section from curated highlights."""
        sections = []
        
        # Themes
        themes = highlights_data.get('themes', [])
        if themes:
            theme_bullets = []
            for theme in themes:
                phrase = theme.get('phrase', '')
                description = theme.get('description', '')
                if phrase:
                    theme_bullets.append(f"- **{phrase}**: {description}")
            
            if theme_bullets:
                sections.append("## Key Themes\n\n" + "\n".join(theme_bullets))
        
        # Breaking changes
        breaking = highlights_data.get('breaking_changes', [])
        if breaking:
            breaking_bullets = []
            for item in breaking:
                module = item.get('module', '')
                bullet = item.get('bullet', '')
                if module and bullet:
                    breaking_bullets.append(f"- **{module}**: {bullet}")
            
            if breaking_bullets:
                sections.append("## Breaking Changes\n\n" + "\n".join(breaking_bullets[:5]))
        
        # Security updates
        security = highlights_data.get('security_updates', [])
        if security:
            security_bullets = []
            for item in security:
                module = item.get('module', '')
                bullet = item.get('bullet', '')
                if module and bullet:
                    security_bullets.append(f"- **{module}**: {bullet}")
            
            if security_bullets:
                sections.append("## Security Updates\n\n" + "\n".join(security_bullets[:5]))
        
        return "\n\n".join(sections) if sections else "_No major themes identified this month._"
    
    def _format_module_entries(self, release_notes_data: Dict) -> str:
        """Format module entries (alphabetical order)."""
        modules = release_notes_data.get('release_notes', [])
        
        # Sort alphabetically by module name
        modules_sorted = sorted(modules, key=lambda m: m.get('name', '').lower())
        
        entries = []
        for module in modules_sorted:
            name = module.get('name', '')
            slug = module.get('slug', '')
            version = module.get('version', '')
            release_date = module.get('release_date', '')
            bullets = module.get('parsed_bullets', [])
            
            if not (name and slug and version):
                continue
            
            # Format bullets
            bullet_text = '\n'.join([f"- {bullet}" for bullet in bullets[:5]])  # First 5 bullets
            
            entry = f"""### {name} [{version}](https://forge.puppet.com/modules/{slug})

Released {release_date}

{bullet_text}"""
            entries.append(entry)
        
        return "\n\n".join(entries)
    
    def _generate_without_template(
        self,
        highlights_data: Dict,
        release_notes_data: Dict,
        month_name: str,
        year: int
    ) -> str:
        """Generate without template (fallback)."""
        markdown = []
        
        # Title
        markdown.append(f"# Puppetlabs Modules Roundup – {month_name} {year}")
        markdown.append("")
        
        # Intro
        markdown.append(f"This month we're catching up on the Puppetlabs modules released in {month_name} {year}.")
        markdown.append("")
        
        # Highlighted updates
        markdown.append("## Highlighted Updates")
        markdown.append("")
        markdown.append(self._format_highlights(highlights_data))
        markdown.append("")
        
        # Module entries
        markdown.append("## Module Updates")
        markdown.append("")
        markdown.append(self._format_module_entries(release_notes_data))
        markdown.append("")
        
        # Closing
        markdown.append("## Until Next Time!")
        markdown.append("")
        markdown.append("Until next month, go forth and keep those Puppet modules up to date. As always, you can find all of these releases on the [Puppet Forge](https://forge.puppet.com/).")
        
        return "\n".join(markdown)
    
    def validate(self, markdown: str) -> List[str]:
        """
        Validate generated markdown against AGENTS.md checklist.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for unresolved placeholders
        placeholders = re.findall(r'\{\{[A-Z_]+\}\}', markdown)
        if placeholders:
            errors.append(f"Unresolved placeholders: {', '.join(set(placeholders))}")
        
        # Check for module entries (should have at least 5)
        module_headers = re.findall(r'^### .+', markdown, re.MULTILINE)
        if len(module_headers) < 5:
            errors.append(f"Expected at least 5 module entries, found {len(module_headers)}")
        
        # Check alphabetical order of modules
        module_names = []
        for match in module_headers:
            # Extract module name from "### name [version](...)"
            name_match = re.search(r'### (.+?) \[', match)
            if name_match:
                module_names.append(name_match.group(1).lower())
        
        sorted_names = sorted(module_names)
        if module_names != sorted_names:
            errors.append("Module entries not in alphabetical order")
        
        # Check that all modules have URLs
        missing_urls = re.findall(r'### .+$(?!.*https://)', markdown, re.MULTILINE)
        if missing_urls:
            errors.append(f"Some module entries missing Forge URLs: {missing_urls}")
        
        return errors


def main():
    parser = argparse.ArgumentParser(
        description='Generate final roundup markdown from curated highlights and release notes'
    )
    parser.add_argument(
        '--highlights',
        required=True,
        help='Path to highlights_candidates.yaml (curated by hand)'
    )
    parser.add_argument(
        '--release-notes',
        required=True,
        help='Path to release_notes_raw.json from Stage 2'
    )
    parser.add_argument(
        '--month',
        help='Month name (e.g., March) - will be inferred from filenames if not provided'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='Year (e.g., 2026) - will be inferred from filenames if not provided'
    )
    parser.add_argument(
        '--output',
        help='Output markdown path (default: posts/YYYY-MM Month Year Puppetlabs Modules Roundup.md)'
    )
    parser.add_argument(
        '--template',
        default='MONTHLY_ROUNDUP_TEMPLATE.md',
        help='Path to template file'
    )
    
    args = parser.parse_args()
    
    # Load inputs
    highlights_path = Path(args.highlights)
    release_notes_path = Path(args.release_notes)
    
    if not highlights_path.exists():
        print(f"ERROR: Highlights file not found: {highlights_path}", file=sys.stderr)
        sys.exit(1)
    if not release_notes_path.exists():
        print(f"ERROR: Release notes file not found: {release_notes_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(highlights_path, 'r') as f:
        highlights_data = yaml.safe_load(f)
    
    with open(release_notes_path, 'r') as f:
        release_notes_data = json.load(f)
    
    # Infer month/year if not provided
    if not args.month or not args.year:
        # Try to extract from filename: "march_2026_..."
        match = re.search(r'(\w+)_(\d{4})', highlights_path.name)
        if match:
            month_name = match.group(1).capitalize()
            year = int(match.group(2))
        else:
            print("ERROR: Could not infer month/year. Provide --month and --year", file=sys.stderr)
            sys.exit(1)
    else:
        month_name = args.month.capitalize()
        year = args.year
    
    print(f"Generating roundup for {month_name} {year}...", file=sys.stderr)
    
    # Generate markdown
    generator = RoundupGenerator(Path(args.template) if args.template else None)
    markdown = generator.generate(highlights_data, release_notes_data, month_name, year)
    
    # Validate
    errors = generator.validate(markdown)
    if errors:
        print("⚠️  Validation warnings:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Format: posts/YYYY-MM Month Year Puppetlabs Modules Roundup.md
        month_num = datetime.strptime(month_name, '%B').month
        output_path = Path(f"posts/{year}-{month_num:02d} {month_name} {year} Puppetlabs Modules Roundup.md")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save output
    with open(output_path, 'w') as f:
        f.write(markdown)
    
    print(f"Roundup generated successfully!", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
