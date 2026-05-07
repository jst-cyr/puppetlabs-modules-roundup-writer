# Documentation Source Parsing Analysis

## Executive Summary

The roundup writer encounters **three distinct documentation source types** for Puppet modules, each with fundamentally different parsing requirements:

| Source Type | Example | Structure | Status |
|---|---|---|---|
| **Forge Changelog (Next.js)** | cd4pe 3.4.0 | Markdown in JSON script tag `__NEXT_DATA__` | ✅ Working |
| **MadCap Flare (help.puppet.com)** | cd4peadm 5.15.0, comply 3.7.1 | Server-rendered HTML with embedded TOC | ❌ Failing |
| **Forge Changelog (HTML)** | lvm 4.0.1 | Simple HTML with semantic headings | ✅ Working |

---

## 1. WHY CD4PE (March 2026) WORKED

**File:** `cd4pe_3_4_0.html`  
**Source:** Puppet Forge (Next.js-rendered React app)

### Root Cause: Embedded Markdown in JSON Payload

The Forge module page for cd4pe is a **Next.js SPA** that embeds release notes as **Markdown in JSON**:

```html
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "release": {
        "changelog": "## [v3.4.0]\n### Added\n- Updated puppetlabs-docker...\n- Updated module with PDK 3.6.1"
      }
    }
  }
}
</script>
```

### Why Parser Succeeds

1. **Extracts JSON from `__NEXT_DATA__` script tag** → Gets raw markdown
2. **Regex-based section extraction** → Finds `## [v3.4.0]` section
3. **Markdown bullet parsing** → Extracts clean lines starting with `- ` or `* `
4. **Output:** Correct 2-5 bullets with actual content

### Code Path
```python
# In _parse_forge_changelog():
next_data = soup.find('script', id='__NEXT_DATA__')
if next_data and next_data.string:
    payload = json.loads(next_data.string)
    changelog = payload.get('props', {}).get('pageProps', {}).get('release', {}).get('changelog')
    # Extract markdown bullets for version
```

---

## 2. WHY CD4PEADM (April 2026) FAILED

**File:** `cd4peadm_5_15_0.html`  
**Source:** help.puppet.com (MadCap Flare server-rendered)

### Root Cause: TOC Navigation Captured as Content

The HTML contains **two separate `<ul>` with `<li>` items**:

1. **Navigation TOC** (~line 333-370): Anchor links to version sections
   ```html
   <ul data-magellan="" class="menu">
     <li class="tree-node"><a href="#Version5150">Version 5.15.0</a></li>
     <li class="tree-node"><a href="#Version5140">Version 5.14.0</a></li>
     ...
   </ul>
   ```

2. **Actual Release Notes** (~line 380+): Content `<ul>` with release info
   ```html
   <h2 id="Version5150">Version 5.15.0</h2>
   <ul>
     <li><p>Added a Hiera configuration option, external_webhook_url...</p></li>
     <li><p>Added an idle timeout to the CD console...</p></li>
   </ul>
   ```

### What the Naive Parser Does

```python
content_root = soup.find('main') or soup.find('article') or soup
for li in content_root.find_all('li'):  # ❌ Finds ALL <li> in entire page
    text = li.get_text(' ', strip=True)
    bullets.append(text)
```

**Result:** Outputs the ENTIRE TOC first:
```
"Continuous Delivery (CD) release notes Version 5.15.0 Version 5.14.0 Version 5.13.0..."
```

### Why Navigation Gets Captured

1. All TOC `<li>` items are found before actual content `<li>` items (DOM order)
2. `_clean_text()` filter checks `if text.startswith('version ')` **but** the TOC text is `"Version 5.15.0 Version 5.14.0..."` (all versions concatenated)
3. This passes the version filter (doesn't start with lowercase "version ")
4. Deduplication+limit keeps only 5 items, so actual content at positions 3-5 survives

---

## 3. COMPLYADM (April 2026) - Complete Failure

**File:** `comply_3_7_1.html`  
**Source:** help.puppet.com (MadCap Flare)

### Why Worse Than CD4PEADM

- TOC items are captured: `"Security Compliance Management release notes..."`
- NO actual release notes content in the TOC area → Only navigation survives
- Resulting bullets are all version headers/nav items

---

## Documentation Source Landscape

### Modules Using Each Source

**Forge Changelog (Next.js + JSON):**
- cd4pe
- Many other puppetlabs modules listed in `forge_changelog`

**MadCap Flare (help.puppet.com):**
- `sce_linux` (version-specific URLs: `scel_relnotes_{version}.htm`)
- `sce_windows` (version-specific URLs: `scew_relnotes_{version}.htm`)
- `cd4peadm` (fixed URL: `cd_release_notes.htm`)
- `comply` (fixed URL: `release_notes.htm`)
- `complyadm` (fixed URL: `release_notes.htm`)

**GitHub Releases / Other:**
- `pe_event_forwarding` (Forge changelog empty → fallback)

---

## MadCap Flare HTML Structure Analysis

### Key Identifiers for Content vs Navigation

| Element | Purpose | Location | Selector |
|---|---|---|---|
| `<div data-mc-content-body="True">` | Main content wrapper | Wraps all content | `.//div[@data-mc-content-body='True']` |
| `<div role="main" id="mc-main-content">` | Primary content container | Inside content body | `div[role='main']#mc-main-content` |
| `<ul data-magellan="">` | TOC navigation | Top of content body | `ul[data-magellan]` |
| `<h2 id="Version5150">` | Version section header | Main content area | `h2[id^='Version']` |
| Content `<ul>` | Release notes list | After version heading | `h2 + ul` or `h2 ~ ul:first-of-type` |

### Extraction Strategy for MadCap Flare

**Problem:** All `<li>` on page are naively combined

**Solution:** Extract version section content only

```python
def _parse_external_docs_madcap(self, html: str, target_version: Optional[str] = None) -> List[str]:
    """
    Parse MadCap Flare HTML for release notes.
    
    Strategy:
    1. Find main content div (data-mc-content-body="True")
    2. Locate first version heading (h2, h3 with "Version" in text)
    3. Extract only <li> items in the first version's content block
    4. Stop at next heading of same/higher level
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find main content container
    content_body = soup.find('div', attrs={'data-mc-content-body': 'True'})
    if not content_body:
        content_body = soup.find('div', attrs={'role': 'main'})
    if not content_body:
        content_body = soup
    
    bullets: List[str] = []
    
    # Skip the data-magellan TOC navigation
    # It's typically the first <ul> with data-magellan attribute
    first_toc = content_body.find('ul', attrs={'data-magellan': True})
    
    # Find first h2 or h3 with version info
    version_heading = None
    for heading in content_body.find_all(['h1', 'h2', 'h3']):
        heading_text = heading.get_text(' ', strip=True)
        if 'version' in heading_text.lower() or heading.get('id', '').startswith('Version'):
            version_heading = heading
            break
    
    if not version_heading:
        return []
    
    # Collect <li> items from first content <ul> after version heading
    node = version_heading.find_next_sibling()
    while node:
        # Stop if we hit another heading
        if node.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            break
        
        # Extract bullets from <ul> or <ol>
        if node.name in ['ul', 'ol']:
            for li in node.find_all('li', recursive=False):  # Direct children only
                text = self._clean_text(li.get_text(' ', strip=True))
                if text and not self._is_navigation_item(text):
                    bullets.append(text)
            # Only process first list block
            break
        
        node = node.find_next_sibling()
    
    return self._dedupe_and_limit(bullets, limit=5)


def _is_navigation_item(self, text: str) -> bool:
    """Detect if text is a navigation/TOC item vs real content."""
    # TOC items are usually version selectors
    if text.lower().startswith('version '):
        return True
    # Concatenated version list (from malformed TOC extraction)
    if re.search(r'Version \d+\.\d+\.\d+ Version \d+\.\d+', text):
        return True
    # Module/product names without content
    if text in [
        'Security Compliance Management release notes',
        'Continuous Delivery (CD) release notes',
        'Release Notes',
    ]:
        return True
    return False
```

---

## Recommended Parsing Strategy: Multi-Type Parser

### Architecture

```python
class ReleaseNotesParser:
    """Unified parser with source-type-specific strategies."""
    
    def parse(self, html: str, source_type: str, version: Optional[str] = None) -> List[str]:
        """
        Dispatch to appropriate parser based on source type.
        
        Types:
        - "forge_changelog": Forge (uses Next.js + JSON or HTML)
        - "external_docs_madcap": MadCap Flare (help.puppet.com)
        - "github_releases": GitHub release pages
        """
        if source_type == 'forge_changelog':
            return self._parse_forge_changelog(html, version)
        elif source_type == 'external_docs_madcap' or 'MadCap' in html:
            return self._parse_madcap_flare(html, version)
        else:
            return self._parse_generic_html(html)
    
    def _detect_source_type(self, html: str) -> str:
        """Auto-detect documentation source from HTML signature."""
        if '__NEXT_DATA__' in html:
            return 'forge_changelog_nextjs'
        elif 'MadCap' in html or 'data-mc-' in html:
            return 'external_docs_madcap'
        elif 'github.com/releases' in html:
            return 'github_releases'
        else:
            return 'generic_html'
```

---

## CSS Selectors for MadCap Flare Content Extraction

### Proposed Selectors (XPath equivalent)

```python
# Primary content container
main_content = soup.select_one('[data-mc-content-body="True"] #mc-main-content')

# Version heading (first major section)
version_heading = main_content.select_one('h2[id^="Version"], h2:contains("Version")')

# Content list following version heading (not TOC)
content_list = version_heading.find_next('ul')
if content_list and content_list != toc_list:
    for li in content_list.find_all('li', recursive=False):
        # Extract <li> that contain <p> (real content)
        # vs <li> that contain only <a> (navigation)
        if li.find('p'):
            bullets.append(extract_text(li))
```

### Distinguishing TOC `<li>` from Content `<li>`

**TOC `<li>` (Navigation):**
- Contains only `<a>` tags
- Text is version numbers or section names
- Parent `<ul>` has `data-magellan` or `class="menu"`
- Example: `<li class="tree-node"><a href="#Version5150">Version 5.15.0</a></li>`

**Content `<li>` (Real bullets):**
- Contains `<p>` tags or direct text
- Text is feature descriptions, bug fixes, etc.
- Parent `<ul>` is direct sibling of heading
- Example: `<li><p>Added a Hiera configuration option...</p></li>`

---

## Implementation Recommendation

### Phase 1: Quick Fix (Current Release)
**For April 2026 roundup:**

1. **Update `_parse_external_docs()` to skip known TOC patterns**
   ```python
   # In _parse_external_docs(), before appending bullets:
   if re.match(r'.*Version \d+\.\d+', text):  # Concatenated version list
       continue
   ```

2. **Or: Manually curate bullets for MadCap modules** (until parser is fixed)
   - Mark cd4peadm, comply, complyadm as needing manual review
   - Use the repo memory: `external_docs` modules should only show link, not parsed bullets

### Phase 2: Proper Parser (Next Month)
**Implement type-specific parsers:**

1. Create `ParserFactory` class
2. Auto-detect source type from HTML signature
3. Route to appropriate parser:
   - `_parse_forge_nextjs()` → Extract from `__NEXT_DATA__` JSON
   - `_parse_madcap_flare()` → Extract from content body, skip TOC
   - `_parse_github_releases()` → Extract from release block

4. Update config to specify source type:
   ```yaml
   external_docs:
     cd4peadm:
       type: "help_puppet_fixed"
       source_type: "madcap_flare"  # NEW
       base_url: "https://help.puppet.com/..."
   ```

### Phase 3: Validation (Ongoing)
- Add snapshot comparison tests: Did bullets change between runs?
- Flag when extracted bullets contain known navigation patterns
- Email alerts for parsing anomalies

---

## Modules Affected

### Immediate Issues (April 2026)
- **cd4peadm v5.15.0** – TOC + real content mixed
- **comply v3.7.1** – TOC only (no real content extracted)
- **complyadm v3.7.1** – TOC only (no real content extracted)

### Requires Monitoring
- **sce_linux v2.6.0, v2.6.1** – Use versioned URLs, different MadCap layout
- **sce_windows** – Similar to sce_linux

### Working Well
- **cd4pe v3.4.0** – Forge Next.js with embedded markdown
- **lvm v4.0.1** – Forge HTML changelog
- All `forge_changelog` modules in config

---

## Testing Strategy

### Test Case 1: cd4pe (Baseline - Should Pass)
```python
def test_parse_forge_nextjs():
    with open('data/raw_html/cd4pe_3_4_0.html') as f:
        html = f.read()
    bullets = parser.parse(html, 'forge_changelog', '3.4.0')
    assert len(bullets) >= 2
    assert any('docker' in b.lower() for b in bullets)
    assert not any('Version ' in b for b in bullets)  # No TOC items
```

### Test Case 2: cd4peadm (Regression - Should Fail with Current Code)
```python
def test_parse_madcap_flare_cd4peadm():
    with open('data/raw_html/cd4peadm_5_15_0.html') as f:
        html = f.read()
    bullets = parser.parse(html, 'external_docs_madcap', '5.15.0')
    
    # Should contain real features
    assert any('external_webhook_url' in b for b in bullets)
    assert any('idle timeout' in b for b in bullets)
    
    # Should NOT contain navigation items
    assert not any(re.match(r'.*Version \d+\.\d+ Version \d+', b) for b in bullets)
```

### Test Case 3: comply (Worst Case - Currently Broken)
```python
def test_parse_madcap_flare_comply():
    with open('data/raw_html/comply_3_7_1.html') as f:
        html = f.read()
    bullets = parser.parse(html, 'external_docs_madcap')
    
    # Should extract SOME meaningful content (or graceful fallback)
    assert len(bullets) > 0
    # For now, if nothing is found, fallback to link-only
    if len(bullets) == 0:
        return 'FALLBACK_TO_LINK'
```

---

## Summary Table

| Module | Version | Source | HTML Type | Current Status | Fix Type |
|---|---|---|---|---|---|
| cd4pe | 3.4.0 | Forge | Next.js JSON | ✅ Working | No change |
| cd4peadm | 5.15.0 | help.puppet.com | MadCap | ❌ TOC + content | Parser rewrite |
| comply | 3.7.1 | help.puppet.com | MadCap | ❌ TOC only | Parser rewrite |
| complyadm | 3.7.1 | help.puppet.com | MadCap | ❌ TOC only | Parser rewrite |
| sce_linux | 2.6.0, 2.6.1 | help.puppet.com | MadCap | ✅ Works* | Already parsing correctly |
| lvm | 4.0.1 | Forge | HTML | ✅ Working | No change |
| pe_event_forwarding | 2.3.0 | Forge | Empty | ⚠️ Fallback | N/A (no data) |

*sce_linux works because its actual release notes contain more `<li>` content, making TOC proportion smaller.

