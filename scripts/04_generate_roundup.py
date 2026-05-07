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
from typing import Dict, List, Optional, Tuple
import re

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class RoundupGenerator:
    """Generate final roundup markdown from curated highlights and release notes."""

    def __init__(self, template_path: Optional[Path] = None):
        """Initialize generator with optional template file."""
        self.template_path = template_path or Path('MONTHLY_ROUNDUP_TEMPLATE.md')
        self.template_content = None
        
        if self.template_path.exists():
            with open(self.template_path, 'r', encoding='utf-8') as f:
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
        return self._generate_post(highlights_data, release_notes_data, month_name, year)
    
    def _format_highlights(self, highlights_data: Dict) -> str:
        """Format highlighted updates section from curated highlights."""
        sections = []
        themes = highlights_data.get('themes', [])
        major_features = highlights_data.get('major_features', [])
        single_updates = highlights_data.get('single_important_updates', [])
        breaking = highlights_data.get('breaking_changes', [])
        security = highlights_data.get('security_updates', [])

        for theme in themes[:2]:
            title = theme.get('title') or theme.get('phrase') or 'Notable theme'
            description = theme.get('description', '').strip()
            bullets = []

            for module_name in theme.get('modules', []):
                feature = self._find_best_item_for_theme(theme, major_features, single_updates, module_name)

                if feature and feature.get('bullet'):
                    bullets.append(feature['bullet'])

            if not bullets and theme.get('affected_modules'):
                bullets.append(f"Affected modules: {theme['affected_modules']}")

            sections.append(self._format_highlight_block(title, description, self._dedupe_preserve_order(bullets)[:2]))

        if not sections and major_features:
            top_features = major_features[:2]
            for feature in top_features:
                title = feature.get('title', 'Notable update')
                description = feature.get('description', '').strip()
                bullet = feature.get('bullet', '').strip()
                sections.append(self._format_highlight_block(title, description, [bullet] if bullet else []))

        if breaking:
            bullets = [f"{item['module']}: {item['bullet']}" for item in breaking[:2] if item.get('module') and item.get('bullet')]
            if bullets:
                sections.append(self._format_highlight_block('Breaking changes to review', 'A small number of releases include compatibility-impacting changes that may need extra review before rollout.', bullets))

        if security:
            bullets = [f"{item['module']}: {item['bullet']}" for item in security[:2] if item.get('module') and item.get('bullet')]
            if bullets:
                sections.append(self._format_highlight_block('Security-related updates', 'The following releases include security-relevant fixes or related maintenance work.', bullets))

        return "\n\n".join(section for section in sections if section) if sections else "_No major themes identified this month._"

    def _format_highlight_block(self, title: str, summary: str, bullets: List[str]) -> str:
        """Format a single highlight section in roundup style."""
        lines = [f"### {title}"]

        if summary:
            lines.append("")
            lines.append(summary)

        cleaned_bullets = [bullet.strip().rstrip('.') + '.' for bullet in bullets if bullet and bullet.strip()]
        if cleaned_bullets:
            lines.append("")
            lines.extend([f"- {bullet}" for bullet in cleaned_bullets])

        return "\n".join(lines)

    def _find_feature_for_module(self, items: List[Dict], module_name: str) -> Optional[Dict]:
        """Return the first highlight item that matches a module name."""
        for item in items:
            if item.get('module') == module_name:
                return item
        return None

    def _find_best_item_for_theme(
        self,
        theme: Dict,
        major_features: List[Dict],
        single_updates: List[Dict],
        module_name: str,
    ) -> Optional[Dict]:
        """Pick the module-specific highlight item that best matches the theme text."""
        candidates = [item for item in major_features + single_updates if item.get('module') == module_name]
        if not candidates:
            return None

        theme_text = ' '.join(
            [
                theme.get('title', ''),
                theme.get('phrase', ''),
                theme.get('description', ''),
                theme.get('candidate_reason', ''),
            ]
        )
        theme_keywords = self._keyword_set(theme_text)

        if not theme_keywords:
            return candidates[0]

        best_item = candidates[0]
        best_score = -1
        for item in candidates:
            candidate_text = ' '.join(
                [item.get('title', ''), item.get('description', ''), item.get('bullet', '')]
            )
            score = len(theme_keywords & self._keyword_set(candidate_text))
            if score > best_score:
                best_item = item
                best_score = score

        return best_item

    def _keyword_set(self, text: str) -> set[str]:
        """Extract a compact keyword set for loose theme matching."""
        stop_words = {
            'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'across',
            'more', 'most', 'than', 'have', 'has', 'had', 'was', 'were', 'will',
            'now', 'new', 'its', 'their', 'while', 'also', 'allow', 'allows',
            'making', 'make', 'made', 'using', 'used', 'use', 'updates', 'update',
            'improvements', 'improvement', 'several', 'focused', 'focuses', 'release',
            'releases', 'module', 'modules', 'support', 'supported'
        }
        words = re.findall(r'[a-z0-9_]{3,}', text.lower())
        return {word for word in words if word not in stop_words}

    def _dedupe_preserve_order(self, items: List[str]) -> List[str]:
        """Remove duplicates while preserving first-seen order."""
        seen = set()
        deduped = []
        for item in items:
            normalized = self._plain_text(item).lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(item)
        return deduped
    
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

            forge_url = module.get('forge_url') or f"https://forge.puppet.com/modules/puppetlabs/{slug}"
            if module.get('source') == 'external_docs':
                summary = self._build_external_summary_block(module)
                bullet_lines = []
            else:
                summary = self._summarize_module(module)
                bullet_lines = [f"- {bullet}" for bullet in bullets[:5] if bullet]
            optional_line = self._optional_release_notes_line(module)

            entry_lines = [
                f"### {name} {version}",
                "",
                f"📅 Latest release: {release_date} (🌐 [View on the Forge]({forge_url}))",
                "",
                summary,
            ]

            if bullet_lines:
                entry_lines.append("")
                entry_lines.extend(bullet_lines)

            if optional_line:
                entry_lines.append("")
                entry_lines.append(optional_line)

            entry = "\n".join(entry_lines)
            entries.append(entry)

        return "\n\n---\n\n".join(entries)

    def _summarize_module(self, module: Dict) -> str:
        """Create a short editorial summary for a module entry."""
        bullets = [bullet.strip() for bullet in module.get('parsed_bullets', []) if bullet and bullet.strip()]
        name = module.get('name', 'This module')

        if not bullets:
            return f"{name} received a maintenance update this month."

        first_bullet = self._strip_attribution(bullets[0]).rstrip('.')
        if module.get('source') == 'external_docs':
            return f"This release focuses on {first_bullet[:1].lower() + first_bullet[1:]}."

        if len(bullets) == 1:
            return f"This release focuses on {first_bullet[:1].lower() + first_bullet[1:]}."

        second_bullet = self._strip_attribution(bullets[1]).rstrip('.')
        return f"This release focuses on {first_bullet[:1].lower() + first_bullet[1:]} while also addressing {second_bullet[:1].lower() + second_bullet[1:]}."

    def _build_external_summary_block(self, module: Dict) -> str:
        """Create a structured deterministic summary for external docs modules."""
        raw_bullets = [
            self._plain_text(bullet).strip()
            for bullet in module.get('parsed_bullets_full', [])
            if bullet and bullet.strip()
        ]
        if not raw_bullets:
            raw_bullets = [
                self._plain_text(bullet).strip()
                for bullet in module.get('parsed_bullets', [])
                if bullet and bullet.strip()
            ]

        cleaned_bullets = [self._strip_attribution(bullet).rstrip('.') for bullet in raw_bullets]
        highlight_lines = self._select_external_highlights(cleaned_bullets, raw_bullets=raw_bullets)
        if not highlight_lines:
            name = module.get('name', 'this module')
            return f"A few highlights from this release:\n- See official release notes for details for {name}."

        lines = ["A few highlights from this release:"]
        lines.extend([f"- {item}" for item in highlight_lines])
        return "\n".join(lines)

    def _select_external_highlights(self, bullets: List[str], raw_bullets: Optional[List[str]] = None) -> List[str]:
        """Select deterministic external highlights: new/enhanced, fixes, and CVE count."""
        if not bullets:
            return []

        normalized = []
        for bullet in bullets:
            text = re.sub(r'\s+', ' ', bullet).strip()
            if text:
                normalized.append(text)

        seen = set()
        unique_bullets = []
        for bullet in normalized:
            key = bullet.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_bullets.append(bullet)

        cve_source = raw_bullets if raw_bullets else unique_bullets
        cve_matches = re.findall(r'\bCVE-\d{4}-\d+\b', ' '.join(cve_source), flags=re.IGNORECASE)
        cve_count = len({match.upper() for match in cve_matches})

        def is_security(text: str) -> bool:
            low = text.lower()
            return 'cve-' in low or 'security' in low or 'vulnerab' in low

        def is_fixed(text: str) -> bool:
            low = text.lower()
            return any(token in low for token in ['fixed', 'resolved', 'issue', 'error', 'fail'])

        def is_feature(text: str) -> bool:
            low = text.lower()
            return any(token in low for token in ['added', 'new', 'enhance', 'improv', 'support', 'introduc', 'updated'])

        security_bullets = [b for b in unique_bullets if is_security(b)]
        non_security_bullets = [b for b in unique_bullets if not is_security(b)]
        feature_candidates = [b for b in non_security_bullets if is_feature(b)]
        fixed_candidates = [b for b in non_security_bullets if is_fixed(b)]

        selected: List[str] = []

        if feature_candidates:
            selected.append(feature_candidates[0])

        for candidate in feature_candidates[1:] + non_security_bullets:
            if candidate not in selected:
                selected.append(candidate)
            if len(selected) >= 2:
                break

        fixed_choice = None
        for candidate in fixed_candidates:
            if candidate not in selected:
                fixed_choice = candidate
                break
        if fixed_choice:
            selected.append(fixed_choice)

        # Fill remaining slots from non-security bullets only.
        if len(selected) < 3:
            for candidate in non_security_bullets:
                if candidate not in selected:
                    selected.append(candidate)
                if len(selected) >= 3:
                    break

        # CVE handling is always last.
        # When there are 3 or fewer CVEs and no other content, list the CVE bullets
        # directly so readers see the specifics rather than a vague count.
        if cve_count > 0:
            if cve_count <= 3 and not non_security_bullets:
                selected.extend(security_bullets[:cve_count])
            else:
                noun = 'CVE' if cve_count == 1 else 'CVEs'
                selected.append(f"{cve_count} {noun} addressed.")

        return [item.rstrip('.') + '.' for item in selected[:5]]

    def _strip_attribution(self, bullet: str) -> str:
        """Trim trailing contributor attribution and excess whitespace from a changelog bullet."""
        bullet = self._plain_text(bullet)
        # Preserve CVE identifiers for security-related summaries.
        if not bullet.lstrip().upper().startswith('CVE-'):
            # Remove leading ticket IDs so summaries read naturally.
            ticket_prefix_patterns = [
                r'^\s*\([A-Z][A-Z0-9_]*-\d+\)\s*',
                r'^\s*[A-Z][A-Z0-9_]*-\d+\s*[:\-]?\s*',
            ]
            for pattern in ticket_prefix_patterns:
                bullet = re.sub(pattern, '', bullet)

        # Remove common trailing PR attribution patterns after link text is flattened.
        attribution_patterns = [
            r'\s*\(#\d+\)\s*$',
            r'\s*#\d+\s*\([^)]+\)\s*$',
            r'\s*#\d+\s*$',
        ]
        for pattern in attribution_patterns:
            bullet = re.sub(pattern, '', bullet)
        return re.sub(r'\s+', ' ', bullet).strip()

    def _plain_text(self, text: str) -> str:
        """Convert simple markdown links to plain text and normalize spacing."""
        text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _optional_release_notes_line(self, module: Dict) -> str:
        """Return an additional release notes link line when the source is external docs."""
        if module.get('source') != 'external_docs':
            return ''

        version = module.get('version', '')
        source_url = module.get('source_url', '')
        if not source_url:
            return ''

        return f"Check the official [release notes for {module.get('name')} {version}]({source_url}) for the full details."

    def _generate_post(
        self,
        highlights_data: Dict,
        release_notes_data: Dict,
        month_name: str,
        year: int
    ) -> str:
        """Generate roundup markdown in the established post format."""
        markdown = []
        intro_paragraphs = self._build_intro(highlights_data, release_notes_data, month_name, year)
        closing_paragraphs = self._build_closing(highlights_data, release_notes_data, month_name, year)

        markdown.append(f"# Puppetlabs Modules Roundup – {month_name} {year}")
        markdown.append("")

        markdown.append("**Tags:** #puppet")
        markdown.append("")

        for paragraph in intro_paragraphs:
            markdown.append(paragraph)
            markdown.append("")

        markdown.append("## Highlighted Updates")
        markdown.append("")
        markdown.append(self._format_highlights(highlights_data))
        markdown.append("")

        markdown.append(f"## What Updates Happened to Puppetlabs Modules in {month_name} {year}?")
        markdown.append("")
        markdown.append(f"The following is an alphabetical listing of modules which received updates in {month_name} {year}. If a module had multiple versions released, the updates are collected together, numbered with the \"latest\" version available.")
        markdown.append("")
        markdown.append("---")
        markdown.append("")
        markdown.append(self._format_module_entries(release_notes_data))
        markdown.append("")

        markdown.append("## Until Next Time!")
        markdown.append("")

        for paragraph in closing_paragraphs:
            markdown.append(paragraph)
            markdown.append("")

        return "\n".join(markdown)

    def _build_intro(
        self,
        highlights_data: Dict,
        release_notes_data: Dict,
        month_name: str,
        year: int,
    ) -> List[str]:
        """Build two varied intro paragraphs for the roundup."""
        module_count = len(release_notes_data.get('release_notes', []))
        theme_titles = [theme.get('title') or theme.get('phrase') for theme in highlights_data.get('themes', [])]
        theme_titles = [title for title in theme_titles if title]
        theme_summary = self._theme_summary(theme_titles)
        module_phrase = self._module_count_phrase(module_count)

        first_paragraphs = [
            f"{month_name} {year} brought {module_phrase} in the Puppetlabs Forge catalog, and this roundup pulls the most important changes into one place.",
            f"In {month_name} {year}, the Puppetlabs module lineup saw {module_phrase}, with the most notable updates collected here for a quick review.",
            f"This look back at {month_name} {year} covers {module_phrase} from Puppetlabs, with an emphasis on the changes most likely to matter in active environments.",
        ]

        second_paragraphs = [
            f"This month’s updates leaned toward {theme_summary}, making the release set more about practical compatibility and operations work than large feature launches.",
            f"Across the month, the clearest themes were {theme_summary}, so the summary below focuses on support changes, maintenance work, and operational impact.",
            f"The overall pattern in these releases was {theme_summary}, which makes this month’s roundup a useful quick scan for teams planning upgrades or routine maintenance.",
        ]

        intro_index = self._variant_index(month_name, year, len(first_paragraphs))
        return [
            first_paragraphs[intro_index],
            second_paragraphs[(intro_index + 1) % len(second_paragraphs)],
        ]

    def _build_closing(
        self,
        highlights_data: Dict,
        release_notes_data: Dict,
        month_name: str,
        year: int,
    ) -> List[str]:
        """Build varied closing paragraphs for the roundup."""
        module_count = len(release_notes_data.get('release_notes', []))
        next_month_name, next_year = self._next_month(month_name, year)
        top_modules = ', '.join(
            module.get('name', '') for module in release_notes_data.get('release_notes', [])[:2] if module.get('name')
        )
        modules_reference = top_modules if top_modules else 'the modules above'

        first_paragraphs = [
            f"That wraps up the {month_name} {year} roundup. If any of {modules_reference} intersect with your environment, the linked Forge pages and release notes are worth a closer look.",
            f"That’s the full pass through the {module_count} Puppetlabs module releases from {month_name} {year}. The Forge links above are the quickest path to the underlying release details.",
            f"That closes out the {month_name} {year} update set. For deeper implementation detail, the linked module pages and release notes remain the best source of truth.",
        ]

        second_paragraphs = [
            "If you have feedback on the roundup format or want a deeper look at a specific module area, the Perforce Community Slack is still the best place to continue the conversation.",
            "Feedback on the series is always useful, especially if there are module families or release-note patterns that deserve more attention in future editions.",
            "If there is a part of the Puppetlabs ecosystem that would benefit from more context in future roundups, that feedback is worth sending along.",
        ]

        final_lines = [
            f"Catch you in the next roundup for {next_month_name} {next_year}.",
            f"The next roundup will pick up with {next_month_name} {next_year} releases.",
            f"More updates coming next month when the {next_month_name} {next_year} releases land.",
        ]

        closing_index = self._variant_index(month_name, year + module_count, len(first_paragraphs))
        return [
            first_paragraphs[closing_index],
            second_paragraphs[(closing_index + 1) % len(second_paragraphs)],
            final_lines[(closing_index + 2) % len(final_lines)],
        ]

    def _module_count_phrase(self, module_count: int) -> str:
        """Return a readable module-count phrase for intro text."""
        if module_count == 1:
            return 'one Puppetlabs module release'
        return f'{module_count} Puppetlabs module releases'

    def _theme_summary(self, theme_titles: List[str]) -> str:
        """Compress top theme titles into a readable summary phrase."""
        if not theme_titles:
            return 'routine maintenance and compatibility work'

        normalized = [title.lower() for title in theme_titles[:2]]
        if len(normalized) == 1:
            return normalized[0]
        return f"{normalized[0]} and {normalized[1]}"

    def _variant_index(self, month_name: str, year: int, count: int) -> int:
        """Choose a deterministic variant index for a given month and year."""
        month_num = datetime.strptime(month_name, '%B').month
        return (year * 12 + month_num) % count

    def _next_month(self, month_name: str, year: int) -> Tuple[str, int]:
        """Return the following month and year."""
        month_num = datetime.strptime(month_name, '%B').month
        if month_num == 12:
            return 'January', year + 1
        next_month_num = month_num + 1
        return datetime(year, next_month_num, 1).strftime('%B'), year
    
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
        
        module_section_match = re.search(
            r'## What Updates Happened to Puppetlabs Modules.*?\n(.*?)\n## Until Next Time!',
            markdown,
            re.DOTALL,
        )
        module_section = module_section_match.group(1) if module_section_match else ''

        module_headers = re.findall(r'^### .+ \d', module_section, re.MULTILINE)
        if not module_headers:
            errors.append('No module entries were generated')
        
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
        release_lines = re.findall(r'^📅 Latest release: .+$', module_section, re.MULTILINE)
        missing_urls = [line for line in release_lines if 'https://' not in line]
        if missing_urls:
            errors.append('Some module entries are missing Forge URLs')

        if '## Highlighted Updates' not in markdown:
            errors.append('Highlighted Updates section is missing')

        if '## Until Next Time!' not in markdown:
            errors.append('Until Next Time section is missing')
        
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
    
    with open(highlights_path, 'r', encoding='utf-8') as f:
        highlights_data = yaml.safe_load(f)
    
    with open(release_notes_path, 'r', encoding='utf-8') as f:
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
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Roundup generated successfully!", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
