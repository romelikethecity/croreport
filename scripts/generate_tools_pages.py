#!/usr/bin/env python3
"""
Generate GTM Tools pages for programmatic SEO
Creates:
- /tools/ index page with 5 categories
- /tools/[tool-slug]/ individual tool pages
- /tools/[tool]-alternatives/ alternatives pages
- /tools/[tool-a]-vs-[tool-b]/ comparison pages (skips if custom_url exists)

Categories: AI SDR, Data Enrichment, Conversation Intelligence, Sales Engagement, CRM & RevOps
"""

import json
import os
from datetime import datetime

from templates import (
    get_html_head,
    get_nav_html,
    get_footer_html,
    get_base_styles,
    get_cta_box,
    BASE_URL,
    CSS_VARIABLES,
    CSS_NAV,
    CSS_LAYOUT,
    CSS_CARDS,
    CSS_CTA,
    CSS_FOOTER,
)

DATA_DIR = 'data'
SITE_DIR = 'site'
TOOLS_DIR = f'{SITE_DIR}/tools'

print("="*70)
print("GENERATING GTM TOOLS PAGES")
print("="*70)

os.makedirs(TOOLS_DIR, exist_ok=True)

# Load tools data
tools_file = f'{DATA_DIR}/tools.json'
if not os.path.exists(tools_file):
    print(f"No tools.json found at {tools_file}")
    exit(1)

with open(tools_file) as f:
    data = json.load(f)

tools_list = data['tools']
tools = {t['slug']: t for t in tools_list}
categories = data['categories']
alternatives = data['alternatives']
comparisons = data['comparisons']

update_date = datetime.now().strftime('%B %d, %Y')

# Group tools by category
tools_by_category = {}
for cat in categories:
    tools_by_category[cat['slug']] = [t for t in tools_list if t['category'] == cat['name']]

# Group comparisons by category
comparisons_by_category = {}
for comp in comparisons:
    tool_a = tools.get(comp['tool_a'].lower().replace(' ', '-').replace('.', ''))
    if tool_a:
        cat_slug = None
        for cat in categories:
            if cat['name'] == tool_a['category']:
                cat_slug = cat['slug']
                break
        if cat_slug:
            if cat_slug not in comparisons_by_category:
                comparisons_by_category[cat_slug] = []
            comparisons_by_category[cat_slug].append(comp)


# =============================================================================
# TOOLS-SPECIFIC CSS (extends base styles)
# =============================================================================

TOOLS_CSS = '''
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    .section-header h2 {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--navy);
    }

    .section-icon { font-size: 1.4rem; }

    .section-description {
        color: var(--gray-600);
        margin-bottom: 24px;
        max-width: 650px;
        font-size: 0.95rem;
    }

    /* Tool Cards Grid */
    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
    }

    @media (max-width: 768px) {
        .tools-grid { grid-template-columns: 1fr; }
    }

    .tool-card {
        display: flex;
        flex-direction: column;
    }

    .tool-card.coming-soon { opacity: 0.6; }

    .tool-card h3 {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--navy);
        margin-bottom: 8px;
    }

    .tool-card p {
        font-size: 0.9rem;
        color: var(--gray-600);
        line-height: 1.55;
        flex-grow: 1;
    }

    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--gray-100);
    }

    .card-meta { font-size: 0.8rem; color: var(--gray-500); }
    .card-link { font-size: 0.85rem; font-weight: 600; color: var(--gold-muted); }

    /* Card Logos */
    .card-logos {
        display: flex;
        gap: 10px;
        margin-bottom: 16px;
    }

    .card-logo {
        width: 40px;
        height: 40px;
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .card-logo img {
        max-width: 32px;
        max-height: 32px;
        object-fit: contain;
    }

    /* Pros/Cons */
    .pros-cons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        margin: 24px 0;
    }
    @media (max-width: 600px) { .pros-cons { grid-template-columns: 1fr; } }

    .pros, .cons {
        background: var(--white);
        border-radius: 10px;
        padding: 20px;
    }
    .pros { border: 1px solid var(--green); }
    .cons { border: 1px solid var(--red); }

    .pros h4, .cons h4 { font-size: 0.95rem; margin-bottom: 12px; }
    .pros h4 { color: var(--green); }
    .cons h4 { color: var(--red); }

    .pros ul, .cons ul { list-style: none; }
    .pros li, .cons li { padding: 6px 0; font-size: 0.9rem; }
    .pros li::before { content: '✓ '; color: var(--green); font-weight: 600; }
    .cons li::before { content: '✗ '; color: var(--red); font-weight: 600; }

    /* Info Card */
    .info-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }

    .info-card h3 {
        font-size: 1.1rem;
        color: var(--navy);
        margin-bottom: 16px;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid var(--gray-100);
    }

    .info-row:last-child { border-bottom: none; }
    .info-label { color: var(--gray-500); font-size: 0.9rem; }
    .info-value { font-weight: 500; font-size: 0.9rem; }
    .info-value a { color: var(--gold-muted); }

    /* Comparison Table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 24px 0;
        background: var(--white);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--gray-200);
    }

    .comparison-table th {
        background: var(--navy);
        color: var(--white);
        padding: 14px 16px;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .comparison-table td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--gray-200);
        font-size: 0.9rem;
    }

    .comparison-table tr:last-child td { border-bottom: none; }
    .comparison-table tr:nth-child(even) { background: var(--gray-50); }
    .winner { color: var(--green); font-weight: 600; }
'''


def get_tools_styles():
    """Get combined CSS for tools pages"""
    return f'''
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {TOOLS_CSS}
    </style>
'''


def generate_tool_card(tool, badge_type='soon', badge_text='Tool Review'):
    """Generate a single tool card"""
    logo_html = ''
    if tool.get('logo'):
        logo_html = f'''
            <div class="card-logos">
                <div class="card-logo"><img src="{tool['logo']}" alt="{tool['name']}"></div>
            </div>'''

    # Use different link text for in-depth reviews
    link_text = 'Read Analysis →' if badge_type == 'live' else 'View Details →'

    return f'''
        <a href="/tools/{tool['slug']}/" class="tool-card">
            <span class="card-badge badge-{badge_type}">{badge_text}</span>
            {logo_html}
            <h3>{tool['name']}</h3>
            <p>{tool['description']}</p>
            <div class="card-footer">
                <span class="card-meta">{tool['pricing'][:30]}...</span>
                <span class="card-link">{link_text}</span>
            </div>
        </a>
'''


def generate_comparison_card(comp, tools_dict, update_date):
    """Generate a comparison card"""
    has_custom = comp.get('custom_url')
    url = comp['custom_url'] if has_custom else f"/tools/{comp['slug']}/"
    badge = 'live' if has_custom else 'comparison'
    badge_text = 'In-Depth' if has_custom else 'Comparison'

    # Get logos for the tools
    tool_a_slug = comp['tool_a'].lower().replace(' ', '-').replace('.', '')
    tool_b_slug = comp['tool_b'].lower().replace(' ', '-').replace('.', '')
    tool_a_data = tools_dict.get(tool_a_slug, {})
    tool_b_data = tools_dict.get(tool_b_slug, {})

    logo_a = tool_a_data.get('logo', '')
    logo_b = tool_b_data.get('logo', '')

    logos_html = ''
    if logo_a or logo_b:
        logos_html = '<div class="card-logos">'
        if logo_a:
            logos_html += f'<div class="card-logo"><img src="{logo_a}" alt="{comp["tool_a"]}"></div>'
        if logo_b:
            logos_html += f'<div class="card-logo"><img src="{logo_b}" alt="{comp["tool_b"]}"></div>'
        logos_html += '</div>'

    return f'''
        <a href="{url}" class="tool-card">
            <span class="card-badge badge-{badge}">{badge_text}</span>
            {logos_html}
            <h3>{comp['title']}</h3>
            <p>{comp['description']}</p>
            <div class="card-footer">
                <span class="card-meta">Updated {update_date[:3]} {datetime.now().year}</span>
                <span class="card-link">Read Analysis →</span>
            </div>
        </a>
'''


def generate_category_section(cat, cat_tools, cat_comparisons, tools_dict, update_date):
    """Generate a category section with tools and comparisons"""
    cards_html = ''

    # Add comparison cards for this category
    for comp in cat_comparisons:
        cards_html += generate_comparison_card(comp, tools_dict, update_date)

    # Add individual tool cards if few comparisons
    if len(cat_comparisons) < 2:
        for tool in cat_tools[:3]:
            # Use 'live' badge and 'In-Depth' text for tools with custom pages
            if tool.get('custom_page'):
                cards_html += generate_tool_card(tool, badge_type='live', badge_text='In-Depth')
            else:
                cards_html += generate_tool_card(tool)

    return f'''
        <div class="section">
            <div class="section-header">
                <span class="section-icon">{cat.get('icon', '')}</span>
                <h2>{cat['name']}</h2>
            </div>
            <p class="section-description">{cat['description']}</p>

            <div class="tools-grid">
{cards_html}
            </div>
        </div>
'''


# ============================================================
# 1. TOOLS INDEX PAGE - 5 Categories
# ============================================================

print("\n1. Generating tools index page...")

# Count stats
total_tools = len(tools_list)
total_comparisons = len(comparisons)
live_comparisons = len([c for c in comparisons if c.get('custom_url')])
num_categories = len(categories)

index_html = get_html_head(
    "GTM Tools & Reviews",
    "Honest reviews of AI SDRs, sales engagement platforms, and GTM tools for revenue leaders. Real pricing, user complaints, and recommendations by company stage.",
    "tools/",
    include_styles=False
)
index_html += get_tools_styles()
index_html += get_nav_html('tools')

index_html += f'''
    <section class="page-header">
        <div class="container">
            <div class="page-label">Tool Reviews</div>
            <h1>GTM Tools & Reviews</h1>
            <p class="lead">The tools your team uses matter more than most vendors want to admit. We dig into real pricing, user complaints, and contract terms so you don't have to learn the hard way.</p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">{total_tools}</div>
                    <div class="stat-label">Tools Reviewed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{total_comparisons}</div>
                    <div class="stat-label">Comparisons</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number green">{live_comparisons}</div>
                    <div class="stat-label">In-Depth Analyses</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number gold">{num_categories}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        </div>
    </section>

    <main>
        <div class="container">
'''

# Generate sections for each category
for cat in categories:
    cat_tools = tools_by_category.get(cat['slug'], [])
    cat_comparisons = comparisons_by_category.get(cat['slug'], [])
    index_html += generate_category_section(cat, cat_tools, cat_comparisons, tools, update_date)

# AI Assessments section
index_html += '''
        <div class="section">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h2>AI Assessments</h2>
            </div>
            <p class="section-description">Evaluate your team's readiness for AI-powered revenue operations</p>
            <div class="tools-grid">
                <a href="/assessment/" class="tool-card">
                    <span class="card-badge badge-live">Interactive</span>
                    <h3>AI Readiness Scorecard</h3>
                    <p>15-question assessment to benchmark your RevOps team's AI readiness. Get personalized recommendations based on your data quality, adoption level, and team capability.</p>
                    <div class="card-footer">
                        <span class="card-meta">3 min assessment</span>
                        <span class="card-link">Take Assessment →</span>
                    </div>
                </a>
            </div>
        </div>
'''

# CTA section
index_html += '''
            <div class="cta-box">
                <h3>Want a Tool Reviewed?</h3>
                <p>We're building this section based on what revenue leaders actually need.</p>
                <a href="mailto:rome@thecroreport.com?subject=Tool Review Request" class="btn btn-gold">Request a Review</a>
            </div>

        </div>
    </main>
'''

index_html += get_footer_html()

with open(f'{TOOLS_DIR}/index.html', 'w') as f:
    f.write(index_html)

print("  Created tools index page")


# ============================================================
# 2. INDIVIDUAL TOOL PAGES
# ============================================================

print("\n2. Generating individual tool pages...")

skipped_tools = 0
for tool in tools_list:
    # Skip if this tool has a custom (manually created) page
    if tool.get('custom_page'):
        print(f"   Skipping {tool['slug']} (has custom page)")
        skipped_tools += 1
        continue

    tool_dir = f"{TOOLS_DIR}/{tool['slug']}"
    os.makedirs(tool_dir, exist_ok=True)

    pros_html = ''.join([f'<li>{p}</li>' for p in tool.get('pros', [])])
    cons_html = ''.join([f'<li>{c}</li>' for c in tool.get('cons', [])])

    logo_html = ''
    if tool.get('logo'):
        logo_html = f'<img src="{tool["logo"]}" alt="{tool["name"]}" style="width: 64px; height: 64px; border-radius: 12px; margin-bottom: 16px;">'

    html = get_html_head(
        f"{tool['name']} Review",
        f"{tool['description']} Pricing, pros, cons, and alternatives.",
        f"tools/{tool['slug']}/",
        include_styles=False
    )
    html += get_tools_styles()
    html += get_nav_html('tools')

    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {tool['name']}
            </nav>
            <div class="page-label">{tool['category']}</div>
            {logo_html}
            <h1>{tool['name']}</h1>
            <p class="lead">{tool['description']}</p>
        </div>
    </section>

    <main>
        <div class="container-narrow">
            <div class="info-card">
                <h3>Quick Facts</h3>
                <div class="info-row">
                    <span class="info-label">Best For</span>
                    <span class="info-value">{tool['best_for']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Pricing</span>
                    <span class="info-value">{tool['pricing']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Category</span>
                    <span class="info-value">{tool['category']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Website</span>
                    <span class="info-value"><a href="{tool['website']}" target="_blank" rel="noopener">{tool['website']}</a></span>
                </div>
            </div>

            <div class="pros-cons">
                <div class="pros">
                    <h4>✓ Pros</h4>
                    <ul>{pros_html}</ul>
                </div>
                <div class="cons">
                    <h4>✗ Cons</h4>
                    <ul>{cons_html}</ul>
                </div>
            </div>

            {get_cta_box("Get Weekly Tool Reviews", "Honest assessments of GTM tools from a practitioner perspective.", "Subscribe to The CRO Report")}
        </div>
    </main>
'''
    html += get_footer_html()

    with open(f'{tool_dir}/index.html', 'w') as f:
        f.write(html)

print(f"  Created {len(tools_list) - skipped_tools} individual tool pages (skipped {skipped_tools} with custom pages)")


# ============================================================
# 3. ALTERNATIVES PAGES
# ============================================================

print("\n3. Generating alternatives pages...")

for alt in alternatives:
    alt_dir = f"{TOOLS_DIR}/{alt['slug']}"
    os.makedirs(alt_dir, exist_ok=True)

    alts_html = ''
    for alt_name in alt['alternatives']:
        alt_slug = alt_name.lower().replace('.', '').replace(' ', '-')
        alt_tool = tools.get(alt_slug, {})
        if alt_tool:
            logo_html = ''
            if alt_tool.get('logo'):
                logo_html = f'<div class="card-logo"><img src="{alt_tool["logo"]}" alt="{alt_name}"></div>'

            # Use 'live' badge for tools with custom pages
            if alt_tool.get('custom_page'):
                badge_class = 'badge-live'
                badge_text = 'In-Depth'
                link_text = 'Read Analysis →'
            else:
                badge_class = 'badge-soon'
                badge_text = 'Alternative'
                link_text = 'View Details →'

            alts_html += f'''
                <a href="/tools/{alt_slug}/" class="tool-card">
                    <span class="card-badge {badge_class}">{badge_text}</span>
                    {f'<div class="card-logos">{logo_html}</div>' if logo_html else ''}
                    <h3>{alt_name}</h3>
                    <p>{alt_tool.get('description', '')}</p>
                    <div class="card-footer">
                        <span class="card-meta">{alt_tool.get('pricing', 'Contact for pricing')[:30]}...</span>
                        <span class="card-link">{link_text}</span>
                    </div>
                </a>
'''

    points_html = ''.join([f'<li style="padding: 8px 0;">{p}</li>' for p in alt['comparison_points']])

    html = get_html_head(
        alt['title'],
        f"{alt['description']} Compare pricing, features, and find the best fit.",
        f"tools/{alt['slug']}/",
        include_styles=False
    )
    html += get_tools_styles()
    html += get_nav_html('tools')

    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {alt['title']}
            </nav>
            <div class="page-label">Alternatives</div>
            <h1>{alt['title']}</h1>
            <p class="lead">{alt['description']}</p>
        </div>
    </section>

    <main>
        <div class="container">
            <div class="tools-grid">
                {alts_html}
            </div>

            <div class="container-narrow" style="margin-top: 40px;">
                <h2 style="color: var(--navy); margin-bottom: 16px;">How to Choose</h2>
                <ul style="margin: 16px 0; padding-left: 24px; color: var(--gray-600);">
                    {points_html}
                </ul>

                {get_cta_box("Need Help Choosing?", "Get tool recommendations tailored to your team size and budget.", "Subscribe to The CRO Report")}
            </div>
        </div>
    </main>
'''
    html += get_footer_html()

    with open(f'{alt_dir}/index.html', 'w') as f:
        f.write(html)

print(f"  Created {len(alternatives)} alternatives pages")


# ============================================================
# 4. COMPARISON PAGES (skip if custom_url exists)
# ============================================================

print("\n4. Generating comparison pages...")

generated_comparisons = 0
skipped_comparisons = 0

for comp in comparisons:
    # Skip if this comparison has a custom (manually created) page
    if comp.get('custom_url'):
        print(f"   Skipping {comp['slug']} (has custom page at {comp['custom_url']})")
        skipped_comparisons += 1
        continue

    comp_dir = f"{TOOLS_DIR}/{comp['slug']}"
    os.makedirs(comp_dir, exist_ok=True)

    tool_a_slug = comp['tool_a'].lower().replace('.', '').replace(' ', '-')
    tool_b_slug = comp['tool_b'].lower().replace('.', '').replace(' ', '-')
    tool_a = tools.get(tool_a_slug, {'name': comp['tool_a']})
    tool_b = tools.get(tool_b_slug, {'name': comp['tool_b']})

    winner_rows = ''
    for category, winner in comp.get('winner_for', {}).items():
        cat_name = category.replace('_', ' ').title()
        winner_rows += f'''
                    <tr>
                        <td>{cat_name}</td>
                        <td class="{'winner' if winner == comp['tool_a'] else ''}">{comp['tool_a']}</td>
                        <td class="{'winner' if winner == comp['tool_b'] else ''}">{comp['tool_b']}</td>
                    </tr>
'''

    html = get_html_head(
        comp['title'],
        f"{comp['description']} Features, pricing, and which is better for your team.",
        f"tools/{comp['slug']}/",
        include_styles=False
    )
    html += get_tools_styles()
    html += get_nav_html('tools')

    html += f'''
    <section class="page-header">
        <div class="container-narrow">
            <nav class="breadcrumb">
                <a href="/">Home</a> → <a href="/tools/">Tools</a> → {comp['title']}
            </nav>
            <div class="page-label">Comparison</div>
            <h1>{comp['title']}</h1>
            <p class="lead">{comp['description']}</p>
        </div>
    </section>

    <main>
        <div class="container-narrow">
            <h2 style="color: var(--navy); margin-bottom: 16px;">Quick Comparison</h2>

            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Factor</th>
                        <th>{comp['tool_a']}</th>
                        <th>{comp['tool_b']}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Category</td>
                        <td>{tool_a.get('category', 'N/A')}</td>
                        <td>{tool_b.get('category', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td>Pricing</td>
                        <td>{tool_a.get('pricing', 'Contact')}</td>
                        <td>{tool_b.get('pricing', 'Contact')}</td>
                    </tr>
                    <tr>
                        <td>Best For</td>
                        <td>{tool_a.get('best_for', 'N/A')}</td>
                        <td>{tool_b.get('best_for', 'N/A')}</td>
                    </tr>
                </tbody>
            </table>

            <h2 style="color: var(--navy); margin: 32px 0 16px;">Winner By Use Case</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Use Case</th>
                        <th>{comp['tool_a']}</th>
                        <th>{comp['tool_b']}</th>
                    </tr>
                </thead>
                <tbody>
                    {winner_rows}
                </tbody>
            </table>

            {get_cta_box("Get Tool Recommendations", "Weekly analysis of GTM tools and trends for sales leaders.", "Subscribe to The CRO Report")}
        </div>
    </main>
'''
    html += get_footer_html()

    with open(f'{comp_dir}/index.html', 'w') as f:
        f.write(html)

    generated_comparisons += 1

print(f"  Created {generated_comparisons} comparison pages (skipped {skipped_comparisons} with custom URLs)")


# ============================================================
# SUMMARY
# ============================================================

generated_tools = len(tools_list) - skipped_tools
total_pages = 1 + generated_tools + len(alternatives) + generated_comparisons
print(f"\n{'='*70}")
print(f"TOOLS SECTION COMPLETE")
print(f"Generated {total_pages} tool pages:")
print(f"   - 1 index page (5 categories)")
print(f"   - {generated_tools} individual tool pages ({skipped_tools} skipped - using custom pages)")
print(f"   - {len(alternatives)} alternatives pages")
print(f"   - {generated_comparisons} comparison pages")
print(f"   - {skipped_comparisons} comparisons skipped (using custom pages)")
print(f"{'='*70}")
