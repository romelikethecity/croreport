#!/usr/bin/env python3
"""
Generate individual job pages for programmatic SEO
Creates pages like /jobs/acme-corp-vp-sales/ for each job posting
Target: 150+ pages per week, each targeting "[Company] [Role] job"

SEO FEATURES:
- Correct canonical URLs (thecroreport.com)
- Salary/location in title tags
- Open Graph tags for LinkedIn shares
- Twitter card tags
- JobPosting JSON-LD schema for rich results
"""

import pandas as pd
from datetime import datetime
import glob
import os
import re
import hashlib
import json
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
BASE_URL = 'https://thecroreport.com'

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
iso_date = datetime.now().strftime('%Y-%m-%d')

def slugify(text):
    """Convert text to URL-friendly slug"""
    if pd.isna(text):
        return ''
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]

def escape_html(text):
    """Escape HTML special characters"""
    if pd.isna(text):
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def escape_json(text):
    """Escape text for JSON"""
    if pd.isna(text):
        return ''
    return str(text).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

def create_job_page(job, idx):
    """Generate an individual job page with full SEO optimization"""
    
    company = str(job.get('company', 'Unknown'))
    title = str(job.get('title', 'Sales Executive'))
    location = str(job.get('location', '')) if pd.notna(job.get('location')) else ''
    
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
    if pd.notna(min_sal) and pd.notna(max_sal) and float(min_sal) > 0 and float(max_sal) > 0:
        salary_display = f"${int(min_sal):,} - ${int(max_sal):,}"
        salary_short = f"${int(min_sal)//1000}K-${int(max_sal)//1000}K"
        salary_schema_min = int(min_sal)
        salary_schema_max = int(max_sal)
    elif pd.notna(max_sal) and float(max_sal) > 0:
        salary_display = f"Up to ${int(max_sal):,}"
        salary_short = f"Up to ${int(max_sal)//1000}K"
        salary_schema_min = None
        salary_schema_max = int(max_sal)
    else:
        salary_display = "Not disclosed"
        salary_short = ""
        salary_schema_min = None
        salary_schema_max = None
    
    seniority = job.get('seniority', 'VP') if pd.notna(job.get('seniority')) else 'VP'
    is_remote = job.get('is_remote') == True or str(job.get('is_remote')).lower() == 'true'
    job_url = job.get('job_url_direct', '#') if pd.notna(job.get('job_url_direct')) else '#'
    
    # Escape for HTML
    company_escaped = escape_html(company)
    title_escaped = escape_html(title)
    location_escaped = escape_html(location)
    
    # === SEO-OPTIMIZED TITLE ===
    # Format: "VP Sales at Acme Corp - $200K-$300K (Remote) | The CRO Report"
    title_parts = [f"{title_escaped} at {company_escaped}"]
    if salary_short:
        title_parts.append(f"- {salary_short}")
    if is_remote:
        title_parts.append("(Remote)")
    elif location:
        # Extract city name for shorter title
        city = location.split(',')[0].strip() if ',' in location else location
        if len(city) < 20:
            title_parts.append(f"({escape_html(city)})")
    page_title = ' '.join(title_parts) + " | The CRO Report"
    
    # === META DESCRIPTION ===
    meta_desc = f"{title_escaped} at {company_escaped}"
    if location:
        meta_desc += f" in {location_escaped}"
    if salary_short:
        meta_desc += f". {salary_short} base salary."
    meta_desc += " Apply now. Updated weekly."
    meta_desc = meta_desc[:155]
    
    # === CANONICAL URL ===
    canonical_url = f"{BASE_URL}/jobs/{slug}/"
    
    # === OPEN GRAPH TAGS ===
    og_title = f"{title_escaped} at {company_escaped}"
    if salary_short:
        og_title += f" ({salary_short})"
    og_description = f"{seniority}-level sales role at {company_escaped}."
    if salary_short:
        og_description += f" {salary_short} base."
    if is_remote:
        og_description += " Remote eligible."
    elif location:
        og_description += f" {location_escaped}."
    
    # === JOBPOSTING SCHEMA (JSON-LD) ===
    schema_data = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": title,
        "description": f"{seniority}-level sales executive position at {company}",
        "datePosted": iso_date,
        "validThrough": (datetime.now().replace(day=1) + pd.DateOffset(months=2)).strftime('%Y-%m-%d'),
        "employmentType": "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": company,
        },
        "jobLocationType": "TELECOMMUTE" if is_remote else None,
        "applicantLocationRequirements": {
            "@type": "Country",
            "name": "United States"
        } if is_remote else None,
    }
    
    # Add location if not remote-only
    if location and not is_remote:
        # Parse location
        loc_parts = location.split(',')
        if len(loc_parts) >= 2:
            schema_data["jobLocation"] = {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": loc_parts[0].strip(),
                    "addressRegion": loc_parts[1].strip() if len(loc_parts) > 1 else "",
                    "addressCountry": "US"
                }
            }
    
    # Add salary if disclosed
    if salary_schema_max:
        schema_data["baseSalary"] = {
            "@type": "MonetaryAmount",
            "currency": "USD",
            "value": {
                "@type": "QuantitativeValue",
                "unitText": "YEAR"
            }
        }
        if salary_schema_min and salary_schema_max:
            schema_data["baseSalary"]["value"]["minValue"] = salary_schema_min
            schema_data["baseSalary"]["value"]["maxValue"] = salary_schema_max
        elif salary_schema_max:
            schema_data["baseSalary"]["value"]["maxValue"] = salary_schema_max
    
    # Remove None values from schema
    schema_data = {k: v for k, v in schema_data.items() if v is not None}
    schema_json = json.dumps(schema_data, indent=2)
    
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
    
    <!-- Open Graph Tags (LinkedIn, Facebook) -->
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
    
    <!-- JobPosting Schema -->
    <script type="application/ld+json">
{schema_json}
    </script>
    
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
            padding: 12px 20px;
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
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            color: #1e3a5f;
            font-weight: 600;
        }}
        .logo img {{ height: 36px; border-radius: 4px; }}
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
            font-weight: 500;
        }}
        .nav-links a:hover {{ color: #1e3a5f; }}
        .btn-subscribe {{
            background: #1e3a5f !important;
            color: white !important;
            padding: 8px 16px;
            border-radius: 6px;
        }}
        
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
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
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
        
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .header h1 {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo">
                <img src="/assets/logo.jpg" alt="The CRO Report">
                <span>The CRO Report</span>
            </a>
            <nav>
                <ul class="nav-links">
                    <li><a href="/jobs/">Jobs</a></li>
                    <li><a href="/salaries/">Salaries</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="https://croreport.substack.com/subscribe" class="btn-subscribe">Subscribe</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <header class="header">
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">The CRO Report</a> → <a href="/jobs/">Jobs</a> → {company_escaped}
            </nav>
            <h1>{title_escaped}</h1>
            <div class="company">{company_escaped}</div>
            <div class="job-meta">
                {f'<span class="meta-item salary">{salary_display}</span>' if salary_display != "Not disclosed" else ''}
                {f'<span class="meta-item">📍 {location_escaped}</span>' if location else ''}
                {'<span class="meta-item">🏠 Remote</span>' if is_remote else ''}
                {f'<span class="meta-item">{seniority}</span>' if seniority else ''}
            </div>
        </div>
    </header>
    
    <div class="content">
        <div class="container">
            <div class="apply-box">
                <p>Interested in this {seniority} role at {company_escaped}?</p>
                <a href="{job_url}" class="apply-btn" target="_blank" rel="noopener">Apply Now →</a>
            </div>
            
            <div class="details">
                <h2>Role Details</h2>
                <div class="detail-row">
                    <span class="detail-label">Company</span>
                    <span class="detail-value">{company_escaped}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Title</span>
                    <span class="detail-value">{title_escaped}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location</span>
                    <span class="detail-value">{location_escaped if location else 'Not specified'}</span>
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
print(f"\n📊 SEO Features Added:")
print(f"   - Correct canonical URLs ({BASE_URL})")
print(f"   - Salary/location in title tags")
print(f"   - Open Graph tags for social sharing")
print(f"   - Twitter card tags")
print(f"   - JobPosting JSON-LD schema")
