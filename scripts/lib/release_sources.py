"""Where to source release notes for a given module.

Extracted from ModuleDiscovery in 01_discover_modules.py so
report_module_releases.py can reuse the exact same classification instead of
duplicating it. Behavior is unchanged from the original methods.
"""

from typing import Dict
from urllib.parse import urljoin


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
