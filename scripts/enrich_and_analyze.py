import pandas as pd
from datetime import datetime
import glob
import os
import re

# ============================================================
# GITHUB ACTIONS CONFIGURATION
# ============================================================
DATA_DIR = "data"
SITE_ASSETS = "site/assets"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SITE_ASSETS, exist_ok=True)

# ============================================================
# LOAD MOST RECENT RAW DATA
# ============================================================

print("="*70)
print("🔧 EXECUTIVE SALES JOB ENRICHMENT & ANALYSIS")
print("="*70)

# Find most recent raw data file in data/ folder
files = glob.glob(f"{DATA_DIR}/raw_jobs_*.csv")
if not files:
    print("\n❌ ERROR: No raw data files found in data/ folder.")
    print("👉 Please upload raw_jobs_YYYYMMDD_HHMM.csv to data/ folder first.")
    exit(1)

latest_file = max(files)
print(f"\n📂 Loading: {latest_file}")

# Load data
df = pd.read_csv(latest_file)
print(f"📊 Loaded {len(df)} raw jobs")

# ============================================================
# STEP 1: REMOVE DUPLICATES (Enhanced)
# ============================================================

print(f"\n{'STEP 1: DEDUPLICATION':-^70}")

# First: Remove exact URL duplicates
df_clean = df.drop_duplicates(subset=['job_url'], keep='first')
url_duplicates_removed = len(df) - len(df_clean)
print(f"Removed {url_duplicates_removed} exact URL duplicates")

# Second: Remove semantic duplicates (same company + same title + same location)
before_semantic_dedup = len(df_clean)
df_clean = df_clean.drop_duplicates(
    subset=['company', 'title', 'location'], 
    keep='first'
)
semantic_duplicates_removed = before_semantic_dedup - len(df_clean)
print(f"Removed {semantic_duplicates_removed} semantic duplicates (same company/title/location)")
print(f"Remaining: {len(df_clean)} unique jobs")

# ============================================================
# STEP 2: STRICT TITLE FILTERING
# ============================================================

print(f"\n{'STEP 2: STRICT EXECUTIVE SALES TITLE FILTER':-^70}")

# First: Must contain sales/revenue keywords
sales_keywords = ['sales', 'revenue', 'cro', 'chief revenue', 'commercial']
df_sales = df_clean[
    df_clean['title'].str.lower().str.contains('|'.join(sales_keywords), na=False)
]
print(f"With sales keywords: {len(df_sales)} ({len(df_sales)/len(df_clean)*100:.1f}%)")

# Second: Must be executive level - STRICT RULES
def is_executive_sales_role(title):
    """STRICT validation - only true VP+ and C-suite roles"""
    title_lower = title.lower().strip()
    
    # BANKING/FINANCIAL SERVICES TITLE EXCLUSIONS
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
            if 'chief' in title_lower or 'head of' in title_lower:
                pass
            else:
                return False
    
    # STANDARD NON-EXECUTIVE EXCLUSIONS
    if 'account executive' in title_lower or 'account manager' in title_lower or 'account director' in title_lower:
        return False
    
    if 'director' in title_lower and 'vice president' not in title_lower and 'vp' not in title_lower:
        return False
    
    if 'manager' in title_lower and 'vice president' not in title_lower and 'vp' not in title_lower:
        return False
    
    # Reject bank AVP titles
    if 'avp,' in title_lower or 'avp ' in title_lower or title_lower.startswith('avp'):
        return False
    if 'assistant vice president' in title_lower:
        return False
    
    # EXECUTIVE TITLE VALIDATION
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
        if f' {acronym} ' in f' {title_lower} ' or f' {acronym},' in f' {title_lower} ' or title_lower.startswith(f'{acronym} ') or title_lower.endswith(f' {acronym}'):
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
    
    sales_focus = ['sales', 'revenue', 'business development']
    
    has_commercial = 'commercial' in title_lower
    if has_commercial:
        banking_commercial_terms = ['commercial bank', 'commercial card', 'commercial lend', 'commercial credit']
        is_banking_commercial = any(term in title_lower for term in banking_commercial_terms)
        if not is_banking_commercial:
            sales_focus.append('commercial')
    
    has_sales_focus = any(focus in title_lower for focus in sales_focus)
    
    return has_sales_focus

# Apply filter
df_filtered = df_sales[df_sales['title'].apply(is_executive_sales_role)]
print(f"After executive filter: {len(df_filtered)} verified executive sales roles")

# ============================================================
# STEP 3: SALARY VALIDATION
# ============================================================

print(f"\n{'STEP 3: SALARY VALIDATION':-^70}")

def validate_salary(row):
    """Enhanced salary validation with executive-level thresholds"""
    min_sal = row.get('min_amount', 0)
    max_sal = row.get('max_amount', 0)
    
    try:
        min_sal = float(min_sal) if pd.notna(min_sal) else 0
        max_sal = float(max_sal) if pd.notna(max_sal) else 0
    except:
        return False, "Invalid salary format"
    
    if min_sal <= 0 and max_sal <= 0:
        return False, "No salary disclosed"
    
    # Executive threshold: minimum $80K for VP+
    if max_sal > 0 and max_sal < 80000:
        return False, f"Below executive threshold (${max_sal:,.0f})"
    
    # Sanity check: max $2M
    if max_sal > 2000000:
        return False, f"Unrealistic salary (${max_sal:,.0f})"
    
    # Range validation
    if min_sal > 0 and max_sal > 0 and min_sal > max_sal:
        return False, "Min > Max"
    
    return True, "Valid"

df_executive = df_filtered.copy()

# Apply salary validation
salary_validation = df_executive.apply(validate_salary, axis=1, result_type='expand')
df_executive['salary_valid'] = salary_validation[0]
df_executive['salary_note'] = salary_validation[1]

valid_salary_count = df_executive['salary_valid'].sum()
print(f"Valid salaries: {valid_salary_count} ({valid_salary_count/len(df_executive)*100:.1f}%)")

# ============================================================
# STEP 4: ENRICHMENT
# ============================================================

print(f"\n{'STEP 4: ENRICHMENT':-^70}")

def determine_seniority(title):
    """Classify seniority level from title"""
    title_lower = title.lower()
    
    c_suite = ['chief revenue officer', 'chief sales officer', 'chief commercial officer', 'chief business officer']
    if any(c in title_lower for c in c_suite):
        return 'C-Level'
    
    if ' cro ' in f' {title_lower} ' or title_lower.startswith('cro ') or title_lower.endswith(' cro'):
        return 'C-Level'
    if ' cso ' in f' {title_lower} ' or title_lower.startswith('cso '):
        return 'C-Level'
    
    if 'executive vice president' in title_lower or ' evp ' in f' {title_lower} ' or 'evp,' in title_lower:
        return 'EVP'
    
    if 'senior vice president' in title_lower or ' svp ' in f' {title_lower} ' or 'svp,' in title_lower:
        return 'SVP'
    
    if 'vice president' in title_lower or ' vp ' in f' {title_lower} ' or 'vp,' in title_lower:
        return 'VP'
    
    if 'head of' in title_lower:
        return 'Head of'
    
    return 'Other'

def determine_company_stage(row):
    """Classify company stage based on available data"""
    employees = row.get('company_num_employees', '')
    
    if pd.isna(employees) or employees == '':
        return 'Unknown'
    
    employees_str = str(employees).lower()
    
    if '10,001' in employees_str or '10001' in employees_str or 'more' in employees_str:
        return 'Enterprise/Public'
    if '5,001' in employees_str or '5001' in employees_str:
        return 'Late Stage'
    if '1,001' in employees_str or '1001' in employees_str:
        return 'Series C/D'
    if '501' in employees_str or '201' in employees_str:
        return 'Series B/C'
    if '51' in employees_str or '11' in employees_str:
        return 'Series A/B'
    if '1-10' in employees_str or '2-10' in employees_str:
        return 'Seed/Series A'
    
    return 'Unknown'

def classify_metro(location):
    """Classify location into metro areas"""
    if pd.isna(location):
        return 'Other'
    
    loc_lower = str(location).lower()
    
    if 'remote' in loc_lower or 'anywhere' in loc_lower or 'work from home' in loc_lower:
        return 'Remote'
    if 'san francisco' in loc_lower or 'sf,' in loc_lower or 'bay area' in loc_lower or 'palo alto' in loc_lower or 'san jose' in loc_lower or 'oakland' in loc_lower:
        return 'San Francisco'
    if 'new york' in loc_lower or 'nyc' in loc_lower or 'manhattan' in loc_lower or 'brooklyn' in loc_lower:
        return 'New York'
    if 'los angeles' in loc_lower or 'la,' in loc_lower or 'santa monica' in loc_lower:
        return 'Los Angeles'
    if 'chicago' in loc_lower:
        return 'Chicago'
    if 'boston' in loc_lower or 'cambridge, ma' in loc_lower:
        return 'Boston'
    if 'seattle' in loc_lower or 'bellevue' in loc_lower:
        return 'Seattle'
    if 'austin' in loc_lower or 'dallas' in loc_lower or 'houston' in loc_lower or ', tx' in loc_lower or 'texas' in loc_lower:
        return 'Texas'
    if 'denver' in loc_lower or 'boulder' in loc_lower or ', co' in loc_lower:
        return 'Denver'
    if 'atlanta' in loc_lower or ', ga' in loc_lower:
        return 'Atlanta'
    
    return 'Other'

def is_tech_company(row):
    """Determine if company is in tech industry"""
    company = str(row.get('company', '')).lower()
    description = str(row.get('description', '')).lower()
    
    tech_keywords = ['software', 'saas', 'cloud', 'ai ', 'artificial intelligence', 'machine learning',
                     'data platform', 'tech', 'digital', 'platform', 'api', 'developer', 'cybersecurity',
                     'fintech', 'healthtech', 'edtech', 'martech']
    
    combined = company + ' ' + description
    return any(kw in combined for kw in tech_keywords)

# Apply enrichments
df_executive['seniority'] = df_executive['title'].apply(determine_seniority)
df_executive['company_stage'] = df_executive.apply(determine_company_stage, axis=1)
df_executive['metro'] = df_executive['location'].apply(classify_metro)
df_executive['is_tech'] = df_executive.apply(is_tech_company, axis=1)
df_executive['is_remote'] = df_executive['location'].str.lower().str.contains('remote|anywhere|work from home', na=False)
df_executive['has_description'] = df_executive['description'].notna() & (df_executive['description'].str.len() > 100)
df_executive['has_salary'] = df_executive['salary_valid']

# Data quality score
def calculate_data_quality(row):
    score = 0
    if row.get('has_salary', False): score += 1
    if row.get('has_description', False): score += 1
    if row.get('company_stage', 'Unknown') != 'Unknown': score += 1
    
    if score >= 3: return 'Premium'
    if score >= 2: return 'Good'
    return 'Basic'

df_executive['data_quality'] = df_executive.apply(calculate_data_quality, axis=1)

print(f"✅ Enrichment complete")
print(f"   Seniority levels: {df_executive['seniority'].value_counts().to_dict()}")

# ============================================================
# STEP 5: SAVE ENRICHED DATA
# ============================================================

print(f"\n{'STEP 5: SAVE ENRICHED DATA':-^70}")

essential_columns = [
    'job_url', 'title', 'company', 'location', 'date_posted',
    'min_amount', 'max_amount', 'currency', 'interval',
    'seniority', 'company_stage', 'metro', 'is_tech', 'is_remote',
    'has_description', 'has_salary', 'data_quality',
    'description', 'company_url', 'company_url_direct',
    'company_num_employees', 'company_revenue'
]

available_columns = [col for col in essential_columns if col in df_executive.columns]
df_output = df_executive[available_columns].copy()

enriched_filename = f"{DATA_DIR}/executive_sales_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
df_output.to_csv(enriched_filename, index=False, quoting=2, lineterminator='\n')
print(f"✅ Saved enriched data: {enriched_filename}")
print(f"   Total jobs: {len(df_output)}")

# ============================================================
# STEP 6: UPDATE TRACKING CSV
# ============================================================

print(f"\n{'STEP 6: TRACKING':-^70}")

tracking_file = f'{DATA_DIR}/Sales_Exec_Openings.csv'
today = datetime.now().strftime('%Y-%m-%d')
total_openings = len(df_output)

if os.path.exists(tracking_file):
    df_tracking = pd.read_csv(tracking_file)
    
    if today in df_tracking['Date'].values:
        df_tracking.loc[df_tracking['Date'] == today, 'Sales Exec Openings'] = total_openings
        print(f"📝 Updated existing entry for {today}: {total_openings} openings")
    else:
        new_row = pd.DataFrame({'Date': [today], 'Sales Exec Openings': [total_openings]})
        df_tracking = pd.concat([df_tracking, new_row], ignore_index=True)
        print(f"✅ Added new entry: {today}, {total_openings} openings")
    
    df_tracking.to_csv(tracking_file, index=False)
else:
    df_tracking = pd.DataFrame({
        'Date': [today],
        'Sales Exec Openings': [total_openings]
    })
    df_tracking.to_csv(tracking_file, index=False)
    print(f"✅ Created new tracking file: {tracking_file}")

# ============================================================
# STEP 7: UPDATE MARKET STATS JSON
# ============================================================

print(f"\n{'STEP 7: MARKET STATS':-^70}")

import json

# Calculate stats
seniority_counts = df_output['seniority'].value_counts().to_dict()
unique_companies = df_output['company'].nunique()
salary_data = df_output[df_output['has_salary'] == True]

market_stats = {
    "total_jobs": len(df_output),
    "unique_companies": unique_companies,
    "salary_disclosure_rate": round(len(salary_data) / len(df_output) * 100, 1) if len(df_output) > 0 else 0,
    "by_seniority": seniority_counts,
    "remote_percentage": round(df_output['is_remote'].sum() / len(df_output) * 100, 1) if len(df_output) > 0 else 0,
    "tech_percentage": round(df_output['is_tech'].sum() / len(df_output) * 100, 1) if len(df_output) > 0 else 0,
    "avg_min_salary": int(salary_data['min_amount'].mean()) if len(salary_data) > 0 else 0,
    "avg_max_salary": int(salary_data['max_amount'].mean()) if len(salary_data) > 0 else 0,
    "last_updated": datetime.now().strftime('%Y-%m-%d')
}

stats_file = f'{DATA_DIR}/market_stats.json'
with open(stats_file, 'w') as f:
    json.dump(market_stats, f, indent=2)
print(f"✅ Saved market stats: {stats_file}")

print(f"\n{'='*70}")
print(f"🎉 ENRICHMENT COMPLETE!")
print(f"{'='*70}")
print(f"📊 {total_openings} executive sales roles")
print(f"📁 {enriched_filename}")
print(f"{'='*70}\n")
