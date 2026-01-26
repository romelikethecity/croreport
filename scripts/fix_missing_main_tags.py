#!/usr/bin/env python3
"""
Fix missing <main> landmark tags in HTML pages.

Injects <main> after the mobile nav script and </main> before the footer.
"""

import os
import re

SITE_DIR = 'site'

def find_pages_missing_main():
    """Find all index.html pages missing <main> tag."""
    missing = []
    for root, dirs, files in os.walk(SITE_DIR):
        # Skip jobs directory (handled separately)
        if '/jobs/' in root or root.endswith('/jobs'):
            continue
        for f in files:
            if f == 'index.html':
                path = os.path.join(root, f)
                with open(path, 'r') as file:
                    content = file.read()
                    if '<main>' not in content:
                        missing.append(path)
    return missing

def fix_main_tags(filepath):
    """Add <main> and </main> tags to a page."""
    with open(filepath, 'r') as f:
        content = f.read()

    if '<main>' in content:
        return False  # Already has main tag

    # Pattern 1: After mobile nav script (most common)
    # Look for the closing script tag after mobile nav functionality
    mobile_script_pattern = r'(mobileLinks\.forEach\([^}]+\}\);?\s*\}\)\(\);\s*</script>)'

    # Pattern 2: Alternative - after .mobile-nav-subscribe link before main content
    alt_pattern = r'(<a[^>]*class="mobile-nav-subscribe"[^>]*>[^<]*</a>\s*</nav>)'

    # Pattern 3: After closing site-header (for simpler pages without mobile nav overlay)
    # Look for </header> followed by blank line or content (not another <header>)
    header_pattern = r'(</header>\s*\n\s*\n\s*)(<(?!header))'

    # Pattern 4: After mobile-menu-btn closing header (for minimal pages)
    simple_header_pattern = r'(<button class="mobile-menu-btn"[^>]*>[^<]*</button>\s*</div>\s*</header>)'

    # Try pattern 1 first
    match = re.search(mobile_script_pattern, content, re.DOTALL)
    if match:
        insert_point = match.end()
        content = content[:insert_point] + '\n\n    <main>\n' + content[insert_point:]
    else:
        # Try pattern 2
        match = re.search(alt_pattern, content, re.DOTALL)
        if match:
            insert_point = match.end()
            content = content[:insert_point] + '\n\n    <main>\n' + content[insert_point:]
        else:
            # Try pattern 3 - after first </header> that's not followed by another header
            match = re.search(header_pattern, content, re.DOTALL)
            if match:
                insert_point = match.start(2)
                content = content[:insert_point] + '<main>\n\n    ' + content[insert_point:]
            else:
                # Try pattern 4 - after simple header with mobile-menu-btn
                match = re.search(simple_header_pattern, content, re.DOTALL)
                if match:
                    insert_point = match.end()
                    content = content[:insert_point] + '\n\n    <main>\n' + content[insert_point:]
                else:
                    print(f"  Warning: Could not find insertion point for <main> in {filepath}")
                    return False

    # Add </main> before footer
    # Look for <footer class="site-footer"> or <footer class="footer">
    footer_pattern = r'(\s*<footer class="(?:site-)?footer")'
    match = re.search(footer_pattern, content)
    if match:
        insert_point = match.start()
        content = content[:insert_point] + '\n\n    </main>\n' + content[insert_point:]
    else:
        print(f"  Warning: Could not find footer in {filepath}")
        return False

    # Write back
    with open(filepath, 'w') as f:
        f.write(content)

    return True

def main():
    print("=" * 70)
    print("FIXING MISSING <main> LANDMARK TAGS")
    print("=" * 70)

    missing = find_pages_missing_main()
    print(f"\nFound {len(missing)} pages missing <main> tag\n")

    fixed = 0
    failed = 0
    for path in missing:
        print(f"Processing: {path}")
        if fix_main_tags(path):
            fixed += 1
        else:
            failed += 1

    print(f"\n" + "=" * 70)
    print(f"Results: {fixed} fixed, {failed} failed")
    print("=" * 70)

if __name__ == '__main__':
    main()
