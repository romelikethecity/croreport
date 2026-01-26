#!/usr/bin/env python3
"""
Fix tool page titles that exceed 60 characters.

Strategy:
- Remove " | The CRO Report" suffix (saves 18 chars)
- Shorten year references
- Remove redundant phrases like "Honest Assessment", "Review", "Pricing, Pros & Cons"
"""

import os
import re

SITE_DIR = 'site/tools'
MAX_TITLE_LENGTH = 60

# Mapping of long titles to short titles
# Format: regex pattern -> replacement
TITLE_FIXES = [
    # Remove site name suffix first
    (r'\s*\|\s*The CRO Report$', ''),

    # Shorten common patterns
    (r'Review (\d{4}): Pricing, Pros & Cons, and Honest Assessment', r'Review \1: Pricing & Pros/Cons'),
    (r'Review (\d{4}): Pricing, Features & Post-Clari Acquisition Analysis', r'Review \1: Post-Acquisition Analysis'),
    (r'Review (\d{4}): Pricing, ZoomInfo Integration & Honest Assessment', r'Review \1: ZoomInfo Integration'),
    (r'Review (\d{4}): Pricing, Features & Honest Assessment', r'Review \1: Features & Pricing'),
    (r'\(Honest Assessment\)', ''),
    (r': Honest Assessment', ''),
    (r'The Honest CRO\'s Take on ', ''),
    (r'Enterprise Complexity or Mid-Market Simplicity\?', 'Compared'),
    (r'Enterprise Data Giant or Scrappy All-in-One\?', 'Compared'),
    (r'Data Enrichment Depth or All-in-One Simplicity\?', 'Compared'),
    (r'The Hype vs Reality of AI SDRs', 'AI SDR Analysis'),
    (r'Annual Lock-in vs Quarterly Flexibility', 'Pricing Compared'),
    (r'Enterprise SEP vs All-in-One Platform', 'Compared'),
    (r'Call Coaching or Revenue Forecasting\?', 'Compared'),
    (r'The Cold Email Platform That Ate the Market', 'Cold Email Leader'),
    (r'The CPQ Platform Built for Modern Revenue Teams', 'CPQ for Revenue Teams'),
    (r'The Proposal Tool That Actually Gets Signed', 'Proposal Software'),
    (r'The Best CRM for Growing Sales Teams', 'CRM for Growth'),
    (r': Website Visitor ID \+ AI SDR', ': Website ID + AI SDR'),
    (r': Enterprise ABM Platform', ': ABM Platform'),
    (r': Enterprise Data Orchestration', ': Data Orchestration'),
    (r': Salesforce Deduplication Specialist', ': Salesforce Deduplication'),
    (r': Lead Routing & GTM Orchestration', ': Lead Routing'),
    (r': AI-Powered Managed Data Services', ': AI Data Services'),
    (r': \$35K/yr AI Sales Engagement', ': AI Sales Engagement'),
    (r': AI Sales Assistant for Deal Execution', ': AI Sales Assistant'),
    (r': Intent-Driven Outbound Platform', ': Intent Outbound'),
    (r': The \$60K Gamble vs the \$2,700 Test', ': Pricing Showdown'),
    (r'Which AI SDR Actually Delivers\?', 'Compared'),
    (r': Website Visitor Intelligence Compared', ' Compared'),
    (r': Cold Email Platforms Compared', ' Compared'),
    (r': Conversation Intelligence Compared', ' Compared'),
    (r': CPQ & Proposal Tools Compared', ' Compared'),
    (r' - Best Tools for 2026', ' Tools 2026'),
]


def shorten_title(title):
    """Apply title shortening rules."""
    original = title
    for pattern, replacement in TITLE_FIXES:
        title = re.sub(pattern, replacement, title)
        title = title.strip()

    # If still too long, try more aggressive shortening
    if len(title) > MAX_TITLE_LENGTH:
        # Remove year from reviews
        title = re.sub(r'Review \d{4}:', 'Review:', title)

    if len(title) > MAX_TITLE_LENGTH:
        # Truncate with ellipsis
        title = title[:MAX_TITLE_LENGTH-3].rstrip() + '...'

    return title


def fix_title_in_file(filepath):
    """Fix title in HTML file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract current title
    title_match = re.search(r'<title>([^<]+)</title>', content)
    if not title_match:
        return False, None, None

    old_title = title_match.group(1)
    if len(old_title) <= MAX_TITLE_LENGTH:
        return False, old_title, old_title  # Already short enough

    new_title = shorten_title(old_title)

    if old_title == new_title:
        return False, old_title, new_title  # No change needed

    # Replace title tag
    content = content.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')

    # Also update og:title and twitter:title if they match the old title
    og_title_old = old_title.replace(' | The CRO Report', '')
    og_title_new = new_title.replace(' | The CRO Report', '')

    # Only update OG/Twitter titles if they were based on the old title
    content = re.sub(
        rf'<meta property="og:title" content="[^"]*{re.escape(og_title_old)}[^"]*">',
        f'<meta property="og:title" content="{og_title_new}">',
        content
    )
    content = re.sub(
        rf'<meta name="twitter:title" content="[^"]*{re.escape(og_title_old)}[^"]*">',
        f'<meta name="twitter:title" content="{og_title_new}">',
        content
    )

    with open(filepath, 'w') as f:
        f.write(content)

    return True, old_title, new_title


def main():
    print("=" * 70)
    print("FIXING TOOL PAGE TITLES (max 60 chars)")
    print("=" * 70)

    fixed = 0
    skipped = 0

    # Walk through tools directory
    for root, dirs, files in os.walk(SITE_DIR):
        for f in files:
            if f == 'index.html':
                filepath = os.path.join(root, f)
                changed, old_title, new_title = fix_title_in_file(filepath)

                if changed:
                    print(f"\n{filepath}")
                    print(f"  OLD ({len(old_title)}): {old_title}")
                    print(f"  NEW ({len(new_title)}): {new_title}")
                    fixed += 1
                elif old_title and len(old_title) > MAX_TITLE_LENGTH:
                    print(f"\n{filepath}")
                    print(f"  SKIPPED ({len(old_title)}): {old_title}")
                    skipped += 1

    print(f"\n" + "=" * 70)
    print(f"Results: {fixed} titles shortened, {skipped} skipped")
    print("=" * 70)


if __name__ == '__main__':
    main()
