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

def read_include(filename):
    """Read an include file."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    print(f"Warning: Include not found: {filepath}")
    return None

def update_html_file(filepath, nav_html, footer_html):
    """Update nav and footer in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern to match the header section (from <header to the mobile nav script closing)
    # This captures the entire navigation block including mobile nav
    header_pattern = r'<header class="site-header">.*?</script>\s*(?=<main|<section|<div class="container">|<div class="page-|<article)'

    # Check if the file has the expected structure
    if '<header class="site-header">' in content:
        # Replace the header/nav block
        content = re.sub(header_pattern, nav_html.strip() + '\n\n    ', content, flags=re.DOTALL)

    # Pattern to match footer
    footer_pattern = r'<footer class="site-footer">.*?</footer>'

    if '<footer class="site-footer">' in content:
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
