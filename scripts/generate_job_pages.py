#!/usr/bin/env python3
"""
Generate individual job pages for programmatic SEO
Creates pages like /jobs/acme-corp-vp-sales/ for each job posting
Target: 150+ pages per week, each targeting "[Company] [Role] job"
"""

import pandas as pd
from datetime import datetime
import glob
import os
import re
import hashlib

DATA_DIR = 'data'
SITE_DIR = 'site'
JOBS_DIR = f'{SITE_DIR}/jobs'

print("="*70)
print("📄 GENERATING INDIVIDUAL JOB PAGES")
print("="*70)

os.makedirs(JOBS_DIR, exist_ok=True)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not files:
    print("❌ No enriched data found")
    exit(1)

latest_file = max(files)
df = pd.read_csv(latest_file)
print(f"📂 Loaded {len(df)} jobs from {latest_file}")

update_date = datetime.now().strftime('%B %d, %Y')

def slugify(text):
    """Convert text to URL-friendly slug"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]

def create_job_page(job, idx):
    """Generate an individual job page"""
    
    company = str(job.get('company', 'Unknown'))
    title = str(job.get('title', 'Sales Executive'))
    location = str(job.get('location', ''))
    
    # Create unique slug
    slug = f"{slugify(company)}-{slugify(title)}"
    if not slug or len(slug) < 5:
        slug = f"job-{idx}"
    
    # Add hash suffix for uniqueness
    hash_suffix = hashlib.md5(f"{company}{title}{location}".encode()).hexdigest()[:6]
    slug = f"{slug}-{hash_suffix}"
    
    # Format salary
    min_sal = job.get('min_amount')
    max_sal = job.get('max_amount')
    if pd.notna(min_sal) and pd.notna(max_sal):
        salary_display = f"${int(min_sal):,} - ${int(max_sal):,}"
        salary_short = f"${int(min_sal)//1000}K-${int(max_sal)//1000}K"
    elif pd.notna(max_sal):
        salary_display = f"Up to ${int(max_sal):,}"
        salary_short = f"Up to ${int(max_sal)//1000}K"
    else:
        salary_display = "Not disclosed"
        salary_short = ""
    
    seniority = job.get('seniority', 'VP')
    is_remote = job.get('is_remote') == True or str(job.get('is_remote')).lower() == 'true'
    job_url = job.get('job_url_direct', '#')
    
    meta_desc = f"{title} at {company}"
    if location:
        meta_desc += f" in {location}"
    if salary_short:
        meta_desc += f". {salary_short} base salary."
    meta_desc += " Apply now."
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} at {company} | The CRO Report</title>
    <meta name="description" content="{meta_desc[:155]}">
    <link rel="canonical" href="https://romelikethecity.github.io/croreport/jobs/{slug}/">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 40px 20px;
        }}
        .header .container {{ max-width: 800px; margin: 0 auto; }}
        .breadcrumb {{ font-size: 0.85rem; opacity: 0.8; margin-bottom: 16px; }}
        .breadcrumb a {{ color: white; text-decoration: none; }}
        .header h1 {{ font-family: 'Fraunces', serif; font-size: 2rem; margin-bottom: 8px; }}
        .header .company {{ font-size: 1.25rem; opacity: 0.9; }}
        
        .container {{ max-width: 800px; margin: 0 auto; padding: 0 20px; }}
        
        .job-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 20px;
        }}
        .meta-item {{
            background: rgba(255,255,255,0.15);
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        .salary {{ background: #d97706; font-weight: 600; }}
        
        .content {{ padding: 40px 0; }}
        
        .apply-box {{
            background: white;
            border: 2px solid #1e3a5f;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-bottom: 32px;
        }}
        .apply-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 16px 48px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            margin-top: 16px;
            transition: background 0.2s;
        }}
        .apply-btn:hover {{ background: #b45309; }}
        
        .details {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 32px;
        }}
        .details h2 {{
            font-family: 'Fraunces', serif;
            font-size: 1.25rem;
            color: #1e3a5f;
            margin-bottom: 16px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .detail-row:last-child {{ border-bottom: none; }}
        .detail-label {{ color: #64748b; }}
        .detail-value {{ font-weight: 500; }}
        
        .cta-box {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
        }}
        .cta-box h2 {{ color: white; font-family: 'Fraunces', serif; margin-bottom: 12px; }}
        .cta-box p {{ opacity: 0.9; margin-bottom: 20px; }}
        .cta-link {{
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
    <header class="header">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">The CRO Report</a> → <a href="/jobs/">Jobs</a> → {company}
            </nav>
            <h1>{title}</h1>
            <div class="company">{company}</div>
            <div class="job-meta">
                {f'<span class="meta-item salary">{salary_display}</span>' if salary_display != "Not disclosed" else ''}
                {f'<span class="meta-item">📍 {location}</span>' if location else ''}
                {'<span class="meta-item">🏠 Remote</span>' if is_remote else ''}
                {f'<span class="meta-item">{seniority}</span>' if seniority else ''}
            </div>
        </div>
    </header>
    
    <div class="content">
        <div class="container">
            <div class="apply-box">
                <p>Interested in this {seniority} role at {company}?</p>
                <a href="{job_url}" class="apply-btn" target="_blank" rel="noopener">Apply Now →</a>
            </div>
            
            <div class="details">
                <h2>Role Details</h2>
                <div class="detail-row">
                    <span class="detail-label">Company</span>
                    <span class="detail-value">{company}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Title</span>
                    <span class="detail-value">{title}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">{location if location else 'Not specified'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Seniority</span>
                    <span class="detail-value">{seniority}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Base Salary</span>
                    <span class="detail-value">{salary_display}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Remote</span>
                    <span class="detail-value">{'Yes' if is_remote else 'No'}</span>
                </div>
            </div>
            
            <div class="cta-box">
                <h2>Want the Full Analysis?</h2>
                <p>Get red flags, predecessor intel, and "should you apply?" assessments for roles like this every week.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-link">Subscribe to The CRO Report →</a>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">All Jobs</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
        <p style="margin-top: 8px; font-size: 0.85rem;">Updated {update_date}</p>
    </footer>
</body>
</html>'''
    
    # Create directory and save
    page_dir = f'{JOBS_DIR}/{slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)
    
    return slug

# Generate individual job pages
print(f"\nGenerating individual job pages...")
job_slugs = []
for idx, row in df.iterrows():
    if pd.notna(row.get('title')) and pd.notna(row.get('company')):
        slug = create_job_page(row, idx)
        job_slugs.append(slug)
        if len(job_slugs) % 50 == 0:
            print(f"  Generated {len(job_slugs)} pages...")

print(f"\n✅ Generated {len(job_slugs)} individual job pages")

# Save job index for linking
with open(f'{DATA_DIR}/job_slugs.txt', 'w') as f:
    f.write('\n'.join(job_slugs))

print(f"✅ Saved job slug index")
