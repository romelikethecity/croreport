from jobspy import scrape_jobs
import pandas as pd
import time
import subprocess
import shutil
from datetime import datetime
import os

# ============================================================
# EXPANDED CONFIGURATION - Maximum Coverage
# ============================================================

# Comprehensive search terms
SEARCH_TERMS = [
    "Chief Revenue Officer",
    "Vice President Sales",
    "VP Sales",
    "SVP Sales",
    "Senior Vice President Sales",
    "Vice President Revenue",
    "SVP Revenue",
    "VP Business Development",
    "Regional VP Sales",
    "Area VP Sales",
    "VP Enterprise Sales",
    "VP SaaS Sales",
    "EVP Sales",
    "Executive Vice President Sales"
]

# Major tech hubs + broad searches
LOCATIONS = [
    "United States",
    "Remote",
    "San Francisco, CA",
    "New York, NY",
    "Seattle, WA",
    "Austin, TX",
    "Boston, MA",
    "Los Angeles, CA"
]

SITES = ["indeed"]

# GitHub repo location - UPDATE THIS TO YOUR PATH
GITHUB_REPO = os.path.expanduser("~/Downloads/croreport-github")

# ============================================================
# SCRAPING LOOP
# ============================================================

all_jobs = []
total_searches = len(SEARCH_TERMS) * len(LOCATIONS) * len(SITES)
current_search = 0

print("="*70)
print("🚀 EXECUTIVE SALES JOB SCRAPER - MAXIMUM COVERAGE EDITION")
print("="*70)
print(f"📊 {len(SEARCH_TERMS)} search terms × {len(LOCATIONS)} locations")
print(f"🔍 Total searches: {total_searches}")
print(f"⏰ Estimated time: {(total_searches * 2) // 60} hours {(total_searches * 2) % 60} minutes")
print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n⚠️  NOTE: 2-minute waits between searches (safe for Indeed)")
print("="*70)

site_stats = {site: {'attempted': 0, 'successful': 0, 'jobs': 0} for site in SITES}

for site in SITES:
    for location in LOCATIONS:
        for term in SEARCH_TERMS:
            current_search += 1
            site_stats[site]['attempted'] += 1
            
            print(f"\n[{current_search}/{total_searches}] 🔎 {term}")
            print(f"   📍 {location}")
            
            try:
                jobs = scrape_jobs(
                    site_name=[site],
                    search_term=term,
                    location=location,
                    results_wanted=300,
                    hours_old=168,  # 7 days only
                    country_indeed='USA'
                )
                
                if len(jobs) > 0:
                    all_jobs.append(jobs)
                    site_stats[site]['successful'] += 1
                    site_stats[site]['jobs'] += len(jobs)
                    print(f"   ✅ Found {len(jobs)} jobs")
                else:
                    print(f"   ⚠️  No results")
                
                # Wait between searches
                if current_search < total_searches:
                    wait_time = 120
                    print(f"   ⏳ Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
                if current_search < total_searches:
                    time.sleep(180)
                continue

# ============================================================
# COMBINE AND SAVE RESULTS
# ============================================================

print("\n" + "="*70)
print("📊 SCRAPING SUMMARY")
print("="*70)

if all_jobs:
    combined = pd.concat(all_jobs, ignore_index=True)
else:
    print("❌ No jobs found! Check your internet connection.")
    exit(1)

for site, stats in site_stats.items():
    success_rate = (stats['successful'] / stats['attempted'] * 100) if stats['attempted'] > 0 else 0
    print(f"\n{site.upper()}:")
    print(f"  Searches attempted: {stats['attempted']}")
    print(f"  Searches successful: {stats['successful']} ({success_rate:.1f}%)")
    print(f"  Jobs found: {stats['jobs']}")

# Save RAW data locally
raw_filename = f"raw_jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
combined.to_csv(raw_filename, index=False)

# Quick stats
unique_count = combined['job_url'].nunique()
duplicate_count = len(combined) - unique_count

print(f"\n" + "="*70)
print("✅ SCRAPING COMPLETE!")
print("="*70)
print(f"📈 Total raw results: {len(combined)}")
print(f"🔗 Unique job URLs: {unique_count}")
print(f"🗑️  Duplicates removed: {duplicate_count}")
print(f"📁 Saved to: {raw_filename}")
print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================
# AUTO-PUSH TO GITHUB
# ============================================================

print("\n" + "="*70)
print("🚀 PUSHING TO GITHUB...")
print("="*70)

try:
    # Ensure data directory exists in repo
    data_dir = os.path.join(GITHUB_REPO, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Copy file to GitHub repo data/ folder
    dest_path = os.path.join(data_dir, raw_filename)
    shutil.copy(raw_filename, dest_path)
    print(f"📁 Copied to: {dest_path}")
    
    # Git add, commit, push
    subprocess.run(["git", "add", "."], cwd=GITHUB_REPO, check=True)
    subprocess.run(["git", "commit", "-m", f"Add raw jobs data {datetime.now().strftime('%Y-%m-%d')}"], cwd=GITHUB_REPO, check=True)
    subprocess.run(["git", "push"], cwd=GITHUB_REPO, check=True)
    
    print("✅ Pushed to GitHub!")
    print("🌐 Site will rebuild automatically - check GitHub Actions")
    print(f"   https://github.com/romelikethecity/croreport/actions")
    
except Exception as e:
    print(f"❌ GitHub push failed: {e}")
    print(f"📁 File saved locally: {raw_filename}")
    print("👉 Manually run:")
    print(f"   cd {GITHUB_REPO}")
    print(f"   cp {os.path.abspath(raw_filename)} data/")
    print("   git add . && git commit -m 'Add jobs' && git push")

print("="*70)
