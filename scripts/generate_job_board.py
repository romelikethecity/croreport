#!/usr/bin/env python3
"""
Generate Job Board Page for The CRO Report
Produces a clean, compact job listing page with separate filter boxes

SEO FEATURES:
- Tracking code included
- Open Graph tags for social sharing
- Twitter card tags
- Canonical URL
"""

import os
import glob
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

BASE_URL = 'https://thecroreport.com'

def get_latest_jobs_file():
    """Find the most recent executive_sales_jobs CSV file"""
    pattern = "data/executive_sales_jobs_*.csv"
    files = glob.glob(pattern)
    if not files:
        # Fallback to master database
        if os.path.exists("data/master_jobs_database.csv"):
            return "data/master_jobs_database.csv"
        return None
    return max(files, key=os.path.getctime)

def calculate_stats(df):
    """Calculate summary statistics for the hero section"""
    total_jobs = len(df)
    
    # Count remote jobs
    remote_count = 0
    if 'is_remote' in df.columns:
        remote_count = df['is_remote'].sum() if df['is_remote'].dtype == bool else (df['is_remote'] == True).sum()
    elif 'location' in df.columns:
        remote_count = df['location'].str.lower().str.contains('remote', na=False).sum()
    
    # Calculate average max salary
    avg_max_salary = 0
    if 'max_amount' in df.columns:
        salary_data = pd.to_numeric(df['max_amount'], errors='coerce')
        salary_data = salary_data[salary_data > 0]
        if len(salary_data) > 0:
            avg_max_salary = int(salary_data.mean() / 1000)  # Convert to K
    
    return {
        'total': total_jobs,
        'remote': remote_count,
        'avg_salary': avg_max_salary
    }

def format_salary(row):
    """Format salary display"""
    min_sal = row.get('min_amount', 0)
    max_sal = row.get('max_amount', 0)
    
    try:
        min_sal = float(min_sal) if pd.notna(min_sal) else 0
        max_sal = float(max_sal) if pd.notna(max_sal) else 0
    except:
        return ""
    
    if min_sal > 0 and max_sal > 0:
        return f"${int(min_sal/1000)}K - ${int(max_sal/1000)}K"
    elif max_sal > 0:
        return f"Up to ${int(max_sal/1000)}K"
    elif min_sal > 0:
        return f"${int(min_sal/1000)}K+"
    return ""

def is_remote(row):
    """Check if job is remote"""
    if 'is_remote' in row and row['is_remote']:
        return True
    if 'location' in row and pd.notna(row['location']):
        return 'remote' in str(row['location']).lower()
    return False

def generate_job_card(row):
    """Generate HTML for a single job card"""
    title = row.get('title', 'Untitled Position')
    company = row.get('company', 'Company')
    location = row.get('location', '')
    job_url = row.get('job_url_direct', row.get('job_url', '#'))
    salary = format_salary(row)
    remote = is_remote(row)
    
    # Clean up location display
    location_display = str(location) if pd.notna(location) else ''
    location_display = location_display.replace(', US', '').replace(', USA', '').strip()
    
    # Skip if company is nan
    if company == 'nan' or pd.isna(company):
        company = 'Company'
    
    remote_badge = '<span class="badge-remote">Remote</span>' if remote else ''
    salary_display = f'<span class="salary">{salary}</span>' if salary else ''
    
    return f'''
                <div class="job-card">
                    <div class="job-info">
                        <h3 class="job-title">{title}</h3>
                        <p class="job-company">{company}</p>
                        <div class="job-meta">
                            <span class="job-location">{location_display}</span>
                            {remote_badge}
                            {salary_display}
                        </div>
                    </div>
                    <a href="{job_url}" target="_blank" rel="noopener" class="btn-apply">Apply &rarr;</a>
                </div>
    '''

def generate_filter_boxes(df):
    """Generate sidebar filter box sections"""
    
    # BY ROLE - based on seniority or title patterns
    roles = ['VP of Sales', 'CRO', 'SVP Sales']
    
    # BY LOCATION - top metros
    locations = []
    if 'metro' in df.columns:
        locations = df['metro'].dropna().value_counts().head(5).index.tolist()
    elif 'location' in df.columns:
        # Extract common locations
        common_locations = ['Remote', 'New York', 'San Francisco', 'Boston', 'Chicago']
        for loc in common_locations:
            if df['location'].str.contains(loc, case=False, na=False).any():
                locations.append(loc)
    
    if not locations:
        locations = ['Remote', 'New York', 'San Francisco', 'Boston', 'Chicago']
    
    role_links = '\n                '.join([f'<a href="/jobs/?role={r.lower().replace(" ", "-")}">{r}</a>' for r in roles])
    location_links = '\n                '.join([f'<a href="/jobs/?location={l.lower().replace(" ", "-")}">{l}</a>' for l in locations])
    
    return f'''
            <div class="filter-box">
                <h4>By Role</h4>
                {role_links}
            </div>
            
            <div class="filter-box">
                <h4>By Location</h4>
                {location_links}
            </div>
            
            <div class="filter-box">
                <h4>By Salary</h4>
                <a href="/jobs/?salary=200k">$200K+</a>
                <a href="/jobs/?salary=300k">$300K+</a>
            </div>
    '''

def generate_html(df, stats):
    """Generate the complete HTML page"""
    
    # Generate job cards
    job_cards = []
    for _, row in df.iterrows():
        job_cards.append(generate_job_card(row))
    
    job_cards_html = '\n'.join(job_cards)
    filter_boxes_html = generate_filter_boxes(df)
    
    current_year = datetime.now().year
    update_date = datetime.now().strftime('%B %d, %Y')
    
    # SEO metadata
    page_title = f"VP Sales & CRO Jobs - {stats['total']} Open Roles | The CRO Report"
    meta_desc = f"Browse {stats['total']} VP Sales, CRO, and executive sales positions. {stats['remote']} remote roles available. Average max salary ${stats['avg_salary']}K. Updated weekly."
    canonical_url = f"{BASE_URL}/jobs/"
    og_title = f"{stats['total']} VP Sales & CRO Jobs"
    og_description = f"Executive sales positions with salary data. {stats['remote']} remote, ${stats['avg_salary']}K avg max salary."
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>{page_title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical_url}">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_description}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{og_title}">
    <meta name="twitter:description" content="{og_description}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: #f7fafc;
        }}
        
        /* Navigation */
        .nav {{
            background: #fff;
            padding: 1rem 2rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #1a365d;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .nav-logo img {{
            height: 36px;
            border-radius: 4px;
        }}
        
        .nav-links {{
            display: flex;
            gap: 2rem;
            align-items: center;
        }}
        
        .nav-links a {{
            color: #4a5568;
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 500;
            transition: color 0.2s;
        }}
        
        .nav-links a:hover {{
            color: #1a365d;
        }}
        
        .btn-subscribe {{
            background: #1a365d;
            color: #fff !important;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
        }}
        
        .btn-subscribe:hover {{
            background: #2d4a73;
        }}
        
        /* Hero Section */
        .hero {{
            background: #1a365d;
            color: #fff;
            padding: 2.5rem 2rem;
        }}
        
        .hero-content {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .hero-eyebrow {{
            color: #d69e2e;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}
        
        .hero h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }}
        
        .hero-tagline {{
            color: #a0aec0;
            font-size: 1rem;
            margin-bottom: 1.25rem;
        }}
        
        .hero-stats {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .hero-stat {{
            font-size: 0.95rem;
        }}
        
        /* Main Layout */
        .main-container {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: 1fr 280px;
            gap: 2rem;
        }}
        
        @media (max-width: 900px) {{
            .main-container {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                order: -1;
            }}
            .nav-links {{
                display: none;
            }}
        }}
        
        /* Job Cards Container */
        .jobs-container {{
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 0;
        }}
        
        .jobs-list {{
            display: flex;
            flex-direction: column;
            gap: 0;
        }}
        
        .job-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .job-card:last-child {{
            border-bottom: none;
        }}
        
        .job-info {{
            flex: 1;
        }}
        
        .job-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 0.25rem;
        }}
        
        .job-company {{
            color: #718096;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }}
        
        .job-meta {{
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .job-location {{
            color: #4a5568;
            font-size: 0.875rem;
        }}
        
        .badge-remote {{
            background: #fef3c7;
            color: #92400e;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .salary {{
            color: #059669;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .btn-apply {{
            background: #fff;
            color: #1a365d;
            border: 1.5px solid #1a365d;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        
        .btn-apply:hover {{
            background: #1a365d;
            color: #fff;
        }}
        
        /* Sidebar */
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        /* Filter Boxes */
        .filter-box {{
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1.25rem;
        }}
        
        .filter-box h4 {{
            color: #718096;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
        }}
        
        .filter-box a {{
            display: block;
            color: #1a365d;
            text-decoration: none;
            font-size: 0.95rem;
            padding: 0.35rem 0;
            transition: color 0.2s;
        }}
        
        .filter-box a:hover {{
            color: #d69e2e;
        }}
        
        /* CTA Box */
        .cta-box {{
            background: #1a365d;
            color: #fff;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .cta-box h4 {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .cta-box p {{
            font-size: 0.875rem;
            color: #a0aec0;
            margin-bottom: 1rem;
        }}
        
        .cta-box .btn-cta {{
            display: inline-block;
            background: #d69e2e;
            color: #fff;
            padding: 0.6rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s;
        }}
        
        .cta-box .btn-cta:hover {{
            background: #b7791f;
        }}
        
        /* Footer */
        .footer {{
            background: #fff;
            padding: 2rem;
            text-align: center;
            color: #718096;
            font-size: 0.875rem;
            margin-top: 2rem;
            border-top: 1px solid #e2e8f0;
        }}
        
        .footer a {{
            color: #1a365d;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">
            <img src="/assets/logo.jpg" alt="The CRO Report">
            The CRO Report
        </a>
        <div class="nav-links">
            <a href="/jobs/">Jobs</a>
            <a href="/salaries/">Salaries</a>
            <a href="/insights/">Market Intel</a>
            <a href="/newsletter/">Newsletter</a>
            <a href="https://croreport.substack.com/subscribe" class="btn-subscribe">Subscribe</a>
        </div>
    </nav>
    
    <section class="hero">
        <div class="hero-content">
            <p class="hero-eyebrow">Executive Sales Careers</p>
            <h1>Sales Leadership Jobs</h1>
            <p class="hero-tagline">VP Sales, CRO, and executive roles at companies worth working for.</p>
            <div class="hero-stats">
                <span class="hero-stat"><strong>{stats['total']}</strong> open roles</span>
                <span class="hero-stat"><strong>{stats['remote']}</strong> remote</span>
                <span class="hero-stat"><strong>${stats['avg_salary']}K</strong> avg max salary</span>
            </div>
        </div>
    </section>
    
    <main class="main-container">
        <div class="jobs-container">
            <div class="jobs-list">
{job_cards_html}
            </div>
        </div>
        
        <aside class="sidebar">
{filter_boxes_html}
            
            <div class="cta-box">
                <h4>Weekly Job Alerts</h4>
                <p>New roles delivered every Thursday.</p>
                <a href="https://croreport.substack.com/subscribe" class="btn-cta">Subscribe Free</a>
            </div>
        </aside>
    </main>
    
    <footer class="footer">
        <p>&copy; {current_year} The CRO Report. <a href="https://croreport.substack.com">Subscribe to the Newsletter</a></p>
        <p style="margin-top: 8px; font-size: 0.8rem; color: #94a3b8;">Updated {update_date}</p>
    </footer>
</body>
</html>
'''
    return html


def main():
    """Main entry point"""
    # Find the jobs data file
    jobs_file = get_latest_jobs_file()
    
    if not jobs_file:
        print("Error: No jobs data file found")
        return
    
    print(f"Reading jobs from: {jobs_file}")
    
    # Load the data
    df = pd.read_csv(jobs_file)
    print(f"Loaded {len(df)} jobs")
    
    # Calculate stats
    stats = calculate_stats(df)
    print(f"Stats: {stats['total']} total, {stats['remote']} remote, ${stats['avg_salary']}K avg")
    
    # Generate HTML
    html = generate_html(df, stats)
    
    # Ensure output directory exists
    os.makedirs("site/jobs", exist_ok=True)
    
    # Write the file
    output_path = "site/jobs/index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated: {output_path}")
    print(f"\n📊 SEO Features Added:")
    print(f"   - Tracking code (GA4 + Clarity)")
    print(f"   - Open Graph tags")
    print(f"   - Twitter card tags")
    print(f"   - Canonical URL")


if __name__ == "__main__":
    main()
