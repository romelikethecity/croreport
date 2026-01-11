#!/usr/bin/env python3
"""
Centralized navigation configuration for The CRO Report.

Edit this file to update navigation across ALL pages on the site.
After editing, regenerate pages by running the build workflow or:
    python3 scripts/generate_job_pages.py
    python3 scripts/generate_category_pages.py
    python3 scripts/generate_job_board.py
    python3 scripts/generate_insights_page.py
    python3 scripts/generate_newsletter_archive.py
"""

# Main navigation items (appear in header)
# Order matters - items appear left to right as listed
NAV_ITEMS = [
    {"href": "/jobs/", "label": "Jobs"},
    {"href": "/salaries/", "label": "Salaries"},
    {"href": "/tools/", "label": "Tools"},
    {"href": "/insights/", "label": "Market Intel"},
    {"href": "/assessment/", "label": "AI Assessment"},
    {"href": "/about/", "label": "About"},
]

# Subscribe/CTA button in nav
SUBSCRIBE_LINK = "/newsletter/"
SUBSCRIBE_LABEL = "Subscribe"

# Footer navigation items
FOOTER_ITEMS = [
    {"href": "/jobs/", "label": "Jobs"},
    {"href": "/salaries/", "label": "Salaries"},
    {"href": "/tools/", "label": "Tools"},
    {"href": "/insights/", "label": "Market Intel"},
    {"href": "/assessment/", "label": "AI Assessment"},
    {"href": "/about/", "label": "About"},
    {"href": "/newsletter/", "label": "Newsletter"},
]

# Site info
SITE_NAME = "The CRO Report"
SITE_URL = "https://thecroreport.com"
COPYRIGHT_YEAR = "2025"


def get_nav_links_html(active_page=None, use_list=True):
    """
    Generate HTML for navigation links.

    Args:
        active_page: Current page identifier (e.g., 'jobs', 'salaries') for highlighting
        use_list: If True, wrap in <ul>/<li>. If False, just <a> tags.

    Returns:
        HTML string for nav links
    """
    links = []
    for item in NAV_ITEMS:
        active_class = ' class="active"' if item['href'].strip('/') == active_page else ''
        if use_list:
            links.append(f'<li><a href="{item["href"]}"{active_class}>{item["label"]}</a></li>')
        else:
            links.append(f'<a href="{item["href"]}"{active_class}>{item["label"]}</a>')

    # Add subscribe button
    if use_list:
        links.append(f'<li><a href="{SUBSCRIBE_LINK}" class="btn-subscribe">{SUBSCRIBE_LABEL}</a></li>')
    else:
        links.append(f'<a href="{SUBSCRIBE_LINK}" class="btn-subscribe">{SUBSCRIBE_LABEL}</a>')

    if use_list:
        return f'<ul class="nav-links">\n                    ' + '\n                    '.join(links) + '\n                </ul>'
    else:
        return '\n            '.join(links)


def get_mobile_nav_links_html():
    """Generate HTML for mobile navigation links."""
    links = []
    for item in NAV_ITEMS:
        links.append(f'<li><a href="{item["href"]}">{item["label"]}</a></li>')

    return f'''<ul class="mobile-nav-links">
            {''.join(f"""
            <li><a href="{item['href']}">{item['label']}</a></li>""" for item in NAV_ITEMS)}
        </ul>
        <a href="{SUBSCRIBE_LINK}" class="mobile-nav-subscribe">{SUBSCRIBE_LABEL}</a>'''


def get_footer_links_html(separator=" · "):
    """Generate HTML for footer links."""
    links = [f'<a href="/">{SITE_NAME}</a>']
    for item in FOOTER_ITEMS:
        links.append(f'<a href="{item["href"]}">{item["label"]}</a>')

    return f'© {COPYRIGHT_YEAR} ' + separator.join(links)


# For quick testing
if __name__ == "__main__":
    print("=== Nav Links (list format) ===")
    print(get_nav_links_html())
    print("\n=== Nav Links (plain format) ===")
    print(get_nav_links_html(use_list=False))
    print("\n=== Mobile Nav ===")
    print(get_mobile_nav_links_html())
    print("\n=== Footer ===")
    print(get_footer_links_html())
