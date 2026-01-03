#!/usr/bin/env python3
"""
Generate company pages for programmatic SEO
Creates pages like /companies/deloitte/, /companies/salesforce/, etc.
Only generates pages for companies with 2+ open roles.
"""

import pandas as pd
from datetime import datetime
import glob
import os
import re
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

DATA_DIR = 'data'
SITE_DIR = 'site'
COMPANIES_DIR = f'{SITE_DIR}/companies'

print("="*70)
print("🏢 GENERATING COMPANY PAGES")
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

# Create companies directory
os.makedirs(COMPANIES_DIR, exist_ok=True)

def slugify(text):
    """Convert company name to URL-safe slug"""
    if pd.isna(text):
        return None
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:60] if slug else None

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
    job_id = str(job.get('id', ''))[-6:] if job.get('id') else ''
    job_url = f"/jobs/{slug}-{job_id}/" if job_id else "#"
    
    # Remote badge
    remote_badge = '<span class="badge remote">Remote</span>' if job.get('is_remote') else ''
    
    # Seniority badge
    seniority = job.get('seniority', '')
    seniority_badge = f'<span class="badge seniority">{seniority}</span>' if seniority else ''
    
    return f'''
    <div class="job-card">
        <div class="job-header">
            <h3><a href="{job_url}">{title}</a></h3>
        </div>
        <div class="job-meta">
            <span class="location">📍 {location}</span>
            <span class="salary">💰 {salary}</span>
            {remote_badge}
            {seniority_badge}
        </div>
    </div>
    '''

def generate_company_page(company_name, company_df):
    """Generate a page for a specific company"""
    
    slug = slugify(company_name)
    if not slug:
        return False
    
    job_count = len(company_df)
    
    # Sort by salary (highest first)
    if 'max_amount' in company_df.columns:
        company_df = company_df.sort_values('max_amount', ascending=False, na_position='last')
    
    # Generate job cards
    job_cards = '\n'.join(generate_job_card(row) for _, row in company_df.iterrows())
    
    # Salary stats if available
    salary_df = company_df[company_df['max_amount'].notna() & (company_df['max_amount'] > 0)]
    if len(salary_df) >= 1:
        avg_min = salary_df['min_amount'].mean()
        avg_max = salary_df['max_amount'].mean()
        salary_stats = f'''
        <div class="salary-summary">
            <h3>💰 Compensation at {company_name}</h3>
            <p>Based on {len(salary_df)} role{'s' if len(salary_df) > 1 else ''} with disclosed compensation:</p>
            <div class="salary-range">
                <strong>Average Range:</strong> ${avg_min/1000:.0f}K - ${avg_max/1000:.0f}K base
            </div>
        </div>
        '''
    else:
        salary_stats = ''
    
    # Location summary
    locations = company_df['location'].dropna().unique()
    location_list = ', '.join(locations[:5])
    if len(locations) > 5:
        location_list += f' and {len(locations) - 5} more'
    
    # Seniority breakdown
    seniority_counts = company_df['seniority'].value_counts().to_dict()
    seniority_summary = ' | '.join([f"{k}: {v}" for k, v in seniority_counts.items() if pd.notna(k)])
    
    # Check if remote
    remote_count = company_df['is_remote'].sum() if 'is_remote' in company_df.columns else 0
    remote_text = f"{remote_count} remote" if remote_count > 0 else ""
    
    description = f"{company_name} has {job_count} open VP Sales and executive sales positions. {seniority_summary}."
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} VP Sales & CRO Jobs | The CRO Report</title>
    <meta name="description" content="{description} Updated {update_date}.">
    <meta name="keywords" content="{company_name} VP Sales jobs, {company_name} CRO jobs, {company_name} sales executive careers">
    <link rel="canonical" href="https://thecroreport.com/companies/{slug}/">
    
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
        
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        
        .company-info {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .company-info h3 {{ color: #1e3a5f; margin-bottom: 12px; }}
        .company-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .stat-item {{
            text-align: center;
            padding: 12px;
            background: #f8fafc;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e3a5f;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 4px;
        }}
        
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
        .badge.seniority {{
            background: #e0e7ff;
            color: #3730a3;
        }}
        
        .breadcrumb {{
            margin-bottom: 24px;
            font-size: 0.9rem;
        }}
        .breadcrumb a {{
            color: #d97706;
            text-decoration: none;
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
        <div class="eyebrow">Company Profile</div>
        <h1>{company_name}</h1>
        <p>Executive Sales Openings</p>
        <div class="count">{job_count} Current Opening{'s' if job_count > 1 else ''}</div>
    </div>
    
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/jobs/">Jobs</a> → <a href="/companies/">Companies</a> → {company_name}
        </nav>
        
        <div class="company-info">
            <h3>🏢 {company_name} Sales Leadership Roles</h3>
            <p>Currently hiring for {job_count} VP Sales and executive sales position{'s' if job_count > 1 else ''}.</p>
            <div class="company-stats">
                <div class="stat-item">
                    <div class="stat-value">{job_count}</div>
                    <div class="stat-label">Open Roles</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{remote_count}</div>
                    <div class="stat-label">Remote</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(salary_df)}</div>
                    <div class="stat-label">With Salary</div>
                </div>
            </div>
        </div>
        
        {salary_stats}
        
        <h2 style="margin-bottom: 20px; color: #1e3a5f;">Open Positions</h2>
        
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
        <p>© 2025 The CRO Report | <a href="/jobs/">All Jobs</a> | <a href="/salaries/">Salary Data</a> | <a href="/insights/">Market Insights</a></p>
    </footer>
</body>
</html>'''
    
    # Create directory and save
    page_dir = f"{COMPANIES_DIR}/{slug}"
    os.makedirs(page_dir, exist_ok=True)
    
    with open(f"{page_dir}/index.html", 'w') as f:
        f.write(html)
    
    return True


def generate_companies_index(companies_data):
    """Generate the main /companies/ index page"""
    
    # Sort by job count
    sorted_companies = sorted(companies_data, key=lambda x: x['count'], reverse=True)
    
    company_cards = ''
    for comp in sorted_companies:
        company_cards += f'''
        <a href="/companies/{comp['slug']}/" class="company-card">
            <div class="company-name">{comp['name']}</div>
            <div class="company-count">{comp['count']} open role{'s' if comp['count'] > 1 else ''}</div>
        </a>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Companies Hiring VP Sales & CROs | The CRO Report</title>
    <meta name="description" content="Browse {len(sorted_companies)} companies currently hiring VP Sales and CRO positions. Updated {update_date}.">
    <link rel="canonical" href="https://thecroreport.com/companies/">
    
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
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        
        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        
        .company-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            display: block;
        }}
        .company-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .company-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e3a5f;
            margin-bottom: 4px;
        }}
        .company-count {{
            font-size: 0.9rem;
            color: #64748b;
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
        <div class="eyebrow">Browse by Company</div>
        <h1>Companies Hiring Sales Executives</h1>
        <p>{len(sorted_companies)} companies with multiple VP Sales and CRO openings</p>
    </div>
    
    <div class="container">
        <div class="companies-grid">
            {company_cards}
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 The CRO Report | <a href="/jobs/">All Jobs</a> | <a href="/salaries/">Salary Data</a> | <a href="/insights/">Market Insights</a></p>
    </footer>
</body>
</html>'''
    
    with open(f"{COMPANIES_DIR}/index.html", 'w') as f:
        f.write(html)
    
    print(f"  ✅ /companies/ index ({len(sorted_companies)} companies)")


# Find companies with 2+ roles
company_counts = df['company'].value_counts()
companies_with_multiple = company_counts[company_counts >= 2]

print(f"\n📊 Found {len(companies_with_multiple)} companies with 2+ open roles")

# Generate pages for each company
companies_data = []
success_count = 0

for company_name, job_count in companies_with_multiple.items():
    if pd.isna(company_name):
        continue
    
    company_df = df[df['company'] == company_name].copy()
    slug = slugify(company_name)
    
    if slug and generate_company_page(company_name, company_df):
        print(f"  ✅ /companies/{slug}/ ({job_count} jobs)")
        companies_data.append({
            'name': company_name,
            'slug': slug,
            'count': job_count
        })
        success_count += 1

# Generate index page
if companies_data:
    generate_companies_index(companies_data)

print(f"\n{'='*70}")
print(f"✅ Generated {success_count} company pages + index")
print(f"{'='*70}")
