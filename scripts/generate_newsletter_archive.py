#!/usr/bin/env python3
"""
Generate newsletter archive page from Substack RSS feed
Creates /newsletter/ page linking to all Substack editions
"""

import xml.etree.ElementTree as ET
import urllib.request
import ssl
import html
import re
import os
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

SUBSTACK_RSS = "https://croreport.substack.com/feed"
SITE_DIR = 'site'
NEWSLETTER_DIR = f'{SITE_DIR}/newsletter'

print("="*70)
print("📰 GENERATING NEWSLETTER ARCHIVE PAGE")
print("="*70)

# Create directory
os.makedirs(NEWSLETTER_DIR, exist_ok=True)

# Fetch RSS feed with retries
print(f"📡 Fetching RSS from {SUBSTACK_RSS}...")
rss_content = None

# Create SSL context that doesn't verify (for environments with cert issues)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

try:
    req = urllib.request.Request(
        SUBSTACK_RSS,
        headers={
            'User-Agent': user_agent,
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        }
    )
    with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
        rss_content = response.read().decode('utf-8')
    if rss_content and '<item>' in rss_content:
        print(f"✅ RSS feed fetched successfully")
    else:
        print("⚠️ RSS fetched but no items found")
        rss_content = None
except Exception as e:
    print(f"❌ Failed to fetch RSS: {e}")
    rss_content = None

posts = []

if rss_content:
    # Parse RSS
    try:
        root = ET.fromstring(rss_content)
        channel = root.find('channel')
        
        for item in channel.findall('item'):
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            
            title_text = title.text if title is not None else "Untitled"
            link_text = link.text if link is not None else "#"
            
            # Parse date
            date_text = ""
            date_sort = datetime.now()
            if pub_date is not None and pub_date.text:
                try:
                    # RSS date format: "Wed, 27 Dec 2025 12:00:00 GMT"
                    date_sort = datetime.strptime(pub_date.text.split('+')[0].strip(), "%a, %d %b %Y %H:%M:%S")
                    date_text = date_sort.strftime("%B %d, %Y")
                except:
                    try:
                        date_sort = datetime.strptime(pub_date.text[:25], "%a, %d %b %Y %H:%M:%S")
                        date_text = date_sort.strftime("%B %d, %Y")
                    except:
                        date_text = pub_date.text[:16] if pub_date.text else ""
            
            # Clean description - get first ~200 chars
            desc_text = ""
            if description is not None and description.text:
                # Remove HTML tags
                desc_text = re.sub(r'<[^>]+>', '', description.text)
                desc_text = html.unescape(desc_text)
                desc_text = desc_text[:250].strip()
                if len(description.text) > 250:
                    desc_text += "..."
            
            posts.append({
                'title': title_text,
                'link': link_text,
                'date': date_text,
                'date_sort': date_sort,
                'description': desc_text
            })
        
        # Sort by date (newest first)
        posts.sort(key=lambda x: x['date_sort'], reverse=True)
        print(f"📄 Found {len(posts)} newsletter editions")
        
    except Exception as e:
        print(f"❌ Failed to parse RSS: {e}")

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
    latest_date = posts[0]['date'] if posts else "N/A"
else:
    post_cards = '''
    <div class="no-posts">
        <p>Newsletter archive is being updated. Visit <a href="https://croreport.substack.com">our Substack</a> directly.</p>
    </div>
    '''
    posts_count = 0
    latest_date = "N/A"

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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
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
            <a href="/" class="logo"><img src="/assets/logo.jpg" alt="The CRO Report" style="height: 40px; vertical-align: middle;"> The CRO Report</a>
            <nav>
                <ul class="nav-links">
                    <li><a href="/jobs/">Jobs</a></li>
                    <li><a href="/salaries/">Salaries</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="https://thecroreport.substack.com" class="btn-subscribe">Subscribe</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
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
        <p>© 2025 The CRO Report | <a href="/jobs/">All Jobs</a> | <a href="/salaries/">Salary Data</a> | <a href="/insights/">Market Insights</a></p>
    </footer>
</body>
</html>'''

# Write the page
with open(f"{NEWSLETTER_DIR}/index.html", 'w') as f:
    f.write(html_content)

print(f"\n{'='*70}")
print(f"✅ Generated /newsletter/ archive page with {posts_count} editions")
print(f"{'='*70}")
