#!/usr/bin/env python3
"""
CRO Report - Compensation Aggregator & Trend Analyzer
=====================================================

This script aggregates weekly job scraper exports into a master database
and generates compensation benchmarking analysis for the newsletter.

Usage:
    1. Weekly: python cro_comp_aggregator.py --add weekly_export.csv
    2. Analysis: python cro_comp_aggregator.py --analyze
    3. Newsletter: python cro_comp_aggregator.py --newsletter

Setup:
    - Create a folder for your data: mkdir ~/cro_report_data
    - Set DATA_DIR below to that path
    - Run --add after each weekly scrape
"""

import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION - GitHub Actions compatible paths
# ============================================================
DATA_DIR = Path("data")
SITE_ASSETS = Path("site/assets")
MASTER_DB = DATA_DIR / "master_jobs_database.csv"
ANALYSIS_OUTPUT = DATA_DIR / "comp_analysis.json"
NEWSLETTER_OUTPUT = DATA_DIR / "comp_newsletter_section.md"

# Chart output paths - save to site/assets for web display
CHART_SENIORITY = SITE_ASSETS / "comp_by_seniority.png"
CHART_STAGE = SITE_ASSETS / "comp_by_stage.png"
CHART_LOCATION = SITE_ASSETS / "comp_by_location.png"

# ============================================================
# CHART STYLING (matches existing newsletter charts)
# ============================================================
DARK_BG = '#FFFFFF'
CYAN = '#4dd0e1'
ORANGE = '#ffa726'
WHITE = '#ffffff'
GRAY = '#8899aa'
GRID_COLOR = '#2a3a4a'

def setup_chart_style():
    """Set up the dark theme matching existing charts with large fonts."""
    import matplotlib.pyplot as plt
    plt.rcParams['figure.facecolor'] = DARK_BG
    plt.rcParams['axes.facecolor'] = DARK_BG
    plt.rcParams['axes.edgecolor'] = GRID_COLOR
    plt.rcParams['axes.labelcolor'] = WHITE
    plt.rcParams['text.color'] = WHITE
    plt.rcParams['xtick.color'] = GRAY
    plt.rcParams['ytick.color'] = GRAY
    plt.rcParams['grid.color'] = GRID_COLOR
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 24

def generate_seniority_chart(analysis):
    """Create horizontal bar chart for comp by seniority."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    if not analysis.get('by_seniority'):
        print("No seniority data available for chart")
        return
    
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Prepare data
    levels = []
    mins = []
    maxs = []
    samples = []
    
    for level in ['VP', 'SVP', 'EVP', 'C-Level']:
        if level in analysis['by_seniority']:
            levels.append(level)
            mins.append(analysis['by_seniority'][level]['min_base_avg'])
            maxs.append(analysis['by_seniority'][level]['max_base_avg'])
            samples.append(analysis['by_seniority'][level]['count'])
    
    y_pos = np.arange(len(levels))
    
    # Draw range bars
    for i, (level, min_val, max_val, n) in enumerate(zip(levels, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=180, zorder=5)
        ax.scatter(max_val, i, color=ORANGE, s=180, zorder=5)
        ax.text(min_val - 22000, i, f'${min_val/1000:.0f}K', ha='right', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 22000, i, f'${max_val/1000:.0f}K', ha='left', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 110000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=20)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(levels, fontsize=26, fontweight='bold')
    ax.set_xlabel('Base Salary Range', fontsize=22, color=GRAY)
    ax.set_xlim(80000, 480000)
    ax.set_title('Compensation by Seniority Level', fontsize=32, color=TEXT_DARK, pad=30, fontweight='bold')
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=20)
    ax.grid(axis='x', alpha=0.3)
    
    min_patch = mpatches.Patch(color=CYAN, label='Min Base (Avg)')
    max_patch = mpatches.Patch(color=ORANGE, label='Max Base (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right', facecolor='#FFFFFF', edgecolor=GRID_COLOR, fontsize=18)
    
    plt.tight_layout()
    plt.savefig(CHART_SENIORITY, dpi=150, facecolor='#FFFFFF', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {CHART_SENIORITY}")

def generate_stage_chart(analysis):
    """Create horizontal bar chart for comp by company stage."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    if not analysis.get('by_company_stage'):
        print("No company stage data available for chart")
        return
    
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(18, 9))
    
    # Prepare data in order
    stage_order = ['Seed/Series A', 'Series A/B', 'Series B/C', 'Series C/D', 'Late Stage', 'Enterprise/Public']
    stages = []
    mins = []
    maxs = []
    samples = []
    
    for stage in stage_order:
        if stage in analysis['by_company_stage']:
            stages.append(stage)
            mins.append(analysis['by_company_stage'][stage]['min_base_avg'])
            maxs.append(analysis['by_company_stage'][stage]['max_base_avg'])
            samples.append(analysis['by_company_stage'][stage]['count'])
    
    # Reverse for display (Enterprise at top)
    stages = stages[::-1]
    mins = mins[::-1]
    maxs = maxs[::-1]
    samples = samples[::-1]
    
    y_pos = np.arange(len(stages))
    
    for i, (stage, min_val, max_val, n) in enumerate(zip(stages, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=180, zorder=5)
        ax.scatter(max_val, i, color=ORANGE, s=180, zorder=5)
        ax.text(min_val - 20000, i, f'${min_val/1000:.0f}K', ha='right', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 20000, i, f'${max_val/1000:.0f}K', ha='left', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 95000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=20)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages, fontsize=24, fontweight='bold')
    ax.set_xlabel('Base Salary Range', fontsize=22, color=GRAY)
    ax.set_xlim(60000, 450000)
    ax.set_title('Compensation by Company Stage', fontsize=32, color=TEXT_DARK, pad=30, fontweight='bold')
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add premium annotation
    if 'Enterprise/Public' in analysis['by_company_stage'] and 'Series B/C' in analysis['by_company_stage']:
        ent = analysis['by_company_stage']['Enterprise/Public']
        ser = analysis['by_company_stage']['Series B/C']
        ent_mid = (ent['min_base_avg'] + ent['max_base_avg']) / 2
        ser_mid = (ser['min_base_avg'] + ser['max_base_avg']) / 2
        premium = int((ent_mid - ser_mid) / ser_mid * 100)
        ax.annotate(f'+{premium}% Enterprise Premium', 
                    xy=(0.98, 0.02), xycoords='axes fraction',
                    ha='right', va='bottom', fontsize=20, color=ORANGE, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFFFFF', edgecolor=ORANGE, alpha=0.9, linewidth=2))
    
    min_patch = mpatches.Patch(color=CYAN, label='Min Base (Avg)')
    max_patch = mpatches.Patch(color=ORANGE, label='Max Base (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right', facecolor='#FFFFFF', edgecolor=GRID_COLOR, fontsize=18)
    
    plt.tight_layout()
    plt.savefig(CHART_STAGE, dpi=150, facecolor='#FFFFFF', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {CHART_STAGE}")

def generate_location_chart(analysis):
    """Create horizontal bar chart for comp by location."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    if not analysis.get('by_metro'):
        print("No location data available for chart")
        return
    
    setup_chart_style()
    fig, ax = plt.subplots(figsize=(18, 9))
    
    # Sort by max salary descending
    sorted_locations = sorted(analysis['by_metro'].items(), key=lambda x: x[1]['max_base_avg'], reverse=True)
    
    locations = [l[0] for l in sorted_locations]
    mins = [l[1]['min_base_avg'] for l in sorted_locations]
    maxs = [l[1]['max_base_avg'] for l in sorted_locations]
    samples = [l[1]['count'] for l in sorted_locations]
    
    y_pos = np.arange(len(locations))
    
    for i, (loc, min_val, max_val, n) in enumerate(zip(locations, mins, maxs, samples)):
        ax.barh(i, max_val - min_val, left=min_val, height=0.5, color=CYAN, alpha=0.8)
        ax.scatter(min_val, i, color=CYAN, s=180, zorder=5)
        ax.scatter(max_val, i, color=ORANGE, s=180, zorder=5)
        ax.text(min_val - 22000, i, f'${min_val/1000:.0f}K', ha='right', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 22000, i, f'${max_val/1000:.0f}K', ha='left', va='center', color=TEXT_DARK, fontsize=22, fontweight='bold')
        ax.text(max_val + 105000, i, f'n={n}', ha='left', va='center', color=GRAY, fontsize=20)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(locations, fontsize=24, fontweight='bold')
    ax.set_xlabel('Base Salary Range', fontsize=22, color=GRAY)
    
    # Dynamic x-axis limit based on data
    max_salary = max(maxs) if maxs else 500000
    ax.set_xlim(50000, max_salary + 160000)
    ax.set_title('Compensation by Location', fontsize=32, color=TEXT_DARK, pad=30, fontweight='bold')
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='x', labelsize=20)
    ax.grid(axis='x', alpha=0.3)
    
    min_patch = mpatches.Patch(color=CYAN, label='Min Base (Avg)')
    max_patch = mpatches.Patch(color=ORANGE, label='Max Base (Avg)')
    ax.legend(handles=[min_patch, max_patch], loc='lower right', facecolor='#FFFFFF', edgecolor=GRID_COLOR, fontsize=18)
    
    plt.tight_layout()
    plt.savefig(CHART_LOCATION, dpi=150, facecolor='#FFFFFF', edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {CHART_LOCATION}")

def generate_all_charts(analysis, current_week_csv=None):
    """Generate all compensation benchmark charts."""
    print("\nGenerating charts...")
    generate_seniority_chart(analysis)
    generate_stage_chart(analysis)
    generate_location_chart(analysis)

# ============================================================
# SENIORITY VALIDATION & CORRECTION
# ============================================================

# Titles that are definitely NOT C-Level regardless of what the scraper says
NON_EXECUTIVE_PATTERNS = [
    'account executive',
    'account director',
    'sales account',
    'account manager',
    'sales manager',
    'sr manager',
    'senior manager',
    'director of revenue accounting',
    'director of sales',
    'regional director',
    'area director',
    'solution sales',
    'solution executive',
]

# Bank title inflation: AVP at banks is NOT executive level
BANK_TITLE_INFLATION = [
    'avp,',  # "AVP, Account Sales Manager"
    'avp ',
    'assistant vice president',
]

# True C-Level title patterns
TRUE_C_LEVEL_PATTERNS = [
    'chief revenue officer',
    'chief sales officer', 
    'chief commercial officer',
    'chief growth officer',
    'chief business officer',
    'cro ',
    'cso ',
    'cco ',
    ' cro',
    ' cso',
]

def validate_seniority(row):
    """
    Validate and correct seniority classification.
    Returns corrected seniority level.
    """
    title = str(row.get('title', '')).lower()
    current_seniority = row.get('seniority', 'Unknown')
    min_amount = row.get('min_amount', 0)
    max_amount = row.get('max_amount', 0)
    
    # Convert to numeric
    try:
        min_amount = float(min_amount) if pd.notna(min_amount) else 0
        max_amount = float(max_amount) if pd.notna(max_amount) else 0
    except:
        min_amount = 0
        max_amount = 0
    
    # Check for bank title inflation (AVP at banks is NOT C-Level)
    for pattern in BANK_TITLE_INFLATION:
        if pattern in title:
            # AVP roles are typically individual contributor or first-line manager
            # Reclassify based on comp
            if max_amount < 200000:
                return 'Non-Executive'  # Will be filtered out
            else:
                return 'VP'  # Generous classification
    
    # Check for non-executive titles misclassified as C-Level
    if current_seniority == 'C-Level':
        for pattern in NON_EXECUTIVE_PATTERNS:
            if pattern in title:
                # Check if it's truly executive comp
                if max_amount >= 250000:
                    return 'VP'  # High-comp IC, classify as VP for analysis
                else:
                    return 'Non-Executive'  # Will be filtered out
        
        # Verify it's actually a C-Level title
        is_true_c_level = any(pattern in title for pattern in TRUE_C_LEVEL_PATTERNS)
        if not is_true_c_level:
            # Not a recognized C-Level title, check comp
            if max_amount >= 300000:
                return 'C-Level'  # Keep if comp supports it
            elif max_amount >= 200000:
                return 'SVP'
            else:
                return 'VP'
    
    # Comp-based sanity checks for other levels
    if current_seniority == 'SVP' and max_amount < 150000:
        return 'VP'
    
    if current_seniority == 'EVP' and max_amount < 200000:
        return 'SVP'
    
    return current_seniority

# ============================================================
# COMPANY STAGE CLASSIFICATION (IMPROVED)
# ============================================================

# Known acquisitions/late-stage companies often misclassified due to small employee count
KNOWN_LATE_STAGE_COMPANIES = {
    'fieldwire': 'Enterprise/Public',  # Acquired by Hilti for ~$300M in 2021
    'zoe financial': 'Series B/C',  # $30M+ raised, operating since 2018
    'chorus.ai': 'Enterprise/Public',  # Acquired by ZoomInfo
    'duo security': 'Enterprise/Public',  # Acquired by Cisco
}

def classify_company_stage(row):
    """
    Classify company into funding stage based on revenue, employee count,
    and known company data.
    """
    company = str(row.get('company', '')).lower().strip()
    rev = str(row.get('company_revenue', '')).lower()
    emp = str(row.get('company_num_employees', '')).lower()
    max_amount = row.get('max_amount', 0)
    
    # Convert max_amount to numeric
    try:
        max_amount = float(max_amount) if pd.notna(max_amount) else 0
    except:
        max_amount = 0
    
    # Check known companies first
    for known_company, stage in KNOWN_LATE_STAGE_COMPANIES.items():
        if known_company in company:
            return stage
    
    # Revenue-based classification (primary, most reliable)
    if 'less than $1m' in rev or '$1m to $5m' in rev:
        return 'Seed/Series A'
    elif '$5m to $25m' in rev:
        return 'Series A/B'
    elif '$25m to $100m' in rev:
        return 'Series B/C'
    elif '$100m to $500m' in rev:
        return 'Series C/D'
    elif '$500m to $1b' in rev:
        return 'Late Stage'
    elif '$1b to $5b' in rev or '$5b to $10b' in rev or 'more than $10b' in rev:
        return 'Enterprise/Public'
    
    # Comp-based inference (if no revenue data)
    # High comp at small company suggests later stage or well-funded
    if max_amount >= 350000:
        # Paying $350K+ base for VP Sales suggests Series C+ or well-funded
        if '2 to 10' in emp or '11 to 50' in emp:
            return 'Series B/C'  # Small but well-funded
        elif '51 to 200' in emp:
            return 'Series C/D'
        else:
            return 'Late Stage'
    
    # Fallback to employee count (least reliable)
    if '2 to 10' in emp or '11 to 50' in emp:
        # Small company with no revenue data
        # Check if comp suggests otherwise
        if max_amount >= 250000:
            return 'Series A/B'  # Higher comp suggests more funding
        return 'Seed/Series A'
    elif '51 to 200' in emp:
        return 'Series A/B'
    elif '201 to 500' in emp:
        return 'Series B/C'
    elif '501 to 1,000' in emp or '1,001 to 5,000' in emp:
        return 'Series C/D'
    elif '5,001 to 10,000' in emp or '10,000+' in emp:
        return 'Enterprise/Public'
    
    return 'Unknown'

def extract_metro(location):
    """Extract metro area from location string."""
    if pd.isna(location):
        return 'Unknown'
    
    location = str(location).lower()
    
    # Major metros
    if 'new york' in location or ', ny' in location:
        return 'New York'
    elif 'san francisco' in location or 'sf,' in location:
        return 'San Francisco'
    elif 'los angeles' in location or ', la' in location or 'santa monica' in location:
        return 'Los Angeles'
    elif 'boston' in location or ', ma' in location:
        return 'Boston'
    elif 'seattle' in location or ', wa' in location:
        return 'Seattle'
    elif 'chicago' in location or ', il' in location:
        return 'Chicago'
    elif 'austin' in location or 'dallas' in location or 'houston' in location or ', tx' in location:
        return 'Texas'
    elif 'denver' in location or ', co' in location:
        return 'Denver'
    elif 'atlanta' in location or ', ga' in location:
        return 'Atlanta'
    elif 'remote' in location:
        return 'Remote'
    else:
        return 'Other'

# ============================================================
# DATA MANAGEMENT
# ============================================================
def initialize_data_dir():
    """Create data and site/assets directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    print(f"Data directory: {DATA_DIR}")
    print(f"Assets directory: {SITE_ASSETS}")

def load_master_database():
    """Load the master database or create empty one."""
    if MASTER_DB.exists():
        df = pd.read_csv(MASTER_DB)
        print(f"Loaded master database: {len(df)} records")
        return df
    else:
        print("No master database found. Starting fresh.")
        return pd.DataFrame()

def save_master_database(df):
    """Save the master database."""
    df.to_csv(MASTER_DB, index=False)
    print(f"Saved master database: {len(df)} records")

def add_weekly_export(csv_path):
    """Add a weekly export to the master database with deduplication."""
    
    # Load new data
    new_df = pd.read_csv(csv_path)
    print(f"Loading weekly export: {len(new_df)} records from {csv_path}")
    
    # Add metadata
    new_df['import_date'] = datetime.now().strftime('%Y-%m-%d')
    new_df['import_week'] = datetime.now().strftime('%Y-W%W')
    
    # Enrich with classifications
    new_df['company_stage'] = new_df.apply(classify_company_stage, axis=1)
    new_df['metro'] = new_df['location'].apply(extract_metro)
    
    # Validate and correct seniority
    new_df['seniority_original'] = new_df['seniority']  # Keep original for debugging
    new_df['seniority'] = new_df.apply(validate_seniority, axis=1)
    
    # Report corrections
    corrections = new_df[new_df['seniority'] != new_df['seniority_original']]
    if len(corrections) > 0:
        print(f"\n⚠️  Corrected {len(corrections)} seniority classifications:")
        for _, row in corrections.head(10).iterrows():
            print(f"   {row['title'][:50]}... : {row['seniority_original']} → {row['seniority']}")
        if len(corrections) > 10:
            print(f"   ... and {len(corrections) - 10} more")
    
    # Load existing master
    master_df = load_master_database()
    
    if len(master_df) == 0:
        # First import
        save_master_database(new_df)
        print(f"Initialized master database with {len(new_df)} records")
        return new_df
    
    # Deduplicate based on job_url (unique identifier)
    existing_urls = set(master_df['job_url'].dropna().unique())
    new_records = new_df[~new_df['job_url'].isin(existing_urls)]
    
    print(f"Found {len(new_records)} new unique records (filtered {len(new_df) - len(new_records)} duplicates)")
    
    # Combine
    combined_df = pd.concat([master_df, new_records], ignore_index=True)
    save_master_database(combined_df)
    
    return combined_df

def revalidate_master_database():
    """Re-run validation on entire master database to fix historical misclassifications."""
    df = load_master_database()
    if len(df) == 0:
        print("No data to revalidate.")
        return df
    
    print(f"\nRevalidating {len(df)} records...")
    
    # Store originals
    df['seniority_original'] = df['seniority']
    df['company_stage_original'] = df['company_stage']
    
    # Re-run classifications
    df['seniority'] = df.apply(validate_seniority, axis=1)
    df['company_stage'] = df.apply(classify_company_stage, axis=1)
    
    # Report changes
    seniority_changes = df[df['seniority'] != df['seniority_original']]
    stage_changes = df[df['company_stage'] != df['company_stage_original']]
    
    print(f"\nSeniority corrections: {len(seniority_changes)}")
    if len(seniority_changes) > 0:
        print("Sample corrections:")
        for _, row in seniority_changes.head(5).iterrows():
            print(f"   {row['company']} - {row['title'][:40]}...")
            print(f"      {row['seniority_original']} → {row['seniority']}")
    
    print(f"\nCompany stage corrections: {len(stage_changes)}")
    if len(stage_changes) > 0:
        print("Sample corrections:")
        for _, row in stage_changes.head(5).iterrows():
            print(f"   {row['company']}: {row['company_stage_original']} → {row['company_stage']}")
    
    # Save corrected database
    save_master_database(df)
    print(f"\n✅ Revalidation complete. Database updated.")
    
    return df

# ============================================================
# COMPENSATION ANALYSIS
# ============================================================
def analyze_compensation(df):
    """Generate comprehensive compensation analysis."""
    
    # Filter to records with salary data
    salary_df = df[
        (df['min_amount'].notna()) & 
        (df['min_amount'] != '') &
        (pd.to_numeric(df['min_amount'], errors='coerce') > 0)
    ].copy()
    
    salary_df['min_amount'] = pd.to_numeric(salary_df['min_amount'], errors='coerce')
    salary_df['max_amount'] = pd.to_numeric(salary_df['max_amount'], errors='coerce')
    salary_df['midpoint'] = (salary_df['min_amount'] + salary_df['max_amount']) / 2
    
    # Filter out non-executive roles from seniority analysis
    executive_df = salary_df[salary_df['seniority'].isin(['C-Level', 'EVP', 'SVP', 'VP'])]
    print(f"Filtered to {len(executive_df)} executive roles (excluded {len(salary_df) - len(executive_df)} non-executive)")
    
    analysis = {
        'generated_at': datetime.now().isoformat(),
        'total_records': len(df),
        'records_with_salary': len(salary_df),
        'executive_records': len(executive_df),
        'disclosure_rate': round(len(salary_df) / len(df) * 100, 1) if len(df) > 0 else 0,
        'date_range': {
            'earliest': df['date_posted'].min() if 'date_posted' in df.columns else None,
            'latest': df['date_posted'].max() if 'date_posted' in df.columns else None
        },
        'by_seniority': {},
        'by_company_stage': {},
        'by_metro': {},
        'by_tech': {},
        'by_remote': {},
        'top_paying_roles': [],
        'weekly_trends': {}
    }
    
    # By Seniority (using executive_df only)
    for seniority in ['C-Level', 'EVP', 'SVP', 'VP']:
        seniority_df = executive_df[executive_df['seniority'] == seniority]
        if len(seniority_df) >= 3:  # Minimum sample size
            analysis['by_seniority'][seniority] = {
                'count': len(seniority_df),
                'min_base_avg': round(seniority_df['min_amount'].mean()),
                'max_base_avg': round(seniority_df['max_amount'].mean()),
                'min_base_median': round(seniority_df['min_amount'].median()),
                'max_base_median': round(seniority_df['max_amount'].median()),
                'range_low': round(seniority_df['min_amount'].min()),
                'range_high': round(seniority_df['max_amount'].max())
            }
    
    # By Company Stage (using executive_df, excluding Unknown)
    stage_df = executive_df[executive_df['company_stage'] != 'Unknown']
    for stage in ['Seed/Series A', 'Series A/B', 'Series B/C', 'Series C/D', 'Late Stage', 'Enterprise/Public']:
        stage_subset = stage_df[stage_df['company_stage'] == stage]
        if len(stage_subset) >= 3:
            analysis['by_company_stage'][stage] = {
                'count': len(stage_subset),
                'min_base_avg': round(stage_subset['min_amount'].mean()),
                'max_base_avg': round(stage_subset['max_amount'].mean()),
                'midpoint_avg': round(stage_subset['midpoint'].mean()),
                'by_seniority': {}
            }
            # Nested by seniority within stage
            for seniority in ['C-Level', 'SVP', 'VP']:
                nested_df = stage_subset[stage_subset['seniority'] == seniority]
                if len(nested_df) >= 2:
                    analysis['by_company_stage'][stage]['by_seniority'][seniority] = {
                        'count': len(nested_df),
                        'min_base_avg': round(nested_df['min_amount'].mean()),
                        'max_base_avg': round(nested_df['max_amount'].mean())
                    }
    
    # By Metro (using executive_df)
    for metro in executive_df['metro'].unique():
        if metro and metro != 'Unknown':
            metro_df = executive_df[executive_df['metro'] == metro]
            if len(metro_df) >= 3:
                analysis['by_metro'][metro] = {
                    'count': len(metro_df),
                    'min_base_avg': round(metro_df['min_amount'].mean()),
                    'max_base_avg': round(metro_df['max_amount'].mean())
                }
    
    # By Tech vs Non-Tech
    if 'is_tech' in executive_df.columns:
        for is_tech in [True, False]:
            label = 'Tech' if is_tech else 'Non-Tech'
            tech_df = executive_df[executive_df['is_tech'] == is_tech]
            if len(tech_df) >= 3:
                analysis['by_tech'][label] = {
                    'count': len(tech_df),
                    'min_base_avg': round(tech_df['min_amount'].mean()),
                    'max_base_avg': round(tech_df['max_amount'].mean())
                }
    
    # By Remote
    if 'is_remote' in executive_df.columns:
        for is_remote in [True, False]:
            label = 'Remote' if is_remote else 'On-site'
            remote_df = executive_df[executive_df['is_remote'] == is_remote]
            if len(remote_df) >= 3:
                analysis['by_remote'][label] = {
                    'count': len(remote_df),
                    'min_base_avg': round(remote_df['min_amount'].mean()),
                    'max_base_avg': round(remote_df['max_amount'].mean())
                }
    
    # Top Paying Roles (from executive roles only)
    top_roles = executive_df.nlargest(10, 'max_amount')[['title', 'company', 'min_amount', 'max_amount', 'seniority', 'company_stage']]
    analysis['top_paying_roles'] = top_roles.to_dict('records')
    
    # Weekly trends
    if 'import_week' in executive_df.columns:
        for week in executive_df['import_week'].unique():
            week_df = executive_df[executive_df['import_week'] == week]
            if len(week_df) >= 5:
                analysis['weekly_trends'][week] = {
                    'count': len(week_df),
                    'avg_min': round(week_df['min_amount'].mean()),
                    'avg_max': round(week_df['max_amount'].mean()),
                    'disclosure_rate': round(len(week_df) / len(df[df['import_week'] == week]) * 100, 1)
                }
    
    # Save analysis
    with open(ANALYSIS_OUTPUT, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"Analysis saved to {ANALYSIS_OUTPUT}")
    return analysis

# ============================================================
# NEWSLETTER SECTION GENERATOR
# ============================================================
def generate_newsletter_section(analysis, current_week_csv=None):
    """Generate markdown section for newsletter."""
    
    md = f"""# 💰 Compensation Benchmarking

**Data as of {datetime.now().strftime('%B %d, %Y')}** | {analysis['executive_records']} executive roles with disclosed salary out of {analysis['total_records']} total ({analysis['disclosure_rate']}% disclosure rate)

"""
    
    # By Seniority
    if analysis['by_seniority']:
        md += "## By Seniority Level\n\n"
        
        for level in ['C-Level', 'EVP', 'SVP', 'VP']:
            if level in analysis['by_seniority']:
                data = analysis['by_seniority'][level]
                md += f"**{level}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,} avg base\n\n"
    
    # By Company Stage
    if analysis['by_company_stage']:
        md += "## By Company Stage\n\n"
        
        for stage in ['Seed/Series A', 'Series A/B', 'Series B/C', 'Series C/D', 'Late Stage', 'Enterprise/Public']:
            if stage in analysis['by_company_stage']:
                data = analysis['by_company_stage'][stage]
                md += f"**{stage}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,} avg base\n\n"
        
        # Stage premium analysis
        stages = analysis['by_company_stage']
        if 'Series B/C' in stages and 'Enterprise/Public' in stages:
            growth_mid = stages['Series B/C']['midpoint_avg']
            enterprise_mid = stages['Enterprise/Public']['midpoint_avg']
            premium = round((enterprise_mid - growth_mid) / growth_mid * 100)
            md += f"**Enterprise Premium**: Enterprise/Public companies pay approximately {premium}% more than Series B/C companies at equivalent levels.\n\n"
    
    # By Metro
    if analysis['by_metro']:
        md += "## By Location\n\n"
        
        # Sort by avg max descending
        sorted_metros = sorted(analysis['by_metro'].items(), key=lambda x: x[1]['max_base_avg'], reverse=True)
        for metro, data in sorted_metros:
            md += f"**{metro}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,} avg base\n\n"
        
        # Remote discount analysis
        if 'Remote' in analysis['by_metro'] and 'New York' in analysis['by_metro']:
            remote_mid = (analysis['by_metro']['Remote']['min_base_avg'] + analysis['by_metro']['Remote']['max_base_avg']) / 2
            ny_mid = (analysis['by_metro']['New York']['min_base_avg'] + analysis['by_metro']['New York']['max_base_avg']) / 2
            discount = round((ny_mid - remote_mid) / ny_mid * 100)
            md += f"**Remote Discount**: Remote roles pay approximately {discount}% less than New York-based roles.\n\n"
    
    # Tech vs Non-Tech
    if analysis['by_tech']:
        md += "## Tech vs. Non-Tech\n\n"
        for label, data in analysis['by_tech'].items():
            md += f"**{label}** (n={data['count']}): ${data['min_base_avg']:,}-${data['max_base_avg']:,} avg base\n\n"
    
    # Top Paying Roles - from current week CSV if provided, otherwise from analysis
    md += "## Highest Paying Roles This Week\n\n"
    
    if current_week_csv:
        # Load current week's data for fresh top roles
        try:
            current_df = pd.read_csv(current_week_csv)
            current_df['min_amount'] = pd.to_numeric(current_df['min_amount'], errors='coerce')
            current_df['max_amount'] = pd.to_numeric(current_df['max_amount'], errors='coerce')
            
            # Apply seniority validation to current week data
            current_df['seniority'] = current_df.apply(validate_seniority, axis=1)
            
            # Filter to executive roles only
            current_executive = current_df[current_df['seniority'].isin(['C-Level', 'EVP', 'SVP', 'VP'])]
            current_salary_df = current_executive[current_executive['max_amount'].notna() & (current_executive['max_amount'] > 0)]
            top_roles = current_salary_df.nlargest(5, 'max_amount')[['title', 'company', 'min_amount', 'max_amount']]
            
            for i, (_, role) in enumerate(top_roles.iterrows(), 1):
                company = role['company'] if pd.notna(role['company']) and role['company'] else 'Undisclosed'
                md += f"{i}. **${role['min_amount']:,.0f}-${role['max_amount']:,.0f}**: {role['title']} @ {company}\n\n"
        except Exception as e:
            print(f"Warning: Could not load current week CSV for top roles: {e}")
            md += "*Unable to load current week's top roles*\n\n"
    elif analysis.get('top_paying_roles'):
        for i, role in enumerate(analysis['top_paying_roles'][:5], 1):
            company = role.get('company') if pd.notna(role.get('company')) and role.get('company') else 'Undisclosed'
            md += f"{i}. **${role['min_amount']:,.0f}-${role['max_amount']:,.0f}**: {role['title']} @ {company}\n\n"
    
    # Weekly Trends (if available)
    if analysis.get('weekly_trends') and len(analysis['weekly_trends']) > 1:
        md += "## Trend Analysis\n\n"
        weeks = sorted(analysis['weekly_trends'].keys())
        if len(weeks) >= 2:
            first_week = analysis['weekly_trends'][weeks[0]]
            last_week = analysis['weekly_trends'][weeks[-1]]
            
            change = round((last_week['avg_max'] - first_week['avg_max']) / first_week['avg_max'] * 100, 1)
            direction = "up" if change > 0 else "down"
            
            md += f"Over {len(weeks)} weeks of data, average max base is **{direction} {abs(change)}%** (${first_week['avg_max']:,} → ${last_week['avg_max']:,}).\n\n"
    
    # Negotiation guidance
    md += "## What This Means for Negotiations\n\n"
    
    if 'Series B/C' in analysis.get('by_company_stage', {}):
        data = analysis['by_company_stage']['Series B/C']
        md += f"**Growth Stage (Series B/C)**: Market for VP Sales is ${data['min_base_avg']:,}-${data['max_base_avg']:,} base. Push for 0.25-0.5% equity to offset the enterprise comp gap.\n\n"
    
    if 'Enterprise/Public' in analysis.get('by_company_stage', {}):
        data = analysis['by_company_stage']['Enterprise/Public']
        md += f"**Enterprise/Public**: ${data['min_base_avg']:,}-${data['max_base_avg']:,} base is standard for VP+. Below that, you're leaving money on the table.\n\n"
    
    md += """
*This analysis is based on disclosed salaries from The CRO Report job board. Actual offers may vary based on experience, location, and negotiation.*
"""
    
    # Save
    with open(NEWSLETTER_OUTPUT, 'w') as f:
        f.write(md)
    
    print(f"Newsletter section saved to {NEWSLETTER_OUTPUT}")
    return md

# ============================================================
# MAIN CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='CRO Report Compensation Aggregator')
    parser.add_argument('--add', type=str, help='Add a weekly CSV export to the master database')
    parser.add_argument('--analyze', action='store_true', help='Run compensation analysis on master database')
    parser.add_argument('--newsletter', type=str, nargs='?', const=None, help='Generate newsletter section. Optionally pass current week CSV for top paying roles.')
    parser.add_argument('--status', action='store_true', help='Show database status')
    parser.add_argument('--revalidate', action='store_true', help='Re-run validation on entire master database to fix historical misclassifications')
    
    args = parser.parse_args()
    
    initialize_data_dir()
    
    if args.add:
        df = add_weekly_export(args.add)
        print(f"\n✅ Import complete. Master database now has {len(df)} records.")
        print(f"   Run --analyze to generate compensation analysis.")
    
    elif args.revalidate:
        revalidate_master_database()
    
    elif args.analyze:
        df = load_master_database()
        if len(df) == 0:
            print("❌ No data in master database. Run --add first.")
            return
        analysis = analyze_compensation(df)
        print(f"\n✅ Analysis complete.")
        print(f"   {analysis['executive_records']} executive roles with salary data")
        print(f"   {len(analysis['by_company_stage'])} company stages analyzed")
        print(f"   Run --newsletter to generate the newsletter section.")
    
    elif args.newsletter is not None or '--newsletter' in sys.argv:
        if not ANALYSIS_OUTPUT.exists():
            print("❌ No analysis found. Run --analyze first.")
            return
        with open(ANALYSIS_OUTPUT) as f:
            analysis = json.load(f)
        
        # If current week CSV provided, use it for top paying roles
        current_week_csv = args.newsletter if args.newsletter else None
        
        # Generate charts
        generate_all_charts(analysis, current_week_csv)
        
        # Generate text section (backup only, images are primary)
        md = generate_newsletter_section(analysis, current_week_csv)
        
        print(f"\n✅ Newsletter assets generated!")
        print(f"   📊 Charts saved to: {DATA_DIR}")
        print(f"      - comp_by_seniority.png")
        print(f"      - comp_by_stage.png")
        print(f"      - comp_by_location.png")
        print(f"   📝 Text backup: {NEWSLETTER_OUTPUT}")
        if current_week_csv:
            print(f"   📋 Top paying roles pulled from: {current_week_csv}")
    
    elif args.status:
        df = load_master_database()
        if len(df) == 0:
            print("Database is empty. Run --add to import your first weekly export.")
        else:
            print(f"Master database: {len(df)} records")
            if 'import_week' in df.columns:
                print(f"Weeks covered: {df['import_week'].nunique()}")
                print(f"Date range: {df['date_posted'].min()} to {df['date_posted'].max()}")
            
            # Count executive vs non-executive
            exec_count = df[df['seniority'].isin(['C-Level', 'EVP', 'SVP', 'VP'])].shape[0]
            print(f"Executive roles: {exec_count} ({round(exec_count/len(df)*100, 1)}%)")
            
            salary_count = df[pd.to_numeric(df['min_amount'], errors='coerce') > 0].shape[0]
            print(f"Records with salary: {salary_count} ({round(salary_count/len(df)*100, 1)}%)")
    
    else:
        parser.print_help()
        print("\n" + "="*60)
        print("Quick Start:")
        print("  1. python cro_comp_aggregator.py --add your_weekly_export.csv")
        print("  2. python cro_comp_aggregator.py --analyze")
        print("  3. python cro_comp_aggregator.py --newsletter")
        print("\nNew Commands:")
        print("  --revalidate  Re-run validation on master DB to fix historical misclassifications")

if __name__ == "__main__":
    main()
