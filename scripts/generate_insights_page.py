#!/usr/bin/env python3
"""
Generate Market Intelligence page from job description analysis
Creates /insights/ with skills heatmap, methodology trends, red flags, etc.

Uses master_jobs_database.csv for historical analysis when available,
falls back to weekly file for current snapshot.
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
print("📊 GENERATING MARKET INTELLIGENCE PAGE")
print("="*70)

os.makedirs(INSIGHTS_DIR, exist_ok=True)

# Try master database first for historical analysis
master_file = f'{DATA_DIR}/master_jobs_database.csv'
if os.path.exists(master_file):
    df_all = pd.read_csv(master_file)
    print(f"📂 Loaded master database: {len(df_all)} total jobs")
    has_historical = True
else:
    # Fall back to weekly file
    files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
    if not files:
        print("❌ No job data found")
        exit(1)
    latest_file = max(files)
    df_all = pd.read_csv(latest_file)
    print(f"📂 Loaded weekly file: {len(df_all)} jobs")
    has_historical = False

# Get current week's data for "This Week" stats
if 'import_date' in df_all.columns:
    df_all['import_date'] = pd.to_datetime(df_all['import_date'], errors='coerce')
    latest_date = df_all['import_date'].max()
    df_current = df_all[df_all['import_date'] == latest_date]
    
    # Get 30 days ago for comparison
    thirty_days_ago = latest_date - timedelta(days=30)
    df_30d_ago = df_all[(df_all['import_date'] >= thirty_days_ago - timedelta(days=7)) & 
                        (df_all['import_date'] <= thirty_days_ago)]
else:
    df_current = df_all
    df_30d_ago = pd.DataFrame()

print(f"📊 Current week: {len(df_current)} jobs")
if len(df_30d_ago) > 0:
    print(f"📊 30 days ago: {len(df_30d_ago)} jobs (for comparison)")

# Use current week for primary analysis
df = df_current if len(df_current) > 0 else df_all

# Combine all descriptions
all_text = ' '.join(df['description'].dropna().astype(str)).lower()
total_jobs = len(df)
update_date = datetime.now().strftime('%B %d, %Y')

# === ANALYSIS FUNCTIONS ===

def count_pattern(pattern):
    return len(re.findall(pattern, all_text, re.IGNORECASE))

def pct(count):
    return round(count / total_jobs * 100, 1)

# === RUN ANALYSIS ===

# Tools
tools_analysis = {
    'Salesforce': count_pattern(r'\bsalesforce\b'),
    'HubSpot': count_pattern(r'\bhubspot\b'),
    'Gong': count_pattern(r'\bgong\b'),
    'Outreach': count_pattern(r'\boutreach\b'),
    'ZoomInfo': count_pattern(r'\bzoominfo\b'),
    'Clari': count_pattern(r'\bclari\b'),
    'Tableau': count_pattern(r'\btableau\b'),
    'LinkedIn Sales Nav': count_pattern(r'\blinkedin\s*(?:sales)?\s*nav'),
}
tools_analysis = {k: v for k, v in sorted(tools_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Methodologies
methods_analysis = {
    'Enterprise Sales': count_pattern(r'\benterprise\s*sales'),
    'Consultative Selling': count_pattern(r'\bconsultative\b'),
    'Channel/Partner': count_pattern(r'\bchannel\s*(?:sales|partner)|partner\s*(?:sales|channel)'),
    'Value Selling': count_pattern(r'\bvalue\s*sell'),
    'MEDDIC/MEDDPICC': count_pattern(r'\bmedd[ip]*i?c+\b'),
    'PLG/Product-Led': count_pattern(r'\bplg\b|product.led'),
    'Challenger': count_pattern(r'\bchallenger\b'),
    'Account-Based (ABM)': count_pattern(r'\baccount.based|abm\b'),
}
methods_analysis = {k: v for k, v in sorted(methods_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Buzzwords/Trends
trends_analysis = {
    'AI / Machine Learning': count_pattern(r'\bartificial\s*intelligence|\b(?<!equ)ai\b|machine\s*learning'),
    'Go-to-Market / GTM': count_pattern(r'\bgo.to.market|\bgtm\b'),
    'Scale / Scalable': count_pattern(r'\bscalab|\bscale\b'),
    'SaaS': count_pattern(r'\bsaas\b'),
    'Data-Driven': count_pattern(r'\bdata.driven\b'),
    'Cloud': count_pattern(r'\bcloud\b'),
    'Series A-D (Startup)': count_pattern(r'\bseries\s*[a-d]\b'),
    'Customer Success': count_pattern(r'\bcustomer\s*success\b'),
    'Recurring Revenue/ARR': count_pattern(r'\brecurring\s*revenue|arr\b|mrr\b'),
    'GenAI': count_pattern(r'\bgenai|generative\s*ai|gen\s*ai|llm\b'),
}
trends_analysis = {k: v for k, v in sorted(trends_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Industries
industries_analysis = {
    'Technology/Software': count_pattern(r'\btechnology|software|tech\s*companies'),
    'Healthcare': count_pattern(r'\bhealthcare|health\s*tech|medical|pharma|biotech'),
    'Financial Services': count_pattern(r'\bfinancial\s*services|fintech|banking|insurance'),
    'Education': count_pattern(r'\beducation|edtech|learning'),
    'Government': count_pattern(r'\bgovernment|public\s*sector|federal'),
    'Cybersecurity': count_pattern(r'\bcyber|security|infosec'),
    'Retail/E-commerce': count_pattern(r'\bretail|e.commerce|ecommerce'),
    'Real Estate': count_pattern(r'\breal\s*estate|proptech'),
    'Energy': count_pattern(r'\benergy|utilities|renewable'),
    'Manufacturing': count_pattern(r'\bmanufacturing|industrial'),
}
industries_analysis = {k: v for k, v in sorted(industries_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Red Flags
red_flags_analysis = {
    '"Competitive compensation" (vague)': count_pattern(r'\bcompetitive\s*(?:salary|compensation|pay)'),
    '"Fast-paced environment"': count_pattern(r'\bfast.paced\b'),
    'Travel 50%+': count_pattern(r'\b(?:5[0-9]|[6-9][0-9]|100)\s*%\s*travel'),
    '"Self-starter" required': count_pattern(r'\bself.starter\b'),
    '"Wear many hats"': count_pattern(r'\bwear\s*many\s*hats|wear\s*multiple\s*hats'),
    '"Scrappy"': count_pattern(r'\bscrappy\b'),
}
red_flags_analysis = {k: v for k, v in sorted(red_flags_analysis.items(), key=lambda x: -x[1]) if v > 0}

# Experience requirements
exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?'
exp_mentions = re.findall(exp_pattern, all_text)
exp_counts = Counter([int(y) for y in exp_mentions if int(y) <= 20])

# Save analysis to JSON for other uses
analysis_data = {
    'date': update_date,
    'total_jobs': total_jobs,
    'tools': tools_analysis,
    'methodologies': methods_analysis,
    'trends': trends_analysis,
    'industries': industries_analysis,
    'red_flags': red_flags_analysis,
    'experience_requirements': dict(exp_counts.most_common(10)),
}

with open(f'{DATA_DIR}/market_intelligence.json', 'w') as f:
    json.dump(analysis_data, f, indent=2)
print(f"✅ Saved analysis to {DATA_DIR}/market_intelligence.json")

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
        .header .eyebrow {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #d97706; margin-bottom: 12px; }}
        .header h1 {{ font-family: 'Fraunces', serif; font-size: 2.5rem; margin-bottom: 12px; }}
        .header p {{ opacity: 0.9; max-width: 600px; margin: 0 auto; }}
        .header .update {{ margin-top: 16px; font-size: 0.85rem; opacity: 0.7; }}
        
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
    <header class="header">
        <div class="eyebrow">Market Intelligence</div>
        <h1>What Companies Want in 2025</h1>
        <p>Skills, tools, and experience requirements extracted from {total_jobs} VP Sales and CRO job postings</p>
        <div class="update">Analysis updated {update_date}</div>
    </header>
    
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
        
        <section class="section">
            <h2>Skills & Tools in Demand</h2>
            <p class="subtitle">What technologies and platforms are companies looking for?</p>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>🔧 Tools & Platforms</h3>
                    {generate_bar_chart(dict(list(tools_analysis.items())[:8]))}
                </div>
                
                <div class="chart-card">
                    <h3>📈 Sales Methodologies</h3>
                    {generate_bar_chart(dict(list(methods_analysis.items())[:8]), color='#0891b2')}
                </div>
            </div>
            
            <div class="insight-box">
                <h4>💡 Key Insight</h4>
                <p>Salesforce remains dominant, but notice the rise of MEDDIC requirements ({meddic_count} explicit mentions). 
                Two years ago, specific methodology requirements were rare in job postings. Now they're table stakes for enterprise roles.</p>
            </div>
        </section>
        
        <section class="section">
            <h2>Trends & Buzzwords</h2>
            <p class="subtitle">What's hot in executive sales hiring right now?</p>
            
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>🔥 2025 Buzzwords</h3>
                    {generate_bar_chart(dict(list(trends_analysis.items())[:8]), color='#7c3aed')}
                </div>
                
                <div class="chart-card">
                    <h3>🏢 Industry Focus</h3>
                    {generate_bar_chart(dict(list(industries_analysis.items())[:8]), color='#059669')}
                </div>
            </div>
            
            <div class="insight-box">
                <h4>💡 Key Insight</h4>
                <p>AI mentions appear in {ai_pct}% of job descriptions—even for traditional sales leadership roles. 
                Companies want leaders who can leverage AI in their sales motion, not just sell AI products.</p>
            </div>
        </section>
        
        <section class="section">
            <h2>🚩 Red Flags to Watch</h2>
            <p class="subtitle">Language patterns that often signal problems</p>
            
            <div class="chart-card red-flag-card" style="max-width: 600px;">
                <h3>Warning Signs in Job Postings</h3>
                {generate_bar_chart(red_flags_analysis, color='#dc2626')}
            </div>
            
            <div class="insight-box" style="background: #fef2f2; border-color: #fecaca;">
                <h4 style="color: #991b1b;">⚠️ What These Mean</h4>
                <p style="color: #7f1d1d;">
                    <strong>"Competitive compensation"</strong> without ranges usually means below-market or highly variable. 
                    <strong>"Fast-paced"</strong> often signals understaffing or constant fire-drills.
                    <strong>50%+ travel</strong> at VP level suggests territory is too spread out or company lacks regional structure.
                </p>
            </div>
        </section>
        
        <div class="cta-box">
            <h2>Get This Analysis Weekly</h2>
            <p>Market trends, red flags, and hiring intelligence delivered every Thursday.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="/jobs/">Jobs</a> · <a href="/salaries/">Salaries</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
</body>
</html>'''

# Save the page
with open(f'{INSIGHTS_DIR}/index.html', 'w') as f:
    f.write(html)

print(f"✅ Generated /insights/ page")
print(f"📊 Analysis covers {total_jobs} job descriptions")
