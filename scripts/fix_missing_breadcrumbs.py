#!/usr/bin/env python3
"""
Add BreadcrumbList schema to pages that are missing it.

Generates appropriate breadcrumbs based on URL path and injects JSON-LD schema.
"""

import os
import re
import json

SITE_DIR = 'site'
BASE_URL = 'https://thecroreport.com'

def get_breadcrumbs_for_path(path):
    """Generate breadcrumb list based on file path."""
    # Remove site/ prefix and index.html suffix
    rel_path = path.replace(f'{SITE_DIR}/', '').replace('/index.html', '')

    if not rel_path or rel_path == 'index.html':
        return None  # Homepage doesn't need breadcrumbs

    parts = rel_path.split('/')
    breadcrumbs = [{"name": "Home", "url": BASE_URL}]

    # Map directory names to display names
    name_map = {
        'tools': 'Tools',
        'salaries': 'Salaries',
        'jobs': 'Jobs',
        'insights': 'Market Intel',
        'companies': 'Companies',
        'assessment': 'AI Assessment',
        'trends': 'Trends',
        'newsletter': 'Newsletter',
        'ai-sdr': 'AI SDR',
        'data-enrichment': 'Data Enrichment',
        'conversation-intelligence': 'Conversation Intelligence',
        'sales-engagement': 'Sales Engagement',
        'forecasting': 'Forecasting',
        'by-location': 'By Location',
        'by-seniority': 'By Seniority',
        'by-stage': 'By Stage',
    }

    current_path = ''
    for i, part in enumerate(parts):
        current_path += f'/{part}'

        # Get display name
        if part in name_map:
            name = name_map[part]
        else:
            # Convert slug to title case
            name = part.replace('-', ' ').title()
            # Handle common patterns
            if 'vs' in name.lower():
                # Keep "vs" lowercase
                name = re.sub(r'\bVs\b', 'vs', name)
            if 'alternatives' in name.lower():
                name = name.replace('Alternatives', 'Alternatives')

        breadcrumbs.append({
            "name": name,
            "url": f"{BASE_URL}{current_path}/"
        })

    return breadcrumbs

def generate_breadcrumb_schema(breadcrumbs):
    """Generate JSON-LD schema for breadcrumbs."""
    if not breadcrumbs:
        return ''

    items = []
    for i, crumb in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": crumb["name"],
            "item": crumb["url"]
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

    return f'''
    <!-- BreadcrumbList Schema -->
    <script type="application/ld+json">
{json.dumps(schema, indent=4)}
    </script>
'''

def fix_breadcrumbs(filepath):
    """Add BreadcrumbList schema to a page."""
    with open(filepath, 'r') as f:
        content = f.read()

    if 'BreadcrumbList' in content:
        return False  # Already has breadcrumbs

    breadcrumbs = get_breadcrumbs_for_path(filepath)
    if not breadcrumbs:
        return False

    schema = generate_breadcrumb_schema(breadcrumbs)

    # Find insertion point - after OG/Twitter tags or before closing </head>
    # Try to find existing schema scripts to insert nearby
    insertion_patterns = [
        (r'(</script>\s*\n\s*<link rel="icon")', r'\1'),  # After existing schema
        (r'(<meta name="twitter:image"[^>]*>)', r'\1'),  # After Twitter tags
        (r'(<link rel="canonical"[^>]*>)', r'\1'),  # After canonical
        (r'(</head>)', r'\1'),  # Before closing head as fallback
    ]

    inserted = False
    for pattern, _ in insertion_patterns:
        match = re.search(pattern, content)
        if match:
            insert_point = match.end()
            content = content[:insert_point] + schema + content[insert_point:]
            inserted = True
            break

    if not inserted:
        print(f"  Warning: Could not find insertion point in {filepath}")
        return False

    with open(filepath, 'w') as f:
        f.write(content)

    return True

def find_pages_missing_breadcrumbs():
    """Find pages missing BreadcrumbList schema."""
    missing = []
    # Focus on high-priority pages: tools, salaries, insights
    priority_dirs = ['tools', 'salaries', 'insights', 'assessment', 'trends']

    for priority_dir in priority_dirs:
        dir_path = os.path.join(SITE_DIR, priority_dir)
        if not os.path.exists(dir_path):
            continue

        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if f == 'index.html':
                    path = os.path.join(root, f)
                    with open(path, 'r') as file:
                        content = file.read()
                        if 'BreadcrumbList' not in content:
                            missing.append(path)

    return missing

def main():
    print("=" * 70)
    print("ADDING BREADCRUMBLIST SCHEMA TO PAGES")
    print("=" * 70)

    missing = find_pages_missing_breadcrumbs()
    print(f"\nFound {len(missing)} priority pages missing BreadcrumbList\n")

    fixed = 0
    failed = 0
    for path in missing:
        print(f"Processing: {path}")
        if fix_breadcrumbs(path):
            fixed += 1
        else:
            failed += 1

    print(f"\n" + "=" * 70)
    print(f"Results: {fixed} fixed, {failed} skipped/failed")
    print("=" * 70)

if __name__ == '__main__':
    main()
