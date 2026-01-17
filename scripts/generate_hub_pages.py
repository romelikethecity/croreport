#!/usr/bin/env python3
"""
Hub Page Generator for pSEO Architecture

Creates hub/index pages that serve as entry points to salary data categories:
- /salaries/by-location/ - All location-based salary pages
- /salaries/by-seniority/ - All seniority-level pages
- /salaries/by-stage/ - All company stage pages
- /trends/ - Salary trends over time

Uses templates.py for consistent site design.
"""

import json
import os
from datetime import datetime

# Import shared templates
from templates import (
    get_html_head,
    get_nav_html,
    get_footer_html,
    CSS_VARIABLES,
    CSS_NAV,
    CSS_LAYOUT,
    CSS_CARDS,
    CSS_CTA,
    CSS_FOOTER
)
from seo_core import generate_breadcrumb_schema

MIN_JOBS_FOR_LISTING = 5

def load_comp_data():
    """Load compensation analysis data."""
    with open('data/comp_analysis.json', 'r') as f:
        return json.load(f)

def fmt_salary(amount):
    """Format salary as $XXXk."""
    if not amount:
        return "N/A"
    return f"${int(amount/1000)}K"

# Hub page specific CSS
HUB_PAGE_CSS = '''
    /* Header */
    .header {
        background: linear-gradient(135deg, var(--navy-medium) 0%, var(--navy-hover) 100%);
        color: white;
        padding: 60px 20px;
        text-align: center;
    }
    .header .eyebrow {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--gold-dark);
        margin-bottom: 12px;
    }
    .header h1 {
        font-family: 'Fraunces', serif;
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .header p { opacity: 0.9; max-width: 600px; margin: 0 auto; }

    /* Hub Content */
    .hub-content {
        max-width: 1100px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    .hub-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 24px;
        margin-top: 30px;
    }

    .hub-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        transition: all 0.2s;
        display: block;
    }

    .hub-card:hover {
        border-color: var(--gold);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .hub-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }

    .hub-card h3 {
        font-family: 'Fraunces', serif;
        font-size: 1.25rem;
        color: var(--navy);
        margin: 0;
    }

    .job-count {
        background: var(--gray-100);
        color: var(--gray-700);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .salary-range {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--green-dark);
        margin-bottom: 8px;
    }

    .card-meta {
        font-size: 0.85rem;
        color: var(--gray-500);
    }

    .hub-intro {
        background: var(--white);
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 40px;
    }

    .hub-intro h2 {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        color: var(--navy-medium);
        margin-bottom: 16px;
    }

    .hub-intro p {
        color: var(--gray-700);
        line-height: 1.7;
        margin: 0;
    }

    /* CTA Section */
    .cta-section {
        background: linear-gradient(135deg, var(--navy-medium) 0%, var(--navy-hover) 100%);
        color: white;
        padding: 48px;
        border-radius: 16px;
        text-align: center;
        margin: 40px 0;
    }
    .cta-section h2 { color: white; margin-bottom: 12px; font-family: 'Fraunces', serif; }
    .cta-section p { opacity: 0.9; margin-bottom: 24px; }
    .cta-btn {
        display: inline-block;
        background: var(--gold-dark);
        color: white;
        padding: 14px 32px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
    }
    .cta-btn:hover { background: #c2660a; }
'''

# Trends page specific CSS
TRENDS_PAGE_CSS = '''
    /* Header */
    .header {
        background: linear-gradient(135deg, var(--navy-medium) 0%, var(--navy-hover) 100%);
        color: white;
        padding: 60px 20px;
        text-align: center;
    }
    .header h1 {
        font-family: 'Fraunces', serif;
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .header p { opacity: 0.9; max-width: 600px; margin: 0 auto; }

    .trends-content {
        max-width: 1000px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    .stats-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }

    .stat-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }

    .stat-value {
        font-family: 'Fraunces', serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--navy);
    }

    .stat-label {
        font-size: 0.85rem;
        color: var(--gray-600);
        margin-top: 8px;
    }

    .chart-container {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 30px;
        margin: 30px 0;
    }

    .trends-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 30px;
        background: var(--white);
        border-radius: 12px;
        overflow: hidden;
    }

    .trends-table th, .trends-table td {
        padding: 16px;
        text-align: left;
        border-bottom: 1px solid var(--gray-200);
    }

    .trends-table th {
        background: var(--gray-50);
        font-weight: 600;
        color: var(--navy);
    }

    .methodology {
        background: var(--white);
        border-radius: 12px;
        padding: 32px;
        margin-top: 40px;
    }

    .methodology h2 {
        font-family: 'Fraunces', serif;
        color: var(--navy-medium);
        margin-bottom: 16px;
    }

    .methodology p {
        color: var(--gray-700);
        line-height: 1.7;
        margin-bottom: 12px;
    }

    /* CTA Section */
    .cta-section {
        background: linear-gradient(135deg, var(--navy-medium) 0%, var(--navy-hover) 100%);
        color: white;
        padding: 48px;
        border-radius: 16px;
        text-align: center;
        margin: 40px 0;
    }
    .cta-section h2 { color: white; margin-bottom: 12px; font-family: 'Fraunces', serif; }
    .cta-section p { opacity: 0.9; margin-bottom: 24px; }
    .cta-btn {
        display: inline-block;
        background: var(--gold-dark);
        color: white;
        padding: 14px 32px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
    }
'''

def generate_hub_page(hub_type, title, description, intro_text, items, page_path, breadcrumbs):
    """Generate a hub page with links to all child pages."""

    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Sort items by count (most data first)
    items = sorted(items, key=lambda x: x.get('count', 0), reverse=True)

    items_html = ""
    for item in items:
        items_html += f"""
        <a href="{item['url']}" class="hub-card">
            <div class="hub-card-header">
                <h3>{item['name']}</h3>
                <span class="job-count">{item['count']} roles</span>
            </div>
            <div class="salary-range">
                {fmt_salary(item.get('avg_min'))} - {fmt_salary(item.get('avg_max'))}
            </div>
            <div class="card-meta">Average base salary range</div>
        </a>
        """

    # Build breadcrumb HTML for display
    breadcrumb_html = ' → '.join([f'<a href="{b["url"]}">{b["name"]}</a>' for b in breadcrumbs[:-1]]) + f' → {breadcrumbs[-1]["name"]}'

    html_head = get_html_head(title, description, page_path, include_styles=False)

    html = f'''{html_head}
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {HUB_PAGE_CSS}
    </style>
    {breadcrumb_schema}

{get_nav_html('salaries')}

    <div class="header">
        <div class="eyebrow">Salary Benchmarks</div>
        <h1>{title}</h1>
        <p>{description}</p>
    </div>

    <main class="hub-content">
        <nav class="breadcrumb" style="padding: 16px 0 0; font-size: 0.85rem; color: var(--gray-500);">
            {breadcrumb_html}
        </nav>

        <div class="hub-intro">
            <h2>About This Data</h2>
            <p>{intro_text}</p>
        </div>

        <div class="hub-grid">
            {items_html}
        </div>

        <div class="cta-section">
            <h2>Get Full Compensation Intelligence</h2>
            <p>Weekly analysis of compensation trends, red flags, and negotiation insights for VP Sales and CRO roles.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </main>

{get_footer_html()}'''

    return html

def generate_trends_page(data):
    """Generate the salary trends page."""
    weekly_data = data.get('weekly_trends', {})

    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Salary Trends', 'url': '/trends/'}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    # Build trend chart data (sorted by week)
    sorted_weeks = sorted(weekly_data.keys())
    chart_labels = []
    chart_data_min = []
    chart_data_max = []

    for week in sorted_weeks:
        stats = weekly_data[week]
        label = week.replace('-W', ' Week ')
        chart_labels.append(f'"{label}"')
        chart_data_min.append(str(int(stats.get('avg_min', 0) / 1000)))
        chart_data_max.append(str(int(stats.get('avg_max', 0) / 1000)))

    # Calculate overall stats
    total_count = sum(w.get('count', 0) for w in weekly_data.values())
    avg_disclosure = sum(w.get('disclosure_rate', 0) for w in weekly_data.values()) / len(weekly_data) if weekly_data else 0

    title = "VP Sales Salary Trends"
    description = f"Track weekly VP Sales and CRO salary trends. See how executive compensation is changing over time based on {total_count}+ job postings."
    page_path = "trends/"

    # Build table rows
    table_rows = ""
    for week in sorted_weeks:
        w = weekly_data[week]
        table_rows += f'''<tr>
            <td>{week.replace("-W", " Week ")}</td>
            <td>{w.get("count", 0)}</td>
            <td>{fmt_salary(w.get("avg_min"))}</td>
            <td>{fmt_salary(w.get("avg_max"))}</td>
            <td>{w.get("disclosure_rate", 0):.1f}%</td>
        </tr>'''

    html_head = get_html_head(title, description, page_path, include_styles=False)

    html = f'''{html_head}
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {TRENDS_PAGE_CSS}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    {breadcrumb_schema}

{get_nav_html('salaries')}

    <div class="header">
        <h1>VP Sales Salary Trends</h1>
        <p>Weekly compensation data from executive sales job postings</p>
    </div>

    <main class="trends-content">
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-value">{total_count}</div>
                <div class="stat-label">Jobs Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(weekly_data)}</div>
                <div class="stat-label">Weeks of Data</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(avg_disclosure)}%</div>
                <div class="stat-label">Avg Disclosure Rate</div>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="trendsChart"></canvas>
        </div>

        <table class="trends-table">
            <thead>
                <tr>
                    <th>Week</th>
                    <th>Jobs Posted</th>
                    <th>Avg Min Base</th>
                    <th>Avg Max Base</th>
                    <th>Disclosure Rate</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <div class="methodology">
            <h2>Data Methodology</h2>
            <p>Our salary data comes from actual job postings that disclose compensation ranges. We track VP Sales, SVP Sales, CRO, and EVP Sales positions posted on major job boards.</p>
            <p>Unlike self-reported salary surveys, our data reflects what companies are actually offering in the market. This tends to be 10-15% lower than self-reported figures, as employees often round up or include bonuses in their reported base salary.</p>
            <p>Data is updated weekly, with each data point representing the average of all disclosed salary ranges for that period.</p>
        </div>

        <div class="cta-section">
            <h2>Get Weekly Trends in Your Inbox</h2>
            <p>Subscribe for weekly analysis of compensation trends, executive movements, and market intelligence.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </main>

{get_footer_html()}

    <script>
        const ctx = document.getElementById('trendsChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: [{','.join(chart_labels)}],
                datasets: [
                    {{
                        label: 'Avg Max Base ($K)',
                        data: [{','.join(chart_data_max)}],
                        borderColor: '#1e3a5f',
                        backgroundColor: 'rgba(30, 58, 95, 0.1)',
                        fill: true,
                        tension: 0.3
                    }},
                    {{
                        label: 'Avg Min Base ($K)',
                        data: [{','.join(chart_data_min)}],
                        borderColor: '#4a90a4',
                        backgroundColor: 'rgba(74, 144, 164, 0.1)',
                        fill: true,
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Weekly Salary Trends (Base in $K)'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: 'Salary ($K)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html

def main():
    """Generate all hub pages."""
    data = load_comp_data()
    generated = []

    # Generate by-location hub
    location_items = []
    for location, stats in data.get('by_metro', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_LISTING:
            location_items.append({
                'name': location,
                'url': f"/salaries/vp-sales-salary-{location.lower().replace(' ', '-')}/",
                'count': stats.get('count'),
                'avg_min': stats.get('min_base_avg'),
                'avg_max': stats.get('max_base_avg')
            })

    if location_items:
        html = generate_hub_page(
            'location',
            'VP Sales Salary by Location',
            'Compare VP Sales and CRO salaries across major US metros.',
            'Our location-based salary data shows how VP Sales compensation varies by geography. Major tech hubs like San Francisco and New York typically pay premium rates, while markets like Chicago and Denver offer competitive compensation with better cost-of-living ratios. Remote roles have become increasingly common, with varying approaches to geographic pay adjustment.',
            location_items,
            'salaries/by-location/',
            [{'name': 'Home', 'url': '/'}, {'name': 'Salaries', 'url': '/salaries/'}, {'name': 'By Location', 'url': '/salaries/by-location/'}]
        )
        os.makedirs('site/salaries/by-location', exist_ok=True)
        with open('site/salaries/by-location/index.html', 'w') as f:
            f.write(html)
        generated.append('/salaries/by-location/')
        print("Generated: /salaries/by-location/")

    # Generate by-stage hub
    stage_items = []
    for stage, stats in data.get('by_company_stage', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_LISTING:
            stage_items.append({
                'name': stage,
                'url': f"/salaries/vp-sales-salary-{stage.lower().replace('/', '-').replace(' ', '-')}/",
                'count': stats.get('count'),
                'avg_min': stats.get('min_base_avg'),
                'avg_max': stats.get('max_base_avg')
            })

    if stage_items:
        html = generate_hub_page(
            'stage',
            'VP Sales Salary by Company Stage',
            'Compare VP Sales compensation at startups vs. enterprises.',
            'Company stage significantly impacts VP Sales compensation structure. Early-stage startups (Seed through Series B) typically offer lower base salaries but compensate with meaningful equity. Growth-stage companies (Series C/D) often pay competitive base with moderate equity. Public companies offer the highest base salaries with RSU grants and comprehensive benefits.',
            stage_items,
            'salaries/by-stage/',
            [{'name': 'Home', 'url': '/'}, {'name': 'Salaries', 'url': '/salaries/'}, {'name': 'By Company Stage', 'url': '/salaries/by-stage/'}]
        )
        os.makedirs('site/salaries/by-stage', exist_ok=True)
        with open('site/salaries/by-stage/index.html', 'w') as f:
            f.write(html)
        generated.append('/salaries/by-stage/')
        print("Generated: /salaries/by-stage/")

    # Generate by-seniority hub
    seniority_items = []
    for seniority, stats in data.get('by_seniority', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_LISTING:
            seniority_items.append({
                'name': seniority,
                'url': f"/salaries/{seniority.lower()}-sales-salary/",
                'count': stats.get('count'),
                'avg_min': stats.get('min_base_avg'),
                'avg_max': stats.get('max_base_avg')
            })

    if seniority_items:
        html = generate_hub_page(
            'seniority',
            'Sales Salary by Seniority Level',
            'Compare compensation across VP, SVP, EVP, and C-level sales roles.',
            'Seniority level is one of the strongest predictors of sales leadership compensation. VP roles show the widest range due to varying scope definitions. SVP roles typically manage multiple teams or larger organizations. C-level roles (CRO, Chief Commercial Officer) carry full revenue responsibility and command premium compensation.',
            seniority_items,
            'salaries/by-seniority/',
            [{'name': 'Home', 'url': '/'}, {'name': 'Salaries', 'url': '/salaries/'}, {'name': 'By Seniority', 'url': '/salaries/by-seniority/'}]
        )
        os.makedirs('site/salaries/by-seniority', exist_ok=True)
        with open('site/salaries/by-seniority/index.html', 'w') as f:
            f.write(html)
        generated.append('/salaries/by-seniority/')
        print("Generated: /salaries/by-seniority/")

    # Generate trends page
    html = generate_trends_page(data)
    os.makedirs('site/trends', exist_ok=True)
    with open('site/trends/index.html', 'w') as f:
        f.write(html)
    generated.append('/trends/')
    print("Generated: /trends/")

    print(f"\n✓ Generated {len(generated)} hub pages")
    return generated

if __name__ == "__main__":
    main()
