#!/usr/bin/env python3
"""
Generate category/filter pages for programmatic SEO
Creates pages like /jobs/vp-sales/, /jobs/remote/, /jobs/new-york/, etc.
"""

import pandas as pd
from datetime import datetime
import glob
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
JOBS_DIR = f'{SITE_DIR}/jobs'

print("="*70)
print("📁 GENERATING CATEGORY JOB PAGES")
print("="*70)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not files:
    print("❌ No enriched data found")
    exit(1)

latest_file = max(files)
df = pd.read_csv(latest_file)
print(f"📂 Loaded {len(df)} jobs from {latest_file}")

update_date = datetime.now().strftime('%B %d, %Y')

# Category definitions
CATEGORIES = {
    # By Seniority
    'vp-sales': {
        'title': 'VP Sales Jobs',
        'h1': 'VP of Sales Jobs',
        'description': 'Find VP of Sales and Vice President of Sales positions at top companies.',
        'filter': lambda df: df[df['seniority'] == 'VP'],
        'keywords': 'VP Sales jobs, Vice President of Sales positions, VP Sales careers'
    },
    'svp-sales': {
        'title': 'SVP Sales Jobs',
        'h1': 'SVP of Sales Jobs',
        'description': 'Senior Vice President of Sales opportunities at leading companies.',
        'filter': lambda df: df[df['seniority'] == 'SVP'],
        'keywords': 'SVP Sales jobs, Senior Vice President Sales, SVP Sales positions'
    },
    'cro-jobs': {
        'title': 'CRO Jobs',
        'h1': 'Chief Revenue Officer Jobs',
        'description': 'Chief Revenue Officer and CRO positions at growth companies.',
        'filter': lambda df: df[df['seniority'] == 'C-Level'],
        'keywords': 'CRO jobs, Chief Revenue Officer positions, CRO careers'
    },
    'evp-sales': {
        'title': 'EVP Sales Jobs',
        'h1': 'EVP of Sales Jobs',
        'description': 'Executive Vice President of Sales roles at enterprise companies.',
        'filter': lambda df: df[df['seniority'] == 'EVP'],
        'keywords': 'EVP Sales jobs, Executive Vice President Sales positions'
    },
    
    # By Location
    'remote': {
        'title': 'Remote VP Sales & CRO Jobs',
        'h1': 'Remote Executive Sales Jobs',
        'description': 'Work-from-home VP Sales and CRO positions. Remote executive sales opportunities.',
        'filter': lambda df: df[df['is_remote'] == True],
        'keywords': 'remote VP Sales jobs, remote CRO jobs, work from home sales executive'
    },
    'new-york': {
        'title': 'VP Sales & CRO Jobs in New York',
        'h1': 'New York Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in New York City and the NYC metro area.',
        'filter': lambda df: df[df['location'].str.contains('New York|NYC|Manhattan|Brooklyn', case=False, na=False)],
        'keywords': 'VP Sales jobs NYC, CRO jobs New York, sales executive jobs Manhattan'
    },
    'san-francisco': {
        'title': 'VP Sales & CRO Jobs in San Francisco',
        'h1': 'San Francisco Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in San Francisco and the Bay Area.',
        'filter': lambda df: df[df['location'].str.contains('San Francisco|SF|Bay Area|Palo Alto|Mountain View|San Jose', case=False, na=False)],
        'keywords': 'VP Sales jobs San Francisco, CRO jobs Bay Area, sales executive jobs SF'
    },
    'boston': {
        'title': 'VP Sales & CRO Jobs in Boston',
        'h1': 'Boston Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Boston and the Greater Boston area.',
        'filter': lambda df: df[df['location'].str.contains('Boston|Cambridge, MA|Massachusetts', case=False, na=False)],
        'keywords': 'VP Sales jobs Boston, CRO jobs Massachusetts, sales executive jobs Boston'
    },
    'los-angeles': {
        'title': 'VP Sales & CRO Jobs in Los Angeles',
        'h1': 'Los Angeles Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Los Angeles and Southern California.',
        'filter': lambda df: df[df['location'].str.contains('Los Angeles|LA|Santa Monica|Irvine|Orange County', case=False, na=False)],
        'keywords': 'VP Sales jobs Los Angeles, CRO jobs LA, sales executive jobs Southern California'
    },
    'chicago': {
        'title': 'VP Sales & CRO Jobs in Chicago',
        'h1': 'Chicago Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Chicago and the Midwest.',
        'filter': lambda df: df[df['location'].str.contains('Chicago|Illinois|IL', case=False, na=False)],
        'keywords': 'VP Sales jobs Chicago, CRO jobs Illinois, sales executive jobs Midwest'
    },
    'texas': {
        'title': 'VP Sales & CRO Jobs in Texas',
        'h1': 'Texas Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Texas including Austin, Dallas, and Houston.',
        'filter': lambda df: df[df['location'].str.contains('Texas|TX|Austin|Dallas|Houston|San Antonio', case=False, na=False)],
        'keywords': 'VP Sales jobs Texas, CRO jobs Austin, sales executive jobs Dallas Houston'
    },
    'atlanta': {
        'title': 'VP Sales & CRO Jobs in Atlanta',
        'h1': 'Atlanta Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Atlanta and Georgia.',
        'filter': lambda df: df[df['location'].str.contains('Atlanta|Georgia|GA', case=False, na=False)],
        'keywords': 'VP Sales jobs Atlanta, CRO jobs Georgia, sales executive jobs Atlanta'
    },
    'seattle': {
        'title': 'VP Sales & CRO Jobs in Seattle',
        'h1': 'Seattle Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Seattle and the Pacific Northwest.',
        'filter': lambda df: df[df['location'].str.contains('Seattle|Washington|WA|Portland', case=False, na=False)],
        'keywords': 'VP Sales jobs Seattle, CRO jobs Washington, sales executive jobs Pacific Northwest'
    },
    'denver': {
        'title': 'VP Sales & CRO Jobs in Denver',
        'h1': 'Denver Executive Sales Jobs',
        'description': 'VP Sales and CRO positions in Denver and Colorado.',
        'filter': lambda df: df[df['location'].str.contains('Denver|Colorado|CO|Boulder', case=False, na=False)],
        'keywords': 'VP Sales jobs Denver, CRO jobs Colorado, sales executive jobs Denver'
    },
    
    # By Company Stage
    'startup-jobs': {
        'title': 'VP Sales Jobs at Startups',
        'h1': 'Startup VP Sales & CRO Jobs',
        'description': 'VP Sales and CRO positions at seed, Series A, and Series B startups.',
        'filter': lambda df: df[df['company_stage'].isin(['Seed/Series A', 'Series A/B', 'Series B/C'])] if 'company_stage' in df.columns else df.head(0),
        'keywords': 'startup VP Sales jobs, Series A CRO jobs, early stage sales executive'
    },
    'growth-stage': {
        'title': 'VP Sales Jobs at Growth Companies',
        'h1': 'Growth Stage VP Sales & CRO Jobs',
        'description': 'VP Sales and CRO positions at Series C, D, and late-stage growth companies.',
        'filter': lambda df: df[df['company_stage'].isin(['Series C/D', 'Late Stage'])] if 'company_stage' in df.columns else df.head(0),
        'keywords': 'growth stage VP Sales jobs, Series C CRO jobs, scale-up sales executive'
    },
    'enterprise-jobs': {
        'title': 'VP Sales Jobs at Enterprise Companies',
        'h1': 'Enterprise VP Sales & CRO Jobs',
        'description': 'VP Sales and CRO positions at public companies and large enterprises.',
        'filter': lambda df: df[df['company_stage'] == 'Enterprise/Public'] if 'company_stage' in df.columns else df.head(0),
        'keywords': 'enterprise VP Sales jobs, public company CRO jobs, Fortune 500 sales executive'
    },
    
    # By Industry (based on company or title keywords)
    'saas-sales': {
        'title': 'SaaS VP Sales & CRO Jobs',
        'h1': 'SaaS Sales Executive Jobs',
        'description': 'VP Sales and CRO positions at SaaS and software companies.',
        'filter': lambda df: df[df['description'].str.contains('SaaS|software|platform|cloud', case=False, na=False) | df['title'].str.contains('SaaS|Software', case=False, na=False)],
        'keywords': 'SaaS VP Sales jobs, software CRO jobs, B2B SaaS sales executive'
    },
    'healthcare-sales': {
        'title': 'Healthcare VP Sales & CRO Jobs',
        'h1': 'Healthcare Sales Executive Jobs',
        'description': 'VP Sales and CRO positions in healthcare, healthtech, and life sciences.',
        'filter': lambda df: df[df['description'].str.contains('healthcare|health care|medical|pharma|biotech|life science', case=False, na=False) | df['company'].str.contains('Health|Medical|Pharma|Bio', case=False, na=False)],
        'keywords': 'healthcare VP Sales jobs, healthtech CRO jobs, medical sales executive'
    },
    'fintech-sales': {
        'title': 'Fintech VP Sales & CRO Jobs',
        'h1': 'Fintech Sales Executive Jobs',
        'description': 'VP Sales and CRO positions at fintech and financial services companies.',
        'filter': lambda df: df[df['description'].str.contains('fintech|financial|banking|payments|insurance', case=False, na=False) | df['company'].str.contains('Bank|Financial|Capital', case=False, na=False)],
        'keywords': 'fintech VP Sales jobs, financial services CRO jobs, banking sales executive'
    },
    
    # Special Categories
    'high-paying': {
        'title': 'High-Paying VP Sales & CRO Jobs',
        'h1': 'Highest Paying Sales Executive Jobs',
        'description': 'VP Sales and CRO positions paying $300K+ base salary.',
        'filter': lambda df: df[df['max_amount'] >= 300000],
        'keywords': '$300K VP Sales jobs, high paying CRO jobs, top sales executive salaries'
    },
    'with-salary': {
        'title': 'VP Sales & CRO Jobs with Disclosed Salary',
        'h1': 'Executive Sales Jobs with Salary Transparency',
        'description': 'VP Sales and CRO positions with disclosed compensation ranges.',
        'filter': lambda df: df[df['max_amount'].notna() & (df['max_amount'] > 0)],
        'keywords': 'VP Sales jobs with salary, CRO jobs compensation disclosed'
    },
}


def generate_job_card(job):
    """Generate HTML for a single job card"""
    title = job.get('title', 'Unknown Title')
    company = job.get('company', 'Unknown Company')
    location = job.get('location', 'Location not specified')
    
    # Salary display
    min_sal = job.get('min_amount')
    max_sal = job.get('max_amount')
    if pd.notna(max_sal) and max_sal > 0:
        if pd.notna(min_sal) and min_sal > 0:
            salary = f"${min_sal/1000:.0f}K - ${max_sal/1000:.0f}K"
        else:
            salary = f"Up to ${max_sal/1000:.0f}K"
    else:
        salary = "Salary not disclosed"
    
    # Generate slug for job detail page
    slug = f"{company}-{title}".lower()
    slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in slug)
    slug = '-'.join(filter(None, slug.split('-')))[:60]
    job_id = job.get('id', '')[-6:] if job.get('id') else ''
    job_url = f"/jobs/{slug}-{job_id}/" if job_id else "#"
    
    # Remote badge
    remote_badge = '<span class="badge remote">Remote</span>' if job.get('is_remote') else ''
    
    return f'''
    <div class="job-card">
        <div class="job-header">
            <h3><a href="{job_url}">{title}</a></h3>
            <div class="company">{company}</div>
        </div>
        <div class="job-meta">
            <span class="location">📍 {location}</span>
            <span class="salary">💰 {salary}</span>
            {remote_badge}
        </div>
    </div>
    '''


def generate_category_page(slug, config, df):
    """Generate a category page with filtered jobs"""
    
    try:
        filtered_df = config['filter'](df)
    except Exception as e:
        print(f"  ⚠️  Filter error for {slug}: {e}")
        return False
    
    if len(filtered_df) < 1:
        print(f"  ⚠️  No jobs for {slug}, skipping")
        return False
    
    # Sort by salary (highest first) then by date
    if 'max_amount' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('max_amount', ascending=False, na_position='last')
    
    job_count = len(filtered_df)
    
    # Generate job cards
    job_cards = '\n'.join(generate_job_card(row) for _, row in filtered_df.head(100).iterrows())
    
    # Salary stats if available
    salary_df = filtered_df[filtered_df['max_amount'].notna() & (filtered_df['max_amount'] > 0)]
    if len(salary_df) >= 3:
        avg_min = salary_df['min_amount'].mean()
        avg_max = salary_df['max_amount'].mean()
        salary_stats = f'''
        <div class="salary-summary">
            <h3>💰 Salary Overview</h3>
            <p>Based on {len(salary_df)} jobs with disclosed compensation:</p>
            <div class="salary-range">
                <strong>Average Range:</strong> ${avg_min/1000:.0f}K - ${avg_max/1000:.0f}K base
            </div>
        </div>
        '''
    else:
        salary_stats = ''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['title']} | The CRO Report</title>
    <meta name="description" content="{config['description']} {job_count} current openings. Updated {update_date}.">
    <meta name="keywords" content="{config['keywords']}">
    <link rel="canonical" href="https://thecroreport.com/jobs/{slug}/">

    <!-- Favicons -->
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
        .hero-header .count {{ 
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 16px;
            font-size: 0.9rem;
        }}
        
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
        .header .count {{ 
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 16px;
            font-size: 0.9rem;
        }}
        
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        
        .salary-summary {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .salary-summary h3 {{ color: #1e3a5f; margin-bottom: 12px; }}
        .salary-range {{ 
            font-size: 1.25rem;
            color: #059669;
            margin-top: 8px;
        }}
        
        .job-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .job-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .job-header h3 {{ 
            font-size: 1.1rem;
            margin-bottom: 4px;
        }}
        .job-header h3 a {{
            color: #1e3a5f;
            text-decoration: none;
        }}
        .job-header h3 a:hover {{
            color: #d97706;
        }}
        .company {{ color: #64748b; font-size: 0.95rem; }}
        .job-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 12px;
            font-size: 0.85rem;
            color: #475569;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge.remote {{
            background: #dcfce7;
            color: #166534;
        }}
        
        .breadcrumb {{
            margin-bottom: 24px;
            font-size: 0.9rem;
        }}
        .breadcrumb a {{
            color: #d97706;
            text-decoration: none;
        }}
        
        .category-nav {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .category-nav h3 {{
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .category-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .category-links a {{
            display: inline-block;
            padding: 6px 12px;
            background: #f1f5f9;
            color: #475569;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.85rem;
            transition: background 0.2s;
        }}
        .category-links a:hover {{
            background: #e2e8f0;
            color: #1e3a5f;
        }}
        .category-links a.active {{
            background: #1e3a5f;
            color: white;
        }}
        
        .cta-box {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin: 40px 0;
        }}
        .cta-box h2 {{ font-family: 'Fraunces', serif; margin-bottom: 12px; }}
        .cta-box p {{ opacity: 0.9; margin-bottom: 20px; }}
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
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .mobile-nav-overlay.active {{ opacity: 1; }}
        .mobile-nav {{
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
        }}
        .mobile-nav.active {{ right: 0; }}
        .mobile-nav-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .mobile-nav-header .logo-text {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e3a5f;
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
            margin: 0 0 2rem 0;
            padding: 0;
        }}
        .mobile-nav-links li {{ border-bottom: 1px solid #f1f5f9; }}
        .mobile-nav-links a {{
            display: block;
            padding: 1rem 0;
            font-size: 1rem;
            font-weight: 500;
            color: #475569;
            text-decoration: none;
        }}
        .mobile-nav-subscribe {{
            display: block;
            width: 100%;
            padding: 1rem;
            background: #1e3a5f;
            color: #fff;
            text-align: center;
            font-weight: 600;
            border-radius: 8px;
            text-decoration: none;
        }}

        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .mobile-menu-btn {{ display: block; }}
            .mobile-nav-overlay {{ display: block; pointer-events: none; }}
            .mobile-nav-overlay.active {{ pointer-events: auto; }}
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
                    <li><a href="/tools/">Tools</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="/about/">About</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="https://thecroreport.substack.com" class="btn-subscribe">Subscribe</a></li>
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
            <li><a href="/jobs/">Jobs</a></li>
            <li><a href="/salaries/">Salaries</a></li>
            <li><a href="/tools/">Tools</a></li>
            <li><a href="/insights/">Market Intel</a></li>
            <li><a href="/about/">About</a></li>
            <li><a href="/newsletter/">Newsletter</a></li>
        </ul>
        <a href="https://thecroreport.substack.com" class="mobile-nav-subscribe">Subscribe</a>
    </nav>

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
    
    <div class="hero-header">
        <div class="eyebrow">Executive Sales Jobs</div>
        <h1>{config['h1']}</h1>
        <p>{config['description']}</p>
        <div class="count">{job_count} Current Openings</div>
    </div>
    
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/jobs/">Jobs</a> → {config['title']}
        </nav>
        
        <nav class="category-nav">
            <h3>Browse by Category</h3>
            <div class="category-links">
                <a href="/jobs/">All Jobs</a>
                <a href="/jobs/vp-sales/" {"class='active'" if slug == 'vp-sales' else ""}>VP Sales</a>
                <a href="/jobs/cro-jobs/" {"class='active'" if slug == 'cro-jobs' else ""}>CRO</a>
                <a href="/jobs/remote/" {"class='active'" if slug == 'remote' else ""}>Remote</a>
                <a href="/jobs/new-york/" {"class='active'" if slug == 'new-york' else ""}>New York</a>
                <a href="/jobs/san-francisco/" {"class='active'" if slug == 'san-francisco' else ""}>San Francisco</a>
                <a href="/jobs/high-paying/" {"class='active'" if slug == 'high-paying' else ""}>$300K+</a>
            </div>
        </nav>
        
        {salary_stats}
        
        <div class="job-list">
            {job_cards}
        </div>
        
        <div class="cta-box">
            <h2>Get Weekly Market Intelligence</h2>
            <p>Join 500+ sales executives getting compensation data, executive movements, and opportunity analysis.</p>
            <a href="https://thecroreport.substack.com" class="cta-btn">Subscribe Free</a>
        </div>
        
        <p class="update-date">Last updated: {update_date}</p>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> | <a href="/jobs/">Jobs</a> | <a href="/salaries/">Salaries</a> | <a href="/tools/">Tools</a> | <a href="/insights/">Market Intel</a> | <a href="/about/">About</a> | <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''
    
    # Create directory and save
    page_dir = f"{JOBS_DIR}/{slug}"
    os.makedirs(page_dir, exist_ok=True)
    
    with open(f"{page_dir}/index.html", 'w') as f:
        f.write(html)
    
    return True


# Generate all category pages
print(f"\n📄 Generating {len(CATEGORIES)} category pages...")

success_count = 0
for slug, config in CATEGORIES.items():
    if generate_category_page(slug, config, df):
        filtered_count = len(config['filter'](df))
        print(f"  ✅ /jobs/{slug}/ ({filtered_count} jobs)")
        success_count += 1

print(f"\n{'='*70}")
print(f"✅ Generated {success_count} category pages")
print(f"{'='*70}")
