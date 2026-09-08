"""Parsing for external (help.puppet.com) release-notes docs.

Extracted from ReleaseNotesFetcher in 02_fetch_release_notes.py. These are
plain functions (no instance state was needed) so they can be shared with
report_module_releases.py, which fetches the same pages independently.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .changelog_parse import clean_text, dedupe_and_limit

_VERSION_HEADING_RE = re.compile(r'\b(\d+\.\d+\.\d+)\b')
_RELEASED_DATE_RE = re.compile(r'Released\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})')


def parse_external_docs(html: str, limit: Optional[int] = 5) -> List[str]:
    """Parse generic (non-MadCap) external docs HTML for release notes bullets."""
    soup = BeautifulSoup(html, 'html.parser')

    bullets: List[str] = []
    content_root = (
        soup.find('main')
        or soup.find('article')
        or soup.find('div', attrs={'role': 'main'})
        or soup
    )

    for li in content_root.find_all('li'):
        text = clean_text(li.get_text(' ', strip=True))
        if text:
            bullets.append(text)

    return dedupe_and_limit(bullets, limit=limit)


def parse_madcap_flare(
    html: str,
    anchor: str = '',
    version: str = '',
    module_name: str = '',
    limit: Optional[int] = 5,
) -> List[str]:
    """Parse MadCap Flare HTML (help.puppet.com) for release notes.

    MadCap Flare pages have a nav TOC with version links, main content in
    div[data-mc-content-body="True"], and real content as <li><p> or <li>
    with descriptions. Scopes to an anchor section or a version-matching
    heading when possible, then filters out pure navigation items.
    """
    soup = BeautifulSoup(html, 'html.parser')
    bullets: List[str] = []

    content_container = soup.find('div', attrs={'data-mc-content-body': 'True'})
    if not content_container:
        content_container = (
            soup.find('main')
            or soup.find('article')
            or soup.find('div', attrs={'role': 'main'})
            or soup
        )

    search_root = _find_anchor_section_root(content_container, anchor)
    if not anchor:
        search_root = _find_version_section_root(search_root, version, module_name)

    for li in search_root.find_all('li'):
        text = _clean_madcap_text(li)
        if text and _is_content_item(text):
            bullets.append(text)

    return dedupe_and_limit(bullets, limit=limit)


def extract_madcap_release_sections(html: str, limit: Optional[int] = None) -> List[Dict]:
    """Parse every version section on a MadCap Flare release-notes page.

    help.puppet.com's cd4peadm/comply/complyadm pages keep the full release
    history on one page, each version as its own heading (e.g. "Version
    5.17.0" or "Security Compliance Management 3.9.0") immediately followed
    by a "Released D Month YYYY." paragraph. `parse_madcap_flare` only scopes
    to one target version/anchor; this mirrors
    `changelog_parse.extract_release_sections()` for the Forge-changelog path
    instead, returning every section so a caller can filter by date range and
    catch a module that shipped more than once in the target month -- which
    `parse_madcap_flare` alone would silently miss (it only ever looks at the
    "current" version's anchor).

    Traversal is read-only (no nodes are moved into a scratch soup, unlike
    `_find_anchor_section_root`/`_find_version_section_root`), since it needs
    to inspect every heading in the page rather than just one.
    """
    soup = BeautifulSoup(html, 'html.parser')
    content_container = soup.find('div', attrs={'data-mc-content-body': 'True'}) or (
        soup.find('main') or soup.find('article') or soup.find('div', attrs={'role': 'main'}) or soup
    )

    heading_tags = ['h1', 'h2', 'h3', 'h4']
    version_headings = []
    for heading in content_container.find_all(heading_tags):
        # NOTE: deliberately not clean_text() here -- it blanks out any string
        # starting with "version " (a rule meant to filter noisy bullet-list
        # items), which would wipe every heading on this page ("Version
        # 5.18.0", etc.) before the version regex ever sees it.
        heading_text = re.sub(r'\s+', ' ', heading.get_text(' ', strip=True)).strip()
        match = _VERSION_HEADING_RE.search(heading_text)
        if match:
            version_headings.append((heading, match.group(1)))

    sections: List[Dict] = []
    for heading, version in version_headings:
        section_nodes = []
        node = heading.find_next_sibling()
        while node is not None:
            if getattr(node, 'name', None) in heading_tags:
                node_text = re.sub(r'\s+', ' ', node.get_text(' ', strip=True)).strip()
                if _VERSION_HEADING_RE.search(node_text):
                    break
            section_nodes.append(node)
            node = node.find_next_sibling()

        release_date = ''
        for section_node in section_nodes[:3]:
            text = section_node.get_text(' ', strip=True) if hasattr(section_node, 'get_text') else ''
            date_match = _RELEASED_DATE_RE.search(text)
            if date_match:
                try:
                    release_date = datetime.strptime(date_match.group(1), '%d %B %Y').strftime('%Y-%m-%d')
                except ValueError:
                    pass
                break

        bullets = []
        for section_node in section_nodes:
            if not hasattr(section_node, 'find_all'):
                continue
            for li in section_node.find_all('li'):
                text = _clean_madcap_text(li)
                if text and _is_content_item(text):
                    bullets.append(text)

        sections.append({
            'version': version,
            'release_date': release_date,
            'bullets': dedupe_and_limit(bullets, limit=limit),
        })

    sections.sort(key=lambda s: s.get('release_date') or '', reverse=True)
    return sections


def _find_version_section_root(content_container, version: str, module_name: str = ''):
    """Scope parsing to the section matching the target version when possible."""
    if not version:
        return content_container

    version_pattern = re.compile(rf'\b{re.escape(version)}\b')
    heading_tags = ['h1', 'h2', 'h3', 'h4']
    version_heading = None

    for heading in content_container.find_all(heading_tags):
        heading_text = clean_text(heading.get_text(' ', strip=True))
        if version_pattern.search(heading_text):
            version_heading = heading
            break

    if not version_heading:
        return content_container

    section_nodes = [version_heading]
    node = version_heading.find_next_sibling()
    while node is not None:
        if getattr(node, 'name', None) == version_heading.name:
            node_text = clean_text(node.get_text(' ', strip=True))
            if re.search(r'\b\d+\.\d+\.\d+\b', node_text):
                break

        section_nodes.append(node)
        node = node.find_next_sibling()

    scoped_soup = BeautifulSoup('', 'html.parser')
    wrapper = scoped_soup.new_tag('div')
    for section_node in section_nodes:
        wrapper.append(section_node)
    scoped_soup.append(wrapper)
    return scoped_soup


def _find_anchor_section_root(content_container, anchor: str):
    """Return a scoped root for an anchor section when available."""
    if not anchor:
        return content_container

    anchor_target = (
        content_container.find(attrs={'id': anchor})
        or content_container.find('a', attrs={'name': anchor})
    )
    if not anchor_target:
        return content_container

    section_nodes = []
    heading_tags = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

    node = anchor_target
    while node is not None:
        section_nodes.append(node)
        node = node.find_next_sibling()
        if node is not None and getattr(node, 'name', None) in heading_tags:
            break

    if len(section_nodes) <= 1:
        parent_block = anchor_target.find_parent(['section', 'article', 'div'])
        return parent_block or content_container

    scoped_soup = BeautifulSoup('', 'html.parser')
    wrapper = scoped_soup.new_tag('div')
    for section_node in section_nodes:
        wrapper.append(section_node)
    scoped_soup.append(wrapper)
    return scoped_soup


def _clean_madcap_text(li_element) -> str:
    """Extract and clean text from a MadCap Flare <li> element.

    Handles <li><p>text</p></li>, <li>text</li>, nested markup, etc.
    Preserves <b> tags as **markdown bold** so titles stay readable.
    """
    p_tag = li_element.find('p')
    el = p_tag if p_tag else li_element

    parts = []
    for child in el.children:
        if hasattr(child, 'name'):
            if child.name == 'b':
                inner = child.get_text(' ', strip=True)
                if inner:
                    parts.append(f'**{inner}**')
            else:
                inner = child.get_text(' ', strip=True)
                if inner:
                    parts.append(inner)
        else:
            raw = str(child)
            stripped = raw.strip()
            if stripped:
                parts.append(stripped)

    text = ' '.join(parts)
    # Remove bold markdown wrapping lone punctuation (MadCap artifact: <b>.</b>)
    text = re.sub(r'\*\*([.,:;!?])\*\*', r'\1', text)
    text = re.sub(r'\s+([.,:;!?])', r'\1', text)
    text = re.sub(r'\s+', ' ', text or '').strip()

    return text


def _is_content_item(text: str) -> bool:
    """Determine if text is actual release note content vs navigation."""
    if len(text) < 10:
        return False

    if re.search(r'Version\s+\d+\.\d+\.\d+', text):
        version_count = len(re.findall(r'Version\s+\d+\.\d+\.\d+', text))
        if version_count > 1 or (version_count == 1 and text.strip().startswith('Version')):
            return False

    if re.match(r'^(?:Version\s+)?\d+\.\d+(?:\.\d+)?$', text):
        return False

    nav_items = [
        'Security Compliance Management',
        'Continuous Delivery',
        'release notes',
    ]
    for item in nav_items:
        if re.match(rf'^{re.escape(item)}(?:\s+\d+\.\d+(?:\.\d+)?)?$', text):
            return False

    if re.match(r'^(?:Security Compliance Management|Continuous Delivery)\s+\d+\.\d+', text):
        return False

    if re.search(r'(Security Compliance Management|Continuous Delivery)\s+release\s+notes', text):
        if re.search(r'(Security Compliance Management|Continuous Delivery)\s+\d+\.\d+', text):
            return False

    return True
