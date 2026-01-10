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

from templates import (
    get_html_head,
    get_nav_html,
    get_footer_html,
    slugify,
    format_salary,
    is_remote,
    BASE_URL,
    CSS_VARIABLES,
    CSS_NAV,
    CSS_LAYOUT,
    CSS_CARDS,
    CSS_CTA,
    CSS_FOOTER,
    TRACKING_CODE,
)

DATA_DIR = 'data'
SITE_DIR = 'site'
COMPANIES_DIR = f'{SITE_DIR}/companies'

print("="*70)
print("GENERATING COMPANY PAGES")
print("="*70)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not files:
    print("No enriched data found")
    exit(1)

latest_file = max(files)
df = pd.read_csv(latest_file)
print(f"Loaded {len(df)} jobs from {latest_file}")

update_date = datetime.now().strftime('%B %d, %Y')

# Create companies directory
os.makedirs(COMPANIES_DIR, exist_ok=True)


# =============================================================================
# COMPANY-SPECIFIC CSS
# =============================================================================

COMPANY_CSS = '''
    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, var(--navy-medium) 0%, var(--navy-hover) 100%);
        color: white;
        padding: 60px 20px;
        text-align: center;
    }
    .hero-header .eyebrow {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--gold-dark);
        margin-bottom: 12px;
    }
    .hero-header h1 {
        font-family: 'Fraunces', serif;
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .hero-header p { opacity: 0.9; max-width: 600px; margin: 0 auto; }
    .hero-header .count {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 8px 16px;
        border-radius: 20px;
        margin-top: 16px;
        font-size: 0.9rem;
    }

    /* Company Info Box */
    .company-info {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .company-info h3 { color: var(--navy-medium); margin-bottom: 12px; }
    .company-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin-top: 16px;
    }
    .stat-item {
        text-align: center;
        padding: 12px;
        background: var(--gray-50);
        border-radius: 8px;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--navy-medium);
    }
    .stat-label-small {
        font-size: 0.8rem;
        color: var(--gray-500);
        margin-top: 4px;
    }

    /* Salary Summary */
    .salary-summary {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .salary-summary h3 { color: var(--navy-medium); margin-bottom: 12px; }
    .salary-range {
        font-size: 1.25rem;
        color: var(--green-dark);
        margin-top: 8px;
    }

    /* Job Cards */
    .job-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .job-header h3 {
        font-size: 1.1rem;
        margin-bottom: 4px;
    }
    .job-header h3 a {
        color: var(--navy-medium);
        text-decoration: none;
    }
    .job-header h3 a:hover {
        color: var(--gold-dark);
    }
    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 12px;
        font-size: 0.85rem;
        color: var(--gray-600);
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge.remote {
        background: #dcfce7;
        color: var(--green-dark);
    }
    .badge.seniority {
        background: #e0e7ff;
        color: #3730a3;
    }

    /* Company Grid for Index */
    .companies-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
    }
    .company-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-decoration: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: transform 0.2s, box-shadow 0.2s;
        display: block;
    }
    .company-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .company-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--navy-medium);
        margin-bottom: 4px;
    }
    .company-count {
        font-size: 0.9rem;
        color: var(--gray-500);
    }

    /* Footer override for dark style */
    .footer {
        background: var(--navy-medium);
        color: #94a3b8;
        padding: 40px 20px;
        text-align: center;
        margin-top: 60px;
    }
    .footer a { color: var(--gold-dark); text-decoration: none; }
'''


def get_company_styles():
    """Get combined CSS for company pages"""
    return f'''
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {COMPANY_CSS}

        /* Add Fraunces font */
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap');
    </style>
'''


def generate_job_card(job):
    """Generate HTML for a single job card"""
    title = job.get('title', 'Unknown Title')
    company = job.get('company', 'Unknown Company')
    location = job.get('location', 'Location not specified')

    # Salary display
    salary = format_salary(job.get('min_amount'), job.get('max_amount'))
    if not salary:
        salary = "Salary not disclosed"

    # Generate slug for job detail page
    slug = f"{company}-{title}".lower()
    slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in slug)
    slug = '-'.join(filter(None, slug.split('-')))[:60]
    job_id = str(job.get('id', ''))[-6:] if job.get('id') else ''
    job_url = f"/jobs/{slug}-{job_id}/" if job_id else "#"

    # Remote badge
    remote_badge = '<span class="badge remote">Remote</span>' if is_remote(job) else ''

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


def generate_company_stats(company_df, company_name):
    """Generate stats section for a company"""
    job_count = len(company_df)
    remote_count = company_df['is_remote'].sum() if 'is_remote' in company_df.columns else 0
    salary_df = company_df[company_df['max_amount'].notna() & (company_df['max_amount'] > 0)]

    return f'''
        <div class="company-info">
            <h3>🏢 {company_name} Sales Leadership Roles</h3>
            <p>Currently hiring for {job_count} VP Sales and executive sales position{'s' if job_count > 1 else ''}.</p>
            <div class="company-stats">
                <div class="stat-item">
                    <div class="stat-value">{job_count}</div>
                    <div class="stat-label-small">Open Roles</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{remote_count}</div>
                    <div class="stat-label-small">Remote</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(salary_df)}</div>
                    <div class="stat-label-small">With Salary</div>
                </div>
            </div>
        </div>
    '''


def generate_salary_summary(company_df, company_name):
    """Generate salary summary section if data available"""
    salary_df = company_df[company_df['max_amount'].notna() & (company_df['max_amount'] > 0)]
    if len(salary_df) < 1:
        return ''

    avg_min = salary_df['min_amount'].mean()
    avg_max = salary_df['max_amount'].mean()

    return f'''
        <div class="salary-summary">
            <h3>💰 Compensation at {company_name}</h3>
            <p>Based on {len(salary_df)} role{'s' if len(salary_df) > 1 else ''} with disclosed compensation:</p>
            <div class="salary-range">
                <strong>Average Range:</strong> ${avg_min/1000:.0f}K - ${avg_max/1000:.0f}K base
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

    # Seniority breakdown
    seniority_counts = company_df['seniority'].value_counts().to_dict()
    seniority_summary = ' | '.join([f"{k}: {v}" for k, v in seniority_counts.items() if pd.notna(k)])

    description = f"{company_name} has {job_count} open VP Sales and executive sales positions. {seniority_summary}."

    html = get_html_head(
        f"{company_name} VP Sales & CRO Jobs",
        f"{description} Updated {update_date}.",
        f"companies/{slug}/",
        include_styles=False
    )
    html += get_company_styles()
    html += get_nav_html()

    html += f'''
    <div class="hero-header">
        <div class="eyebrow">Company Profile</div>
        <h1>{company_name}</h1>
        <p>Executive Sales Openings</p>
        <div class="count">{job_count} Current Opening{'s' if job_count > 1 else ''}</div>
    </div>

    <div class="container" style="max-width: 900px; padding: 40px 20px;">
        <nav class="breadcrumb">
            <a href="/">Home</a> → <a href="/jobs/">Jobs</a> → <a href="/companies/">Companies</a> → {company_name}
        </nav>

        {generate_company_stats(company_df, company_name)}

        {generate_salary_summary(company_df, company_name)}

        <h2 style="margin-bottom: 20px; color: var(--navy-medium);">Open Positions</h2>

        <div class="job-list">
            {job_cards}
        </div>

        <div class="cta-box">
            <h3>Get Weekly Market Intelligence</h3>
            <p>Join 500+ sales executives getting compensation data, executive movements, and opportunity analysis.</p>
            <a href="https://thecroreport.substack.com" class="btn btn-gold">Subscribe Free →</a>
        </div>

        <p style="text-align: center; color: var(--gray-500); font-size: 0.85rem; margin-top: 32px;">Last updated: {update_date}</p>
    </div>

    <footer class="footer">
        <p>&copy; 2025 <a href="/">The CRO Report</a> | <a href="/jobs/">Jobs</a> | <a href="/salaries/">Salaries</a> | <a href="/tools/">Tools</a> | <a href="/insights/">Market Intel</a> | <a href="/about/">About</a> | <a href="https://croreport.substack.com">Newsletter</a></p>
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

    html = get_html_head(
        "Companies Hiring VP Sales & CROs",
        f"Browse {len(sorted_companies)} companies currently hiring VP Sales and CRO positions. Updated {update_date}.",
        "companies/",
        include_styles=False
    )
    html += get_company_styles()
    html += get_nav_html()

    html += f'''
    <div class="hero-header">
        <div class="eyebrow">Browse by Company</div>
        <h1>Companies Hiring Sales Executives</h1>
        <p>{len(sorted_companies)} companies with multiple VP Sales and CRO openings</p>
    </div>

    <div class="container" style="max-width: 1000px; padding: 40px 20px;">
        <div class="companies-grid">
            {company_cards}
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2025 <a href="/">The CRO Report</a> | <a href="/jobs/">Jobs</a> | <a href="/salaries/">Salaries</a> | <a href="/tools/">Tools</a> | <a href="/insights/">Market Intel</a> | <a href="/about/">About</a> | <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''

    with open(f"{COMPANIES_DIR}/index.html", 'w') as f:
        f.write(html)

    print(f"  /companies/ index ({len(sorted_companies)} companies)")


# Find companies with 2+ roles
company_counts = df['company'].value_counts()
companies_with_multiple = company_counts[company_counts >= 2]

print(f"\nFound {len(companies_with_multiple)} companies with 2+ open roles")

# Generate pages for each company
companies_data = []
success_count = 0

for company_name, job_count in companies_with_multiple.items():
    if pd.isna(company_name):
        continue

    company_df = df[df['company'] == company_name].copy()
    slug = slugify(company_name)

    if slug and generate_company_page(company_name, company_df):
        print(f"  /companies/{slug}/ ({job_count} jobs)")
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
print(f"Generated {success_count} company pages + index")
print(f"{'='*70}")
