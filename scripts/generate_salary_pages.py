#!/usr/bin/env python3
"""
Generate salary benchmark pages for programmatic SEO
Creates pages like /salaries/vp-sales-nyc, /salaries/cro-remote, /salaries/series-b-c/, etc.

DATA SOURCE: master_jobs_database.csv (historical data for larger sample size)

CONTENT STRATEGY:
- Free: Basic salary ranges, top locations, seniority levels
- Gated: Company stage breakdowns, top paying companies (except top metros)
"""

import pandas as pd
from datetime import datetime
import os
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

DATA_DIR = 'data'
SITE_DIR = 'site'
SALARIES_DIR = f'{SITE_DIR}/salaries'
MASTER_DB = f'{DATA_DIR}/master_jobs_database.csv'

print("="*70)
print("[SALARY] GENERATING SALARY BENCHMARK PAGES")
print("="*70)

os.makedirs(SALARIES_DIR, exist_ok=True)

# Load master database for comprehensive salary data
if not os.path.exists(MASTER_DB):
    print(f"❌ Master database not found at {MASTER_DB}")
    exit(1)

df = pd.read_csv(MASTER_DB)
print(f"[FILE] Loaded {len(df)} jobs from {MASTER_DB}")

# Filter to jobs with salary data
df_salary = df[df['max_amount'].notna() & (df['max_amount'] > 0)].copy()
print(f"[DATA] {len(df_salary)} jobs with salary data")

update_date = datetime.now().strftime('%B %d, %Y')

def get_nav_bar():
    """Standard nav bar matching homepage"""
    return '''
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo">
                <img src="/assets/logo.jpg" alt="The CRO Report" class="logo-img">
                <span>The CRO Report</span>
            </a>
            <nav>
                <ul class="nav-links">
                    <li><a href="/jobs/">Jobs</a></li>
                    <li><a href="/salaries/">Salaries</a></li>
                    <li><a href="/tools/">Tools</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="/about/">About</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="https://croreport.substack.com/subscribe" class="btn-subscribe">Subscribe</a></li>
                </ul>
            </nav>
            <button class="mobile-menu-btn" aria-label="Menu">☰</button>
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
            <li><a href="/jobs/">Jobs</a></li>
            <li><a href="/salaries/">Salaries</a></li>
            <li><a href="/tools/">Tools</a></li>
            <li><a href="/insights/">Market Intel</a></li>
            <li><a href="/about/">About</a></li>
            <li><a href="/newsletter/">Newsletter</a></li>
        </ul>
        <a href="https://croreport.substack.com/subscribe" class="mobile-nav-subscribe">Subscribe</a>
    </nav>

    <script>
        (function() {
            const menuBtn = document.querySelector('.mobile-menu-btn');
            const closeBtn = document.querySelector('.mobile-nav-close');
            const overlay = document.querySelector('.mobile-nav-overlay');
            const mobileNav = document.querySelector('.mobile-nav');
            const mobileLinks = document.querySelectorAll('.mobile-nav-links a, .mobile-nav-subscribe');

            function openMenu() {
                mobileNav.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }

            function closeMenu() {
                mobileNav.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }

            menuBtn.addEventListener('click', openMenu);
            closeBtn.addEventListener('click', closeMenu);
            overlay.addEventListener('click', closeMenu);

            mobileLinks.forEach(link => {
                link.addEventListener('click', closeMenu);
            });
        })();
    </script>
'''

def get_nav_styles():
    """CSS for nav bar matching homepage"""
    return '''
        .site-header {
            background: white;
            padding: 12px 20px;
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            color: #1e3a5f;
            font-weight: 600;
        }
        .logo-img {
            height: 36px;
            width: auto;
            border-radius: 4px;
        }
        .nav-links {
            display: flex;
            list-style: none;
            gap: 24px;
            align-items: center;
            margin: 0;
            padding: 0;
        }
        .nav-links a {
            color: #475569;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .nav-links a:hover { color: #1e3a5f; }
        .btn-subscribe {
            background: #1e3a5f !important;
            color: white !important;
            padding: 8px 16px;
            border-radius: 6px;
        }
        .btn-subscribe:hover {
            background: #2d4a6f !important;
        }
        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #1e3a5f;
        }

        /* Mobile Navigation */
        .mobile-nav-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .mobile-nav-overlay.active {
            opacity: 1;
        }
        .mobile-nav {
            position: fixed;
            top: 0;
            right: -100%;
            width: 280px;
            max-width: 85%;
            height: 100vh;
            background: #fff;
            z-index: 1000;
            padding: 1.5rem;
            box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
            transition: right 0.3s ease;
            overflow-y: auto;
        }
        .mobile-nav.active {
            right: 0;
        }
        .mobile-nav-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .mobile-nav-header .logo-text {
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e3a5f;
        }
        .mobile-nav-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #64748b;
        }
        .mobile-nav-links {
            list-style: none;
            margin: 0 0 2rem 0;
            padding: 0;
        }
        .mobile-nav-links li {
            border-bottom: 1px solid #f1f5f9;
        }
        .mobile-nav-links a {
            display: block;
            padding: 1rem 0;
            font-size: 1rem;
            font-weight: 500;
            color: #475569;
            text-decoration: none;
        }
        .mobile-nav-subscribe {
            display: block;
            width: 100%;
            padding: 1rem;
            background: #1e3a5f;
            color: #fff;
            text-align: center;
            font-weight: 600;
            font-size: 1rem;
            border-radius: 8px;
            text-decoration: none;
        }

        @media (max-width: 768px) {
            .nav-links { display: none; }
            .mobile-menu-btn { display: block; }
            .mobile-nav-overlay { display: block; pointer-events: none; }
            .mobile-nav-overlay.active { pointer-events: auto; }
        }
'''

def create_salary_page(title, slug, df_subset, description, show_top_companies=True):
    """Generate a salary benchmark page"""
    
    if len(df_subset) < 3:
        return False  # Not enough data
    
    avg_min = df_subset['min_amount'].mean()
    avg_max = df_subset['max_amount'].mean()
    median_min = df_subset['min_amount'].median()
    median_max = df_subset['max_amount'].median()
    min_salary = df_subset['min_amount'].min()
    max_salary = df_subset['max_amount'].max()
    count = len(df_subset)
    
    # Top paying companies - only show if flag is True
    if show_top_companies:
        top_companies = df_subset.nlargest(5, 'max_amount')[['company', 'title', 'min_amount', 'max_amount']].to_dict('records')
        top_companies_html = f'''
        <section class="section">
            <h2>Top Paying Companies</h2>
            <div class="top-companies">
                {''.join([f"""
                <div class="company-row">
                    <div class="company-info">
                        <h3>{c['company']}</h3>
                        <p>{c['title']}</p>
                    </div>
                    <div class="company-salary">${c['min_amount']/1000:.0f}K - ${c['max_amount']/1000:.0f}K</div>
                </div>
                """ for c in top_companies])}
            </div>
        </section>
        '''
    else:
        top_companies_html = '''
        <section class="section gated-section">
            <h2>Top Paying Companies</h2>
            <p class="gated-message">Subscribe to see which companies are paying top dollar for this role.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn-small">Unlock Full Data →</a>
        </section>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Salary | The CRO Report</title>
    <meta name="description" content="{description} Based on {count} job postings. Updated {update_date}.">
    <link rel="canonical" href="https://thecroreport.com/salaries/{slug}/">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://thecroreport.com/salaries/{slug}/">
    <meta property="og:title" content="{title} Salary | The CRO Report">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title} Salary | The CRO Report">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">

        <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
        
        {get_nav_styles()}
        
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        .header .eyebrow {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #d97706;
            margin-bottom: 12px;
        }}
        .header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .header p {{ opacity: 0.9; max-width: 600px; margin: 0 auto; }}
        
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 20px; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: -40px auto 40px;
            position: relative;
            z-index: 10;
        }}
        @media (max-width: 600px) {{ .stats-grid {{ grid-template-columns: 1fr; }} }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .stat-card .label {{ font-size: 0.85rem; color: #64748b; margin-bottom: 8px; }}
        .stat-card .value {{ font-family: 'Fraunces', serif; font-size: 2rem; font-weight: 600; color: #1e3a5f; }}
        .stat-card .sublabel {{ font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }}
        
        .section {{ padding: 40px 0; }}
        .section h2 {{ font-family: 'Fraunces', serif; font-size: 1.5rem; color: #1e3a5f; margin-bottom: 20px; }}
        
        .range-visual {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 32px;
        }}
        .range-bar {{
            height: 24px;
            background: linear-gradient(90deg, #dbeafe 0%, #1e3a5f 50%, #0f172a 100%);
            border-radius: 12px;
            position: relative;
            margin: 20px 0;
        }}
        .range-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #64748b;
        }}
        .range-labels strong {{ color: #0f172a; }}
        
        .top-companies {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }}
        .company-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .company-row:last-child {{ border-bottom: none; }}
        .company-info h3 {{ font-size: 1rem; font-weight: 600; }}
        .company-info p {{ font-size: 0.85rem; color: #64748b; }}
        .company-salary {{
            font-weight: 600;
            color: #166534;
            background: #f0fdf4;
            padding: 6px 12px;
            border-radius: 6px;
        }}
        
        .gated-section {{
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
        }}
        .gated-message {{
            color: #64748b;
            margin-bottom: 16px;
        }}
        .cta-btn-small {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .cta-section {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 48px;
            border-radius: 16px;
            text-align: center;
            margin: 40px 0;
        }}
        .cta-section h2 {{ color: white; margin-bottom: 12px; }}
        .cta-section p {{ opacity: 0.9; margin-bottom: 24px; }}
        .cta-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 14px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer {{
            background: #1e3a5f;
            color: #94a3b8;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }}
        .footer a {{ color: #d97706; text-decoration: none; }}
        
        .breadcrumb {{
            padding: 16px 0;
            font-size: 0.85rem;
            color: #64748b;
        }}
        .breadcrumb a {{ color: #1e3a5f; text-decoration: none; }}
    </style>
</head>
<body>
    {get_nav_bar()}
    
    <div class="header">
        <div class="eyebrow">Salary Benchmarks</div>
        <h1>{title} Salary</h1>
        <p>{description}</p>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Average Range</div>
                <div class="value">${avg_min/1000:.0f}K - ${avg_max/1000:.0f}K</div>
                <div class="sublabel">Base salary</div>
            </div>
            <div class="stat-card">
                <div class="label">Median</div>
                <div class="value">${median_max/1000:.0f}K</div>
                <div class="sublabel">Maximum base</div>
            </div>
            <div class="stat-card">
                <div class="label">Sample Size</div>
                <div class="value">{count}</div>
                <div class="sublabel">Job postings</div>
            </div>
        </div>
        
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {title}
        </nav>
        
        <section class="section">
            <h2>Salary Range</h2>
            <div class="range-visual">
                <div class="range-labels">
                    <span>Minimum: <strong>${min_salary/1000:.0f}K</strong></span>
                    <span>Maximum: <strong>${max_salary/1000:.0f}K</strong></span>
                </div>
                <div class="range-bar"></div>
                <p style="font-size: 0.9rem; color: #64748b; margin-top: 16px;">
                    Based on {count} job postings with disclosed compensation. Updated {update_date}.
                </p>
            </div>
        </section>
        
        {top_companies_html}
        
        <div class="cta-section">
            <h2>Get Full Compensation Intelligence</h2>
            <p>Weekly analysis of compensation trends, red flags, and negotiation insights for VP Sales and CRO roles.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="/tools/">Tools</a> · <a href="/insights/">Market Intel</a> · <a href="/about/">About</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''

    # Create directory and save
    page_dir = f'{SALARIES_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    
    return True

# Generate pages by metro (if metro column exists)
if 'metro' in df_salary.columns:
    metros = ['New York', 'San Francisco', 'Boston', 'Chicago', 'Los Angeles', 'Seattle', 'Austin', 'Denver', 'Atlanta', 'Remote', 'Texas']
    metro_pages = []

    for metro in metros:
        df_metro = df_salary[df_salary['metro'] == metro]
        if len(df_metro) >= 3:
            slug = metro.lower().replace(' ', '-')
            title = f"VP Sales {metro}"
            desc = f"Current VP Sales and CRO salary data for {metro}."
            # Show top companies for top 4 metros only (free teaser)
            show_companies = metro in ['New York', 'San Francisco', 'Remote', 'Boston']
            if create_salary_page(title, slug, df_metro, desc, show_top_companies=show_companies):
                metro_pages.append({'title': title, 'slug': slug, 'count': len(df_metro), 'avg_min': df_metro['min_amount'].mean(), 'avg_max': df_metro['max_amount'].mean()})
                print(f"✅ Created: /salaries/{slug}/ ({len(df_metro)} roles)")
else:
    metro_pages = []
    print("[WARNING] Skipping metro pages - 'metro' column not found in data")

# Generate pages by seniority
seniorities = [('VP', 'vp-sales'), ('SVP', 'svp-sales'), ('C-Level', 'cro')]
seniority_pages = []

for sen, slug in seniorities:
    df_sen = df_salary[df_salary['seniority'] == sen]
    if len(df_sen) >= 3:
        title = f"{sen} Sales" if sen != 'C-Level' else "CRO / Chief Revenue Officer"
        desc = f"Current {title} salary benchmarks across all markets."
        if create_salary_page(title, slug, df_sen, desc, show_top_companies=True):
            seniority_pages.append({'title': title, 'slug': slug, 'count': len(df_sen), 'avg_min': df_sen['min_amount'].mean(), 'avg_max': df_sen['max_amount'].mean()})
            print(f"✅ Created: /salaries/{slug}/ ({len(df_sen)} roles)")

# Generate pages by company stage (if column exists) - GATED CONTENT
stage_pages = []
if 'company_stage' in df_salary.columns:
    stages = [
        ('Seed/Series A', 'seed-series-a'),
        ('Series A/B', 'series-a-b'),
        ('Series B/C', 'series-b-c'),
        ('Series C/D', 'series-c-d'),
        ('Late Stage', 'late-stage'),
        ('Enterprise/Public', 'enterprise-public')
    ]
    
    for stage, slug in stages:
        df_stage = df_salary[df_salary['company_stage'] == stage]
        if len(df_stage) >= 3:
            title = f"{stage} Company"
            desc = f"VP Sales and CRO salary benchmarks at {stage} companies."
            # Company stage pages are gated - no top companies shown
            if create_salary_page(title, slug, df_stage, desc, show_top_companies=False):
                stage_pages.append({'title': title, 'slug': slug, 'count': len(df_stage), 'avg_min': df_stage['min_amount'].mean(), 'avg_max': df_stage['max_amount'].mean()})
                print(f"✅ Created: /salaries/{slug}/ ({len(df_stage)} roles) [GATED]")
else:
    print("[WARNING] Skipping company stage pages - 'company_stage' column not found in data")

# Calculate overall stats for index page
overall_avg_min = df_salary['min_amount'].mean()
overall_avg_max = df_salary['max_amount'].mean()

# Pre-compute HTML sections to avoid f-string nesting issues
metro_cards_html = ''
for p in sorted(metro_pages, key=lambda x: -x['avg_max']):
    metro_cards_html += f'''
    <a href="{p['slug']}/" class="salary-card">
        <h3>{p['title']}</h3>
        <div class="range">${p['avg_min']/1000:.0f}K - ${p['avg_max']/1000:.0f}K avg</div>
        <div class="meta">{p['count']} roles with salary data</div>
    </a>
    '''

seniority_cards_html = ''
for p in sorted(seniority_pages, key=lambda x: -x['avg_max']):
    seniority_cards_html += f'''
    <a href="{p['slug']}/" class="salary-card">
        <h3>{p['title']}</h3>
        <div class="range">${p['avg_min']/1000:.0f}K - ${p['avg_max']/1000:.0f}K avg</div>
        <div class="meta">{p['count']} roles with salary data</div>
    </a>
    '''

if stage_pages:
    stage_cards_html = ''
    for p in sorted(stage_pages, key=lambda x: -x['avg_max']):
        stage_cards_html += f'''
        <a href="{p['slug']}/" class="salary-card">
            <h3>{p['title']}</h3>
            <div class="range">${p['avg_min']/1000:.0f}K - ${p['avg_max']/1000:.0f}K avg</div>
            <div class="meta">{p['count']} roles</div>
        </a>
        '''
else:
    stage_cards_html = '''
    <div class="salary-card gated">
        <h3>Seed / Series A</h3>
        <div class="range">$XXX avg max</div>
        <div class="lock">Subscribe for company stage data</div>
    </div>
    <div class="salary-card gated">
        <h3>Series B/C</h3>
        <div class="range">$XXX avg max</div>
        <div class="lock">Subscribe for company stage data</div>
    </div>
    <div class="salary-card gated">
        <h3>Enterprise / Public</h3>
        <div class="range">$XXX avg max</div>
        <div class="lock">Subscribe for company stage data</div>
    </div>
    '''

# Generate index page
index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Executive Salary Benchmarks | The CRO Report</title>
    <meta name="description" content="2026 VP Sales and CRO salary benchmarks based on {len(df_salary)} actual job postings. See compensation by location (NYC, SF, Remote), seniority level, and company stage.">
    <link rel="canonical" href="https://thecroreport.com/salaries/">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://thecroreport.com/salaries/">
    <meta property="og:title" content="Sales Executive Salary Benchmarks">
    <meta property="og:description" content="VP Sales and CRO salary data by location, seniority, and company stage.">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Sales Executive Salary Benchmarks">
    <meta name="twitter:description" content="VP Sales and CRO salary data by location, seniority, and company stage.">
    <meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">

    <!-- Dataset Schema for Google Dataset Search -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "VP Sales and CRO Salary Benchmarks {datetime.now().year}",
        "description": "Salary data for VP Sales, SVP Sales, and CRO positions based on {len(df_salary)} job postings with disclosed compensation ranges. Updated weekly.",
        "url": "https://thecroreport.com/salaries/",
        "keywords": ["VP Sales salary", "CRO salary", "sales executive compensation", "sales leadership salary"],
        "creator": {{
            "@type": "Organization",
            "name": "The CRO Report",
            "url": "https://thecroreport.com"
        }},
        "dateModified": "{datetime.now().strftime('%Y-%m-%d')}",
        "temporalCoverage": "{datetime.now().year}",
        "spatialCoverage": "United States",
        "variableMeasured": [
            {{
                "@type": "PropertyValue",
                "name": "Base Salary Range",
                "description": "Minimum and maximum base salary from job postings"
            }},
            {{
                "@type": "PropertyValue",
                "name": "Location",
                "description": "Geographic location including NYC, San Francisco, Boston, Remote"
            }},
            {{
                "@type": "PropertyValue",
                "name": "Seniority Level",
                "description": "VP Sales, SVP Sales, or CRO"
            }}
        ]
    }}
    </script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
        
        {get_nav_styles()}
        
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        .header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .header p {{ opacity: 0.9; }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        
        .stats-row {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 24px;
            flex-wrap: wrap;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-family: 'Fraunces', serif;
            font-size: 1.75rem;
            font-weight: 600;
            color: #d97706;
        }}
        .stat-label {{
            font-size: 0.85rem;
            opacity: 0.8;
        }}
        
        h2 {{ font-family: 'Fraunces', serif; font-size: 1.5rem; color: #1e3a5f; margin: 40px 0 20px; }}
        
        .salary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        
        .salary-card {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
        }}
        .salary-card:hover {{
            border-color: #1e3a5f;
            box-shadow: 0 4px 16px rgba(30,58,95,0.12);
            transform: translateY(-2px);
        }}
        .salary-card h3 {{ font-size: 1.1rem; margin-bottom: 8px; color: #1e3a5f; }}
        .salary-card .range {{ font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 600; color: #166534; }}
        .salary-card .meta {{ font-size: 0.85rem; color: #64748b; margin-top: 8px; }}
        
        .salary-card.gated {{
            background: #f8fafc;
            border-style: dashed;
        }}
        .salary-card.gated .range {{
            color: #94a3b8;
            filter: blur(4px);
        }}
        .salary-card.gated .lock {{
            font-size: 0.75rem;
            color: #d97706;
            margin-top: 8px;
        }}
        
        .cta-inline {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin: 40px 0;
        }}
        .cta-inline h3 {{ font-family: 'Fraunces', serif; margin-bottom: 12px; }}
        .cta-inline p {{ opacity: 0.9; margin-bottom: 16px; }}
        .cta-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer {{
            background: #1e3a5f;
            color: #94a3b8;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }}
        .footer a {{ color: #d97706; text-decoration: none; }}
    </style>
</head>
<body>
    {get_nav_bar()}
    
    <div class="header">
        <h1>Sales Executive Salary Benchmarks</h1>
        <p>Based on {len(df_salary)} job postings with disclosed compensation</p>
        <div class="stats-row">
            <div class="stat">
                <div class="stat-value">${overall_avg_min/1000:.0f}K - ${overall_avg_max/1000:.0f}K</div>
                <div class="stat-label">Average Range</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(df_salary)}</div>
                <div class="stat-label">Roles Analyzed</div>
            </div>
        </div>
        <p style="margin-top: 16px; font-size: 0.85rem; opacity: 0.7;">Updated {update_date}</p>
    </div>

    <div class="container">
        <div style="background: #f1f5f9; border-radius: 12px; padding: 32px; margin-bottom: 40px;">
            <p style="color: #475569; margin: 0; font-size: 1.05rem; line-height: 1.7;">
                Our sales executive salary benchmarks track compensation across {len(df_salary)} job postings with disclosed ranges.
                The current average for VP Sales and CRO roles sits between <strong>${overall_avg_min/1000:.0f}K - ${overall_avg_max/1000:.0f}K</strong> base,
                though this varies significantly by location, seniority, and company stage.
            </p>
        </div>

        <h2>VP Sales Salary by Location: NYC, San Francisco, Seattle & More</h2>
        <div class="salary-grid">
            {metro_cards_html}
        </div>
        
        <h2>Sales Executive Salary by Seniority: VP, SVP & CRO</h2>
        <div class="salary-grid">
            {seniority_cards_html}
        </div>

        <h2>Sales Leadership Salary by Company Stage</h2>
        <p style="color: #64748b; margin-bottom: 16px;">How does compensation vary from Seed to Enterprise?</p>
        <div class="salary-grid">
            {stage_cards_html}
        </div>

        <div class="methodology-section" style="background: #f1f5f9; border-radius: 12px; padding: 32px; margin: 40px 0;">
            <h2 style="font-family: 'Fraunces', serif; font-size: 1.3rem; color: #1e3a5f; margin-bottom: 16px;">How We Calculate These Benchmarks</h2>
            <p style="color: #475569; margin-bottom: 12px;">
                Unlike survey-based compensation reports that rely on self-reporting (which typically skews 10-15% high),
                our salary data comes from actual job postings with disclosed ranges. When companies post "$250K-$350K base," that's what we report.
            </p>
            <p style="color: #475569; margin-bottom: 12px;">
                <strong>Data source:</strong> {len(df_salary)} VP Sales, SVP Sales, and CRO job postings from our master database, updated weekly.
            </p>
            <p style="color: #475569; margin-bottom: 0;">
                <strong>What we track:</strong> Base salary ranges (min/max), geographic location, seniority level, and company stage where available.
                OTE estimates assume standard 30-50% variable compensation for revenue roles.
            </p>
        </div>

        <div class="cta-inline">
            <h3>Get Weekly Compensation Intelligence</h3>
            <p>Full salary breakdowns, company stage analysis, and negotiation insights every Thursday.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe Free →</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="/tools/">Tools</a> · <a href="/insights/">Market Intel</a> · <a href="/about/">About</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''

with open(f'{SALARIES_DIR}/index.html', 'w') as f:
    f.write(index_html)

print(f"\n✅ Created salary index: /salaries/")
print(f"[DATA] Generated {len(metro_pages)} location pages")
print(f"[DATA] Generated {len(seniority_pages)} seniority pages")
print(f"[DATA] Generated {len(stage_pages)} company stage pages")
print(f"[STATS] Total salary data points: {len(df_salary)} jobs from master database")
