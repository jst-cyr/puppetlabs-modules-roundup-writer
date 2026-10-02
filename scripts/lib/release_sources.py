"""Where to source release notes for a given module.

Extracted from ModuleDiscovery in 01_discover_modules.py so
report_module_releases.py can reuse the exact same classification instead of
duplicating it. Behavior is unchanged from the original methods.
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import urldefrag, urljoin

import requests


def get_release_notes_source(module_name: str, config: Dict) -> Dict:
    """Determine release notes source for a module, per release_notes_sources.yaml."""
    manual_review = set(config.get('manual_review', []))
    external = config.get('external_docs', {})

    if module_name in manual_review:
        return {'source': 'manual_review'}

    if module_name in external:
        return {'source': 'external_docs', 'config': external[module_name]}

    return {'source': config.get('default_source', 'forge_changelog')}


def build_external_docs_url(module_name: str, version: str, config: Dict) -> str:
    """Construct an external (help.puppet.com) docs URL from a version pattern."""
    if not version:
        return ''

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

    full_url = urljoin(base_url, url)

    # Check for version_anchor flag to append anchor to URL
    if config.get('version_anchor', False):
        anchor_format = config.get('version_anchor_format', 'Version{version_nodots}')
        version_anchor = anchor_format.replace('{version_nodots}', version_underscore)
        full_url = f"{full_url}#{version_anchor}"

    return full_url


def build_external_docs_url_candidates(version: str, config: Dict) -> List[str]:
    """Build the configured URL plus a 'v'-prefix-toggled fallback.

    help.puppet.com has changed a module's version-in-filename convention
    mid-stream before without warning (sce_linux switched from
    `scel_relnotes_NNN.htm` to the `v`-prefixed `scel_relnotes_vNNN.htm`
    scheme sce_windows already used, starting at its 2.9.0 release), so a
    single static `version_transform` can go stale for new releases. Returns
    the configured variant first, then the opposite-prefix variant, deduped
    (modules whose url_pattern has no `{version_underscore}` placeholder at
    all produce the same URL for both, collapsing to one candidate).
    """
    if not version:
        return []

    configured_transform = config.get('version_transform', '')
    candidates = []
    seen = set()
    for transform in (configured_transform, '' if configured_transform else 'v'):
        probe_config = dict(config)
        if transform:
            probe_config['version_transform'] = transform
        else:
            probe_config.pop('version_transform', None)
        url = build_external_docs_url('', version, probe_config)
        if url and url not in seen:
            seen.add(url)
            candidates.append(url)
    return candidates


def fetch_external_docs_html(
    session: requests.Session, version: str, config: Dict, timeout: int = 10
) -> Tuple[Optional[str], Optional[str]]:
    """Fetch an external-docs page, retrying the alternate-prefix URL on 404.

    Returns (html, url_used) for the first candidate that loads, or
    (None, None) if every candidate fails.
    """
    for url in build_external_docs_url_candidates(version, config):
        fetch_url, _ = urldefrag(url)
        try:
            response = session.get(fetch_url, timeout=timeout)
            response.raise_for_status()
        except requests.HTTPError:
            continue  # try the next candidate (e.g. alternate version prefix)
        except requests.RequestException:
            break  # connection/timeout errors won't be fixed by a different URL
        return response.text, url
    return None, None
