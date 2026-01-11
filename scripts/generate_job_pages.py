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
            font-family: 'Fraunces', serif;
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
                    <li><a href="/tools/">Tools</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="/about/">About</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="https://croreport.substack.com/subscribe" class="btn-subscribe">Subscribe</a></li>
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
        <a href="https://croreport.substack.com/subscribe" class="mobile-nav-subscribe">Subscribe</a>
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
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="/tools/">Tools</a> · <a href="/insights/">Market Intel</a> · <a href="/about/">About</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
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

# ============================================================================
# STALE JOB HANDLING - Find expired jobs and show similar recommendations
# ============================================================================
print("\n" + "="*70)
print("🔄 HANDLING STALE JOB PAGES")
print("="*70)

def find_similar_jobs(stale_slug, current_jobs_df, num_recommendations=5):
    """Find similar live jobs based on the stale job's characteristics"""
    # Try to extract info from slug (company-title-hash format)
    parts = stale_slug.rsplit('-', 1)  # Split off hash
    if len(parts) < 2:
        # Can't parse, return random jobs
        return current_jobs_df.head(num_recommendations).to_dict('records')

    slug_text = parts[0].lower()

    # Score each current job by similarity
    scores = []
    for idx, job in current_jobs_df.iterrows():
        score = 0
        company = str(job.get('company', '')).lower()
        title = str(job.get('title', '')).lower()

        # Company match (highest weight)
        if company and slugify(company) in slug_text:
            score += 50

        # Title/seniority match
        if 'cro' in slug_text or 'chief-revenue' in slug_text:
            if 'cro' in title or 'chief revenue' in title:
                score += 30
        if 'vp' in slug_text or 'vice-president' in slug_text:
            if 'vp' in title or 'vice president' in title:
                score += 30
        if 'svp' in slug_text or 'senior-vice' in slug_text:
            if 'svp' in title or 'senior vice' in title:
                score += 30
        if 'director' in slug_text:
            if 'director' in title:
                score += 20

        # Remote preference
        is_remote = job.get('is_remote') == True or str(job.get('is_remote')).lower() == 'true'
        if 'remote' in slug_text and is_remote:
            score += 10

        # Has salary (prefer jobs with disclosed salary)
        if pd.notna(job.get('max_amount')) and float(job.get('max_amount', 0)) > 0:
            score += 5

        scores.append((idx, score))

    # Sort by score descending, take top N
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [s[0] for s in scores[:num_recommendations]]

    return current_jobs_df.loc[top_indices].to_dict('records')

def create_stale_job_page(stale_slug, similar_jobs):
    """Generate a page for an expired job with similar job recommendations"""

    # Parse what we can from the slug
    parts = stale_slug.rsplit('-', 1)
    slug_text = parts[0] if len(parts) >= 2 else stale_slug

    # Try to extract company and title from slug
    slug_parts = slug_text.split('-')
    if len(slug_parts) >= 2:
        # Heuristic: company is usually first few words, title contains vp/cro/director
        title_keywords = ['vp', 'vice', 'president', 'cro', 'chief', 'revenue', 'officer', 'svp', 'senior', 'director', 'sales', 'head']
        title_start = len(slug_parts)
        for i, part in enumerate(slug_parts):
            if part in title_keywords:
                title_start = i
                break

        company_parts = slug_parts[:title_start] if title_start > 0 else slug_parts[:2]
        title_parts = slug_parts[title_start:] if title_start < len(slug_parts) else slug_parts[2:]

        company_display = ' '.join(company_parts).title()
        title_display = ' '.join(title_parts).title() if title_parts else 'Sales Executive'
    else:
        company_display = 'This Company'
        title_display = 'Sales Executive'

    # Build similar jobs HTML
    similar_jobs_html = ""
    for job in similar_jobs:
        company = escape_html(str(job.get('company', 'Unknown')))
        title = escape_html(str(job.get('title', 'Sales Role')))
        location = escape_html(str(job.get('location', ''))) if pd.notna(job.get('location')) else ''
        is_remote = job.get('is_remote') == True or str(job.get('is_remote')).lower() == 'true'

        min_sal = job.get('min_amount')
        max_sal = job.get('max_amount')
        if pd.notna(min_sal) and pd.notna(max_sal) and float(min_sal) > 0 and float(max_sal) > 0:
            salary = f"${int(min_sal)//1000}K-${int(max_sal)//1000}K"
        elif pd.notna(max_sal) and float(max_sal) > 0:
            salary = f"Up to ${int(max_sal)//1000}K"
        else:
            salary = ""

        # Generate slug for this job
        job_slug = f"{slugify(job.get('company', ''))}-{slugify(job.get('title', ''))}"
        hash_suffix = hashlib.md5(f"{job.get('company','')}{job.get('title','')}{job.get('location','')}".encode()).hexdigest()[:6]
        job_slug = f"{job_slug}-{hash_suffix}"

        location_badge = '🏠 Remote' if is_remote else f'📍 {location}' if location else ''

        similar_jobs_html += f'''
            <a href="/jobs/{job_slug}/" class="similar-job-card">
                <div class="job-title">{title}</div>
                <div class="job-company">{company}</div>
                <div class="job-meta-row">
                    {f'<span class="salary-badge">{salary}</span>' if salary else ''}
                    {f'<span class="location-badge">{location_badge}</span>' if location_badge else ''}
                </div>
            </a>
        '''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta Tags -->
    <title>{title_display} at {company_display} - Position Filled | The CRO Report</title>
    <meta name="description" content="This {title_display} position at {company_display} is no longer available. Browse similar VP Sales and CRO opportunities.">
    <link rel="canonical" href="{BASE_URL}/jobs/{stale_slug}/">
    <meta name="robots" content="noindex, follow">

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

        .expired-header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .expired-header .container {{ max-width: 800px; margin: 0 auto; }}
        .expired-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-bottom: 16px;
        }}
        .expired-header h1 {{
            font-family: 'Fraunces', serif;
            font-size: 1.75rem;
            margin-bottom: 8px;
        }}
        .expired-header .company {{ font-size: 1.1rem; opacity: 0.9; }}

        .container {{ max-width: 900px; margin: 0 auto; padding: 0 20px; }}

        .content {{ padding: 40px 0; }}

        .message-box {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .message-box h2 {{
            font-family: 'Fraunces', serif;
            color: #1e3a5f;
            margin-bottom: 12px;
        }}
        .message-box p {{ color: #64748b; margin-bottom: 20px; }}
        .browse-all-btn {{
            display: inline-block;
            background: #1e3a5f;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        .browse-all-btn:hover {{ background: #2d4a6f; }}

        .similar-section {{
            margin-bottom: 40px;
        }}
        .similar-section h2 {{
            font-family: 'Fraunces', serif;
            color: #1e3a5f;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}

        .similar-jobs-grid {{
            display: grid;
            gap: 16px;
        }}
        .similar-job-card {{
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            text-decoration: none;
            color: inherit;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 2px solid transparent;
            transition: all 0.2s;
        }}
        .similar-job-card:hover {{
            border-color: #d97706;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .job-title {{
            font-weight: 600;
            font-size: 1.1rem;
            color: #0f172a;
            margin-bottom: 4px;
        }}
        .job-company {{
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 12px;
        }}
        .job-meta-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .salary-badge {{
            background: #fef3c7;
            color: #92400e;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .location-badge {{
            color: #64748b;
            font-size: 0.85rem;
        }}

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
            top: 0; left: 0; right: 0; bottom: 0;
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
            font-family: 'Fraunces', serif;
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
            .expired-header h1 {{ font-size: 1.4rem; }}
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
                    <li><a href="/tools/">Tools</a></li>
                    <li><a href="/insights/">Market Intel</a></li>
                    <li><a href="/about/">About</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="https://croreport.substack.com/subscribe" class="btn-subscribe">Subscribe</a></li>
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
        <a href="https://croreport.substack.com/subscribe" class="mobile-nav-subscribe">Subscribe</a>
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

    <header class="expired-header">
        <div class="container">
            <span class="expired-badge">Position Filled</span>
            <h1>{title_display}</h1>
            <div class="company">{company_display}</div>
        </div>
    </header>

    <div class="content">
        <div class="container">
            <div class="message-box">
                <h2>This position is no longer available</h2>
                <p>Good news - we have similar opportunities that might be a great fit for you.</p>
                <a href="/jobs/" class="browse-all-btn">Browse All Open Roles →</a>
            </div>

            <div class="similar-section">
                <h2>Similar Opportunities</h2>
                <div class="similar-jobs-grid">
                    {similar_jobs_html}
                </div>
            </div>

            <div class="cta-box">
                <h2>Get New Roles First</h2>
                <p>Subscribe to The CRO Report for weekly job alerts, salary insights, and market intelligence.</p>
                <a href="https://croreport.substack.com/subscribe" class="cta-link">Subscribe Free →</a>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="/tools/">Tools</a> · <a href="/insights/">Market Intel</a> · <a href="/about/">About</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
        <p style="margin-top: 8px; font-size: 0.85rem;">Updated {update_date}</p>
    </footer>
</body>
</html>'''

    # Save the stale page
    page_dir = f'{JOBS_DIR}/{stale_slug}'
    os.makedirs(page_dir, exist_ok=True)
    with open(f'{page_dir}/index.html', 'w') as f:
        f.write(html)

# Find all existing job page directories
existing_pages = set()
for item in os.listdir(JOBS_DIR):
    item_path = os.path.join(JOBS_DIR, item)
    if os.path.isdir(item_path) and item != 'index.html':
        existing_pages.add(item)

# Convert current job slugs to a set for comparison
current_slugs = set(job_slugs)

# Find stale pages (exist on disk but not in current data)
stale_slugs = existing_pages - current_slugs

print(f"\n📊 Page Analysis:")
print(f"   - Current live jobs: {len(current_slugs)}")
print(f"   - Existing pages on disk: {len(existing_pages)}")
print(f"   - Stale pages to update: {len(stale_slugs)}")

if stale_slugs:
    print(f"\n🔄 Updating {len(stale_slugs)} stale job pages with similar recommendations...")
    stale_count = 0
    for stale_slug in stale_slugs:
        # Find similar jobs
        similar_jobs = find_similar_jobs(stale_slug, df, num_recommendations=5)
        # Create the stale page
        create_stale_job_page(stale_slug, similar_jobs)
        stale_count += 1
        if stale_count % 50 == 0:
            print(f"   Updated {stale_count} stale pages...")

    print(f"\n✅ Updated {len(stale_slugs)} stale job pages with similar job recommendations")
else:
    print(f"\n✅ No stale job pages found - all pages are current")

print(f"\n📊 SEO Features Added:")
print(f"   - Correct canonical URLs ({BASE_URL})")
print(f"   - Salary/location in title tags")
print(f"   - Open Graph tags for social sharing")
print(f"   - Twitter card tags")
print(f"   - JobPosting JSON-LD schema")
print(f"   - Stale page handling with similar job recommendations")
