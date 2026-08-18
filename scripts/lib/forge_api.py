"""Client for Forge's public v3/modules JSON API.

This is a different (and cheaper) data source than the HTML-scraping approach
in 01_discover_modules.py: the v3 API returns every module's full release
history (and, for Forge-hosted changelogs, the full changelog markdown)
inline, in a handful of paged requests. See MODULE_RELEASES_REPORT_SPEC.md
for how this was verified for the puppetlabs-scoped case.
"""

import sys
from typing import Iterator, Optional

# Matches the filters 01_discover_modules.py uses for its HTML listing
# (module_groups=base pe_only), plus hide_deprecated / hide_contribution,
# which mirror what the Forge web app itself requests for that same listing
# (confirmed by inspecting its own pagination links). `owner` is appended
# separately since omitting it entirely pages the whole Forge catalog.
_BASE_URL = (
    "https://forge.puppet.com/v3/modules"
    "?limit=100&sort_by=latest_release&module_groups=base+pe_only"
    "&hide_deprecated=true&hide_contribution=true&offset=0"
)


def iter_forge_modules(session, owner: Optional[str] = None) -> Iterator[dict]:
    """Yield every module dict from the v3 API, following pagination.

    Pass `owner` (e.g. 'puppetlabs') to scope to a single publisher; omit it
    to page the entire Forge catalog across all publishers (~1,500 modules,
    ~15 pages as of 2026-08).

    Each dict includes the module's embedded `releases` array (full release
    history: version/created_at/deleted_at), `owner` (with `slug`, the
    publisher's Forge username), and `current_release.changelog` (full
    markdown changelog, when the module hosts one on Forge).
    """
    url = _BASE_URL + (f"&owner={owner}" if owner else "")
    page = 0
    while url:
        response = session.get(url, timeout=60, headers={'Accept': 'application/json'})
        response.raise_for_status()
        payload = response.json()
        page += 1

        results = payload.get('results', [])
        total = (payload.get('pagination') or {}).get('total')
        if owner is None and total:
            print(f"  ...page {page}, {len(results)} modules (total {total})", file=sys.stderr)

        for module in results:
            yield module

        next_path = (payload.get('pagination') or {}).get('next')
        url = f"https://forge.puppet.com{next_path}" if next_path else None
