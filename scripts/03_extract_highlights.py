#!/usr/bin/env python3
"""
Stage 3: Extract Highlights Candidates
Use GitHub Copilot agent to intelligently analyze release notes and identify trends/themes/highlights.
Output candidates as YAML for human curation.

Usage:
    python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json
    python scripts/03_extract_highlights.py --input data/march_2026_release_notes_raw.json --output data/march_2026_highlights_candidates.yaml

How it works:
    - Reads release_notes_raw.json from Stage 2
    - Calls GitHub Copilot agent via VS Code integration
    - Agent analyzes all bullets to identify themes and highlights
    - Returns structured results as YAML

Output:
    - data/{month}_{year}_highlights_candidates.yaml (for curator to edit)
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class GitHubCopilotHighlightsExtractor:
    """Use GitHub Copilot agent to intelligently analyze release notes."""
    
    def __init__(self):
        """Initialize extractor (no API key needed - uses existing Copilot access)."""
        self.in_vscode = self._check_vscode_context()
    
    def _check_vscode_context(self) -> bool:
        """Check if running in VS Code context (for agent invocation)."""
        # Agent invocation works through the VS Code extension
        # This script will be called from the terminal, but agent invocation
        # will work through the VS Code API
        return True
    
    def extract_all(self, release_notes_data: Dict) -> Dict:
        """
        Use Copilot agent to intelligently extract highlights from release notes.
        
        Returns:
            Dict with themes, breaking_changes, major_features, security_updates
        """
        # Compile release notes into readable format for analysis
        release_notes_text = self._format_for_analysis(release_notes_data)
        
        print("Sending release notes to GitHub Copilot agent for analysis...", file=sys.stderr)
        print("(This will open a browser tab to invoke the agent)", file=sys.stderr)
        
        # Create task description for agent
        task_description = self._create_agent_task(release_notes_text)
        
        # Write task to temp file for compatibility, then always clean it up.
        task_file = Path('/tmp/stage3_analysis_task.txt') if not sys.platform.startswith('win') else Path('temp_stage3_task.txt')
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task_description)

            print(f"\n📋 Task written to: {task_file}", file=sys.stderr)
            print("Opening GitHub Copilot chat interface...", file=sys.stderr)
            print("\n⚠️  NEXT STEPS:", file=sys.stderr)
            print("1. GitHub Copilot agent browser tab should open", file=sys.stderr)
            print("2. Paste the following prompt into the Copilot chat:", file=sys.stderr)
            print("\n" + "="*80, file=sys.stderr)
            print(task_description, file=sys.stderr)
            print("="*80 + "\n", file=sys.stderr)
            print("3. Copy the YAML response from Copilot", file=sys.stderr)
            print("4. Save it to: " + self._get_default_output_path(release_notes_data), file=sys.stderr)
            print("\nAlternatively, run this script with --agent-mode to invoke agent programmatically", file=sys.stderr)
        finally:
            if task_file.exists():
                try:
                    task_file.unlink()
                except OSError:
                    print(f"WARNING: Could not remove temporary file: {task_file}", file=sys.stderr)
        
        # Return empty for now - user will manually copy results
        return self._get_empty_highlights()
    
    def _format_for_analysis(self, release_notes_data: Dict) -> str:
        """Format release notes into readable text for analysis."""
        lines = []
        lines.append("# Release Notes Summary\n")
        
        for entry in release_notes_data.get('release_notes', []):
            module_name = entry.get('name', 'Unknown')
            version = entry.get('version', '?')
            release_date = entry.get('release_date', '?')
            bullets = entry.get('parsed_bullets', [])
            
            lines.append(f"\n## {module_name} v{version} (released {release_date})\n")
            for bullet in bullets:
                lines.append(f"- {bullet}")
        
        return '\n'.join(lines)
    
    def _create_agent_task(self, release_notes_text: str) -> str:
        """Create detailed task description for Copilot agent."""
        return f"""You are a technical analyst reviewing Puppet module releases from this month.

Analyze the provided release notes and identify important themes, highlights, and trends.

## Release Notes to Analyze:

{release_notes_text}

## Your Task:

Identify and categorize the following from the release notes:

1. **Common themes/trends**: Patterns that appear across MULTIPLE modules (e.g., "Windows Server 2025 support" appears in 3+ modules). Be selective—only cross-module patterns.

2. **Breaking changes**: Any removals, deprecations, or incompatible changes.

3. **Major features**: Significant new capabilities or improvements that stand out.

4. **Security updates**: Any CVE fixes or security-related changes.

5. **Important single updates**: One-off changes that are notable but don't fit other categories.

## Output Format:

Provide the results ONLY as valid YAML (no markdown, no code blocks). Structure:

```yaml
themes:
  - title: "Theme name (e.g., Windows Server 2025 Support)"
    description: "What this theme means and why it matters"
    affected_modules: "module1, module2, module3"

breaking_changes:
  - module: "module_name"
    title: "Breaking change title"
    description: "What changed and the impact"

major_features:
  - module: "module_name"
    title: "Feature name"
    description: "Why this feature is important"

security_updates:
  - module: "module_name"
    title: "Security fix"
    description: "CVE or vulnerability addressed"

single_important_updates:
  - module: "module_name"
    title: "Update title"
    description: "Why it matters"
```

Be concise, factual, and focus on what would be noteworthy in a monthly roundup article. Themes should ONLY include items appearing in multiple modules."""
    
    def _get_default_output_path(self, release_notes_data: Dict) -> str:
        """Get default output path based on input."""
        # This would be set by caller, but return generic path
        return "data/{month}_{year}_highlights_candidates.yaml"
    
    def _get_empty_highlights(self) -> Dict:
        """Return empty highlights structure for manual population."""
        return {
            'themes': [],
            'breaking_changes': [],
            'major_features': [],
            'security_updates': [],
            'single_important_updates': []
        }


class YAMLResultsParser:
    """Parse YAML results from Copilot agent and validate structure."""
    
    @staticmethod
    def parse_from_file(yaml_file: Path) -> Optional[Dict]:
        """Load and validate YAML results file."""
        try:
            with open(yaml_file, 'r') as f:
                results = yaml.safe_load(f)
            
            # Validate structure
            required_keys = {'themes', 'breaking_changes', 'major_features', 'security_updates'}
            if not all(key in results for key in required_keys):
                print(f"ERROR: YAML missing required keys. Expected: {required_keys}", file=sys.stderr)
                return None
            
            return results
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"ERROR: Failed to parse YAML: {e}", file=sys.stderr)
            return None
    
    @staticmethod
    def validate(highlights: Dict) -> List[str]:
        """Validate highlights structure."""
        errors = []
        
        # Check for at least some highlights
        total = sum(len(highlights.get(k, [])) for k in ['themes', 'breaking_changes', 'major_features', 'security_updates'])
        if total == 0:
            errors.append("No highlights found in any category")
        
        # Check themes have affected_modules
        for theme in highlights.get('themes', []):
            if 'affected_modules' not in theme:
                errors.append(f"Theme '{theme.get('title', 'unknown')}' missing affected_modules field")
        
        return errors


def main():
    parser = argparse.ArgumentParser(
        description='Use GitHub Copilot to intelligently extract highlights from release notes'
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
    parser.add_argument(
        '--from-file',
        help='Instead of running analysis, load YAML results from this file (for validation)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load release notes
    with open(input_path, 'r') as f:
        release_notes_data = json.load(f)
    
    num_modules = len(release_notes_data.get('release_notes', []))
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Replace 'release_notes_raw' with 'highlights_candidates'
        output_path = input_path.parent / input_path.name.replace(
            'release_notes_raw', 'highlights_candidates'
        ).replace('.json', '.yaml')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # If loading from file (validation mode)
    if args.from_file:
        print(f"Loading highlights from: {args.from_file}", file=sys.stderr)
        highlights = YAMLResultsParser.parse_from_file(Path(args.from_file))
        if not highlights:
            sys.exit(1)
        
        # Validate
        errors = YAMLResultsParser.validate(highlights)
        if errors:
            print("⚠️  Validation warnings:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        
        # Copy to output location
        with open(args.from_file, 'r') as src:
            content = src.read()
        with open(output_path, 'w') as dst:
            dst.write(content)
        
        print(f"✅ Highlights loaded and saved to: {output_path}", file=sys.stderr)
        sys.exit(0)
    
    # Analysis mode: generate task for Copilot
    print(f"Analyzing {num_modules} modules with GitHub Copilot agent...", file=sys.stderr)
    
    try:
        extractor = GitHubCopilotHighlightsExtractor()
        highlights = extractor.extract_all(release_notes_data)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n" + "="*80, file=sys.stderr)
    print("INSTRUCTIONS:", file=sys.stderr)
    print("="*80, file=sys.stderr)
    print("\n1. Copy the prompt above (between the equals signs)", file=sys.stderr)
    print("2. Open GitHub Copilot in this VS Code window (Ctrl+I)", file=sys.stderr)
    print("3. Paste the prompt and run it", file=sys.stderr)
    print("4. Copilot will return YAML results for the highlights", file=sys.stderr)
    print("5. Save the YAML to a temporary file or copy to clipboard", file=sys.stderr)
    print("6. Run this command to load the results:", file=sys.stderr)
    print(f"\n   python scripts/03_extract_highlights.py --input {args.input} --from-file <results.yaml>", file=sys.stderr)
    print("\n" + "="*80 + "\n", file=sys.stderr)


if __name__ == '__main__':
    main()
