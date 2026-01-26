#!/usr/bin/env python3
"""
Add OG/Twitter tags to manual pages that are missing them.
"""

import re
import os

BASE_URL = "https://thecroreport.com"

# Pages to fix with their metadata
PAGES_TO_FIX = [
    {
        "path": "site/tools/linkedin-sales-navigator/index.html",
        "url": f"{BASE_URL}/tools/linkedin-sales-navigator/",
        "title": "LinkedIn Sales Navigator Review for Sales Teams",
        "desc": "Comprehensive review of LinkedIn Sales Navigator for enterprise sales teams."
    },
    {
        "path": "site/tools/cognism/index.html",
        "url": f"{BASE_URL}/tools/cognism/",
        "title": "Cognism Review for Sales Teams",
        "desc": "Comprehensive review of Cognism for B2B sales teams."
    },
    {
        "path": "site/tools/gong-vs-chorus/index.html",
        "url": f"{BASE_URL}/tools/gong-vs-chorus/",
        "title": "Gong vs Chorus (2025 Comparison)",
        "desc": "Detailed comparison of Gong and Chorus conversation intelligence platforms."
    },
]


def add_og_tags(page_info):
    """Add OG/Twitter tags to a page."""
    filepath = page_info["path"]

    if not os.path.exists(filepath):
        print(f"  File not found: {filepath}")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    if 'og:title' in content:
        print(f"  Already has OG tags: {filepath}")
        return False

    og_tags = f'''
    <!-- Open Graph Tags -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_info['url']}">
    <meta property="og:title" content="{page_info['title']}">
    <meta property="og:description" content="{page_info['desc']}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">

    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{page_info['title']}">
    <meta name="twitter:description" content="{page_info['desc']}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">
'''

    # Also add canonical if missing
    canonical_tag = f'    <link rel="canonical" href="{page_info["url"]}">\n'

    # Find insertion point - after <title> tag
    title_match = re.search(r'(<title>[^<]+</title>)', content)
    if title_match:
        insert_point = title_match.end()
        # Check if there's already a meta description
        meta_desc = re.search(r'<meta name="description"', content)
        if meta_desc:
            insert_point = meta_desc.end()
            # Find end of meta description tag
            desc_end = content.find('>', insert_point)
            if desc_end > 0:
                insert_point = desc_end + 1

        # Check if canonical exists
        if 'rel="canonical"' not in content:
            og_tags = canonical_tag + og_tags

        content = content[:insert_point] + og_tags + content[insert_point:]

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"  Fixed: {filepath}")
        return True

    print(f"  Could not find insertion point: {filepath}")
    return False


def main():
    print("=" * 70)
    print("ADDING OG/TWITTER TAGS TO MANUAL PAGES")
    print("=" * 70)

    fixed = 0
    for page in PAGES_TO_FIX:
        if add_og_tags(page):
            fixed += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {fixed} pages fixed")
    print("=" * 70)


if __name__ == '__main__':
    main()
