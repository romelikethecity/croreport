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

    # Build the CSS to add - all the styles needed for the standard nav
    css_to_add = ''

    # Site header styles
    if '.site-header' not in content or 'padding: 12px 20px' not in content:
        css_to_add += '\n        .site-header { padding: 12px 20px; background: #fff; border-bottom: 1px solid #e2e8f0; position: sticky; top: 0; z-index: 100; }'

    if '.header-container' not in content:
        css_to_add += '\n        .header-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }'

    # Logo styles - ensure no underline and correct color
    if '.logo {' not in content or 'text-decoration: none' not in content:
        css_to_add += "\n        .logo { display: flex; align-items: center; gap: 10px; text-decoration: none; font-family: 'Fraunces', Georgia, serif; font-size: 1.1rem; font-weight: 600; color: #1e3a5f; }"

    if '.logo-img' not in content:
        css_to_add += '\n        .logo-img { height: 32px; width: auto; border-radius: 8px; }'

    # Nav links - ensure list-style: none and proper layout
    # Check if nav-links block has list-style: none (search for the pattern together)
    nav_links_pattern = re.search(r'\.nav-links\s*\{[^}]*list-style:\s*none', content)
    if not nav_links_pattern:
        css_to_add += '\n        .nav-links { display: flex; gap: 24px; list-style: none; align-items: center; margin: 0; padding: 0; }'
        css_to_add += '\n        .nav-links a { text-decoration: none; color: #475569; font-size: 0.9rem; font-weight: 500; transition: color 0.2s; }'
        css_to_add += '\n        .nav-links a:hover { color: #1e3a5f; }'

    if '.btn-subscribe' not in content:
        css_to_add += '\n        .btn-subscribe { background: #1e3a5f; color: #fff !important; padding: 8px 16px; border-radius: 6px; font-weight: 600; }'
        css_to_add += '\n        .btn-subscribe:hover { background: #2d4a6f; }'

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
        # Find the nav section by looking for the mobile-nav-subscribe link
        # The nav ends with the script that handles mobile menu clicks
        # Pattern: Match from <header> through mobile-nav-subscribe, then to first })(); </script>

        # First, find where the header starts
        header_start = content.find('<header class="site-header">')
        if header_start != -1:
            # Find the mobile-nav-subscribe link after the header
            mobile_nav_sub = content.find('class="mobile-nav-subscribe"', header_start)
            if mobile_nav_sub != -1:
                # Find the first })(); </script> after the mobile-nav-subscribe
                script_end_pattern = r'\}\)\(\);\s*</script>'
                match = re.search(script_end_pattern, content[mobile_nav_sub:])
                if match:
                    nav_end = mobile_nav_sub + match.end()
                    content = content[:header_start] + nav_html.strip() + content[nav_end:]
            else:
                # Fallback: no mobile nav, try to match until first })(); </script> after header
                script_end_pattern = r'\}\)\(\);\s*</script>'
                match = re.search(script_end_pattern, content[header_start:])
                if match:
                    nav_end = header_start + match.end()
                    content = content[:header_start] + nav_html.strip() + content[nav_end:]

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
