#!/usr/bin/env python3
"""
Generate trend graphs for The CRO Report
Outputs to site/assets/ for GitHub Pages
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os

DATA_DIR = 'data'
ASSETS_DIR = 'site/assets'

print("="*70)
print("📊 GENERATING TREND GRAPHS")
print("="*70)

# Ensure output directory exists
os.makedirs(ASSETS_DIR, exist_ok=True)

tracking_file = f'{DATA_DIR}/Sales_Exec_Openings.csv'
if not os.path.exists(tracking_file):
    print(f"⚠️  No tracking file found at {tracking_file}")
    exit(0)

df = pd.read_csv(tracking_file)
df['Date'] = pd.to_datetime(df['Date'])
print(f"✅ Loaded {len(df)} data points")

# Professional styling - CRO Report brand
plt.style.use('dark_background')
colors = {
    'line': '#22d3ee',
    'fill': '#0891b2',
    'grid': '#374151',
    'text': '#e5e7eb',
    'highlight': '#f5a623',
    'bg': '#1f2937'
}

def create_graph(df_subset, title, filename, show_annotations=True):
    """Create a professionally styled graph"""
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])
    
    ax.plot(df_subset['Date'], df_subset['Sales Exec Openings'], 
            color=colors['line'], linewidth=3, zorder=3)
    ax.fill_between(df_subset['Date'], df_subset['Sales Exec Openings'], 
                     alpha=0.2, color=colors['fill'], zorder=2)
    
    ax.set_title(title, fontsize=36, fontweight='bold', pad=30, color=colors['text'])
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
        
        ax.plot(current_date, current_val, 'o', color=colors['highlight'], 
                markersize=14, zorder=5, markeredgewidth=3, markeredgecolor=colors['bg'])
        
        ax.text(1.01, 0.5, f'Sales Exec\nOpenings', 
               transform=ax.transAxes, fontsize=22, fontweight='bold', 
               color=colors['line'], verticalalignment='center')
        
        if len(df_subset) > 90:
            max_val = df_subset['Sales Exec Openings'].max()
            max_date = df_subset[df_subset['Sales Exec Openings'] == max_val]['Date'].iloc[0]
            ax.plot(max_date, max_val, 'o', color=colors['highlight'], 
                   markersize=12, zorder=5, alpha=0.7)
    
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
    
    output_path = f'{ASSETS_DIR}/{filename}'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=colors['bg'])
    print(f"✅ Saved: {output_path}")
    plt.close()

# Generate graphs
print("\n1. All-Time View")
create_graph(df, 'Executive Sales Market Trends - Complete History', 'trend_all_time.png')

print("\n2. Last 90 Days")
ninety_days_ago = df['Date'].max() - timedelta(days=90)
df_90d = df[df['Date'] >= ninety_days_ago]
create_graph(df_90d, 'Executive Sales Trends - Last 90 Days', 'trend_90_days.png')

print("\n✅ ALL GRAPHS GENERATED")
