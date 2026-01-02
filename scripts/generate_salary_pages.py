#!/usr/bin/env python3
"""
Generate salary benchmark pages for programmatic SEO
Creates pages like /salaries/vp-sales-nyc, /salaries/cro-remote, etc.
"""

import pandas as pd
from datetime import datetime
import glob
import os
import json

DATA_DIR = 'data'
SITE_DIR = 'site'
SALARIES_DIR = f'{SITE_DIR}/salaries'

print("="*70)
print("💰 GENERATING SALARY BENCHMARK PAGES")
print("="*70)

os.makedirs(SALARIES_DIR, exist_ok=True)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not files:
    print("❌ No enriched data found")
    exit(1)

latest_file = max(files)
df = pd.read_csv(latest_file)
print(f"📂 Loaded {len(df)} jobs from {latest_file}")

# Filter to jobs with salary data
df_salary = df[df['max_amount'].notna() & (df['max_amount'] > 0)].copy()
print(f"📊 {len(df_salary)} jobs with salary data")

update_date = datetime.now().strftime('%B %d, %Y')

def create_salary_page(title, slug, df_subset, description):
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
    
    # Top paying companies
    top_companies = df_subset.nlargest(5, 'max_amount')[['company', 'title', 'min_amount', 'max_amount']].to_dict('records')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Salary | The CRO Report</title>
    <meta name="description" content="{description} Based on {count} current job postings. Updated {update_date}.">
    <link rel="canonical" href="https://romelikethecity.github.io/croreport/salaries/{slug}/">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
        
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
    <header class="header">
        <div class="eyebrow">Salary Benchmarks</div>
        <h1>{title} Salary</h1>
        <p>{description}</p>
    </header>
    
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
                <div class="sublabel">Current postings</div>
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
        
        <div class="cta-section">
            <h2>Get Full Compensation Intelligence</h2>
            <p>Weekly analysis of compensation trends, red flags, and negotiation insights for VP Sales and CRO roles.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''
    
    # Create directory and save
    page_dir = f'{SALARIES_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    
    return True

# Generate pages by metro
metros = ['New York', 'San Francisco', 'Boston', 'Chicago', 'Los Angeles', 'Seattle', 'Austin', 'Denver', 'Atlanta', 'Remote', 'Texas']
metro_pages = []

for metro in metros:
    df_metro = df_salary[df_salary['metro'] == metro]
    if len(df_metro) >= 3:
        slug = metro.lower().replace(' ', '-')
        title = f"VP Sales {metro}"
        desc = f"Current VP Sales and CRO salary data for {metro}."
        if create_salary_page(title, slug, df_metro, desc):
            metro_pages.append({'title': title, 'slug': slug, 'count': len(df_metro), 'avg_max': df_metro['max_amount'].mean()})
            print(f"✅ Created: /salaries/{slug}/ ({len(df_metro)} roles)")

# Generate pages by seniority
seniorities = [('VP', 'vp-sales'), ('SVP', 'svp-sales'), ('C-Level', 'cro')]
seniority_pages = []

for sen, slug in seniorities:
    df_sen = df_salary[df_salary['seniority'] == sen]
    if len(df_sen) >= 3:
        title = f"{sen} Sales" if sen != 'C-Level' else "CRO / Chief Revenue Officer"
        desc = f"Current {title} salary benchmarks across all markets."
        if create_salary_page(title, slug, df_sen, desc):
            seniority_pages.append({'title': title, 'slug': slug, 'count': len(df_sen), 'avg_max': df_sen['max_amount'].mean()})
            print(f"✅ Created: /salaries/{slug}/ ({len(df_sen)} roles)")

# Generate index page
index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Executive Salary Benchmarks | The CRO Report</title>
    <meta name="description" content="VP Sales and CRO salary data by location and seniority. Based on {len(df_salary)} current job postings with disclosed compensation.">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        .header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .header p {{ opacity: 0.9; }}
        
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        
        h2 {{ font-family: 'Fraunces', serif; font-size: 1.5rem; color: #1e3a5f; margin: 32px 0 16px; }}
        
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
    <header class="header">
        <h1>Sales Executive Salary Benchmarks</h1>
        <p>Based on {len(df_salary)} current job postings · Updated {update_date}</p>
    </header>
    
    <div class="container">
        <h2>By Location</h2>
        <div class="salary-grid">
            {''.join([f"""
            <a href="{p['slug']}/" class="salary-card">
                <h3>{p['title']}</h3>
                <div class="range">${p['avg_max']/1000:.0f}K avg max</div>
                <div class="meta">{p['count']} roles with salary data</div>
            </a>
            """ for p in sorted(metro_pages, key=lambda x: -x['avg_max'])])}
        </div>
        
        <h2>By Seniority</h2>
        <div class="salary-grid">
            {''.join([f"""
            <a href="{p['slug']}/" class="salary-card">
                <h3>{p['title']}</h3>
                <div class="range">${p['avg_max']/1000:.0f}K avg max</div>
                <div class="meta">{p['count']} roles with salary data</div>
            </a>
            """ for p in sorted(seniority_pages, key=lambda x: -x['avg_max'])])}
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''

with open(f'{SALARIES_DIR}/index.html', 'w') as f:
    f.write(index_html)

print(f"\n✅ Created salary index: /salaries/")
print(f"📊 Generated {len(metro_pages) + len(seniority_pages)} salary pages")
