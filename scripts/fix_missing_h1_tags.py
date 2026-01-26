#!/usr/bin/env python3
"""
Fix pages missing H1 tags by injecting a proper H1 header section.
Mainly targets old salary pages with FAQ-style format.
"""

import os
import re
from glob import glob

SITE_DIR = 'site'


def extract_title(content):
    """Extract page title from <title> tag."""
    match = re.search(r'<title>([^<]+)</title>', content)
    if match:
        title = match.group(1)
        # Remove site name suffix
        title = re.sub(r'\s*\|\s*The CRO Report$', '', title)
        title = re.sub(r'\s*-\s*The CRO Report$', '', title)
        return title.strip()
    return None


def fix_h1_in_page(filepath):
    """Add H1 tag to pages missing it."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if already has H1
    if '<h1' in content:
        return False

    title = extract_title(content)
    if not title:
        print(f"  Warning: No title found in {filepath}")
        return False

    # Pattern for FAQ section style pages - inject H1 before the FAQ section
    faq_pattern = r'(</script>\s*\n\s*)(<section class="faq-section">)'
    match = re.search(faq_pattern, content)
    if match:
        h1_section = f'''
    <main>
    <div class="header" style="background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%); color: white; padding: 60px 20px; text-align: center;">
        <div class="eyebrow" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #d97706; margin-bottom: 12px;">Salary Benchmarks</div>
        <h1 style="font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px;">{title}</h1>
    </div>

'''
        content = content[:match.start(2)] + h1_section + content[match.start(2):]

        # Also need to close </main> before footer
        footer_pattern = r'(\s*<footer class="(?:site-)?footer")'
        footer_match = re.search(footer_pattern, content)
        if footer_match:
            content = content[:footer_match.start()] + '\n    </main>\n' + content[footer_match.start():]

        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Fixed: {filepath}")
        return True

    # Pattern 2: After mobile nav script (for other page types)
    mobile_script_pattern = r'(mobileLinks\.forEach\([^}]+\}\);?\s*\}\)\(\);\s*</script>)(\s*\n)'
    match = re.search(mobile_script_pattern, content, re.DOTALL)
    if match:
        h1_section = f'''

    <main>
    <div class="hero-header" style="background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%); color: white; padding: 60px 20px; text-align: center;">
        <h1 style="font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px;">{title}</h1>
    </div>
'''
        insert_point = match.end(1)
        content = content[:insert_point] + h1_section + content[insert_point:]

        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Fixed (type 2): {filepath}")
        return True

    print(f"  Warning: Could not find injection point in {filepath}")
    return False


def main():
    print("=" * 70)
    print("FIXING PAGES MISSING H1 TAGS")
    print("=" * 70)

    # Find all pages missing H1
    all_pages = glob(f"{SITE_DIR}/**/index.html", recursive=True)
    missing_h1 = []

    for page in all_pages:
        with open(page, 'r') as f:
            content = f.read()
        if '<h1' not in content:
            missing_h1.append(page)

    print(f"\nFound {len(missing_h1)} pages missing H1 tags\n")

    fixed = 0
    for page in missing_h1:
        if fix_h1_in_page(page):
            fixed += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {fixed} pages fixed")
    print("=" * 70)


if __name__ == '__main__':
    main()
