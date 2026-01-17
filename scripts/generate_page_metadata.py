#!/usr/bin/env python3
"""
Page Metadata Generator for pSEO Architecture

Aggregates metadata from all generated pages into a structured JSON file
for auditing, validation, and internal linking optimization.

Each page entry includes:
- slug, url, title
- intent (informational, transactional, navigational)
- primary_keyword, supporting_keywords
- parent_hub, related_pages
- schema_types
- content stats (word_count, faq_count)
- last_modified

Run after all page generators to collect metadata.
"""

import json
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path


def extract_page_metadata(html_path):
    """Extract metadata from a generated HTML page."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    metadata = {}

    # Extract URL from canonical or path
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        url = canonical['href'].replace('https://thecroreport.com', '')
        metadata['url'] = url
    else:
        # Derive from file path
        rel_path = str(html_path).replace('site/', '/').replace('/index.html', '/')
        metadata['url'] = rel_path

    # Extract slug from URL
    metadata['slug'] = metadata['url'].strip('/').split('/')[-1] or 'home'

    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.text.replace(' | The CRO Report', '').strip()

    # Extract meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        metadata['description'] = meta_desc['content']

    # Determine intent based on URL patterns
    url = metadata.get('url', '')
    if '/salaries/' in url:
        if 'by-location' in url or 'by-stage' in url or 'by-seniority' in url:
            metadata['intent'] = 'navigational'  # Hub pages
        else:
            metadata['intent'] = 'informational'  # Salary data pages
    elif '/tools/' in url:
        if url.count('/') <= 2:  # Category hubs
            metadata['intent'] = 'navigational'
        else:
            metadata['intent'] = 'transactional'  # Tool review pages
    elif '/trends/' in url:
        metadata['intent'] = 'informational'
    elif '/jobs/' in url:
        metadata['intent'] = 'transactional'
    else:
        metadata['intent'] = 'informational'

    # Extract primary keyword from title
    title = metadata.get('title', '')
    metadata['primary_keyword'] = title

    # Generate supporting keywords
    supporting = []
    if 'salary' in title.lower():
        supporting.append(title.lower().replace('salary', 'pay'))
        supporting.append(title.lower().replace('salary', 'compensation'))
        if 'vp sales' in title.lower():
            supporting.append(title.lower().replace('vp sales', 'vice president sales'))
    elif 'review' in title.lower():
        tool_name = title.replace(' Review', '')
        supporting.append(f"{tool_name} pricing")
        supporting.append(f"{tool_name} alternatives")
        supporting.append(f"is {tool_name} worth it")
    metadata['supporting_keywords'] = supporting[:3]

    # Determine parent hub
    if '/salaries/vp-sales-salary-' in url:
        if any(loc in url for loc in ['san-francisco', 'new-york', 'boston', 'chicago', 'seattle', 'denver', 'atlanta', 'los-angeles', 'texas', 'remote', 'other']):
            metadata['parent_hub'] = '/salaries/by-location/'
        elif any(stage in url for stage in ['seed', 'series-a', 'series-b', 'series-c', 'late-stage', 'enterprise']):
            metadata['parent_hub'] = '/salaries/by-stage/'
        else:
            metadata['parent_hub'] = '/salaries/'
    elif '/salaries/c-level' in url or '/salaries/svp-' in url:
        metadata['parent_hub'] = '/salaries/by-seniority/'
    elif '/tools/' in url and url.count('/') > 2:
        # Individual tool page - parent is category
        parts = url.strip('/').split('/')
        if len(parts) >= 2:
            metadata['parent_hub'] = f"/tools/{parts[1]}/"
    elif '/salaries/by-' in url:
        metadata['parent_hub'] = '/salaries/'
    else:
        metadata['parent_hub'] = '/'

    # Extract schema types from JSON-LD
    schema_types = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            schema = json.loads(script.string)
            if '@type' in schema:
                schema_types.append(schema['@type'])
        except:
            pass
    metadata['schema_types'] = schema_types

    # Count content words (excluding nav, footer, scripts)
    main_content = soup.find('main') or soup.find('div', class_='container')
    if main_content:
        # Remove script and style tags
        for tag in main_content.find_all(['script', 'style', 'nav']):
            tag.decompose()
        text = main_content.get_text(separator=' ', strip=True)
        metadata['word_count'] = len(text.split())
    else:
        body = soup.find('body')
        if body:
            for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            text = body.get_text(separator=' ', strip=True)
            metadata['word_count'] = len(text.split())
        else:
            metadata['word_count'] = 0

    # Count FAQs
    faq_items = soup.find_all('div', class_='faq-item')
    metadata['faq_count'] = len(faq_items)

    # Last modified (use file modification time)
    metadata['last_modified'] = datetime.fromtimestamp(
        os.path.getmtime(html_path)
    ).strftime('%Y-%m-%d')

    return metadata


def find_related_pages(page_metadata, all_pages):
    """Find related pages based on type and keywords."""
    related = []
    current_url = page_metadata.get('url', '')
    current_hub = page_metadata.get('parent_hub', '')

    # Find siblings (same parent hub)
    siblings = [
        p for p in all_pages
        if p.get('parent_hub') == current_hub
        and p.get('url') != current_url
    ]

    # Sort by word count (prefer more substantial pages)
    siblings.sort(key=lambda x: x.get('word_count', 0), reverse=True)

    # Add top 3 siblings
    for sib in siblings[:3]:
        related.append(sib.get('url'))

    # Add parent hub if not root
    if current_hub and current_hub != '/':
        related.append(current_hub)

    return related[:5]


def generate_metadata():
    """Generate metadata for all pages in site/."""
    site_dir = Path('site')
    all_pages = []

    # Find all HTML files
    html_files = list(site_dir.rglob('*.html'))
    print(f"Found {len(html_files)} HTML files")

    # Extract metadata from each page
    for html_path in html_files:
        try:
            metadata = extract_page_metadata(html_path)
            all_pages.append(metadata)
        except Exception as e:
            print(f"Error processing {html_path}: {e}")

    # Second pass: add related pages
    for page in all_pages:
        page['related_pages'] = find_related_pages(page, all_pages)

    # Sort by URL for consistent output
    all_pages.sort(key=lambda x: x.get('url', ''))

    # Create output structure
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_pages': len(all_pages),
        'by_intent': {
            'informational': len([p for p in all_pages if p.get('intent') == 'informational']),
            'transactional': len([p for p in all_pages if p.get('intent') == 'transactional']),
            'navigational': len([p for p in all_pages if p.get('intent') == 'navigational']),
        },
        'content_stats': {
            'avg_word_count': sum(p.get('word_count', 0) for p in all_pages) // max(len(all_pages), 1),
            'avg_faq_count': sum(p.get('faq_count', 0) for p in all_pages) / max(len(all_pages), 1),
            'pages_with_faqs': len([p for p in all_pages if p.get('faq_count', 0) > 0]),
        },
        'pages': all_pages
    }

    # Write to file
    output_path = 'data/page_metadata.json'
    os.makedirs('data', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Generated metadata for {len(all_pages)} pages")
    print(f"  - Informational: {output['by_intent']['informational']}")
    print(f"  - Transactional: {output['by_intent']['transactional']}")
    print(f"  - Navigational: {output['by_intent']['navigational']}")
    print(f"  - Avg word count: {output['content_stats']['avg_word_count']}")
    print(f"  - Avg FAQ count: {output['content_stats']['avg_faq_count']:.1f}")
    print(f"\nOutput: {output_path}")

    return output


if __name__ == '__main__':
    generate_metadata()
