#!/usr/bin/env python3
"""
Executive Sales Job Enrichment & Analysis
Adapted for GitHub Actions - reads from data/, outputs to data/
"""

import pandas as pd
from datetime import datetime
import glob
import os
import re

# Paths relative to repo root
DATA_DIR = 'data'
SITE_DIR = 'site'

print("="*70)
print("🔧 EXECUTIVE SALES JOB ENRICHMENT & ANALYSIS")
print("="*70)

# Find most recent raw data file
files = glob.glob(f"{DATA_DIR}/raw_jobs_*.csv")
if not files:
    # Check if enriched data already exists
    enriched_files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
    if enriched_files:
        print(f"✅ Using existing enriched data: {max(enriched_files)}")
        exit(0)
    else:
        print("\n❌ ERROR: No raw or enriched data files found.")
        exit(1)

latest_file = max(files)
print(f"\n📂 Loading: {latest_file}")

df = pd.read_csv(latest_file)
print(f"📊 Loaded {len(df)} raw jobs")

# ============================================================
# STEP 1: REMOVE DUPLICATES
# ============================================================

print(f"\n{'STEP 1: DEDUPLICATION':-^70}")

df_clean = df.drop_duplicates(subset=['job_url'], keep='first')
url_duplicates_removed = len(df) - len(df_clean)
print(f"Removed {url_duplicates_removed} exact URL duplicates")

before_semantic_dedup = len(df_clean)
df_clean = df_clean.drop_duplicates(
    subset=['company', 'title', 'location'], 
    keep='first'
)
semantic_duplicates_removed = before_semantic_dedup - len(df_clean)
print(f"Removed {semantic_duplicates_removed} semantic duplicates")
print(f"Remaining: {len(df_clean)} unique jobs")

# ============================================================
# STEP 2: STRICT TITLE FILTERING
# ============================================================

print(f"\n{'STEP 2: STRICT EXECUTIVE SALES TITLE FILTER':-^70}")

sales_keywords = ['sales', 'revenue', 'cro', 'chief revenue', 'commercial']
df_sales = df_clean[
    df_clean['title'].str.lower().str.contains('|'.join(sales_keywords), na=False)
]
print(f"With sales keywords: {len(df_sales)}")

def is_executive_sales_role(title):
    """STRICT validation - only true VP+ and C-suite roles"""
    title_lower = title.lower().strip()
    
    # Banking IC exclusions
    banking_ic_patterns = [
        'relationship manager', 'commercial banker', 'commercial bank ',
        'commercial bank-', 'private banker', 'business banker',
        'commercial card', 'treasury management', 'loan officer',
        'credit officer', 'portfolio manager', 'wealth advisor',
        'financial advisor', 'investment banker', 'middle market bank',
        'emerging middle market',
    ]
    
    for pattern in banking_ic_patterns:
        if pattern in title_lower:
            if 'chief' not in title_lower and 'head of' not in title_lower:
                return False
    
    # Standard exclusions
    if 'account executive' in title_lower or 'account manager' in title_lower or 'account director' in title_lower:
        return False
    if 'director' in title_lower and 'vice president' not in title_lower and 'vp' not in title_lower:
        return False
    if 'manager' in title_lower and 'vice president' not in title_lower and 'vp' not in title_lower:
        return False
    if 'avp,' in title_lower or 'avp ' in title_lower or title_lower.startswith('avp'):
        return False
    if 'assistant vice president' in title_lower:
        return False
    
    # Must have executive title
    has_executive_title = False
    
    c_suite_titles = [
        'chief revenue officer', 'chief sales officer', 'chief commercial officer',
        'chief business officer', 'chief business development officer',
    ]
    
    for c_title in c_suite_titles:
        if c_title in title_lower:
            has_executive_title = True
            break
    
    c_suite_acronyms = ['cro', 'cso', 'cco', 'cbo']
    for acronym in c_suite_acronyms:
        if f' {acronym} ' in f' {title_lower} ' or f' {acronym},' in f' {title_lower} ':
            has_executive_title = True
            break
    
    vp_patterns = ['executive vice president', 'senior vice president', 'vice president']
    for vp in vp_patterns:
        if vp in title_lower:
            has_executive_title = True
            break
    
    title_with_spaces = ' ' + title_lower + ' '
    if ' evp ' in title_with_spaces or ' svp ' in title_with_spaces or ' vp ' in title_with_spaces:
        has_executive_title = True
    if 'evp,' in title_lower or 'svp,' in title_lower or 'vp,' in title_lower:
        has_executive_title = True
    if 'evp of' in title_lower or 'svp of' in title_lower or 'vp of' in title_lower:
        has_executive_title = True
    
    if not has_executive_title:
        return False
    
    # Must have sales focus
    sales_focus = ['sales', 'revenue', 'business development']
    has_commercial = 'commercial' in title_lower
    if has_commercial:
        banking_commercial_terms = ['commercial bank', 'commercial card', 'commercial lend', 'commercial credit']
        is_banking_commercial = any(term in title_lower for term in banking_commercial_terms)
        if not is_banking_commercial:
            sales_focus.append('commercial')
    
    has_sales_focus = any(term in title_lower for term in sales_focus)
    
    return has_sales_focus

df_filtered = df_sales[df_sales['title'].apply(is_executive_sales_role)]
print(f"Executive roles: {len(df_filtered)}")

# ============================================================
# STEP 3: ASSIGN SENIORITY
# ============================================================

print(f"\n{'STEP 3: SENIORITY CLASSIFICATION':-^70}")

def assign_seniority(title):
    title_lower = title.lower()
    
    c_suite = ['chief revenue officer', 'chief sales officer', 'chief commercial officer', 'cro', 'cso', 'cco']
    for c in c_suite:
        if c in title_lower:
            return 'C-Level'
    
    if 'executive vice president' in title_lower or ' evp ' in f' {title_lower} ':
        return 'EVP'
    if 'senior vice president' in title_lower or ' svp ' in f' {title_lower} ':
        return 'SVP'
    if 'vice president' in title_lower or ' vp ' in f' {title_lower} ':
        return 'VP'
    if 'head of' in title_lower:
        return 'Head of'
    
    return 'Other'

df_executive = df_filtered.copy()
df_executive['seniority'] = df_executive['title'].apply(assign_seniority)

seniority_counts = df_executive['seniority'].value_counts()
for level, count in seniority_counts.items():
    print(f"  {level}: {count}")

# ============================================================
# STEP 4: ENRICH DATA
# ============================================================

print(f"\n{'STEP 4: ENRICHMENT':-^70}")

# Metro classification
def classify_metro(location):
    if pd.isna(location):
        return 'Other'
    loc_lower = location.lower()
    
    metros = {
        'San Francisco': ['san francisco', 'sf,', 'bay area', 'palo alto', 'mountain view', 'san jose', 'oakland', 'berkeley', 'sunnyvale', 'menlo park', 'redwood city', 'fremont', 'santa clara'],
        'New York': ['new york', 'ny,', 'nyc', 'manhattan', 'brooklyn', 'queens', 'jersey city', 'hoboken', 'newark'],
        'Los Angeles': ['los angeles', 'la,', 'santa monica', 'pasadena', 'long beach', 'burbank', 'glendale', 'irvine', 'orange county'],
        'Boston': ['boston', 'cambridge, ma', 'somerville', 'brookline', 'quincy, ma'],
        'Seattle': ['seattle', 'bellevue', 'redmond', 'kirkland, wa', 'tacoma'],
        'Chicago': ['chicago', 'evanston', 'naperville', 'oak brook'],
        'Austin': ['austin', 'round rock', 'cedar park'],
        'Denver': ['denver', 'boulder', 'aurora, co', 'lakewood, co'],
        'Atlanta': ['atlanta', 'marietta', 'alpharetta', 'sandy springs'],
        'Miami': ['miami', 'fort lauderdale', 'boca raton', 'west palm'],
        'Dallas': ['dallas', 'fort worth', 'plano', 'irving', 'arlington, tx', 'frisco'],
        'Remote': ['remote', 'anywhere', 'work from home', 'united states']
    }
    
    for metro, keywords in metros.items():
        if any(kw in loc_lower for kw in keywords):
            return metro
    
    # Texas consolidation
    if ', tx' in loc_lower or 'texas' in loc_lower:
        return 'Texas'
    
    return 'Other'

df_executive['metro'] = df_executive['location'].apply(classify_metro)

# Data quality flags
df_executive['has_salary'] = df_executive['max_amount'].notna() & (df_executive['max_amount'] > 0)
df_executive['has_description'] = df_executive['description'].notna() if 'description' in df_executive.columns else False

salary_count = df_executive['has_salary'].sum()
print(f"With salary data: {salary_count} ({salary_count/len(df_executive)*100:.1f}%)")

# ============================================================
# STEP 5: SAVE OUTPUT
# ============================================================

print(f"\n{'STEP 5: SAVING OUTPUT':-^70}")

output_cols = ['job_url_direct', 'title', 'company', 'location', 'date_posted', 
               'description', 'min_amount', 'max_amount', 'is_remote', 'seniority', 'metro',
               'is_tech', 'company_industry', 'company_num_employees', 'company_revenue', 'has_salary']

# Add any missing columns
for col in output_cols:
    if col not in df_executive.columns:
        df_executive[col] = None

df_output = df_executive[output_cols].copy()

enriched_filename = f"{DATA_DIR}/executive_sales_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
df_output.to_csv(enriched_filename, index=False)
print(f"✅ Saved: {enriched_filename}")

# ============================================================
# STEP 6: UPDATE TRACKING
# ============================================================

print(f"\n{'STEP 6: UPDATE TRACKING':-^70}")

tracking_file = f'{DATA_DIR}/Sales_Exec_Openings.csv'
today = datetime.now().strftime('%Y-%m-%d')
total_openings = len(df_output)

if os.path.exists(tracking_file):
    df_tracking = pd.read_csv(tracking_file)
    if today in df_tracking['Date'].values:
        df_tracking.loc[df_tracking['Date'] == today, 'Sales Exec Openings'] = total_openings
        print(f"📝 Updated entry for {today}: {total_openings}")
    else:
        new_row = pd.DataFrame({'Date': [today], 'Sales Exec Openings': [total_openings]})
        df_tracking = pd.concat([df_tracking, new_row], ignore_index=True)
        print(f"✅ Added entry: {today}, {total_openings}")
    df_tracking.to_csv(tracking_file, index=False)
else:
    df_tracking = pd.DataFrame({'Date': [today], 'Sales Exec Openings': [total_openings]})
    df_tracking.to_csv(tracking_file, index=False)
    print(f"✅ Created tracking file with {total_openings} openings")

# ============================================================
# STEP 7: GENERATE SUMMARY JSON (for homepage)
# ============================================================

print(f"\n{'STEP 7: GENERATE STATS':-^70}")

import json

# Calculate week-over-week change
if os.path.exists(tracking_file) and len(df_tracking) >= 2:
    df_tracking_sorted = df_tracking.sort_values('Date')
    current = df_tracking_sorted['Sales Exec Openings'].iloc[-1]
    previous = df_tracking_sorted['Sales Exec Openings'].iloc[-2]
    wow_change = ((current - previous) / previous * 100) if previous > 0 else 0
else:
    current = total_openings
    wow_change = 0

# Peak comparison (162 was 2022 high)
peak = 162
vs_peak = ((current - peak) / peak * 100)

# Remote percentage
remote_count = len(df_output[df_output['is_remote'] == True]) if 'is_remote' in df_output.columns else 0
remote_pct = (remote_count / len(df_output) * 100) if len(df_output) > 0 else 0

# Average max salary
avg_max_salary = df_output[df_output['max_amount'].notna()]['max_amount'].mean()

stats = {
    'date': today,
    'total_roles': int(current),
    'wow_change': round(wow_change, 1),
    'vs_peak_pct': round(vs_peak, 1),
    'remote_pct': round(remote_pct, 0),
    'avg_max_salary': int(avg_max_salary) if pd.notna(avg_max_salary) else 0,
    'unique_companies': int(df_output['company'].nunique()),
    'salary_transparency_pct': round(salary_count / len(df_output) * 100, 1)
}

with open(f'{DATA_DIR}/market_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"✅ Saved market stats: {stats}")

print(f"\n{'='*70}")
print(f"🎉 ENRICHMENT COMPLETE!")
print(f"📊 {total_openings} executive sales roles processed")
print(f"{'='*70}")
