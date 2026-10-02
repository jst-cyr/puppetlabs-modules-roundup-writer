"""Fallback fetch of a module's archived changelog history from GitHub.

Some modules (aws_inventory, azure_inventory, gcloud_inventory, http_request,
terraform, vault, ...) truncate their live CHANGELOG.md once it grows long,
moving older entries into a separate ARCHIVE.md in the same repo and leaving
a pointer behind (e.g. "Release notes prior to 0.9.0 have been moved to
ARCHIVE.md"). Forge's v3 API only ever serves the *live* CHANGELOG.md, so
once a version's section has been archived this way it's gone from
`current_release.changelog` entirely for every release, not just the one
that triggered the truncation -- not a parsing failure, the content just
isn't in the API payload anymore. This fetches ARCHIVE.md directly from the
module's own GitHub repo as a fallback source for those older versions.
"""

import re
from typing import Dict, Optional

import requests

_GITHUB_SOURCE_RE = re.compile(r'github\.com[:/]([^/]+)/([^/.]+)')
_BRANCHES = ('main', 'master')


def github_repo_from_source(source_url: str) -> Optional[Dict[str, str]]:
    """Parse {owner, repo} out of a module metadata `source` URL.

    e.g. "https://github.com/puppetlabs/puppetlabs-aws_inventory.git"
    -> {'owner': 'puppetlabs', 'repo': 'puppetlabs-aws_inventory'}
    """
    if not source_url:
        return None
    match = _GITHUB_SOURCE_RE.search(source_url)
    if not match:
        return None
    return {'owner': match.group(1), 'repo': match.group(2)}


def fetch_archive_changelog(
    session: requests.Session, owner: str, repo: str, timeout: int = 10
) -> Optional[str]:
    """Fetch ARCHIVE.md from a module's GitHub repo, trying main then master."""
    for branch in _BRANCHES:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/ARCHIVE.md"
        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException:
            continue
        if response.status_code == 200:
            return response.text
    return None
