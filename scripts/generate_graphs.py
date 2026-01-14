#!/usr/bin/env python3
"""
Executive Sales Trends Graph Generator
Generates multiple timeframe views with professional styling
Outputs to site/assets/ for GitHub Pages
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import glob

# ============================================================
# GITHUB ACTIONS CONFIGURATION
# ============================================================
DATA_DIR = "data"
SITE_ASSETS = "site/assets"

os.makedirs(SITE_ASSETS, exist_ok=True)

print("="*70)
print("📊 EXECUTIVE SALES TRENDS - GRAPH GENERATOR")
print("="*70)

# Load tracking data
tracking_file = f'{DATA_DIR}/Sales_Exec_Openings.csv'
if not os.path.exists(tracking_file):
    print(f"\n❌ ERROR: {tracking_file} not found")
    exit(1)

df = pd.read_csv(tracking_file)
df['Date'] = pd.to_datetime(df['Date'])
print(f"\n✅ Loaded {len(df)} data points")
print(f"📅 Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")

# Professional styling - matching The CRO Report brand
plt.style.use('dark_background')
colors = {
    'line': '#22d3ee',      # Cyan/teal
    'fill': '#0891b2',      # Darker cyan for fill
    'grid': '#374151',      # Dark gray grid
    'text': '#e5e7eb',      # Light gray text
    'highlight': '#f5a623', # Yellow/gold from logo
    'bg': '#1f2937'         # Dark background
}

def create_graph(df_subset, title, filename, show_annotations=True):
    """Create a professionally styled graph matching The CRO Report brand"""
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])
    
    # Plot line with area fill
    ax.plot(df_subset['Date'], df_subset['Sales Exec Openings'], 
            color=colors['line'], linewidth=3, label='Sales Exec Openings', zorder=3)
    ax.fill_between(df_subset['Date'], df_subset['Sales Exec Openings'], 
                     alpha=0.2, color=colors['fill'], zorder=2)
    
    # Styling with large fonts
    ax.set_title(title, fontsize=36, fontweight='bold', pad=30, color=colors['text'])
    ax.set_xlabel('', fontsize=24)
    ax.set_ylabel('Openings', fontsize=24, fontweight='bold', color=colors['text'])
    ax.grid(True, alpha=0.15, color=colors['grid'], linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(colors['grid'])
    ax.spines['left'].set_color(colors['grid'])
    ax.tick_params(colors=colors['text'], which='both', labelsize=20)
    
    if show_annotations:
        current_val = df_subset['Sales Exec Openings'].iloc[-1]
        current_date = df_subset['Date'].iloc[-1]
        
        # Yellow dot at current position
        ax.plot(current_date, current_val, 'o', color=colors['highlight'], 
                markersize=14, zorder=5, markeredgewidth=3, markeredgecolor=colors['bg'])
        
        # Label
        ax.text(1.01, 0.5, f'Sales Exec\nOpenings', 
               transform=ax.transAxes,
               fontsize=22, fontweight='bold', 
               color=colors['line'],
               verticalalignment='center')
        
        # Max marker for longer timeframes
        max_val = df_subset['Sales Exec Openings'].max()
        max_date = df_subset[df_subset['Sales Exec Openings'] == max_val]['Date'].iloc[0]
        if len(df_subset) > 90:
            ax.plot(max_date, max_val, 'o', color=colors['highlight'], 
                   markersize=12, zorder=5, alpha=0.7)
    
    # X-axis formatting based on timeframe
    days_spanned = (df_subset['Date'].max() - df_subset['Date'].min()).days
    
    if days_spanned > 365 * 2:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    elif days_spanned > 365:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    elif days_spanned > 180:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    elif days_spanned > 60:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    plt.xticks(rotation=45, ha='right', fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    
    # Save to site/assets/
    output_path = f"{SITE_ASSETS}/{filename}"
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'], edgecolor='none')
    print(f"✅ Saved: {output_path}")
    plt.close()

# ============================================================
# GENERATE ALL TIMEFRAMES
# ============================================================

print(f"\n{'GENERATING GRAPHS':-^70}")

# 1. ALL TIME
print("\n1. All-Time View")
create_graph(df, 'Executive Sales Market Trends - Complete History', 'trend_all_time.png')

# 2. LAST 12 MONTHS
print("\n2. Last 12 Months")
twelve_months_ago = df['Date'].max() - timedelta(days=365)
df_12m = df[df['Date'] >= twelve_months_ago]
if len(df_12m) > 0:
    create_graph(df_12m, 'Executive Sales Trends - Last 12 Months', 'trend_12_months.png')

# 3. LAST 6 MONTHS
print("\n3. Last 6 Months")
six_months_ago = df['Date'].max() - timedelta(days=180)
df_6m = df[df['Date'] >= six_months_ago]
if len(df_6m) > 0:
    create_graph(df_6m, 'Executive Sales Trends - Last 6 Months', 'trend_6_months.png')

# 4. LAST 90 DAYS
print("\n4. Last 90 Days")
ninety_days_ago = df['Date'].max() - timedelta(days=90)
df_90d = df[df['Date'] >= ninety_days_ago]
if len(df_90d) > 0:
    create_graph(df_90d, 'Executive Sales Trends - Last 90 Days', 'trend_90_days.png')

# 5. LAST 30 DAYS
print("\n5. Last 30 Days")
thirty_days_ago = df['Date'].max() - timedelta(days=30)
df_30d = df[df['Date'] >= thirty_days_ago]
if len(df_30d) > 0:
    create_graph(df_30d, 'Executive Sales Trends - Last 30 Days', 'trend_30_days.png')

# ============================================================
# SOCIAL PREVIEW
# ============================================================

def create_social_preview():
    """Create social preview image with highest paying job this week"""
    job_files = glob.glob(f'{DATA_DIR}/executive_sales_jobs_*.csv')
    if not job_files:
        print(f"\n⚠️  No jobs file found - skipping social preview")
        return
    
    latest_file = sorted(job_files)[-1]
    print(f"\n6. Social Preview")
    print(f"   Loading: {latest_file}")
    
    try:
        jobs_df = pd.read_csv(latest_file)
        
        if 'max_amount' not in jobs_df.columns:
            print("   ⚠️  No max_amount column found")
            return
        
        valid_jobs = jobs_df[jobs_df['max_amount'].notna() & (jobs_df['max_amount'] > 0)]
        
        if valid_jobs.empty:
            print("   ⚠️  No jobs with valid salary data")
            return
        
        top_job = valid_jobs.loc[valid_jobs['max_amount'].idxmax()]
        max_salary = int(top_job['max_amount'])
        salary_k = f"${max_salary // 1000}k"
        
        print(f"   Found top salary: {salary_k}")
        
        fig, ax = plt.subplots(figsize=(14.56, 10.48), facecolor=colors['bg'])
        ax.set_facecolor(colors['bg'])
        ax.axis('off')
        
        ax.text(0.5, 0.75, salary_k, 
               transform=ax.transAxes,
               fontsize=200, fontweight='bold', 
               color=colors['highlight'],
               horizontalalignment='center',
               verticalalignment='center')
        
        ax.text(0.5, 0.42, "This Week's\nHighest Paying Role", 
               transform=ax.transAxes,
               fontsize=65, fontweight='bold', 
               color=colors['text'],
               horizontalalignment='center',
               verticalalignment='center',
               linespacing=1.2)
        
        ax.text(0.5, 0.18, "The CRO Report", 
               transform=ax.transAxes,
               fontsize=50, fontweight='bold', 
               color=colors['line'],
               horizontalalignment='center',
               verticalalignment='center')
        
        plt.tight_layout(pad=0)
        output_path = f"{SITE_ASSETS}/social_preview.png"
        plt.savefig(output_path, dpi=100, bbox_inches='tight', 
                   facecolor=colors['bg'], edgecolor='none', pad_inches=0)
        print(f"✅ Saved: {output_path}")
        plt.close()
        
    except Exception as e:
        print(f"   ❌ Error creating social preview: {e}")

create_social_preview()

print(f"\n{'='*70}")
print("✅ ALL GRAPHS GENERATED!")
print(f"{'='*70}")
