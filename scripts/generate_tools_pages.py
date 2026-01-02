#!/usr/bin/env python3
"""
Generate GTM Tools pages for programmatic SEO
Creates:
- /tools/ index page
- /tools/[tool-slug]/ individual tool pages
- /tools/[tool]-alternatives/ alternatives pages
- /tools/[tool-a]-vs-[tool-b]/ comparison pages

Target keywords: "Outreach alternatives", "Gong vs Chorus", etc.
"""

import json
import os
from datetime import datetime

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

tools = {t['slug']: t for t in data['tools']}
categories = data['categories']
alternatives = data['alternatives']
comparisons = data['comparisons']

update_date = datetime.now().strftime('%B %d, %Y')

def page_header():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }
        
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        .header .eyebrow {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #d97706;
            margin-bottom: 12px;
        }
        .header h1 { font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }
        .header p { opacity: 0.9; max-width: 600px; margin: 0 auto; }
        
        .container { max-width: 900px; margin: 0 auto; padding: 0 20px; }
        .content { padding: 40px 0; }
        
        h2 { font-family: 'Fraunces', serif; font-size: 1.5rem; color: #1e3a5f; margin: 32px 0 16px; }
        h3 { font-size: 1.1rem; color: #1e3a5f; margin-bottom: 8px; }
        
        .card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.2s;
        }
        .card:hover { border-color: #1e3a5f; box-shadow: 0 4px 12px rgba(30,58,95,0.1); }
        .card a { text-decoration: none; color: inherit; }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }
        
        .tag { 
            display: inline-block;
            background: #f1f5f9;
            color: #475569;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .tag.pro { background: #dcfce7; color: #166534; }
        .tag.con { background: #fee2e2; color: #991b1b; }
        
        .pros-cons { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0; }
        @media (max-width: 600px) { .pros-cons { grid-template-columns: 1fr; } }
        .pros-cons h4 { font-size: 0.9rem; margin-bottom: 12px; }
        .pros-cons ul { list-style: none; }
        .pros-cons li { padding: 8px 0; font-size: 0.9rem; }
        .pros li::before { content: '✓'; color: #16a34a; margin-right: 8px; }
        .cons li::before { content: '✗'; color: #dc2626; margin-right: 8px; }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
        }
        .comparison-table th, .comparison-table td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        .comparison-table th { background: #f8fafc; font-weight: 600; }
        .comparison-table .winner { color: #16a34a; font-weight: 500; }
        
        .cta-box {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin: 40px 0;
        }
        .cta-box h2 { color: white; }
        .cta-box p { opacity: 0.9; margin: 12px 0 20px; }
        .cta-btn {
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }
        
        .breadcrumb { font-size: 0.85rem; color: #64748b; padding: 16px 0; }
        .breadcrumb a { color: #1e3a5f; text-decoration: none; }
        
        .footer {
            background: #1e3a5f;
            color: #94a3b8;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }
        .footer a { color: #d97706; text-decoration: none; }
    </style>
'''

def page_footer():
    return f'''
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/tools/">Tools</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
        <p style="margin-top: 8px; font-size: 0.85rem;">Updated {update_date}</p>
    </footer>
</body>
</html>'''

# ============================================================
# 1. TOOLS INDEX PAGE
# ============================================================

print("\n1. Generating tools index page...")

index_html = page_header() + f'''
    <title>GTM Tools for Sales Leaders | The CRO Report</title>
    <meta name="description" content="Reviews and comparisons of sales engagement, revenue intelligence, and CRM tools. Practitioner perspective for VP Sales and CROs.">
</head>
<body>
    <header class="header">
        <div class="eyebrow">GTM Tools</div>
        <h1>Tools for Revenue Leaders</h1>
        <p>Honest reviews, alternatives, and comparisons of sales and revenue tools. No vendor spin.</p>
    </header>
    
    <div class="container">
        <div class="content">
            <h2>Popular Comparisons</h2>
            <div class="card-grid">
'''

for comp in comparisons:
    index_html += f'''
                <a href="{comp['slug']}/" class="card">
                    <h3>{comp['title']}</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">{comp['description']}</p>
                </a>
'''

index_html += '''
            </div>
            
            <h2>Find Alternatives</h2>
            <div class="card-grid">
'''

for alt in alternatives:
    index_html += f'''
                <a href="{alt['slug']}/" class="card">
                    <h3>{alt['title']}</h3>
                    <p style="color: #64748b; font-size: 0.9rem;">{alt['description']}</p>
                </a>
'''

index_html += '''
            </div>
            
            <h2>All Tools</h2>
            <div class="card-grid">
'''

for tool in data['tools']:
    index_html += f'''
                <a href="{tool['slug']}/" class="card">
                    <h3>{tool['name']}</h3>
                    <span class="tag">{tool['category']}</span>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 8px;">{tool['description']}</p>
                </a>
'''

index_html += '''
            </div>
            
            <div class="cta-box">
                <h2>Get Weekly GTM Intelligence</h2>
                <p>Tool reviews, market trends, and career intelligence for sales leaders.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </div>
''' + page_footer()

with open(f'{TOOLS_DIR}/index.html', 'w') as f:
    f.write(index_html)
print(f"✅ Created /tools/index.html")

# ============================================================
# 2. INDIVIDUAL TOOL PAGES
# ============================================================

print("\n2. Generating individual tool pages...")

for tool in data['tools']:
    tool_dir = f"{TOOLS_DIR}/{tool['slug']}"
    os.makedirs(tool_dir, exist_ok=True)
    
    pros_html = ''.join([f'<li>{p}</li>' for p in tool.get('pros', [])])
    cons_html = ''.join([f'<li>{c}</li>' for c in tool.get('cons', [])])
    
    html = page_header() + f'''
    <title>{tool['name']} Review for Sales Teams | The CRO Report</title>
    <meta name="description" content="{tool['name']} review for sales leaders. {tool['description']} Pricing, pros, cons, and alternatives.">
</head>
<body>
    <header class="header">
        <div class="eyebrow">{tool['category']}</div>
        <h1>{tool['name']}</h1>
        <p>{tool['description']}</p>
    </header>
    
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/tools/">Tools</a> → {tool['name']}
        </nav>
        
        <div class="content">
            <div class="card">
                <h3>Quick Facts</h3>
                <p><strong>Best For:</strong> {tool['best_for']}</p>
                <p><strong>Pricing:</strong> {tool['pricing']}</p>
                <p><strong>Website:</strong> <a href="{tool['website']}" target="_blank" rel="noopener">{tool['website']}</a></p>
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
            
            <h2>Looking for Alternatives?</h2>
            <p>See our <a href="/tools/{tool['slug']}-alternatives/">full list of {tool['name']} alternatives</a> with detailed comparisons.</p>
            
            <div class="cta-box">
                <h2>Get Weekly Tool Reviews</h2>
                <p>Honest assessments of GTM tools from a practitioner perspective.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </div>
''' + page_footer()
    
    with open(f'{tool_dir}/index.html', 'w') as f:
        f.write(html)

print(f"✅ Created {len(data['tools'])} individual tool pages")

# ============================================================
# 3. ALTERNATIVES PAGES
# ============================================================

print("\n3. Generating alternatives pages...")

for alt in alternatives:
    alt_dir = f"{TOOLS_DIR}/{alt['slug']}"
    os.makedirs(alt_dir, exist_ok=True)
    
    main_tool = tools.get(alt['main_tool'].lower().replace('.', '').replace(' ', '-'))
    
    alts_html = ''
    for alt_name in alt['alternatives']:
        alt_slug = alt_name.lower().replace('.', '').replace(' ', '-')
        alt_tool = tools.get(alt_slug, {})
        if alt_tool:
            alts_html += f'''
            <div class="card">
                <h3><a href="/tools/{alt_slug}/">{alt_name}</a></h3>
                <span class="tag">{alt_tool.get('category', '')}</span>
                <p style="margin: 12px 0;">{alt_tool.get('description', '')}</p>
                <p><strong>Pricing:</strong> {alt_tool.get('pricing', 'Contact for pricing')}</p>
                <p><strong>Best for:</strong> {alt_tool.get('best_for', '')}</p>
            </div>
'''
    
    points_html = ''.join([f'<li>{p}</li>' for p in alt['comparison_points']])
    
    html = page_header() + f'''
    <title>{alt['title']} (2025) | Best {alt['main_tool']} Competitors</title>
    <meta name="description" content="{alt['description']} Compare pricing, features, and find the best fit for your sales team.">
</head>
<body>
    <header class="header">
        <div class="eyebrow">Alternatives</div>
        <h1>{alt['title']}</h1>
        <p>{alt['description']}</p>
    </header>
    
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/tools/">Tools</a> → {alt['title']}
        </nav>
        
        <div class="content">
            <h2>Top {alt['main_tool']} Alternatives for 2025</h2>
            
            {alts_html}
            
            <h2>How to Choose</h2>
            <ul style="margin: 16px 0; padding-left: 24px;">
                {points_html}
            </ul>
            
            <div class="cta-box">
                <h2>Need Help Choosing?</h2>
                <p>Get tool recommendations tailored to your team size and budget.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </div>
''' + page_footer()
    
    with open(f'{alt_dir}/index.html', 'w') as f:
        f.write(html)

print(f"✅ Created {len(alternatives)} alternatives pages")

# ============================================================
# 4. COMPARISON PAGES
# ============================================================

print("\n4. Generating comparison pages...")

for comp in comparisons:
    comp_dir = f"{TOOLS_DIR}/{comp['slug']}"
    os.makedirs(comp_dir, exist_ok=True)
    
    tool_a_slug = comp['tool_a'].lower().replace('.', '').replace(' ', '-')
    tool_b_slug = comp['tool_b'].lower().replace('.', '').replace(' ', '-')
    tool_a = tools.get(tool_a_slug, {'name': comp['tool_a']})
    tool_b = tools.get(tool_b_slug, {'name': comp['tool_b']})
    
    winner_rows = ''
    for category, winner in comp['winner_for'].items():
        cat_name = category.replace('_', ' ').title()
        winner_rows += f'''
            <tr>
                <td>{cat_name}</td>
                <td class="{'winner' if winner == comp['tool_a'] else ''}">{comp['tool_a']}</td>
                <td class="{'winner' if winner == comp['tool_b'] else ''}">{comp['tool_b']}</td>
            </tr>
'''
    
    html = page_header() + f'''
    <title>{comp['title']} (2025 Comparison) | The CRO Report</title>
    <meta name="description" content="{comp['description']} Features, pricing, and which is better for your sales team.">
</head>
<body>
    <header class="header">
        <div class="eyebrow">Comparison</div>
        <h1>{comp['title']}</h1>
        <p>{comp['description']}</p>
    </header>
    
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/tools/">Tools</a> → {comp['title']}
        </nav>
        
        <div class="content">
            <h2>Quick Comparison</h2>
            
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Category</th>
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
            
            <h2>Winner By Category</h2>
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
            
            <h2>The Bottom Line</h2>
            <p>Choose <strong>{comp['tool_a']}</strong> if you need enterprise features and have budget for premium tooling.</p>
            <p>Choose <strong>{comp['tool_b']}</strong> if you want better value or simpler implementation.</p>
            
            <div class="cta-box">
                <h2>Get Tool Recommendations</h2>
                <p>Weekly analysis of GTM tools and trends for sales leaders.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </div>
''' + page_footer()
    
    with open(f'{comp_dir}/index.html', 'w') as f:
        f.write(html)

print(f"✅ Created {len(comparisons)} comparison pages")

# ============================================================
# SUMMARY
# ============================================================

total_pages = 1 + len(data['tools']) + len(alternatives) + len(comparisons)
print(f"\n{'='*70}")
print(f"✅ TOOLS SECTION COMPLETE")
print(f"📊 Generated {total_pages} tool pages:")
print(f"   - 1 index page")
print(f"   - {len(data['tools'])} individual tool pages")
print(f"   - {len(alternatives)} alternatives pages")
print(f"   - {len(comparisons)} comparison pages")
print(f"{'='*70}")
