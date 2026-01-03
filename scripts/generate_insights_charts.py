#!/usr/bin/env python3
"""
Generate insight charts as images for newsletter inclusion.
Reads from market_intelligence.json and creates clean bar charts.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
SITE_ASSETS = Path("site/assets")

# Clean white style colors
NAVY = '#1E3A5F'
PURPLE = '#8B5CF6'
GREEN = '#22C55E'
GRAY = '#64748B'

def setup_style():
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.facecolor'] = '#FFFFFF'
    plt.rcParams['axes.edgecolor'] = '#E2E8F0'
    plt.rcParams['font.family'] = 'sans-serif'

def create_horizontal_bar_chart(data, title, color, output_path, max_items=10):
    """Create a clean horizontal bar chart."""
    if not data:
        print(f"No data for {title}")
        return
    
    setup_style()
    
    # Take top N items
    items = list(data.items())[:max_items]
    labels = [item[0] for item in items]
    values = [item[1] for item in items]
    
    # Reverse for horizontal bar (top item at top)
    labels = labels[::-1]
    values = values[::-1]
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(labels) * 0.6)))
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=color, height=0.6, alpha=0.9)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                str(val), va='center', ha='left', fontsize=12, fontweight='bold', color=GRAY)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=12, color=NAVY)
    ax.set_title(title, fontsize=18, fontweight='bold', color=NAVY, pad=20)
    
    # Clean up axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False, bottom=True)
    ax.set_xlim(0, max(values) * 1.15)
    ax.xaxis.set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"📊 Saved: {output_path}")

def main():
    # Load market intelligence data
    intel_file = DATA_DIR / "market_intelligence.json"
    if not intel_file.exists():
        print("❌ market_intelligence.json not found. Run generate_insights_page.py first.")
        return
    
    with open(intel_file) as f:
        data = json.load(f)
    
    print("="*60)
    print("📊 GENERATING INSIGHTS CHARTS")
    print("="*60)
    
    # Ensure output directory exists
    SITE_ASSETS.mkdir(parents=True, exist_ok=True)
    
    # Tools & Platforms
    if data.get('tools'):
        create_horizontal_bar_chart(
            data['tools'],
            'Tools & Platforms in Demand',
            NAVY,
            SITE_ASSETS / 'insights_tools.png',
            max_items=8
        )
    
    # Buzzwords/Trends
    if data.get('trends'):
        create_horizontal_bar_chart(
            data['trends'],
            '2025 Buzzwords & Trends',
            PURPLE,
            SITE_ASSETS / 'insights_buzzwords.png',
            max_items=10
        )
    
    # Industries
    if data.get('industries'):
        create_horizontal_bar_chart(
            data['industries'],
            'Industry Focus',
            GREEN,
            SITE_ASSETS / 'insights_industries.png',
            max_items=10
        )
    
    # Methodologies
    if data.get('methodologies'):
        create_horizontal_bar_chart(
            data['methodologies'],
            'Sales Methodologies Required',
            '#F59E0B',  # Amber
            SITE_ASSETS / 'insights_methodologies.png',
            max_items=8
        )
    
    print("\n✅ All insights charts generated!")

if __name__ == "__main__":
    main()
