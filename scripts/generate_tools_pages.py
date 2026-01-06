#!/usr/bin/env python3
"""
Generate GTM Tools pages for programmatic SEO
Creates:
- /tools/ index page with 5 categories
- /tools/[tool-slug]/ individual tool pages
- /tools/[tool]-alternatives/ alternatives pages
- /tools/[tool-a]-vs-[tool-b]/ comparison pages (skips if custom_url exists)

Categories: AI SDR, Data Enrichment, Conversation Intelligence, Sales Engagement, CRM & RevOps
"""

import json
import os
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

# SEO: Always use thecroreport.com as canonical domain
BASE_URL = 'https://thecroreport.com'

DATA_DIR = 'data'
SITE_DIR = 'site'
TOOLS_DIR = f'{SITE_DIR}/tools'

print("="*70)
print("🔧 GENERATING GTM TOOLS PAGES")
print("="*70)

os.makedirs(TOOLS_DIR, exist_ok=True)

# Load tools data
tools_file = f'{DATA_DIR}/tools.json'
if not os.path.exists(tools_file):
    print(f"❌ No tools.json found at {tools_file}")
    exit(1)

with open(tools_file) as f:
    data = json.load(f)

tools_list = data['tools']
tools = {t['slug']: t for t in tools_list}
categories = data['categories']
alternatives = data['alternatives']
comparisons = data['comparisons']

update_date = datetime.now().strftime('%B %d, %Y')

# Group tools by category
tools_by_category = {}
for cat in categories:
    tools_by_category[cat['slug']] = [t for t in tools_list if t['category'] == cat['name']]

# Group comparisons by category
comparisons_by_category = {}
for comp in comparisons:
    tool_a = tools.get(comp['tool_a'].lower().replace(' ', '-').replace('.', ''))
    if tool_a:
        cat_slug = None
        for cat in categories:
            if cat['name'] == tool_a['category']:
                cat_slug = cat['slug']
                break
        if cat_slug:
            if cat_slug not in comparisons_by_category:
                comparisons_by_category[cat_slug] = []
            comparisons_by_category[cat_slug].append(comp)


def get_head(title, description, page_path):
    """Generate SEO-compliant head section per thecroreport-seo-SKILL.md"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | The CRO Report</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{BASE_URL}/{page_path}">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/{page_path}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
'''


def get_styles():
    """Site-consistent styles"""
    return '''
    <style>
        :root {
            --navy: #0a1628;
            --navy-light: #132038;
            --gold: #d4a853;
            --gold-muted: #b8956a;
            --red: #dc3545;
            --green: #28a745;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-800: #1e293b;
            --white: #ffffff;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gray-50);
            color: var(--gray-800);
            line-height: 1.6;
        }
        
        /* Navigation */
        .site-header {
            background: var(--white);
            border-bottom: 1px solid var(--gray-200);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: var(--navy);
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .logo img { width: 40px; height: 40px; border-radius: 8px; }
        
        .nav { display: flex; gap: 28px; align-items: center; }
        .nav a { 
            color: var(--gray-600); 
            text-decoration: none; 
            font-size: 0.95rem; 
            font-weight: 500; 
            transition: color 0.2s; 
        }
        .nav a:hover { color: var(--navy); }
        .nav a.active { color: var(--navy); font-weight: 600; }
        
        .nav-cta {
            background: var(--navy);
            color: var(--white) !important;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
        }
        .nav-cta:hover { background: var(--navy-light); }
        
        /* Page Header */
        .page-header {
            background: var(--white);
            padding: 48px 0 40px;
            border-bottom: 1px solid var(--gray-200);
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
        .container-narrow { max-width: 900px; margin: 0 auto; padding: 0 24px; }
        
        .breadcrumb {
            font-size: 0.85rem;
            color: var(--gray-500);
            margin-bottom: 16px;
        }
        .breadcrumb a { color: var(--gold-muted); text-decoration: none; }
        .breadcrumb a:hover { text-decoration: underline; }
        
        .page-label {
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--gold-muted);
            margin-bottom: 12px;
        }
        
        .page-header h1 {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 12px;
        }
        
        .page-header .lead {
            font-size: 1.1rem;
            color: var(--gray-600);
            max-width: 700px;
            line-height: 1.7;
        }
        
        /* Stats Row */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 32px;
        }
        
        @media (max-width: 768px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }
        
        .stat-box {
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            border-radius: 10px;
            padding: 18px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--navy);
            line-height: 1;
        }
        
        .stat-number.gold { color: var(--gold-muted); }
        .stat-number.red { color: var(--red); }
        .stat-number.green { color: var(--green); }
        
        .stat-label {
            font-size: 0.75rem;
            color: var(--gray-500);
            margin-top: 6px;
        }
        
        /* Main Content */
        main { padding: 48px 0; }
        
        .section { margin-bottom: 56px; }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .section-header h2 {
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--navy);
        }
        
        .section-icon { font-size: 1.4rem; }
        
        .section-description {
            color: var(--gray-600);
            margin-bottom: 24px;
            max-width: 650px;
            font-size: 0.95rem;
        }
        
        /* Tool Cards */
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        
        .tool-card {
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
        }
        
        .tool-card:hover {
            border-color: var(--gold);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }
        
        .tool-card.coming-soon {
            opacity: 0.6;
        }
        
        .card-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 14px;
            width: fit-content;
        }
        
        .badge-live { background: rgba(40, 167, 69, 0.12); color: var(--green); }
        .badge-soon { background: rgba(100, 116, 139, 0.12); color: var(--gray-500); }
        .badge-comparison { background: rgba(212, 168, 83, 0.15); color: var(--gold-muted); }
        
        .card-logos {
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
        }
        
        .card-logo {
            width: 40px;
            height: 40px;
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .card-logo img {
            max-width: 32px;
            max-height: 32px;
            object-fit: contain;
        }
        
        .tool-card h3 {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--navy);
            margin-bottom: 8px;
        }
        
        .tool-card p {
            font-size: 0.9rem;
            color: var(--gray-600);
            line-height: 1.55;
            flex-grow: 1;
        }
        
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--gray-100);
        }
        
        .card-meta { font-size: 0.8rem; color: var(--gray-500); }
        .card-link { font-size: 0.85rem; font-weight: 600; color: var(--gold-muted); }
        
        /* Pros/Cons */
        .pros-cons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin: 24px 0;
        }
        @media (max-width: 600px) { .pros-cons { grid-template-columns: 1fr; } }
        
        .pros, .cons {
            background: var(--white);
            border-radius: 10px;
            padding: 20px;
        }
        .pros { border: 1px solid var(--green); }
        .cons { border: 1px solid var(--red); }
        
        .pros h4, .cons h4 { font-size: 0.95rem; margin-bottom: 12px; }
        .pros h4 { color: var(--green); }
        .cons h4 { color: var(--red); }
        
        .pros ul, .cons ul { list-style: none; }
        .pros li, .cons li { padding: 6px 0; font-size: 0.9rem; }
        .pros li::before { content: '✓ '; color: var(--green); font-weight: 600; }
        .cons li::before { content: '✗ '; color: var(--red); font-weight: 600; }
        
        /* Info Card */
        .info-card {
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        .info-card h3 {
            font-size: 1.1rem;
            color: var(--navy);
            margin-bottom: 16px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid var(--gray-100);
        }
        
        .info-row:last-child { border-bottom: none; }
        .info-label { color: var(--gray-500); font-size: 0.9rem; }
        .info-value { font-weight: 500; font-size: 0.9rem; }
        
        /* Comparison Table */
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--gray-200);
        }
        
        .comparison-table th {
            background: var(--navy);
            color: var(--white);
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .comparison-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--gray-200);
            font-size: 0.9rem;
        }
        
        .comparison-table tr:last-child td { border-bottom: none; }
        .comparison-table tr:nth-child(even) { background: var(--gray-50); }
        .winner { color: var(--green); font-weight: 600; }
        
        /* CTA Box */
        .cta-box {
            background: var(--navy);
            color: var(--white);
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin: 40px 0;
        }
        
        .cta-box h3 {
            font-size: 1.25rem;
            margin-bottom: 10px;
        }
        
        .cta-box p {
            color: var(--gray-300);
            margin-bottom: 20px;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.95rem;
        }
        
        .btn-gold { background: var(--gold); color: var(--navy); }
        .btn-gold:hover { background: var(--gold-muted); }
        
        /* Insight Box */
        .insight-box {
            background: var(--navy);
            color: var(--white);
            border-radius: 12px;
            padding: 24px;
            margin-top: 24px;
        }
        
        .insight-box h4 {
            color: var(--gold);
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .insight-box p { 
            font-size: 0.95rem; 
            line-height: 1.65; 
            color: var(--gray-300);
        }
        
        /* Footer */
        .site-footer {
            background: var(--white);
            border-top: 1px solid var(--gray-200);
            padding: 24px 0;
            margin-top: 48px;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            color: var(--gray-500);
        }
        
        .footer-content a { color: var(--gray-600); text-decoration: none; }
        .footer-links a { margin-left: 24px; }
        .footer-links a:hover { color: var(--navy); }
        
        @media (max-width: 768px) {
            .nav { display: none; }
            .tools-grid { grid-template-columns: 1fr; }
            .footer-content { flex-direction: column; gap: 12px; text-align: center; }
            .footer-links a { margin: 0 12px; }
        }
    </style>
</head>
'''


def get_nav(active_page='tools'):
    """Site navigation matching other pages"""
    return f'''
<body>
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo">
                <img src="/assets/logo.jpg" alt="The CRO Report">
                The CRO Report
            </a>
            <nav class="nav">
                <a href="/jobs/">Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/tools/" class="{'active' if active_page == 'tools' else ''}">Tools</a>
                <a href="/insights/">Market Intel</a>
                <a href="/newsletter/">Newsletter</a>
                <a href="https://croreport.substack.com/subscribe" class="nav-cta">Subscribe</a>
            </nav>
        </div>
    </header>
'''


def get_footer():
    """Site footer"""
    return f'''
    <footer class="site-footer">
        <div class="footer-content">
            <span>© 2025 <a href="/">The CRO Report</a></span>
            <div class="footer-links">
                <a href="/jobs/">Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/tools/">Tools</a>
                <a href="https://croreport.substack.com">Newsletter</a>
            </div>
        </div>
    </footer>
</body>
</html>
'''


# ============================================================
# 1. TOOLS INDEX PAGE - 5 Categories
# ============================================================

print("\n1. Generating tools index page...")

# Count stats
total_tools = len(tools_list)
total_comparisons = len(comparisons)
live_comparisons = len([c for c in comparisons if c.get('custom_url')])
num_categories = len(categories)

index_html = get_head(
    "GTM Tools & Reviews",
    "Honest reviews of AI SDRs, sales engagement platforms, and GTM tools for revenue leaders. Real pricing, user complaints, and recommendations by company stage.",
    "tools/"
)
index_html += get_styles()
index_html += get_nav()

index_html += f'''
    <section class="page-header">
        <div class="container">
            <div class="page-label">Tool Reviews</div>
            <h1>GTM Tools & Reviews</h1>
            <p class="lead">The tools your team uses matter more than most vendors want to admit. We dig into real pricing, user complaints, and contract terms so you don't have to learn the hard way.</p>
            
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">{total_tools}</div>
                    <div class="stat-label">Tools Reviewed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{total_comparisons}</div>
                    <div class="stat-label">Comparisons</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number green">{live_comparisons}</div>
                    <div class="stat-label">In-Depth Analyses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number gold">{num_categories}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        </div>
    </section>
    
    <main>
        <div class="container">
'''

# Generate sections for each category
for cat in categories:
    cat_tools = tools_by_category.get(cat['slug'], [])
    cat_comparisons = comparisons_by_category.get(cat['slug'], [])
    
    index_html += f'''
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">{cat.get('icon', '📦')}</span>
                    <h2>{cat['name']}</h2>
                </div>
                <p class="section-description">{cat['description']}</p>
                
                <div class="tools-grid">
'''
    
    # Add comparison cards for this category
    for comp in cat_comparisons:
        has_custom = comp.get('custom_url')
        url = comp['custom_url'] if has_custom else f"/tools/{comp['slug']}/"
        badge = 'badge-live' if has_custom else 'badge-comparison'
        badge_text = 'In-Depth' if has_custom else 'Comparison'
        
        # Get logos for the tools
        tool_a_slug = comp['tool_a'].lower().replace(' ', '-').replace('.', '')
        tool_b_slug = comp['tool_b'].lower().replace(' ', '-').replace('.', '')
        tool_a_data = tools.get(tool_a_slug, {})
        tool_b_data = tools.get(tool_b_slug, {})
        
        logo_a = tool_a_data.get('logo', '')
        logo_b = tool_b_data.get('logo', '')
        
        logos_html = ''
        if logo_a or logo_b:
            logos_html = '<div class="card-logos">'
            if logo_a:
                logos_html += f'<div class="card-logo"><img src="{logo_a}" alt="{comp["tool_a"]}"></div>'
            if logo_b:
                logos_html += f'<div class="card-logo"><img src="{logo_b}" alt="{comp["tool_b"]}"></div>'
            logos_html += '</div>'
        
        index_html += f'''
                    <a href="{url}" class="tool-card">
                        <span class="card-badge {badge}">{badge_text}</span>
                        {logos_html}
                        <h3>{comp['title']}</h3>
                        <p>{comp['description']}</p>
                        <div class="card-footer">
                            <span class="card-meta">Updated {update_date[:3]} {datetime.now().year}</span>
                            <span class="card-link">Read Analysis →</span>
                        </div>
                    </a>
'''
    
    # Add individual tool cards if few comparisons
    if len(cat_comparisons) < 2:
        for tool in cat_tools[:3]:
            logo_html = ''
            if tool.get('logo'):
                logo_html = f'''
                        <div class="card-logos">
                            <div class="card-logo"><img src="{tool['logo']}" alt="{tool['name']}"></div>
                        </div>'''
            
            index_html += f'''
                    <a href="/tools/{tool['slug']}/" class="tool-card">
                        <span class="card-badge badge-soon">Tool Review</span>
                        {logo_html}
                        <h3>{tool['name']}</h3>
                        <p>{tool['description']}</p>
                        <div class="card-footer">
                            <span class="card-meta">{tool['pricing'][:30]}...</span>
                            <span class="card-link">View Details →</span>
                        </div>
                    </a>
'''
    
    index_html += '''
                </div>
            </div>
'''

# CTA section
index_html += '''
            <div class="cta-box">
                <h3>Want a Tool Reviewed?</h3>
                <p>We're building this section based on what revenue leaders actually need.</p>
                <a href="mailto:rome@thecroreport.com?subject=Tool Review Request" class="btn btn-gold">Request a Review</a>
            </div>
            
        </div>
    </main>
'''

index_html += get_footer()

with open(f'{TOOLS_DIR}/index.html', 'w') as f:
    f.write(index_html)

print("✅ Created tools index page")


# ============================================================
# 2. INDIVIDUAL TOOL PAGES
# ============================================================

print("\n2. Generating individual tool pages...")

for tool in tools_list:
    tool_dir = f"{TOOLS_DIR}/{tool['slug']}"
    os.makedirs(tool_dir, exist_ok=True)
    
    pros_html = ''.join([f'<li>{p}</li>' for p in tool.get('pros', [])])
    cons_html = ''.join([f'<li>{c}</li>' for c in tool.get('cons', [])])
    
    logo_html = ''
    if tool.get('logo'):
        logo_html = f'<img src="{tool["logo"]}" alt="{tool["name"]}" style="width: 64px; height: 64px; border-radius: 12px; margin-bottom: 16px;">'
    
    html = get_head(
        f"{tool['name']} Review",
        f"{tool['description']} Pricing, pros, cons, and alternatives.",
        f"tools/{tool['slug']}/"
    )
    html += get_styles()
    html += get_nav()
    
    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {tool['name']}
            </nav>
            <div class="page-label">{tool['category']}</div>
            {logo_html}
            <h1>{tool['name']}</h1>
            <p class="lead">{tool['description']}</p>
        </div>
    </section>
    
    <main>
        <div class="container-narrow">
            <div class="info-card">
                <h3>Quick Facts</h3>
                <div class="info-row">
                    <span class="info-label">Best For</span>
                    <span class="info-value">{tool['best_for']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Pricing</span>
                    <span class="info-value">{tool['pricing']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Category</span>
                    <span class="info-value">{tool['category']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Website</span>
                    <span class="info-value"><a href="{tool['website']}" target="_blank" rel="noopener">{tool['website']}</a></span>
                </div>
            </div>
            
            <div class="pros-cons">
                <div class="pros">
                    <h4>✓ Pros</h4>
                    <ul>{pros_html}</ul>
                </div>
                <div class="cons">
                    <h4>✗ Cons</h4>
                    <ul>{cons_html}</ul>
                </div>
            </div>
            
            <div class="cta-box">
                <h3>Get Weekly Tool Reviews</h3>
                <p>Honest assessments of GTM tools from a practitioner perspective.</p>
                <a href="https://croreport.substack.com/subscribe" class="btn btn-gold">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </main>
'''
    html += get_footer()
    
    with open(f'{tool_dir}/index.html', 'w') as f:
        f.write(html)

print(f"✅ Created {len(tools_list)} individual tool pages")


# ============================================================
# 3. ALTERNATIVES PAGES
# ============================================================

print("\n3. Generating alternatives pages...")

for alt in alternatives:
    alt_dir = f"{TOOLS_DIR}/{alt['slug']}"
    os.makedirs(alt_dir, exist_ok=True)
    
    alts_html = ''
    for alt_name in alt['alternatives']:
        alt_slug = alt_name.lower().replace('.', '').replace(' ', '-')
        alt_tool = tools.get(alt_slug, {})
        if alt_tool:
            logo_html = ''
            if alt_tool.get('logo'):
                logo_html = f'<div class="card-logo"><img src="{alt_tool["logo"]}" alt="{alt_name}"></div>'
            
            alts_html += f'''
                    <a href="/tools/{alt_slug}/" class="tool-card">
                        <span class="card-badge badge-soon">Alternative</span>
                        {f'<div class="card-logos">{logo_html}</div>' if logo_html else ''}
                        <h3>{alt_name}</h3>
                        <p>{alt_tool.get('description', '')}</p>
                        <div class="card-footer">
                            <span class="card-meta">{alt_tool.get('pricing', 'Contact for pricing')[:30]}...</span>
                            <span class="card-link">View Details →</span>
                        </div>
                    </a>
'''
    
    points_html = ''.join([f'<li style="padding: 8px 0;">{p}</li>' for p in alt['comparison_points']])
    
    html = get_head(
        alt['title'],
        f"{alt['description']} Compare pricing, features, and find the best fit.",
        f"tools/{alt['slug']}/"
    )
    html += get_styles()
    html += get_nav()
    
    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {alt['title']}
            </nav>
            <div class="page-label">Alternatives</div>
            <h1>{alt['title']}</h1>
            <p class="lead">{alt['description']}</p>
        </div>
    </section>
    
    <main>
        <div class="container">
            <div class="tools-grid">
                {alts_html}
            </div>
            
            <div class="container-narrow" style="margin-top: 40px;">
                <h2 style="color: var(--navy); margin-bottom: 16px;">How to Choose</h2>
                <ul style="margin: 16px 0; padding-left: 24px; color: var(--gray-600);">
                    {points_html}
                </ul>
                
                <div class="cta-box">
                    <h3>Need Help Choosing?</h3>
                    <p>Get tool recommendations tailored to your team size and budget.</p>
                    <a href="https://croreport.substack.com/subscribe" class="btn btn-gold">Subscribe to The CRO Report →</a>
                </div>
            </div>
        </div>
    </main>
'''
    html += get_footer()
    
    with open(f'{alt_dir}/index.html', 'w') as f:
        f.write(html)

print(f"✅ Created {len(alternatives)} alternatives pages")


# ============================================================
# 4. COMPARISON PAGES (skip if custom_url exists)
# ============================================================

print("\n4. Generating comparison pages...")

generated_comparisons = 0
skipped_comparisons = 0

for comp in comparisons:
    # Skip if this comparison has a custom (manually created) page
    if comp.get('custom_url'):
        print(f"   ⏭️  Skipping {comp['slug']} (has custom page at {comp['custom_url']})")
        skipped_comparisons += 1
        continue
    
    comp_dir = f"{TOOLS_DIR}/{comp['slug']}"
    os.makedirs(comp_dir, exist_ok=True)
    
    tool_a_slug = comp['tool_a'].lower().replace('.', '').replace(' ', '-')
    tool_b_slug = comp['tool_b'].lower().replace('.', '').replace(' ', '-')
    tool_a = tools.get(tool_a_slug, {'name': comp['tool_a']})
    tool_b = tools.get(tool_b_slug, {'name': comp['tool_b']})
    
    winner_rows = ''
    for category, winner in comp.get('winner_for', {}).items():
        cat_name = category.replace('_', ' ').title()
        winner_rows += f'''
                        <tr>
                            <td>{cat_name}</td>
                            <td class="{'winner' if winner == comp['tool_a'] else ''}">{comp['tool_a']}</td>
                            <td class="{'winner' if winner == comp['tool_b'] else ''}">{comp['tool_b']}</td>
                        </tr>
'''
    
    html = get_head(
        comp['title'],
        f"{comp['description']} Features, pricing, and which is better for your team.",
        f"tools/{comp['slug']}/"
    )
    html += get_styles()
    html += get_nav()
    
    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {comp['title']}
            </nav>
            <div class="page-label">Comparison</div>
            <h1>{comp['title']}</h1>
            <p class="lead">{comp['description']}</p>
        </div>
    </section>
    
    <main>
        <div class="container-narrow">
            <h2 style="color: var(--navy); margin-bottom: 16px;">Quick Comparison</h2>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Factor</th>
                        <th>{comp['tool_a']}</th>
                        <th>{comp['tool_b']}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Category</td>
                        <td>{tool_a.get('category', 'N/A')}</td>
                        <td>{tool_b.get('category', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Pricing</td>
                        <td>{tool_a.get('pricing', 'Contact')}</td>
                        <td>{tool_b.get('pricing', 'Contact')}</td>
                    </tr>
                    <tr>
                        <td>Best For</td>
                        <td>{tool_a.get('best_for', 'N/A')}</td>
                        <td>{tool_b.get('best_for', 'N/A')}</td>
                    </tr>
                </tbody>
            </table>
            
            <h2 style="color: var(--navy); margin: 32px 0 16px;">Winner By Use Case</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Use Case</th>
                        <th>{comp['tool_a']}</th>
                        <th>{comp['tool_b']}</th>
                    </tr>
                </thead>
                <tbody>
                    {winner_rows}
                </tbody>
            </table>
            
            <div class="cta-box">
                <h3>Get Tool Recommendations</h3>
                <p>Weekly analysis of GTM tools and trends for sales leaders.</p>
                <a href="https://croreport.substack.com/subscribe" class="btn btn-gold">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </main>
'''
    html += get_footer()
    
    with open(f'{comp_dir}/index.html', 'w') as f:
        f.write(html)
    
    generated_comparisons += 1

print(f"✅ Created {generated_comparisons} comparison pages (skipped {skipped_comparisons} with custom URLs)")


# ============================================================
# SUMMARY
# ============================================================

total_pages = 1 + len(tools_list) + len(alternatives) + generated_comparisons
print(f"\n{'='*70}")
print(f"✅ TOOLS SECTION COMPLETE")
print(f"📊 Generated {total_pages} tool pages:")
print(f"   - 1 index page (5 categories)")
print(f"   - {len(tools_list)} individual tool pages")
print(f"   - {len(alternatives)} alternatives pages")
print(f"   - {generated_comparisons} comparison pages")
print(f"   - {skipped_comparisons} comparisons skipped (using custom pages)")
print(f"{'='*70}")
