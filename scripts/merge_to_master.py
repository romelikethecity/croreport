#!/usr/bin/env python3
"""
Merge weekly enriched data into the master jobs database
Preserves all fields including descriptions for historical analysis

Run after enrichment: python scripts/merge_to_master.py
"""

import pandas as pd
from datetime import datetime
import glob
import os

DATA_DIR = 'data'

print("="*70)
print("📚 MERGING TO MASTER DATABASE")
print("="*70)

# Find most recent enriched file
enriched_files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not enriched_files:
    print("❌ No enriched data files found")
    exit(1)

latest_enriched = max(enriched_files)
print(f"📂 Loading weekly data: {latest_enriched}")

df_new = pd.read_csv(latest_enriched)
print(f"   {len(df_new)} new jobs")

# Add import metadata
today = datetime.now()
df_new['import_date'] = today.strftime('%Y-%m-%d')
df_new['import_week'] = today.strftime('%Y-W%W')

# Load or create master database
master_file = f'{DATA_DIR}/master_jobs_database.csv'

if os.path.exists(master_file):
    print(f"\n📂 Loading existing master: {master_file}")
    df_master = pd.read_csv(master_file)
    print(f"   {len(df_master)} existing jobs")
    
    # Check for duplicates by job_url_direct
    existing_urls = set(df_master['job_url_direct'].dropna())
    new_urls = set(df_new['job_url_direct'].dropna())
    
    truly_new = new_urls - existing_urls
    duplicates = new_urls & existing_urls
    
    print(f"\n📊 Deduplication:")
    print(f"   Already in master: {len(duplicates)}")
    print(f"   Truly new: {len(truly_new)}")
    
    # Filter to truly new jobs
    df_to_add = df_new[df_new['job_url_direct'].isin(truly_new)]
    
    # Merge
    df_master = pd.concat([df_master, df_to_add], ignore_index=True)
    
else:
    print(f"\n📂 Creating new master database")
    df_master = df_new.copy()

# Ensure all important columns exist
required_cols = [
    'job_url_direct', 'title', 'company', 'location', 'date_posted',
    'description', 'min_amount', 'max_amount', 'is_remote', 'seniority',
    'metro', 'is_tech', 'company_industry', 'company_num_employees',
    'company_revenue', 'import_date', 'import_week', 'has_salary'
]

for col in required_cols:
    if col not in df_master.columns:
        df_master[col] = None

# Sort by import date (newest first)
df_master = df_master.sort_values('import_date', ascending=False)

# Save
df_master.to_csv(master_file, index=False)

# Report
print(f"\n✅ MASTER DATABASE UPDATED")
print(f"   Total jobs: {len(df_master)}")
print(f"   With descriptions: {df_master['description'].notna().sum()} ({df_master['description'].notna().sum()/len(df_master)*100:.1f}%)")
print(f"   With salary: {df_master['has_salary'].sum() if 'has_salary' in df_master.columns else 'N/A'}")
print(f"   Date range: {df_master['import_date'].min()} to {df_master['import_date'].max()}")

# File size
size_mb = os.path.getsize(master_file) / (1024*1024)
print(f"   File size: {size_mb:.1f} MB")

print(f"\n📁 Saved: {master_file}")
