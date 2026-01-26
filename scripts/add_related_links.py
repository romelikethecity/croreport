#!/usr/bin/env python3
"""
Add related links section to pages for better internal linking.

Strategy:
- Job pages: Link to salary pages, tools, and related jobs
- Salary pages: Cross-link between salary pages
- Tool pages: Link to other tools in same category
- Company pages: Link to salary data and jobs

This helps with:
1. Better crawlability (internal linking)
2. User engagement (discover more content)
3. SEO (topical relevance)
"""

import os
import re
from glob import glob
import random

SITE_DIR = 'site'
BASE_URL = 'https://thecroreport.com'

# Related links templates by section
SALARY_RELATED_LINKS = '''
    <section class="related-links" style="background: #f8fafc; padding: 32px; border-radius: 12px; margin-top: 40px;">
        <h3 style="color: #1e3a5f; font-family: 'Fraunces', serif; margin-bottom: 16px;">Explore More Salary Data</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <a href="/salaries/vp-sales/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">VP Sales Salaries</a>
            <a href="/salaries/cro/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">CRO Salaries</a>
            <a href="/salaries/remote/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Remote Roles</a>
            <a href="/salaries/new-york/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">New York</a>
            <a href="/salaries/san-francisco/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">San Francisco</a>
        </div>
        <p style="margin-top: 16px; font-size: 0.85rem; color: #64748b;">
            Looking for jobs? <a href="/jobs/" style="color: #d97706;">Browse 150+ open positions</a>
        </p>
    </section>
'''

TOOL_RELATED_LINKS = '''
    <section class="related-links" style="background: #f8fafc; padding: 32px; border-radius: 12px; margin-top: 40px;">
        <h3 style="color: #1e3a5f; font-family: 'Fraunces', serif; margin-bottom: 16px;">Explore More Tools</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <a href="/tools/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">All Tools</a>
            <a href="/tools/sales-engagement/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Sales Engagement</a>
            <a href="/tools/conversation-intelligence/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Conversation Intelligence</a>
            <a href="/tools/data-providers/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Data Providers</a>
        </div>
        <p style="margin-top: 16px; font-size: 0.85rem; color: #64748b;">
            Looking for jobs? <a href="/jobs/" style="color: #d97706;">Browse 150+ open positions</a>
        </p>
    </section>
'''

JOB_RELATED_LINKS = '''
    <section class="related-links" style="background: #f8fafc; padding: 32px; border-radius: 12px; margin-top: 40px;">
        <h3 style="color: #1e3a5f; font-family: 'Fraunces', serif; margin-bottom: 16px;">Helpful Resources</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <a href="/jobs/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">All Jobs</a>
            <a href="/salaries/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Salary Data</a>
            <a href="/tools/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Sales Tools</a>
            <a href="/companies/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Companies Hiring</a>
        </div>
    </section>
'''

COMPANY_RELATED_LINKS = '''
    <section class="related-links" style="background: #f8fafc; padding: 32px; border-radius: 12px; margin-top: 40px;">
        <h3 style="color: #1e3a5f; font-family: 'Fraunces', serif; margin-bottom: 16px;">Helpful Resources</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 12px;">
            <a href="/companies/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">All Companies</a>
            <a href="/jobs/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">All Jobs</a>
            <a href="/salaries/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Salary Data</a>
            <a href="/tools/" style="padding: 8px 16px; background: white; border-radius: 8px; text-decoration: none; color: #475569; border: 1px solid #e2e8f0;">Sales Tools</a>
        </div>
    </section>
'''


def get_related_links_for_page(filepath):
    """Determine which related links section to add based on page path."""
    rel_path = os.path.relpath(filepath, SITE_DIR)
    parts = rel_path.split('/')

    if len(parts) < 1:
        return None

    section = parts[0]

    if section == 'salaries':
        return SALARY_RELATED_LINKS
    elif section == 'tools':
        return TOOL_RELATED_LINKS
    elif section == 'jobs':
        return JOB_RELATED_LINKS
    elif section == 'companies':
        return COMPANY_RELATED_LINKS

    return None


def add_related_links_to_page(filepath):
    """Add related links section to a page."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if already has related links
    if 'related-links' in content:
        return False

    related_links = get_related_links_for_page(filepath)
    if not related_links:
        return False

    # Find insertion point - before footer
    # Look for various footer patterns
    footer_patterns = [
        r'(\s*<footer class="footer">)',
        r'(\s*<footer class="site-footer">)',
        r'(\s*</main>\s*\n\s*<footer)',
    ]

    for pattern in footer_patterns:
        match = re.search(pattern, content)
        if match:
            insert_point = match.start()
            # Insert related links before footer
            new_content = content[:insert_point] + '\n' + related_links + '\n' + content[insert_point:]

            with open(filepath, 'w') as f:
                f.write(new_content)
            return True

    return False


def main():
    print("=" * 70)
    print("ADDING RELATED LINKS TO PAGES")
    print("=" * 70)

    # Process each section
    sections = ['salaries', 'tools', 'companies']

    total_fixed = 0

    for section in sections:
        print(f"\nProcessing {section}...")
        pages = glob(f"{SITE_DIR}/{section}/**/index.html", recursive=True)
        fixed = 0

        for page in pages:
            if add_related_links_to_page(page):
                fixed += 1

        print(f"  Added related links to {fixed} {section} pages")
        total_fixed += fixed

    # Process stale job pages (they're a lot, so just sample for testing)
    print(f"\nProcessing job pages...")
    job_pages = glob(f"{SITE_DIR}/jobs/**/index.html", recursive=True)
    # Exclude index and category pages
    job_pages = [p for p in job_pages if '/jobs/index.html' not in p
                 and '/jobs/vp-sales/' not in p
                 and '/jobs/cro-jobs/' not in p]

    fixed = 0
    for page in job_pages:
        if add_related_links_to_page(page):
            fixed += 1
            if fixed % 100 == 0:
                print(f"  Processed {fixed} job pages...")

    print(f"  Added related links to {fixed} job pages")
    total_fixed += fixed

    print(f"\n{'=' * 70}")
    print(f"Total: Added related links to {total_fixed} pages")
    print("=" * 70)


if __name__ == '__main__':
    main()
