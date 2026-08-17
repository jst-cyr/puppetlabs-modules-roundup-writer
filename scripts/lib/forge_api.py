"""Client for Forge's public v3/modules JSON API.

This is a different (and cheaper) data source than the HTML-scraping approach
in 01_discover_modules.py: the v3 API returns every module's full release
history (and, for Forge-hosted changelogs, the full changelog markdown)
inline, in ~2 paged requests total for the whole puppetlabs namespace. See
MODULE_RELEASES_REPORT_SPEC.md for how this was verified.
"""

from typing import Iterator

# Matches the filters 01_discover_modules.py uses for its HTML listing
# (module_groups=base pe_only, owner puppetlabs), plus hide_deprecated /
# hide_contribution, which mirror what the Forge web app itself requests
# for that same listing (confirmed by inspecting its own pagination links).
_FIRST_PAGE_URL = (
    "https://forge.puppet.com/v3/modules"
    "?limit=100&sort_by=latest_release&module_groups=base+pe_only"
    "&owner=puppetlabs&hide_deprecated=true&hide_contribution=true&offset=0"
)


def iter_puppetlabs_modules(session, first_page_url: str = _FIRST_PAGE_URL) -> Iterator[dict]:
    """Yield every puppetlabs module dict from the v3 API, following pagination.

    Each dict includes the module's embedded `releases` array (full release
    history: version/created_at/deleted_at) and `current_release.changelog`
    (full markdown changelog, when the module hosts one on Forge).
    """
    url = first_page_url
    while url:
        response = session.get(url, timeout=60, headers={'Accept': 'application/json'})
        response.raise_for_status()
        payload = response.json()

        for module in payload.get('results', []):
            yield module

        next_path = (payload.get('pagination') or {}).get('next')
        url = f"https://forge.puppet.com{next_path}" if next_path else None
