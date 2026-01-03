import pandas as pd
from datetime import datetime
import glob

# ============================================================
# LOAD MOST RECENT RAW DATA
# ============================================================

print("="*70)
print("🔧 EXECUTIVE SALES JOB ENRICHMENT & ANALYSIS")
print("="*70)

# Find most recent raw data file
files = glob.glob("raw_jobs_*.csv")
if not files:
    print("\n❌ ERROR: No raw data files found.")
    print("👉 Please run scrape_jobs_weekly.py first.")
    exit(1)

latest_file = max(files)
print(f"\n📂 Loading: {latest_file}")

# Load data
df = pd.read_csv(latest_file)
print(f"📊 Loaded {len(df)} raw jobs")

# ============================================================
# STEP 1: REMOVE DUPLICATES
# ============================================================

print(f"\n{'STEP 1: DEDUPLICATION':-^70}")
df_clean = df.drop_duplicates(subset=['job_url'], keep='first')
duplicates_removed = len(df) - len(df_clean)
print(f"Removed {duplicates_removed} duplicates")
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
    """Strict validation - title must match executive patterns"""
    title_lower = title.lower().strip()
    
    # MUST contain one of these executive indicators IN THE TITLE
    executive_indicators = [
        'chief revenue officer',
        'cro',
        'vice president',
        'vp ',  # Space after to avoid matching words like "development"
        'svp ',
        'senior vice president',
        'evp ',
        'executive vice president'
    ]
    
    has_executive_title = any(indicator in title_lower for indicator in executive_indicators)
    if not has_executive_title:
        return False
    
    # MUST contain sales/revenue/commercial focus
    sales_focus = [
        'sales',
        'revenue', 
        'commercial',
        'business development'  # Include BD for VP level
    ]
    
    has_sales_focus = any(focus in title_lower for focus in sales_focus)
    if not has_sales_focus:
        return False
    
    # Special case: Allow "sales and marketing" or "sales & marketing" 
    # These are legitimate hybrid roles
    if 'sales' in title_lower and 'marketing' in title_lower:
        return True
    
    # EXCLUSIONS: Non-sales VP roles (but not if they also have sales keywords)
    # Only exclude if the title has NO sales/revenue keywords
    exclusions = [
        'finance',
        'financial',
        'operations',
        'information security',
        'technology',
        'engineering',
        'product',
        'human resources',
        'legal',
        'compliance',
        'risk',
        'audit',
        'supply chain'
    ]
    
    # Check for exclusions
    has_exclusion = any(exclusion in title_lower for exclusion in exclusions)
    if has_exclusion:
        return False
    
    # Additional validation: Reject obvious non-executive roles
    non_executive = [
        'assistant',
        'associate',
        'coordinator',
        'representative',
        'specialist',
        'analyst',
        'agent',
        'consultant'
    ]
    
    # If title contains these low-level words, reject
    # UNLESS it says "senior" or "principal" before them
    for term in non_executive:
        if term in title_lower:
            # Allow "Senior VP" roles even if they have "specialist"
            if 'vice president' not in title_lower and 'vp' not in title_lower and 'chief' not in title_lower:
                return False
    
    return True

# Apply strict filter
df_filtered = df_sales[df_sales['title'].apply(is_executive_sales_role)]
print(f"After strict executive filter: {len(df_filtered)} ({len(df_filtered)/len(df_clean)*100:.1f}% of total)")

# Show what was filtered out
rejected = df_sales[~df_sales['title'].apply(is_executive_sales_role)]
print(f"Rejected: {len(rejected)} non-executive or non-sales roles")

if len(rejected) > 0:
    print("\nExample rejected titles:")
    for title in rejected['title'].head(10):
        print(f"  ✗ {title}")

# ============================================================
# STEP 3: ENRICHMENT - ADD CLASSIFICATION COLUMNS
# ============================================================

print(f"\n{'STEP 3: DATA ENRICHMENT':-^70}")

# Use df_filtered (already filtered to executive sales roles)
df_executive = df_filtered.copy()

# Seniority classification
def classify_seniority(title):
    title_lower = str(title).lower()
    if 'chief' in title_lower or 'cro' in title_lower or 'cco' in title_lower:
        return 'C-Level'
    elif 'evp' in title_lower or 'executive vice president' in title_lower:
        return 'EVP'
    elif 'svp' in title_lower or 'senior vice president' in title_lower:
        return 'SVP'
    elif 'vp' in title_lower or 'vice president' in title_lower:
        return 'VP'
    elif 'head of' in title_lower:
        return 'Head of'
    else:
        return 'Other'

df_executive['seniority'] = df_executive['title'].apply(classify_seniority)

# Tech company indicator
tech_keywords = [
    'software', 'saas', 'tech', 'ai', 'cloud', 'data', 'platform', 
    'digital', 'cyber', 'fintech', 'analytics', 'enterprise software',
    'machine learning', 'automation', 'api', 'infrastructure'
]
df_executive['is_tech'] = df_executive['company'].str.lower().str.contains(
    '|'.join(tech_keywords), na=False
).fillna(False)

# Data quality scoring
def calculate_data_quality(row):
    score = 0
    if pd.notna(row['description']) and len(str(row['description'])) > 100:
        score += 40
    if pd.notna(row['min_amount']):
        score += 30
    if pd.notna(row['location']) and str(row['location']) not in ['', 'nan']:
        score += 15
    if pd.notna(row['company']) and str(row['company']) not in ['', 'nan']:
        score += 15
    return score

df_executive['data_quality_score'] = df_executive.apply(calculate_data_quality, axis=1)
df_executive['data_quality'] = df_executive['data_quality_score'].apply(
    lambda x: 'Premium' if x >= 85 else 'Good' if x >= 55 else 'Basic'
)

# Key field indicators
df_executive['has_description'] = df_executive['description'].notna() & (df_executive['description'].str.len() > 100)
df_executive['has_salary'] = df_executive['min_amount'].notna()

# Week identifier
df_executive['week_added'] = datetime.now().strftime('%Y-%m-%d')

print(f"✅ Added enrichment columns: seniority, is_tech, data_quality, etc.")

# ============================================================
# STEP 4: SORT BY PRIORITY
# ============================================================

print(f"\n{'STEP 4: SORTING':-^70}")
# Sort by: Seniority (C-Level first) → Data Quality → Date Posted
seniority_order = {'C-Level': 1, 'EVP': 2, 'SVP': 3, 'VP': 4, 'Head of': 5, 'Other': 6}
df_executive['seniority_rank'] = df_executive['seniority'].map(seniority_order)

df_executive = df_executive.sort_values(
    ['seniority_rank', 'data_quality_score', 'date_posted'], 
    ascending=[True, False, False]
)
df_executive = df_executive.drop('seniority_rank', axis=1)
print("✅ Sorted by seniority, quality, and recency")

# ============================================================
# STEP 5: SAVE ENRICHED DATA
# ============================================================

print(f"\n{'STEP 5: SAVING':-^70}")
enriched_filename = f"executive_sales_jobs_{datetime.now().strftime('%Y%m%d')}.csv"
df_executive.to_csv(enriched_filename, index=False)
print(f"✅ Saved enriched data: {enriched_filename}")

# ============================================================
# STEP 6: GENERATE COMPREHENSIVE SUMMARY
# ============================================================

print("\n" + "="*70)
print("📊 WEEKLY EXECUTIVE SALES JOB MARKET REPORT")
print("="*70)

print(f"\n{'VOLUME METRICS':-^70}")
print(f"Total raw jobs scraped................ {len(df):>6}")
print(f"After deduplication................... {len(df_clean):>6}")
print(f"Sales-focused roles................... {len(df_filtered):>6}")
print(f"Executive-level (VP+)................. {len(df_executive):>6}")

print(f"\n{'SENIORITY BREAKDOWN':-^70}")
seniority_counts = df_executive['seniority'].value_counts()
for level in ['C-Level', 'EVP', 'SVP', 'VP', 'Head of']:
    count = seniority_counts.get(level, 0)
    pct = (count / len(df_executive) * 100) if len(df_executive) > 0 else 0
    print(f"{level:.<45} {count:>5} ({pct:>5.1f}%)")

print(f"\n{'DATA QUALITY':-^70}")
quality_counts = df_executive['data_quality'].value_counts()
for quality in ['Premium', 'Good', 'Basic']:
    count = quality_counts.get(quality, 0)
    pct = (count / len(df_executive) * 100) if len(df_executive) > 0 else 0
    print(f"{quality:.<45} {count:>5} ({pct:>5.1f}%)")

print(f"\n{'JOB CHARACTERISTICS':-^70}")
tech_count = len(df_executive[df_executive['is_tech'] == True])
remote_count = len(df_executive[df_executive['is_remote'] == True])
desc_count = len(df_executive[df_executive['has_description'] == True])
salary_count = len(df_executive[df_executive['has_salary'] == True])

print(f"Tech companies........................ {tech_count:>6} ({tech_count/len(df_executive)*100:.1f}%)")
print(f"Remote positions...................... {remote_count:>6} ({remote_count/len(df_executive)*100:.1f}%)")
print(f"With full description................. {desc_count:>6} ({desc_count/len(df_executive)*100:.1f}%)")
print(f"With salary data...................... {salary_count:>6} ({salary_count/len(df_executive)*100:.1f}%)")

print(f"\n{'TOP 15 HIRING COMPANIES':-^70}")
top_companies = df_executive['company'].value_counts().head(15)
for i, (company, count) in enumerate(top_companies.items(), 1):
    print(f"{i:>2}. {str(company)[:50]:.<52} {count:>3}")

print(f"\n{'TOP 10 LOCATIONS':-^70}")
top_locations = df_executive['location'].value_counts().head(10)
for i, (location, count) in enumerate(top_locations.items(), 1):
    print(f"{i:>2}. {str(location)[:50]:.<52} {count:>3}")

print(f"\n{'SALARY INSIGHTS (Where Available)':-^70}")
if salary_count > 0:
    salary_data = df_executive[df_executive['has_salary']]
    avg_min = salary_data['min_amount'].mean()
    avg_max = salary_data['max_amount'].mean()
    median_min = salary_data['min_amount'].median()
    
    print(f"Average minimum salary................ ${avg_min:>12,.0f}")
    print(f"Average maximum salary................ ${avg_max:>12,.0f}")
    print(f"Median minimum salary................. ${median_min:>12,.0f}")
else:
    print("No salary data available")

# ============================================================
# SAVE TEXT SUMMARY
# ============================================================

summary_filename = f"summary_{datetime.now().strftime('%Y%m%d')}.txt"
with open(summary_filename, 'w') as f:
    f.write("WEEKLY EXECUTIVE SALES JOB MARKET REPORT\n")
    f.write("="*70 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("VOLUME METRICS\n")
    f.write("-" * 70 + "\n")
    f.write(f"Total Executive Sales Roles (VP+): {len(df_executive)}\n")
    f.write(f"C-Level: {seniority_counts.get('C-Level', 0)}\n")
    f.write(f"SVP: {seniority_counts.get('SVP', 0)}\n")
    f.write(f"VP: {seniority_counts.get('VP', 0)}\n\n")
    
    f.write("KEY METRICS\n")
    f.write("-" * 70 + "\n")
    f.write(f"With Salary: {salary_count} ({salary_count/len(df_executive)*100:.1f}%)\n")
    f.write(f"Tech Companies: {tech_count} ({tech_count/len(df_executive)*100:.1f}%)\n")
    f.write(f"Remote: {remote_count} ({remote_count/len(df_executive)*100:.1f}%)\n")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE!")
print("="*70)
print(f"📊 {len(df_executive)} executive sales roles ready for your audience")
print(f"📁 Enriched data: {enriched_filename}")
print(f"📄 Summary report: {summary_filename}")
print("="*70)
