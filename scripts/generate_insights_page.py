#!/usr/bin/env python3
"""
Generate Market Intelligence page from job description analysis
Creates /insights/ with skills heatmap, methodology trends, red flags, etc.

Uses master_jobs_database.csv for historical analysis.
"""

import pandas as pd
import re
import json
from collections import Counter
from datetime import datetime, timedelta
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
INSIGHTS_DIR = f'{SITE_DIR}/insights'

print("="*70)
print("[INSIGHTS] GENERATING MARKET INTELLIGENCE PAGE")
print("="*70)

os.makedirs(INSIGHTS_DIR, exist_ok=True)

# Try master database first for historical analysis
master_file = f'{DATA_DIR}/master_jobs_database.csv'
if os.path.exists(master_file):
    df = pd.read_csv(master_file)
    print(f"[FILE] Loaded master database: {len(df)} total jobs")
else:
    # Fall back to weekly file
    files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
    if not files:
        print("[ERROR] No job data found")
        exit(1)
    latest_file = max(files)
    df = pd.read_csv(latest_file)
    print(f"[FILE] Loaded weekly file: {len(df)} jobs")

# Filter to jobs with descriptions for analysis
df_with_desc = df[df['description'].notna() & (df['description'].str.len() > 50)].copy()
print(f"[DATA] {len(df_with_desc)} jobs with descriptions for analysis")

total_jobs = len(df_with_desc)
update_date = datetime.now().strftime('%B %d, %Y')

# === ANALYSIS FUNCTIONS ===

def count_jobs_with_pattern(pattern):
    """Count how many JOBS mention the pattern (not total occurrences)"""
    count = 0
    for desc in df_with_desc['description'].dropna():
        if re.search(pattern, str(desc), re.IGNORECASE):
            count += 1
    return count

def pct(count):
    """Calculate percentage of jobs"""
    if total_jobs == 0:
        return 0
    return round(count / total_jobs * 100, 1)

# === RUN ANALYSIS ===

print("[ANALYSIS] Counting tools...")
# Tools - count jobs that mention each tool
tools_analysis = {
    'Salesforce': count_jobs_with_pattern(r'\bsalesforce\b'),
    'HubSpot': count_jobs_with_pattern(r'\bhubspot\b'),
    'Gong': count_jobs_with_pattern(r'\bgong\b'),
    'Outreach': count_jobs_with_pattern(r'\boutreach\b'),
    'ZoomInfo': count_jobs_with_pattern(r'\bzoominfo\b'),
    'Clari': count_jobs_with_pattern(r'\bclari\b'),
    'Tableau': count_jobs_with_pattern(r'\btableau\b'),
    'LinkedIn Sales Nav': count_jobs_with_pattern(r'\blinkedin\s*(?:sales)?\s*nav'),
}
tools_analysis = {k: v for k, v in sorted(tools_analysis.items(), key=lambda x: -x[1]) if v > 0}

print("[ANALYSIS] Counting methodologies...")
# Methodologies
methods_analysis = {
    'Enterprise Sales': count_jobs_with_pattern(r'\benterprise\s*sales'),
    'Consultative Selling': count_jobs_with_pattern(r'\bconsultative\b'),
    'Channel/Partner': count_jobs_with_pattern(r'\bchannel\s*(?:sales|partner)|partner\s*(?:sales|channel)'),
    'Value Selling': count_jobs_with_pattern(r'\bvalue\s*sell'),
    'MEDDIC/MEDDPICC': count_jobs_with_pattern(r'\bmedd[ip]*i?c+\b'),
    'PLG/Product-Led': count_jobs_with_pattern(r'\bplg\b|product.led'),
    'Challenger': count_jobs_with_pattern(r'\bchallenger\b'),
    'Account-Based (ABM)': count_jobs_with_pattern(r'\baccount.based|abm\b'),
}
methods_analysis = {k: v for k, v in sorted(methods_analysis.items(), key=lambda x: -x[1]) if v > 0}

print("[ANALYSIS] Counting trends...")
# Buzzwords/Trends
trends_analysis = {
    'AI / Machine Learning': count_jobs_with_pattern(r'\bartificial\s*intelligence|\bai\b|machine\s*learning'),
    'Go-to-Market / GTM': count_jobs_with_pattern(r'\bgo.to.market|\bgtm\b'),
    'Scale / Scalable': count_jobs_with_pattern(r'\bscalab|\bscale\b'),
    'SaaS': count_jobs_with_pattern(r'\bsaas\b'),
    'Data-Driven': count_jobs_with_pattern(r'\bdata.driven\b'),
    'Cloud': count_jobs_with_pattern(r'\bcloud\b'),
    'Series A-D (Startup)': count_jobs_with_pattern(r'\bseries\s*[a-d]\b'),
    'Customer Success': count_jobs_with_pattern(r'\bcustomer\s*success\b'),
    'Recurring Revenue/ARR': count_jobs_with_pattern(r'\brecurring\s*revenue|arr\b|mrr\b'),
    'GenAI': count_jobs_with_pattern(r'\bgenai|generative\s*ai|gen\s*ai|llm\b'),
}
trends_analysis = {k: v for k, v in sorted(trends_analysis.items(), key=lambda x: -x[1]) if v > 0}

print("[ANALYSIS] Counting industries...")
# Industries
industries_analysis = {
    'Technology/Software': count_jobs_with_pattern(r'\btechnology|software|tech\s*companies'),
    'Healthcare': count_jobs_with_pattern(r'\bhealthcare|health\s*tech|medical|pharma|biotech'),
    'Financial Services': count_jobs_with_pattern(r'\bfinancial\s*services|fintech|banking|insurance'),
    'Education': count_jobs_with_pattern(r'\beducation|edtech|learning'),
    'Government': count_jobs_with_pattern(r'\bgovernment|public\s*sector|federal'),
    'Cybersecurity': count_jobs_with_pattern(r'\bcyber|security|infosec'),
    'Retail/E-commerce': count_jobs_with_pattern(r'\bretail|e.commerce|ecommerce'),
    'Real Estate': count_jobs_with_pattern(r'\breal\s*estate|proptech'),
    'Energy': count_jobs_with_pattern(r'\benergy|utilities|renewable'),
    'Manufacturing': count_jobs_with_pattern(r'\bmanufacturing|industrial'),
}
industries_analysis = {k: v for k, v in sorted(industries_analysis.items(), key=lambda x: -x[1]) if v > 0}

print("[ANALYSIS] Counting red flags...")
# Red Flags
red_flags_analysis = {
    '"Competitive compensation" (vague)': count_jobs_with_pattern(r'\bcompetitive\s*(?:salary|compensation|pay)'),
    '"Fast-paced environment"': count_jobs_with_pattern(r'\bfast.paced\b'),
    'Travel 50%+': count_jobs_with_pattern(r'\b(?:5[0-9]|[6-9][0-9]|100)\s*%\s*travel'),
    '"Self-starter" required': count_jobs_with_pattern(r'\bself.starter\b'),
    '"Wear many hats"': count_jobs_with_pattern(r'\bwear\s*many\s*hats|wear\s*multiple\s*hats'),
    '"Scrappy"': count_jobs_with_pattern(r'\bscrappy\b'),
}
red_flags_analysis = {k: v for k, v in sorted(red_flags_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Save analysis to JSON for other uses
analysis_data = {
    'date': update_date,
    'total_jobs': total_jobs,
    'tools': tools_analysis,
    'methodologies': methods_analysis,
    'trends': trends_analysis,
    'industries': industries_analysis,
    'red_flags': red_flags_analysis,
}

with open(f'{DATA_DIR}/market_intelligence.json', 'w') as f:
    json.dump(analysis_data, f, indent=2)
print(f"[FILE] Saved analysis to {DATA_DIR}/market_intelligence.json")

# === GENERATE HTML ===

def generate_bar_chart(data, max_val=None, color='#1e3a5f'):
    """Generate HTML for a horizontal bar chart"""
    if not max_val:
        max_val = max(data.values()) if data else 1
    
    html = '<div class="bar-chart">'
    for label, value in data.items():
        width = (value / max_val) * 100
        html += f'''
        <div class="bar-row">
            <div class="bar-label">{label}</div>
            <div class="bar-container">
                <div class="bar" style="width: {width}%; background: {color};"></div>
                <span class="bar-value">{value}</span>
            </div>
        </div>
        '''
    html += '</div>'
    return html

# Top insight callouts
ai_pct = pct(trends_analysis.get('AI / Machine Learning', 0))
salesforce_pct = pct(tools_analysis.get('Salesforce', 0))
meddic_count = methods_analysis.get('MEDDIC/MEDDPICC', 0)
red_flag_vague_comp = red_flags_analysis.get('"Competitive compensation" (vague)', 0)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VP Sales & CRO Job Market Intelligence | The CRO Report</title>
    <meta name="description" content="What skills, tools, and experience are companies looking for in VP Sales and CRO roles? Analysis of {total_jobs} executive sales job postings.">
    <link rel="canonical" href="https://thecroreport.com/insights/">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://thecroreport.com/insights/">
    <meta property="og:title" content="VP Sales & CRO Job Market Intelligence">
    <meta property="og:description" content="What skills, tools, and experience are companies looking for in VP Sales and CRO roles?">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="VP Sales & CRO Job Market Intelligence">
    <meta name="twitter:description" content="What skills, tools, and experience are companies looking for in VP Sales and CRO roles?">
    <meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">

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
        
        /* Navigation */
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
        .logo-img {{
            height: 32px;
            width: auto;
        }}
        .nav-links {{
            display: flex;
            gap: 24px;
            list-style: none;
            align-items: center;
        }}
        .nav-links a {{
            text-decoration: none;
            color: #475569;
            font-size: 0.9rem;
            font-weight: 500;
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
            font-weight: 600;
        }}
        .btn-subscribe:hover {{
            background: #2d4a6f;
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
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .mobile-nav-overlay.active {{
            opacity: 1;
        }}
        .mobile-nav {{
            position: fixed;
            top: 0;
            right: -100%;
            width: 280px;
            height: 100%;
            background: white;
            z-index: 1000;
            transition: right 0.3s ease;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
        }}
        .mobile-nav.active {{
            right: 0;
        }}
        .mobile-nav-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .mobile-nav-header .logo-text {{
            font-family: 'Fraunces', serif;
            font-size: 1.1rem;
            color: #1e3a5f;
            font-weight: 600;
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
            padding: 20px;
        }}
        .mobile-nav-links li {{
            margin-bottom: 8px;
        }}
        .mobile-nav-links a {{
            display: block;
            padding: 12px 16px;
            color: #1e3a5f;
            text-decoration: none;
            font-size: 1rem;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        .mobile-nav-links a:hover {{
            background: #f1f5f9;
        }}
        .mobile-nav-subscribe {{
            display: block;
            margin: 20px;
            padding: 14px;
            background: #1e3a5f;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
        }}
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .mobile-menu-btn {{ display: block; }}
            .mobile-nav-overlay {{ display: block; pointer-events: none; }}
            .mobile-nav-overlay.active {{ pointer-events: auto; }}
        }}
        
        .hero-header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        .hero-header .eyebrow {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #d97706; margin-bottom: 12px; }}
        .hero-header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .hero-header p {{ opacity: 0.9; max-width: 600px; margin: 0 auto; }}
        .hero-header .update {{ margin-top: 16px; font-size: 0.85rem; opacity: 0.7; }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 0 20px; }}
        
        .callouts {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: -40px auto 40px;
            position: relative;
            z-index: 10;
        }}
        @media (max-width: 800px) {{ .callouts {{ grid-template-columns: repeat(2, 1fr); }} }}
        
        .callout {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .callout .number {{ font-family: 'Fraunces', serif; font-size: 2.5rem; font-weight: 600; color: #1e3a5f; }}
        .callout .label {{ font-size: 0.85rem; color: #64748b; margin-top: 4px; }}
        
        .section {{ padding: 40px 0; }}
        .section h2 {{ font-family: 'Fraunces', serif; font-size: 1.75rem; color: #1e3a5f; margin-bottom: 8px; }}
        .section .subtitle {{ color: #64748b; margin-bottom: 24px; }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 32px;
        }}
        @media (max-width: 800px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
        
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .chart-card h3 {{ font-size: 1.1rem; color: #1e3a5f; margin-bottom: 16px; }}
        
        .bar-chart {{ }}
        .bar-row {{ display: flex; align-items: center; margin-bottom: 12px; }}
        .bar-label {{ width: 140px; font-size: 0.85rem; color: #475569; flex-shrink: 0; }}
        .bar-container {{ flex: 1; display: flex; align-items: center; gap: 8px; }}
        .bar {{ height: 24px; border-radius: 4px; min-width: 4px; }}
        .bar-value {{ font-size: 0.8rem; font-weight: 600; color: #64748b; }}
        
        .red-flag-card {{
            background: #fef2f2;
            border: 1px solid #fecaca;
        }}
        .red-flag-card h3 {{ color: #991b1b; }}
        .red-flag-card .bar {{ background: #dc2626 !important; }}
        
        .insight-box {{
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 12px;
            padding: 20px;
            margin: 24px 0;
        }}
        .insight-box h4 {{ color: #92400e; margin-bottom: 8px; }}
        .insight-box p {{ color: #78350f; font-size: 0.95rem; }}
        
        .cta-box {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin: 40px 0;
        }}
        .cta-box h2 {{ color: white; font-family: 'Fraunces', serif; margin-bottom: 12px; }}
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
    </style>
</head>
<body>
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
                    <li><a href="/assessment/">AI Assessment</a></li>
                    <li><a href="/about/">About</a></li>
                    <li><a href="/newsletter/">Newsletter</a></li>
                    <li><a href="/newsletter/" class="btn-subscribe">Subscribe</a></li>
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
            <li><a href="/assessment/">AI Assessment</a></li>
            <li><a href="/about/">About</a></li>
            <li><a href="/newsletter/">Newsletter</a></li>
        </ul>
        <a href="/newsletter/" class="mobile-nav-subscribe">Subscribe</a>
    </nav>

    <div class="hero-header">
        <div class="eyebrow">Market Intelligence</div>
        <h1>What Companies Want in {datetime.now().year}</h1>
        <p>Skills, tools, and experience requirements extracted from {total_jobs} VP Sales and CRO job postings</p>
        <div class="update">Analysis updated {update_date}</div>
    </div>

    <div class="container">
        <div class="callouts">
            <div class="callout">
                <div class="number">{ai_pct}%</div>
                <div class="label">Mention AI/ML</div>
            </div>
            <div class="callout">
                <div class="number">{salesforce_pct}%</div>
                <div class="label">Want Salesforce</div>
            </div>
            <div class="callout">
                <div class="number">{meddic_count}</div>
                <div class="label">Require MEDDIC</div>
            </div>
            <div class="callout">
                <div class="number">{red_flag_vague_comp}</div>
                <div class="label">Vague on Comp</div>
            </div>
        </div>
        
        <div style="background: #f1f5f9; border-radius: 12px; padding: 32px; margin-bottom: 40px;">
            <p style="color: #475569; margin: 0; font-size: 1.05rem; line-height: 1.7;">
                This report analyzes {total_jobs} VP Sales and CRO job postings to surface what companies actually prioritize—not what recruiters claim matters.
            </p>
        </div>

        <section class="section">
            <h2>Skills & Tools in Demand</h2>
            <p class="subtitle">What technologies and platforms are companies looking for?</p>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Tools & Platforms</h3>
                    {generate_bar_chart(dict(list(tools_analysis.items())[:8]))}
                </div>
                
                <div class="chart-card">
                    <h3>Sales Methodologies</h3>
                    {generate_bar_chart(dict(list(methods_analysis.items())[:8]), color='#0891b2')}
                </div>
            </div>
            
            <div class="insight-box">
                <h4>Key Insight: Tools Are Table Stakes</h4>
                <p><strong>Salesforce appears in {salesforce_pct}% of job descriptions</strong>—but that's not a differentiator anymore. It's assumed. What's more telling is the rise of revenue intelligence tools like Gong and Clari. Companies want leaders who can operationalize data, not just manage pipelines.</p>
                <p style="margin-top: 12px;">MEDDIC/MEDDPICC now shows up in {meddic_count} postings explicitly. Two years ago, methodology requirements were rare in job postings. Now they're screening criteria for enterprise roles.</p>
            </div>
        </section>
        
        <section class="section">
            <h2>Trends & Buzzwords</h2>
            <p class="subtitle">What's hot in executive sales hiring right now?</p>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>2025 Buzzwords</h3>
                    {generate_bar_chart(dict(list(trends_analysis.items())[:8]), color='#7c3aed')}
                </div>
                
                <div class="chart-card">
                    <h3>Industry Focus</h3>
                    {generate_bar_chart(dict(list(industries_analysis.items())[:8]), color='#059669')}
                </div>
            </div>
            
            <div class="insight-box">
                <h4>Key Insight: AI Is Now Expected</h4>
                <p><strong>{ai_pct}% of postings mention AI or machine learning</strong>—and these aren't just AI companies. Traditional enterprise sales roles now expect leaders who can leverage AI in their sales motion: forecasting, lead scoring, conversation intelligence, pipeline analysis.</p>
                <p style="margin-top: 12px;">If you can't articulate how you've used AI tools to improve sales outcomes, you're already behind.</p>
            </div>
        </section>
        
        <section class="section">
            <h2>Red Flags to Watch</h2>
            <p class="subtitle">Language patterns that often signal problems</p>
            
            <div class="chart-card red-flag-card" style="max-width: 600px;">
                <h3>Warning Signs in Job Postings</h3>
                {generate_bar_chart(red_flags_analysis, color='#dc2626')}
            </div>
            
            <div class="insight-box" style="background: #fef2f2; border-color: #fecaca;">
                <h4 style="color: #991b1b;">What These Red Flags Actually Mean</h4>
                <p style="color: #7f1d1d; margin-bottom: 12px;">
                    <strong>"Competitive compensation" ({red_flag_vague_comp} postings):</strong> Without disclosed ranges, this typically means below-market or highly variable comp. Companies confident in their offers publish them.
                </p>
                <p style="color: #7f1d1d; margin-bottom: 12px;">
                    <strong>"Fast-paced environment":</strong> Often signals understaffing or constant fire-drills. Ask about team size and recent turnover.
                </p>
                <p style="color: #7f1d1d; margin-bottom: 12px;">
                    <strong>"Self-starter" / "Wear many hats":</strong> Common at Seed/Series A, but a red flag at Series B+. Usually means you'll lack RevOps support and spend time on admin work.
                </p>
                <p style="color: #7f1d1d; margin-bottom: 0;">
                    <strong>50%+ travel:</strong> At VP level, this suggests territory is geographically spread without regional structure, or the company hasn't invested in inside sales.
                </p>
            </div>
        </section>

        <section class="section">
            <h2>About This Data</h2>
            <div style="background: #f1f5f9; border-radius: 12px; padding: 32px; max-width: 700px;">
                <p style="color: #475569; margin-bottom: 12px;">
                    <strong>Source:</strong> {total_jobs} VP Sales, SVP Sales, and CRO job postings from our master database.
                </p>
                <p style="color: #475569; margin-bottom: 12px;">
                    <strong>Method:</strong> We scan job descriptions for specific keywords and phrases, counting unique postings that mention each term—not total occurrences.
                </p>
                <p style="color: #475569; margin-bottom: 0;">
                    <strong>Updated:</strong> {update_date}. This analysis refreshes weekly as new postings hit our database.
                </p>
            </div>
        </section>

        <div class="cta-box">
            <h2>Get This Analysis Weekly</h2>
            <p>Market trends, red flags, and hiring intelligence delivered every Thursday.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2025 <a href="/">The CRO Report</a> | <a href="/jobs/">Jobs</a> | <a href="/salaries/">Salaries</a> | <a href="/tools/">Tools</a> | <a href="/insights/">Market Intel</a> | <a href="/about/">About</a> | <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>

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
</body>
</html>'''

# Save the page
with open(f'{INSIGHTS_DIR}/index.html', 'w') as f:
    f.write(html)

print(f"[DONE] Generated /insights/ page")
print(f"[DATA] Analysis covers {total_jobs} job descriptions")
print(f"[STATS] AI mentions: {ai_pct}%, Salesforce: {salesforce_pct}%, MEDDIC: {meddic_count}")
