#!/usr/bin/env python3
"""
Stage 5 (optional): Count Internal vs. Community Contributions
Scans a generated roundup post for GitHub contributor attributions
(`([user](https://github.com/user))`) and classifies each contribution as
internal (Puppet/Perforce, per config/internal_contributors.yaml) or community.

Counts CONTRIBUTIONS (one per attributed bullet), not unique contributors --
someone who lands 5 PRs in a month counts 5 times.

Usage:
    python scripts/05_count_contributions.py --post "posts/2026-06 June 2026 Puppetlabs Modules Roundup.md"

Output:
    Human-readable summary to stdout. Any GitHub handle not found in
    config/internal_contributors.yaml is reported under "Unknown" so the
    curator can classify it and add it to the config for next time.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from lib.contributor_classification import ATTRIBUTION_RE, classify_handle, load_classification

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "internal_contributors.yaml"


def count_contributions(post_path: Path):
    text = post_path.read_text(encoding="utf-8")
    counts = Counter()
    for display_name, url_name in ATTRIBUTION_RE.findall(text):
        # The link text and URL segment should match for a real attribution;
        # skip anything else (e.g. a stray link that isn't a user attribution).
        if display_name.lower() != url_name.lower():
            continue
        counts[display_name] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description="Count internal vs. community contributions in a roundup post")
    parser.add_argument("--post", required=True, help="Path to the generated roundup post markdown file")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to internal_contributors.yaml")
    args = parser.parse_args()

    post_path = Path(args.post)
    if not post_path.exists():
        print(f"ERROR: post file not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    internal_set, community_set = load_classification(config_path)
    counts = count_contributions(post_path)

    internal_total = 0
    community_total = 0
    unknown_total = 0
    internal_rows, community_rows, unknown_rows = [], [], []

    for user, n in counts.items():
        classification = classify_handle(user, internal_set, community_set)
        if classification == "internal":
            internal_total += n
            internal_rows.append((user, n))
        elif classification == "community":
            community_total += n
            community_rows.append((user, n))
        else:
            unknown_total += n
            unknown_rows.append((user, n))

    total = internal_total + community_total + unknown_total

    def print_rows(label, rows, total_n):
        print(f"\n{label} ({total_n} contributions, {len(rows)} contributors):")
        for user, n in sorted(rows, key=lambda r: -r[1]):
            print(f"  {n:>3}  {user}")

    print(f"Contribution count for {post_path.name}")
    print(f"Total attributed contributions: {total}")
    print_rows("Internal (Puppet/Perforce)", internal_rows, internal_total)
    print_rows("Community", community_rows, community_total)
    if unknown_rows:
        print_rows("UNKNOWN -- not in config/internal_contributors.yaml, please classify", unknown_rows, unknown_total)
        print(
            f"\nAdd these {len(unknown_rows)} handle(s) to the 'internal' or 'community' list in "
            f"{config_path} before trusting these totals.",
            file=sys.stderr,
        )

    print(f"\nSummary: {internal_total} internal / {community_total} community / {unknown_total} unknown = {total} total")


if __name__ == "__main__":
    main()
