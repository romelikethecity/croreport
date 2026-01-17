#!/usr/bin/env python3
"""
Generate XML sitemaps for The CRO Report

Creates category-indexed sitemaps for better crawlability at scale:
- sitemap_index.xml - Points to all category sitemaps
- sitemaps/sitemap-main.xml - Homepage and top-level pages
- sitemaps/sitemap-salaries.xml - All salary pages
- sitemaps/sitemap-tools.xml - All tool pages
- sitemaps/sitemap-jobs.xml - All job pages
- sitemaps/sitemap-insights.xml - All insight/trend pages
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple

SITE_DIR = 'site'
SITEMAPS_DIR = f'{SITE_DIR}/sitemaps'
BASE_URL = 'https://thecroreport.com'
MAX_URLS_PER_SITEMAP = 50000  # Google's limit

print("="*70)
print("GENERATING CATEGORY-INDEXED SITEMAPS")
print("="*70)


def categorize_url(url_path: str) -> str:
    """Categorize a URL into its sitemap category."""
    if url_path == '/':
        return 'main'
    elif url_path in ['/jobs/', '/salaries/', '/insights/', '/tools/', '/trends/']:
        return 'main'
    elif '/salaries/' in url_path:
        return 'salaries'
    elif '/tools/' in url_path:
        return 'tools'
    elif '/jobs/' in url_path:
        return 'jobs'
    elif '/insights/' in url_path or '/trends/' in url_path:
        return 'insights'
    else:
        return 'main'


def get_url_priority(url_path: str, category: str) -> Tuple[str, str]:
    """Get priority and changefreq for a URL."""
    if url_path == '/':
        return '1.0', 'weekly'
    elif url_path in ['/jobs/', '/salaries/', '/insights/', '/tools/', '/trends/']:
        return '0.9', 'weekly'
    elif category == 'jobs':
        return '0.6', 'weekly'
    elif category == 'salaries':
        return '0.7', 'weekly'
    elif category == 'tools':
        return '0.5', 'monthly'
    elif category == 'insights':
        return '0.6', 'weekly'
    else:
        return '0.5', 'monthly'


def collect_urls() -> Dict[str, List[dict]]:
    """Collect all HTML pages and categorize them."""
    categorized_urls = {
        'main': [],
        'salaries': [],
        'tools': [],
        'jobs': [],
        'insights': []
    }

    for root, dirs, files in os.walk(SITE_DIR):
        # Skip the sitemaps directory itself
        if 'sitemaps' in root:
            continue

        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, SITE_DIR)

                # Convert filepath to URL
                if rel_path == 'index.html':
                    url_path = '/'
                elif rel_path.endswith('/index.html'):
                    url_path = '/' + rel_path[:-10]
                else:
                    url_path = '/' + rel_path.replace('.html', '/')

                # Clean up path
                url_path = url_path.replace('//', '/')
                if not url_path.endswith('/') and url_path != '/':
                    url_path += '/'

                # Categorize and get metadata
                category = categorize_url(url_path)
                priority, changefreq = get_url_priority(url_path, category)

                categorized_urls[category].append({
                    'loc': f'{BASE_URL}{url_path}',
                    'lastmod': datetime.now().strftime('%Y-%m-%d'),
                    'changefreq': changefreq,
                    'priority': priority
                })

    return categorized_urls


def generate_sitemap_xml(urls: List[dict]) -> str:
    """Generate sitemap XML content for a list of URLs."""
    # Sort URLs by priority
    urls.sort(key=lambda x: (-float(x['priority']), x['loc']))

    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

    for url in urls:
        xml += f'''  <url>
    <loc>{url['loc']}</loc>
    <lastmod>{url['lastmod']}</lastmod>
    <changefreq>{url['changefreq']}</changefreq>
    <priority>{url['priority']}</priority>
  </url>
'''

    xml += '</urlset>'
    return xml


def generate_sitemap_index(sitemap_files: List[str]) -> str:
    """Generate sitemap index XML pointing to category sitemaps."""
    lastmod = datetime.now().strftime('%Y-%m-%d')

    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

    for sitemap_file in sitemap_files:
        xml += f'''  <sitemap>
    <loc>{BASE_URL}/sitemaps/{sitemap_file}</loc>
    <lastmod>{lastmod}</lastmod>
  </sitemap>
'''

    xml += '</sitemapindex>'
    return xml


def main():
    # Create sitemaps directory
    os.makedirs(SITEMAPS_DIR, exist_ok=True)

    # Collect and categorize URLs
    categorized_urls = collect_urls()

    # Track generated sitemaps
    generated_sitemaps = []
    total_urls = 0

    # Generate category sitemaps
    for category, urls in categorized_urls.items():
        if not urls:
            continue

        # Handle large categories that exceed 50K limit
        if len(urls) > MAX_URLS_PER_SITEMAP:
            # Split into multiple sitemaps
            for i in range(0, len(urls), MAX_URLS_PER_SITEMAP):
                chunk = urls[i:i + MAX_URLS_PER_SITEMAP]
                chunk_num = i // MAX_URLS_PER_SITEMAP + 1
                filename = f'sitemap-{category}-{chunk_num}.xml'

                sitemap_xml = generate_sitemap_xml(chunk)
                filepath = f'{SITEMAPS_DIR}/{filename}'

                with open(filepath, 'w') as f:
                    f.write(sitemap_xml)

                generated_sitemaps.append(filename)
                total_urls += len(chunk)
                print(f"  Generated {filename} with {len(chunk)} URLs")
        else:
            filename = f'sitemap-{category}.xml'
            sitemap_xml = generate_sitemap_xml(urls)
            filepath = f'{SITEMAPS_DIR}/{filename}'

            with open(filepath, 'w') as f:
                f.write(sitemap_xml)

            generated_sitemaps.append(filename)
            total_urls += len(urls)
            print(f"  Generated {filename} with {len(urls)} URLs")

    # Generate sitemap index
    sitemap_index = generate_sitemap_index(generated_sitemaps)
    index_path = f'{SITE_DIR}/sitemap_index.xml'

    with open(index_path, 'w') as f:
        f.write(sitemap_index)

    print(f"\nGenerated sitemap_index.xml pointing to {len(generated_sitemaps)} sitemaps")

    # Also keep a flat sitemap.xml for backwards compatibility
    # (some crawlers may still look for it)
    all_urls = []
    for urls in categorized_urls.values():
        all_urls.extend(urls)

    flat_sitemap = generate_sitemap_xml(all_urls)
    flat_path = f'{SITE_DIR}/sitemap.xml'

    with open(flat_path, 'w') as f:
        f.write(flat_sitemap)

    print(f"Generated sitemap.xml (flat) with {len(all_urls)} URLs")

    # Update robots.txt to point to sitemap index
    robots_path = f'{SITE_DIR}/robots.txt'
    robots_content = f'''User-agent: *
Allow: /

# Category-indexed sitemaps for better crawlability
Sitemap: {BASE_URL}/sitemap_index.xml

# Flat sitemap for backwards compatibility
Sitemap: {BASE_URL}/sitemap.xml
'''

    with open(robots_path, 'w') as f:
        f.write(robots_content)

    print(f"Updated robots.txt with sitemap index reference")

    print("\n" + "="*70)
    print(f"SITEMAP GENERATION COMPLETE")
    print(f"  Total URLs indexed: {total_urls}")
    print(f"  Category sitemaps: {len(generated_sitemaps)}")
    print(f"  Index file: {index_path}")
    print("="*70)


if __name__ == '__main__':
    main()
