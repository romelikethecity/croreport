#!/usr/bin/env python3
"""
Merge weekly enriched data into master database.
This ensures the master_jobs_database.csv is up to date for the website.
"""

import pandas as pd
import os
import glob
from datetime import datetime

DATA_DIR = "data"

print("="*70)
print("📊 MERGE TO MASTER DATABASE")
print("="*70)

# Find most recent enriched file
enriched_files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not enriched_files:
    print("❌ No enriched files found")
    exit(0)

latest_enriched = max(enriched_files)
print(f"\n📂 Latest enriched file: {latest_enriched}")

# Load new data
new_df = pd.read_csv(latest_enriched)
print(f"📊 New records: {len(new_df)}")

# Add import metadata
new_df['import_date'] = datetime.now().strftime('%Y-%m-%d')
new_df['import_week'] = datetime.now().strftime('%Y-W%W')

# Load or create master database
master_file = f"{DATA_DIR}/master_jobs_database.csv"

if os.path.exists(master_file):
    master_df = pd.read_csv(master_file)
    print(f"📂 Existing master database: {len(master_df)} records")
    
    # Deduplicate based on job_url
    if 'job_url_direct' in new_df.columns and 'job_url_direct' in master_df.columns:
        existing_urls = set(master_df['job_url_direct'].dropna().unique())
        new_records = new_df[~new_df['job_url_direct'].isin(existing_urls)]
        print(f"✅ New unique records: {len(new_records)}")
        
        if len(new_records) > 0:
            combined_df = pd.concat([master_df, new_records], ignore_index=True)
        else:
            combined_df = master_df
    else:
        # No job_url column, just replace
        combined_df = new_df
else:
    print("📂 Creating new master database")
    combined_df = new_df

# Save master database
combined_df.to_csv(master_file, index=False)
print(f"\n✅ Master database saved: {len(combined_df)} total records")

# Update historical tracking file for trend charts
tracking_file = f"{DATA_DIR}/Sales_Exec_Openings.csv"
if os.path.exists(tracking_file):
    tracking_df = pd.read_csv(tracking_file)
    job_count = len(new_df)

    # Extract date from filename (executive_sales_jobs_YYYYMMDD.csv)
    import re
    filename = os.path.basename(latest_enriched)
    date_match = re.search(r'(\d{8})', filename)
    if date_match:
        date_str = date_match.group(1)
        file_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    else:
        file_date = datetime.now().strftime('%Y-%m-%d')

    # Check if this date exists and needs updating
    if file_date in tracking_df['Date'].values:
        existing_count = tracking_df.loc[tracking_df['Date'] == file_date, 'Sales Exec Openings'].values[0]
        if existing_count != job_count:
            # Update existing entry with correct count
            tracking_df.loc[tracking_df['Date'] == file_date, 'Sales Exec Openings'] = job_count
            tracking_df.to_csv(tracking_file, index=False)
            print(f"📈 Updated trend tracking: {file_date} → {job_count} jobs (was {existing_count})")
        else:
            print(f"📈 Trend tracking already correct for {file_date}: {job_count} jobs")
    else:
        # Add new entry
        with open(tracking_file, 'a') as f:
            f.write(f"\n{file_date},{job_count}")
        print(f"📈 Added trend tracking: {file_date} → {job_count} jobs")

print(f"{'='*70}")
