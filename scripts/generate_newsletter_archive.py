#!/usr/bin/env python3
"""
Generate newsletter archive page from local markdown files
Reads /newsletters/*/cro_report.md with YAML frontmatter
Creates /newsletter/ page with teaser cards linking to Substack
"""

import os
import re
import glob
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

try:
    from nav_config import NAV_ITEMS, FOOTER_ITEMS, SUBSCRIBE_LINK, SUBSCRIBE_LABEL, SITE_NAME, COPYRIGHT_YEAR
except:
    NAV_ITEMS = [
        {"href": "/jobs/", "label": "Jobs"},
        {"href": "/salaries/", "label": "Salaries"},
        {"href": "/tools/", "label": "Tools"},
        {"href": "/insights/", "label": "Market Intel"},
        {"href": "/assessment/", "label": "AI Assessment"},
        {"href": "/about/", "label": "About"},
    ]
    FOOTER_ITEMS = NAV_ITEMS + [{"href": "/newsletter/", "label": "Newsletter"}]
    SUBSCRIBE_LINK = "/newsletter/"
    SUBSCRIBE_LABEL = "Subscribe"
    SITE_NAME = "The CRO Report"
    COPYRIGHT_YEAR = "2025"

def build_nav_list_html():
    items = [f'<li><a href="{item["href"]}">{item["label"]}</a></li>' for item in NAV_ITEMS]
    items.append(f'<li><a href="{SUBSCRIBE_LINK}" class="btn-subscribe">{SUBSCRIBE_LABEL}</a></li>')
    return '\n                    '.join(items)

def build_nav_div_html():
    items = [f'<a href="{item["href"]}">{item["label"]}</a>' for item in NAV_ITEMS]
    items.append(f'<a href="{SUBSCRIBE_LINK}" class="btn-subscribe">{SUBSCRIBE_LABEL}</a>')
    return '\n            '.join(items)

def build_mobile_nav_html():
    items = [f'<li><a href="{item["href"]}">{item["label"]}</a></li>' for item in NAV_ITEMS]
    return '\n            '.join(items)

def build_footer_links_html(separator=" | "):
    links = [f'<a href="/">{SITE_NAME}</a>']
    links.extend([f'<a href="{item["href"]}">{item["label"]}</a>' for item in FOOTER_ITEMS])
    return f'© {COPYRIGHT_YEAR} ' + separator.join(links)

NAV_LIST_HTML = build_nav_list_html()
NAV_DIV_HTML = build_nav_div_html()
MOBILE_NAV_HTML = build_mobile_nav_html()
FOOTER_LINKS_HTML = build_footer_links_html()

NEWSLETTERS_DIR = 'newsletters'
SITE_DIR = 'site'
NEWSLETTER_DIR = f'{SITE_DIR}/newsletter'

print("="*70)
print("📰 GENERATING NEWSLETTER ARCHIVE PAGE")
print("="*70)

# Create directory
os.makedirs(NEWSLETTER_DIR, exist_ok=True)

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown file"""
    if not content.startswith('---'):
        return None, content

    # Find the closing ---
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return None, content

    frontmatter_text = content[3:end_match.start() + 3]
    body = content[end_match.end() + 3 + 1:]

    # Parse simple YAML (key: value format)
    frontmatter = {}
    for line in frontmatter_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            frontmatter[key] = value

    return frontmatter, body

# Scan for newsletter files
print(f"📂 Scanning {NEWSLETTERS_DIR}/ for newsletters...")
newsletter_files = glob.glob(f'{NEWSLETTERS_DIR}/*.md')
print(f"   Found {len(newsletter_files)} newsletter files")

posts = []

for filepath in newsletter_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = parse_frontmatter(content)

        if not frontmatter:
            print(f"   ⚠️ No frontmatter in {filepath}, skipping")
            continue

        # Required fields
        title = frontmatter.get('title', '')
        date_str = frontmatter.get('date', '')
        excerpt = frontmatter.get('excerpt', '')
        substack_url = frontmatter.get('substack_url', '')

        if not all([title, date_str, substack_url]):
            print(f"   ⚠️ Missing required frontmatter in {filepath}")
            print(f"      title: {'✓' if title else '✗'}, date: {'✓' if date_str else '✗'}, substack_url: {'✓' if substack_url else '✗'}")
            continue

        # Parse date for sorting
        try:
            date_sort = datetime.strptime(date_str, '%Y-%m-%d')
            date_display = date_sort.strftime('%B %d, %Y')
        except:
            print(f"   ⚠️ Invalid date format in {filepath}: {date_str}")
            continue

        posts.append({
            'title': title,
            'link': substack_url,
            'date': date_display,
            'date_sort': date_sort,
            'description': excerpt
        })
        print(f"   ✅ {date_str}: {title[:50]}...")

    except Exception as e:
        print(f"   ❌ Error reading {filepath}: {e}")

# Sort by date (newest first)
posts.sort(key=lambda x: x['date_sort'], reverse=True)
print(f"\n📄 Loaded {len(posts)} newsletter editions")

# Generate post cards
if posts:
    post_cards = ''
    for i, post in enumerate(posts):
        # Add "Latest" badge to first post
        latest_badge = '<span class="badge-latest">Latest</span>' if i == 0 else ''

        post_cards += f'''
        <a href="{post['link']}" class="post-card" target="_blank" rel="noopener">
            <div class="post-header">
                <h3>{post['title']}</h3>
                {latest_badge}
            </div>
            <p class="post-date">{post['date']}</p>
            <p class="post-excerpt">{post['description']}</p>
            <span class="read-more">Read on Substack →</span>
        </a>
        '''

    posts_count = len(posts)
else:
    post_cards = '''
    <div class="no-posts">
        <p>Newsletter archive is being updated. Visit <a href="https://croreport.substack.com">our Substack</a> directly.</p>
    </div>
    '''
    posts_count = 0

update_date = datetime.now().strftime('%B %d, %Y')

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The CRO Report Newsletter Archive | Weekly Sales Executive Intelligence</title>
    <meta name="description" content="Archive of The CRO Report weekly newsletter. {posts_count} editions of VP Sales and CRO job market intelligence, compensation data, and executive movements.">
    <meta name="keywords" content="CRO Report newsletter, VP Sales market intelligence, sales executive newsletter, CRO jobs newsletter">
    <link rel="canonical" href="https://thecroreport.com/newsletter/">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap"></noscript>

    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}

        .site-header {{
            background: white;
            padding: 16px 20px;
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            font-family: 'Fraunces', serif;
            font-size: 1.25rem;
            color: #1e3a5f;
            text-decoration: none;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .nav-links {{
            display: flex;
            list-style: none;
            gap: 24px;
            align-items: center;
        }}
        .nav-links a {{
            color: #475569;
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.2s;
        }}
        .nav-links a:hover {{
            color: #1e3a5f;
        }}
        .btn-subscribe {{
            background: #1e3a5f;
            color: white !important;
            padding: 8px 16px;
            border-radius: 6px;
        }}
        .btn-subscribe:hover {{
            background: #2d4a6f;
        }}

        .hero-header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        .hero-header .eyebrow {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #d97706;
            margin-bottom: 12px;
        }}
        .hero-header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .hero-header p {{ opacity: 0.9; max-width: 600px; margin: 0 auto; }}
        .hero-header .stats {{
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-top: 24px;
        }}
        .hero-header .stat {{
            text-align: center;
        }}
        .hero-header .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
        }}
        .hero-header .stat-label {{
            font-size: 0.8rem;
            opacity: 0.8;
        }}

        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}

        .subscribe-banner {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-align: center;
            border: 2px solid #d97706;
        }}
        .subscribe-banner h2 {{
            color: #1e3a5f;
            margin-bottom: 8px;
            font-family: 'Fraunces', serif;
        }}
        .subscribe-banner p {{
            color: #64748b;
            margin-bottom: 16px;
        }}
        .subscribe-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 14px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .subscribe-btn:hover {{
            background: #b45309;
        }}

        .post-card {{
            display: block;
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .post-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .post-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
        }}
        .post-header h3 {{
            color: #1e3a5f;
            font-size: 1.15rem;
            line-height: 1.4;
        }}
        .badge-latest {{
            background: #d97706;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            white-space: nowrap;
        }}
        .post-date {{
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 8px;
        }}
        .post-excerpt {{
            color: #475569;
            font-size: 0.9rem;
            margin-top: 12px;
            line-height: 1.5;
        }}
        .read-more {{
            display: inline-block;
            color: #d97706;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 12px;
        }}

        .no-posts {{
            text-align: center;
            padding: 40px;
            color: #64748b;
        }}
        .no-posts a {{
            color: #d97706;
        }}

        .footer {{
            background: #1e3a5f;
            color: #94a3b8;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }}
        .footer a {{ color: #d97706; text-decoration: none; }}

        .update-date {{
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 32px;
        }}

        /* Mobile Navigation */
        .mobile-menu-btn {{
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #1e3a5f;
        }}
        .mobile-nav-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .mobile-nav-overlay.active {{
            opacity: 1;
        }}
        .mobile-nav {{
            position: fixed;
            top: 0;
            right: -100%;
            width: 280px;
            height: 100%;
            background: white;
            z-index: 1000;
            transition: right 0.3s ease;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
        }}
        .mobile-nav.active {{
            right: 0;
        }}
        .mobile-nav-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .mobile-nav-header .logo-text {{
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            color: #1e3a5f;
            font-weight: 600;
        }}
        .mobile-nav-close {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #64748b;
        }}
        .mobile-nav-links {{
            list-style: none;
            padding: 20px;
        }}
        .mobile-nav-links li {{
            margin-bottom: 8px;
        }}
        .mobile-nav-links a {{
            display: block;
            padding: 12px 16px;
            color: #1e3a5f;
            text-decoration: none;
            font-size: 1rem;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        .mobile-nav-links a:hover {{
            background: #f1f5f9;
        }}
        .mobile-nav-subscribe {{
            display: block;
            margin: 20px;
            padding: 14px;
            background: #1e3a5f;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .mobile-menu-btn {{ display: block; }}
            .mobile-nav-overlay {{ display: block; pointer-events: none; }}
            .mobile-nav-overlay.active {{ pointer-events: auto; }}
        }}
        @media (max-width: 600px) {{
            .hero-header .stats {{
                flex-direction: column;
                gap: 16px;
            }}
            .post-header {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo"><img src="/assets/logo.jpg" alt="The CRO Report" width="40" height="40" style="vertical-align: middle;"> The CRO Report</a>
            <nav>
                <ul class="nav-links">
                    {NAV_LIST_HTML}
                </ul>
            </nav>
            <button class="mobile-menu-btn" aria-label="Open menu">☰</button>
        </div>
    </header>

    <!-- Mobile Navigation -->
    <div class="mobile-nav-overlay"></div>
    <nav class="mobile-nav">
        <div class="mobile-nav-header">
            <span class="logo-text">The CRO Report</span>
            <button class="mobile-nav-close" aria-label="Close menu">✕</button>
        </div>
        <ul class="mobile-nav-links">
            {MOBILE_NAV_HTML}
        </ul>
        <a href="{SUBSCRIBE_LINK}" class="mobile-nav-subscribe">{SUBSCRIBE_LABEL}</a>
    </nav>

    <div class="hero-header">
        <div class="eyebrow">Weekly Intelligence</div>
        <h1>The CRO Report Newsletter</h1>
        <p>Weekly market data, compensation benchmarks, executive movements, and company deep-dives for VP Sales and CRO leaders.</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{posts_count}</div>
                <div class="stat-label">Editions</div>
            </div>
            <div class="stat">
                <div class="stat-value">Weekly</div>
                <div class="stat-label">Frequency</div>
            </div>
            <div class="stat">
                <div class="stat-value">Free</div>
                <div class="stat-label">To Subscribe</div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="subscribe-banner">
            <h2>📬 Get It In Your Inbox</h2>
            <p>Join 500+ sales executives getting weekly market intelligence.</p>
            <a href="https://croreport.substack.com/subscribe" class="subscribe-btn" target="_blank" rel="noopener">Subscribe Free</a>
        </div>

        <h2 style="margin-bottom: 24px; color: #1e3a5f;">📰 Newsletter Archive</h2>

        <div class="posts-list">
            {post_cards}
        </div>

        <p class="update-date">Archive updated: {update_date}</p>
    </div>

    <footer class="footer">
        <p>{FOOTER_LINKS_HTML}</p>
    </footer>

    <script>
        (function() {{
            const menuBtn = document.querySelector('.mobile-menu-btn');
            const closeBtn = document.querySelector('.mobile-nav-close');
            const overlay = document.querySelector('.mobile-nav-overlay');
            const mobileNav = document.querySelector('.mobile-nav');
            const mobileLinks = document.querySelectorAll('.mobile-nav-links a, .mobile-nav-subscribe');

            function openMenu() {{
                mobileNav.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }}

            function closeMenu() {{
                mobileNav.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }}

            menuBtn.addEventListener('click', openMenu);
            closeBtn.addEventListener('click', closeMenu);
            overlay.addEventListener('click', closeMenu);
            mobileLinks.forEach(link => {{ link.addEventListener('click', closeMenu); }});
        }})();
    </script>
</body>
</html>'''

# Write the page
with open(f"{NEWSLETTER_DIR}/index.html", 'w') as f:
    f.write(html_content)

print(f"\n{'='*70}")
print(f"✅ Generated /newsletter/ archive page with {posts_count} editions")
print(f"{'='*70}")
