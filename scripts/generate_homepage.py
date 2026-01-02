#!/usr/bin/env python3
"""
Generate the main homepage for The CRO Report
Includes Market Pulse, Who's Moving teasers, and newsletter signup
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

DATA_DIR = 'data'
SITE_DIR = 'site'

print("="*70)
print("🏠 GENERATING HOMEPAGE")
print("="*70)

# Load market stats
stats_file = f'{DATA_DIR}/market_stats.json'
if os.path.exists(stats_file):
    with open(stats_file) as f:
        stats = json.load(f)
    print(f"✅ Loaded market stats: {stats['total_roles']} roles")
else:
    stats = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'total_roles': 0,
        'wow_change': 0,
        'vs_peak_pct': 0,
        'remote_pct': 0,
        'avg_max_salary': 0
    }
    print("⚠️  No market stats found, using defaults")

# Load moves
moves_file = f'{DATA_DIR}/moves.json'
if os.path.exists(moves_file):
    with open(moves_file) as f:
        moves_data = json.load(f)
    moves = moves_data.get('moves', [])[:2]  # Latest 2 moves
    print(f"✅ Loaded {len(moves)} executive moves")
else:
    moves = []
    print("⚠️  No moves.json found")

# Format date
update_date = datetime.strptime(stats['date'], '%Y-%m-%d').strftime('%B %d, %Y')

# Generate moves HTML
if moves:
    moves_html = ''
    for move in moves:
        moves_html += f'''
        <div class="move-card">
            <span class="eyebrow">New Appointment</span>
            <h3>{move['name']}</h3>
            <div class="role">→ {move['new_role']} at {move['new_company']}</div>
            <div class="previous">Previously: {move['previous']}</div>
            <a href="https://croreport.substack.com/subscribe" class="cta">Read full analysis →</a>
        </div>
        '''
else:
    moves_html = '''
    <div class="move-card">
        <span class="eyebrow">Coming Soon</span>
        <h3>Executive Moves</h3>
        <div class="previous">Subscribe to get weekly executive movement analysis</div>
        <a href="https://croreport.substack.com/subscribe" class="cta">Subscribe →</a>
    </div>
    '''

# Determine WoW direction
wow_direction = 'up' if stats['wow_change'] >= 0 else 'down'
wow_arrow = '↑' if stats['wow_change'] >= 0 else '↓'

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The CRO Report | Intelligence for Revenue Leaders</title>
    <meta name="description" content="Weekly market data, compensation benchmarks, and executive moves for VP Sales and CRO leaders. {stats['total_roles']} open roles tracked.">
    
    <link rel="icon" type="image/jpeg" href="/assets/logo.jpg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --navy: #1e3a5f;
            --navy-light: #2d4a6f;
            --navy-dark: #152d4a;
            --gold: #d97706;
            --gold-hover: #b45309;
            --white: #ffffff;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-300: #cbd5e1;
            --gray-500: #64748b;
            --gray-600: #475569;
            --gray-900: #0f172a;
        }}
        
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ font-size: 16px; -webkit-font-smoothing: antialiased; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; color: var(--gray-900); background: var(--white); line-height: 1.6; }}
        
        h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif; font-weight: 600; line-height: 1.2; color: var(--navy); }}
        h1 {{ font-size: clamp(2.25rem, 5vw, 3.5rem); }}
        h2 {{ font-size: clamp(1.5rem, 3vw, 2rem); margin-bottom: 1.5rem; }}
        p {{ color: var(--gray-600); margin-bottom: 1rem; }}
        a {{ color: var(--navy); text-decoration: none; transition: color 0.2s; }}
        a:hover {{ color: var(--gold); }}
        
        .eyebrow {{ display: inline-block; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--gold); margin-bottom: 1rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
        
        /* Header */
        .site-header {{ padding: 1rem 0; background: var(--white); border-bottom: 1px solid var(--gray-200); position: sticky; top: 0; z-index: 100; }}
        .site-header .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-family: 'Fraunces', serif; font-size: 1.25rem; font-weight: 600; color: var(--navy); }}
        .nav-links {{ display: flex; gap: 2rem; list-style: none; }}
        .nav-links a {{ font-size: 0.9rem; font-weight: 500; color: var(--gray-600); }}
        @media (max-width: 600px) {{ .nav-links {{ display: none; }} }}
        
        /* Buttons */
        .btn {{ display: inline-flex; align-items: center; padding: 0.75rem 1.5rem; font-weight: 600; border-radius: 8px; transition: all 0.2s; }}
        .btn--primary {{ background: var(--navy); color: var(--white); }}
        .btn--primary:hover {{ background: var(--navy-light); color: var(--white); }}
        .btn--secondary {{ background: var(--white); color: var(--navy); border: 1px solid var(--gray-300); }}
        .btn--secondary:hover {{ border-color: var(--navy); }}
        
        /* Hero */
        .hero {{ padding: 5rem 0 3rem; background: linear-gradient(180deg, var(--gray-50) 0%, var(--white) 100%); text-align: center; }}
        .hero h1 {{ margin-bottom: 1.5rem; }}
        .hero .lead {{ font-size: 1.25rem; color: var(--gray-500); max-width: 580px; margin: 0 auto 2rem; }}
        .hero-actions {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
        
        /* Market Pulse */
        .market-pulse {{ background: var(--navy); color: var(--white); padding: 2.5rem 0; }}
        .pulse-header {{ text-align: center; margin-bottom: 2rem; }}
        .pulse-header h2 {{ color: var(--white); margin-bottom: 0.5rem; font-size: 1.5rem; }}
        .pulse-header p {{ color: var(--gray-300); margin: 0; font-size: 0.9rem; }}
        
        .pulse-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-bottom: 2rem; }}
        @media (max-width: 800px) {{ .pulse-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        
        .pulse-stat {{ text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 12px; }}
        .pulse-stat .number {{ font-family: 'Fraunces', serif; font-size: 2.5rem; font-weight: 600; line-height: 1; }}
        .pulse-stat .change {{ font-size: 0.875rem; font-weight: 600; margin-top: 0.25rem; display: inline-flex; align-items: center; gap: 0.25rem; }}
        .pulse-stat .change.up {{ color: #4ade80; }}
        .pulse-stat .change.down {{ color: #f87171; }}
        .pulse-stat .label {{ font-size: 0.8rem; color: var(--gray-300); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem; }}
        
        .pulse-cta {{ text-align: center; }}
        .pulse-cta a {{ color: var(--gold); font-weight: 600; font-size: 0.9rem; }}
        
        /* Who's Moving */
        .whos-moving {{ background: var(--gray-50); padding: 3rem 0; }}
        .moves-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }}
        @media (max-width: 700px) {{ .moves-grid {{ grid-template-columns: 1fr; }} }}
        
        .move-card {{ background: var(--white); border: 1px solid var(--gray-200); border-radius: 12px; padding: 1.5rem; transition: all 0.2s; }}
        .move-card:hover {{ border-color: var(--navy); box-shadow: 0 4px 12px rgba(30,58,95,0.1); }}
        .move-card .eyebrow {{ margin-bottom: 0.5rem; font-size: 0.7rem; }}
        .move-card h3 {{ font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem; }}
        .move-card .role {{ color: var(--navy); font-weight: 500; margin-bottom: 0.75rem; font-size: 0.9rem; }}
        .move-card .previous {{ font-size: 0.85rem; color: var(--gray-500); }}
        .move-card .cta {{ font-size: 0.85rem; color: var(--gold); font-weight: 500; margin-top: 1rem; display: inline-block; }}
        
        /* Pillars */
        .pillars {{ padding: 4rem 0; }}
        .pillars-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }}
        @media (max-width: 900px) {{ .pillars-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 600px) {{ .pillars-grid {{ grid-template-columns: 1fr; }} }}
        
        .pillar {{ background: var(--white); border: 1px solid var(--gray-200); border-radius: 16px; padding: 2rem; transition: all 0.2s; }}
        .pillar:hover {{ border-color: var(--navy); box-shadow: 0 8px 24px rgba(30,58,95,0.1); }}
        .pillar-icon {{ font-size: 2rem; margin-bottom: 1rem; }}
        .pillar h3 {{ font-size: 1.5rem; margin-bottom: 0.75rem; }}
        .pillar > p {{ margin-bottom: 1.5rem; }}
        .pillar-links {{ list-style: none; margin-bottom: 1.5rem; }}
        .pillar-links li {{ padding: 0.5rem 0; border-bottom: 1px solid var(--gray-100); }}
        .pillar-links a {{ font-size: 0.9rem; color: var(--gray-600); }}
        .pillar-links a:hover {{ color: var(--navy); }}
        
        /* Newsletter */
        .newsletter {{ background: var(--navy-dark); color: var(--white); padding: 4rem 0; }}
        .newsletter-content {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; }}
        @media (max-width: 800px) {{ .newsletter-content {{ grid-template-columns: 1fr; text-align: center; }} }}
        
        .newsletter-copy h2 {{ color: var(--white); margin-bottom: 1rem; }}
        .newsletter-copy p {{ color: var(--gray-300); margin-bottom: 1rem; max-width: 400px; }}
        @media (max-width: 800px) {{ .newsletter-copy p {{ margin: 0 auto 1rem; }} }}
        .newsletter-copy ul {{ list-style: none; margin-bottom: 1rem; }}
        .newsletter-copy li {{ color: var(--gray-300); font-size: 0.9rem; padding: 0.5rem 0; display: flex; align-items: center; gap: 0.5rem; }}
        @media (max-width: 800px) {{ .newsletter-copy li {{ justify-content: center; }} }}
        .newsletter-copy li::before {{ content: '✓'; color: var(--gold); font-weight: bold; }}
        
        .newsletter-embed {{ display: flex; justify-content: center; }}
        .newsletter-embed iframe {{ border-radius: 12px; max-width: 100%; }}
        
        /* Footer */
        .site-footer {{ background: var(--navy-dark); color: var(--gray-400); padding: 3rem 0; text-align: center; }}
        .site-footer a {{ color: var(--gold); }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a href="/" class="logo"><img src="/assets/logo.jpg" alt="The CRO Report" style="height: 40px; vertical-align: middle;"> The CRO Report</a>
            <nav>
                <ul class="nav-links">
                    <li><a href="/jobs/">Jobs</a></li>
                    <li><a href="/salaries/">Salaries</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="#subscribe" class="btn btn--primary" style="padding: 0.5rem 1rem; font-size: 0.85rem; color: white;">Subscribe</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <span class="eyebrow">For VPs, CROs & Sales Leaders</span>
                <h1>Intelligence That<br>Moves Revenue</h1>
                <p class="lead">Weekly market data, compensation benchmarks, and executive moves. The job market intelligence sales leaders actually need.</p>
                <div class="hero-actions">
                    <a href="#subscribe" class="btn btn--primary">Get the Weekly Report</a>
                    <a href="/jobs/" class="btn btn--secondary">Browse {stats['total_roles']} Jobs</a>
                </div>
            </div>
        </section>

        <section class="market-pulse">
            <div class="container">
                <div class="pulse-header">
                    <h2>📊 Market Pulse</h2>
                    <p>Week of {update_date}</p>
                </div>
                
                <div class="pulse-grid">
                    <div class="pulse-stat">
                        <span class="number">{stats['total_roles']}</span>
                        <span class="change {wow_direction}">{wow_arrow} {abs(stats['wow_change']):.0f}% WoW</span>
                        <span class="label">Open Roles</span>
                    </div>
                    <div class="pulse-stat">
                        <span class="number">{abs(stats['vs_peak_pct']):.0f}%</span>
                        <span class="change">{'below' if stats['vs_peak_pct'] < 0 else 'above'} peak</span>
                        <span class="label">vs. 2022 High</span>
                    </div>
                    <div class="pulse-stat">
                        <span class="number">{stats['remote_pct']:.0f}%</span>
                        <span class="change">remote</span>
                        <span class="label">Location Flex</span>
                    </div>
                    <div class="pulse-stat">
                        <span class="number">${stats['avg_max_salary']//1000:.0f}k</span>
                        <span class="change">avg max</span>
                        <span class="label">Compensation</span>
                    </div>
                </div>
                
                <div class="pulse-cta">
                    <a href="#subscribe">Get full market analysis every Thursday →</a>
                </div>
            </div>
        </section>

        <section class="whos-moving">
            <div class="container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                    <div>
                        <span class="eyebrow">Who's Moving</span>
                        <h2 style="margin-bottom: 0;">Executive Moves This Week</h2>
                    </div>
                    <a href="https://croreport.substack.com/subscribe" class="btn btn--secondary" style="padding: 0.5rem 1rem; font-size: 0.85rem;">See All Moves</a>
                </div>
                
                <div class="moves-grid">
                    {moves_html}
                </div>
            </div>
        </section>

        <section class="pillars">
            <div class="container">
                <div class="pillars-grid">
                    <article class="pillar">
                        <div class="pillar-icon">📈</div>
                        <h3>Executive Sales Jobs</h3>
                        <p>VP Sales, CRO, and sales leadership positions. Salary data included. Updated weekly.</p>
                        <ul class="pillar-links">
                            <li><a href="/jobs/">All Open Roles ({stats['total_roles']})</a></li>
                            <li><a href="/salaries/">Salary Benchmarks</a></li>
                            <li><a href="/salaries/remote/">Remote Roles</a></li>
                        </ul>
                        <a href="/jobs/" class="btn btn--secondary">Browse Jobs →</a>
                    </article>
                    
                    <article class="pillar">
                        <div class="pillar-icon">💰</div>
                        <h3>Compensation Data</h3>
                        <p>Salary benchmarks by market and seniority. Know your market value before you negotiate.</p>
                        <ul class="pillar-links">
                            <li><a href="/salaries/new-york/">NYC: $171k-$241k avg</a></li>
                            <li><a href="/salaries/san-francisco/">SF: $239k-$337k avg</a></li>
                            <li><a href="/salaries/cro/">CRO: $217k-$292k avg</a></li>
                        </ul>
                        <a href="/salaries/" class="btn btn--secondary">All Salary Data →</a>
                    </article>
                    
                    <article class="pillar">
                        <div class="pillar-icon">📊</div>
                        <h3>Market Intelligence</h3>
                        <p>What skills, tools, and methodologies are companies looking for right now?</p>
                        <ul class="pillar-links">
                            <li><a href="/insights/">Skills & Tools in Demand</a></li>
                            <li><a href="/insights/">Methodology Requirements</a></li>
                            <li><a href="/insights/">Red Flags to Watch</a></li>
                        </ul>
                        <a href="/insights/" class="btn btn--secondary">See Analysis →</a>
                    </article>
                </div>
            </div>
        </section>

        <section class="newsletter" id="subscribe">
            <div class="container">
                <div class="newsletter-content">
                    <div class="newsletter-copy">
                        <span class="eyebrow" style="color: var(--gold);">The CRO Report</span>
                        <h2>Weekly intelligence for sales executives</h2>
                        <p>The job market data VPs and CROs actually need. Every Thursday.</p>
                        <ul>
                            <li>Market snapshot: roles, trends, what's changing</li>
                            <li>Who's moving: executive appointments analyzed</li>
                            <li>Company deep-dives: opportunities + red flags</li>
                            <li>Roles to skip (and why)</li>
                        </ul>
                    </div>
                    <div class="newsletter-embed">
                        <iframe src="https://croreport.substack.com/embed" width="400" height="280" style="border:1px solid #334155; background:white;" frameborder="0" scrolling="no"></iframe>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
        </div>
    </footer>
</body>
</html>'''

# Save homepage
with open(f'{SITE_DIR}/index.html', 'w') as f:
    f.write(html)

print(f"✅ Saved homepage: {SITE_DIR}/index.html")
