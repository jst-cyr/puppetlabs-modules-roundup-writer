"""GitHub-handle attribution and internal/community classification.

Extracted from 05_count_contributions.py so the same regex and classification
logic can be applied per-bullet (report_module_releases.py) as well as
per-post (05_count_contributions.py). Behavior is unchanged.
"""

import re
from pathlib import Path
from typing import Tuple

import yaml

# Matches a markdown link whose URL is exactly a GitHub profile, e.g.
# "[jcpunk](https://github.com/jcpunk)". Callers should additionally check
# that the link text and URL segment match (see 05_count_contributions.py's
# `count_contributions`) to avoid treating an unrelated link as attribution.
ATTRIBUTION_RE = re.compile(r"\[([A-Za-z0-9_-]+)\]\(https://github\.com/([A-Za-z0-9_-]+)\)")


def load_classification(config_path: Path) -> Tuple[set, set]:
    """Load config/internal_contributors.yaml into (internal, community) lowercased handle sets."""
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    internal = {u.lower() for u in (data.get("internal") or [])}
    community = {u.lower() for u in (data.get("community") or [])}
    return internal, community


def classify_handle(handle: str, internal_set: set, community_set: set) -> str:
    """Classify a GitHub handle as 'internal', 'community', or 'unknown'."""
    key = handle.lower()
    if key in internal_set:
        return "internal"
    if key in community_set:
        return "community"
    return "unknown"
