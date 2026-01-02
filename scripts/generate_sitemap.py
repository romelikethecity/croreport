#!/usr/bin/env python3
"""
Generate XML sitemap for The CRO Report
Creates sitemap.xml with all pages for search engine indexing
"""

import os
import glob
from datetime import datetime

SITE_DIR = 'site'
BASE_URL = 'https://thecroreport.com'

print("="*70)
print("🗺️  GENERATING SITEMAP")
print("="*70)

# Collect all HTML pages
urls = []

# Walk through site directory
for root, dirs, files in os.walk(SITE_DIR):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            # Convert filepath to URL
            rel_path = os.path.relpath(filepath, SITE_DIR)
            
            # Handle index.html files
            if rel_path == 'index.html':
                url_path = '/'
            elif rel_path.endswith('/index.html'):
                url_path = '/' + rel_path[:-10]  # Remove 'index.html'
            else:
                url_path = '/' + rel_path.replace('.html', '/')
            
            # Clean up path
            url_path = url_path.replace('//', '/')
            if not url_path.endswith('/') and url_path != '/':
                url_path += '/'
            
            # Determine priority based on page type
            if url_path == '/':
                priority = '1.0'
                changefreq = 'weekly'
            elif url_path in ['/jobs/', '/salaries/', '/insights/', '/tools/']:
                priority = '0.9'
                changefreq = 'weekly'
            elif '/jobs/' in url_path and url_path != '/jobs/':
                priority = '0.6'
                changefreq = 'weekly'
            elif '/salaries/' in url_path:
                priority = '0.7'
                changefreq = 'weekly'
            elif '/tools/' in url_path:
                priority = '0.5'
                changefreq = 'monthly'
            else:
                priority = '0.5'
                changefreq = 'monthly'
            
            urls.append({
                'loc': f'{BASE_URL}{url_path}',
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': changefreq,
                'priority': priority
            })

# Sort URLs - homepage first, then by priority
urls.sort(key=lambda x: (x['priority'] != '1.0', -float(x['priority']), x['loc']))

# Generate sitemap XML
sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

for url in urls:
    sitemap += f'''  <url>
    <loc>{url['loc']}</loc>
    <lastmod>{url['lastmod']}</lastmod>
    <changefreq>{url['changefreq']}</changefreq>
    <priority>{url['priority']}</priority>
  </url>
'''

sitemap += '</urlset>'

# Write sitemap
sitemap_path = f'{SITE_DIR}/sitemap.xml'
with open(sitemap_path, 'w') as f:
    f.write(sitemap)

print(f"✅ Generated sitemap with {len(urls)} URLs")
print(f"📁 Saved to: {sitemap_path}")

# Also create robots.txt if it doesn't exist
robots_path = f'{SITE_DIR}/robots.txt'
robots_content = f'''User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
'''

with open(robots_path, 'w') as f:
    f.write(robots_content)

print(f"✅ Generated robots.txt")
print(f"📁 Saved to: {robots_path}")
