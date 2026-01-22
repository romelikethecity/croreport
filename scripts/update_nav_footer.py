#!/usr/bin/env python3
"""
Update navigation and footer across all HTML files in the site.

This script reads shared includes from templates/includes/ and updates
all HTML files to use consistent navigation and footer.

Run this as the last step in the build process to ensure all pages
have the latest nav/footer.
"""

import os
import re
import glob

SITE_DIR = 'site'
TEMPLATES_DIR = 'templates/includes'

# CSS that must exist for the nav to work correctly
NAV_CSS_REQUIRED = '''
        /* Standard Nav Styles */
        .header-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo-img { height: 32px; width: auto; border-radius: 8px; }
        .btn-subscribe { background: var(--navy, #1e3a5f); color: var(--white, #ffffff) !important; padding: 8px 16px; border-radius: 6px; font-weight: 600; }
        .btn-subscribe:hover { background: var(--navy-light, #2d4a6f); }
'''

def read_include(filename):
    """Read an include file."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    print(f"Warning: Include not found: {filepath}")
    return None

def update_nav_css(content):
    """Ensure the page has the required CSS classes for the nav to work."""
    # Check if .header-container already exists
    if '.header-container' in content and '.btn-subscribe' in content and '.logo-img' in content:
        return content  # Already has the styles

    # Build the CSS to add
    css_to_add = ''
    if '.header-container' not in content:
        css_to_add += '\n        .header-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }'
    if '.logo-img' not in content:
        css_to_add += '\n        .logo-img { height: 32px; width: auto; border-radius: 8px; }'
    if '.btn-subscribe' not in content:
        css_to_add += '\n        .btn-subscribe { background: var(--navy, #1e3a5f); color: var(--white, #ffffff) !important; padding: 8px 16px; border-radius: 6px; font-weight: 600; }'
        css_to_add += '\n        .btn-subscribe:hover { background: var(--navy-light, #2d4a6f); }'

    if not css_to_add:
        return content

    # Find the first </style> tag and insert CSS before it
    style_close_match = re.search(r'(</style>)', content)
    if style_close_match:
        insert_pos = style_close_match.start()
        content = content[:insert_pos] + css_to_add + '\n    ' + content[insert_pos:]

    return content

def update_html_file(filepath, nav_html, footer_html):
    """Update nav and footer in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # First, ensure the required CSS classes exist
    content = update_nav_css(content)

    # Check if the file has the expected structure
    if '<header class="site-header">' in content:
        # Pattern: Match from <header class="site-header"> through the mobile nav script
        # The mobile nav script always ends with })(); </script>
        # This pattern captures the entire nav section regardless of what follows
        header_pattern_with_script = r'<header class="site-header">.*?\}\)\(\);\s*</script>'

        # Try pattern with script first (most common)
        match = re.search(header_pattern_with_script, content, flags=re.DOTALL)
        if match:
            content = content[:match.start()] + nav_html.strip() + content[match.end():]
        else:
            # Pattern 2: Pages without inline script (nav ends with </nav>)
            # Content markers that indicate where nav section ends
            content_markers = r'<main|<section|<div class="container|<div class="page-|<article|<div class="hero|<header class="(?!site-header)'
            header_pattern_no_script = rf'<header class="site-header">.*?</nav>\s*(?={content_markers})'
            content = re.sub(header_pattern_no_script, nav_html.strip() + '\n\n    ', content, flags=re.DOTALL)

    # Alternative structure: pages using <nav class="nav"> as top-level nav (not inside header)
    elif '<nav class="nav">' in content and '<header class="site-header">' not in content:
        # These pages use <nav class="nav"> with nested nav-links div
        # Pattern: Match through the mobile nav script ending with })();
        alt_nav_pattern = r'<nav class="nav">.*?\}\)\(\);\s*</script>'
        match = re.search(alt_nav_pattern, content, flags=re.DOTALL)
        if match:
            content = content[:match.start()] + nav_html.strip() + content[match.end():]

    # Pattern to match footer - support both .site-footer and .footer classes
    footer_pattern = r'<footer class="(?:site-footer|footer)">.*?</footer>'

    if '<footer class="site-footer">' in content or '<footer class="footer">' in content:
        content = re.sub(footer_pattern, footer_html.strip(), content, flags=re.DOTALL)

    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("=" * 70)
    print("🔄 UPDATING NAV & FOOTER ACROSS ALL PAGES")
    print("=" * 70)

    # Read includes
    nav_html = read_include('nav.html')
    footer_html = read_include('footer.html')

    if not nav_html or not footer_html:
        print("❌ Could not load includes. Aborting.")
        return

    # Find all HTML files
    html_files = glob.glob(f'{SITE_DIR}/**/*.html', recursive=True)
    html_files += glob.glob(f'{SITE_DIR}/*.html')
    html_files = list(set(html_files))  # Remove duplicates

    print(f"📁 Found {len(html_files)} HTML files")

    updated = 0
    skipped = 0

    for filepath in html_files:
        try:
            if update_html_file(filepath, nav_html, footer_html):
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"⚠️  Error processing {filepath}: {e}")

    print(f"✅ Updated: {updated} files")
    print(f"⏭️  Skipped (no changes): {skipped} files")
    print("=" * 70)

if __name__ == '__main__':
    main()
