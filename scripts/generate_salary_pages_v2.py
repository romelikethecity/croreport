#!/usr/bin/env python3
"""
Enhanced Salary Page Generator v2 with pSEO optimizations:
- Schema.org markup (Dataset, FAQPage, BreadcrumbList)
- Data-driven FAQ sections
- Internal linking engine
- Content enrichment based on actual data
"""

import json
import os
from datetime import datetime
from seo_core import (
    generate_breadcrumb_schema,
    generate_faq_schema,
    generate_salary_dataset_schema,
    generate_salary_faqs,
    get_related_salary_pages,
    generate_related_pages_html,
    generate_faq_html,
    get_seo_styles
)

# Minimum jobs required to create a page (avoid thin content)
MIN_JOBS_FOR_PAGE = 5

def load_comp_data():
    """Load compensation analysis data."""
    with open('data/comp_analysis.json', 'r') as f:
        return json.load(f)

def fmt_salary(amount):
    """Format salary as $XXXk."""
    if not amount:
        return "N/A"
    return f"${int(amount/1000)}K"

def get_national_averages(data):
    """Calculate national averages for comparison."""
    all_metros = data.get('by_metro', {})
    total_count = 0
    weighted_min = 0
    weighted_max = 0

    for metro, stats in all_metros.items():
        count = stats.get('count', 0)
        total_count += count
        weighted_min += stats.get('min_base_avg', 0) * count
        weighted_max += stats.get('max_base_avg', 0) * count

    if total_count > 0:
        return {
            'national_avg_min': weighted_min / total_count,
            'national_avg_max': weighted_max / total_count
        }
    return {}

def generate_location_context(location, data):
    """Generate contextual content for a location."""
    context = ""

    location_contexts = {
        'San Francisco': "San Francisco remains the highest-paying market for sales leadership, driven by the concentration of well-funded startups and enterprise tech companies. Competition for talent is fierce, with many companies offering premium packages to attract proven leaders.",
        'New York': "New York offers strong compensation for sales executives, particularly in fintech, media, and enterprise software. The market benefits from a large pool of enterprise buyers and established sales cultures.",
        'Boston': "Boston's sales leadership market is anchored by its thriving biotech, healthcare tech, and enterprise software sectors. The city's strong university system creates a pipeline of analytical sales talent.",
        'Seattle': "Seattle's sales executive market is influenced by major tech employers and a growing startup ecosystem. Remote-friendly policies have made the market more competitive nationally.",
        'Chicago': "Chicago offers solid compensation for sales leaders, particularly in B2B SaaS and manufacturing tech. Lower cost of living compared to coastal cities provides better purchasing power.",
        'Denver': "Denver has emerged as a sales leadership hub, with many companies establishing sales headquarters there. The combination of talent availability and quality of life drives relocation.",
        'Texas': "Texas markets (Austin, Dallas, Houston) offer competitive compensation with no state income tax, effectively increasing take-home pay by 5-10% versus coastal markets.",
        'Atlanta': "Atlanta's sales market is growing rapidly, with many companies establishing regional headquarters. Strong talent availability and reasonable costs make it attractive for scaling sales teams.",
        'Los Angeles': "Los Angeles offers diverse opportunities across entertainment tech, ecommerce, and enterprise software. The market is more distributed than SF, with multiple tech hubs.",
        'Remote': "Remote sales leadership roles have become standard post-2020. Compensation varies significantly based on company policy—some offer location-adjusted pay, others pay at headquarters rates regardless of location."
    }

    context = location_contexts.get(location, f"{location} offers competitive compensation for sales leadership roles, with variations based on company stage and industry.")

    return f"""
    <section class="location-context">
        <h2>Sales Leadership Market: {location}</h2>
        <p>{context}</p>
    </section>
    """

def generate_stage_context(stage, data):
    """Generate contextual content for a company stage."""
    stage_contexts = {
        'Seed/Series A': """
            <p>Early-stage companies (Seed through Series A) typically offer lower base salaries but compensate with significant equity grants. Expect 0.5-2% equity for VP-level hires, with 4-year vesting and 1-year cliff standard.</p>
            <p><strong>Key considerations:</strong> Evaluate equity value realistically—most startups don't reach IPO. Focus on the team, market opportunity, and your ability to influence outcomes. Cash runway matters: ensure the company can pay your salary for 18+ months.</p>
        """,
        'Series A/B': """
            <p>Series A/B companies are typically finding product-market fit and scaling initial go-to-market. Sales leaders at this stage often build the foundational sales playbook and hire the first dedicated sales team.</p>
            <p><strong>Key considerations:</strong> Equity grants range from 0.25-1%. Look for clear paths to the next funding round and realistic revenue targets. Your impact on company trajectory is significant at this stage.</p>
        """,
        'Series B/C': """
            <p>Series B/C companies are scaling proven go-to-market motions. Sales leadership roles focus on building repeatable processes, expanding into new segments, and professionalizing the sales organization.</p>
            <p><strong>Key considerations:</strong> Equity grants of 0.1-0.5% are typical. Evaluate the path to profitability or IPO. These companies offer a balance of growth potential and relative stability.</p>
        """,
        'Series C/D': """
            <p>Late-stage private companies (Series C/D) often pay near-public-company rates while still offering meaningful equity upside. These roles typically involve managing larger teams and more complex go-to-market strategies.</p>
            <p><strong>Key considerations:</strong> Equity grants may be 0.05-0.25%. Assess secondary sale opportunities and realistic IPO/acquisition timelines. Many offer competitive benefits packages.</p>
        """,
        'Late Stage': """
            <p>Late-stage companies preparing for IPO or acquisition offer the most predictable compensation. Base salaries are competitive with public companies, and equity has clearer near-term liquidity potential.</p>
            <p><strong>Key considerations:</strong> Evaluate lockup periods post-IPO and understand the stock's likely trading dynamics. These roles suit leaders who want upside with reduced early-stage risk.</p>
        """,
        'Enterprise/Public': """
            <p>Public and large enterprise companies offer the highest base salaries and most comprehensive benefits. Compensation is more standardized with clear bands and annual refresh grants.</p>
            <p><strong>Key considerations:</strong> RSU grants typically vest over 4 years with annual refreshes. Total compensation is more predictable but upside is limited compared to pre-IPO companies. Focus on scope, title progression, and team size.</p>
        """
    }

    context = stage_contexts.get(stage, f"<p>{stage} companies offer varying compensation based on their specific situation and growth trajectory.</p>")

    return f"""
    <section class="stage-context">
        <h2>Compensation at {stage} Companies</h2>
        {context}
    </section>
    """

def generate_seniority_context(seniority, data):
    """Generate contextual content for a seniority level."""
    seniority_contexts = {
        'VP': """
            <p>Vice President of Sales roles vary significantly in scope—from managing a single team of 5-10 reps to overseeing multiple sales functions with 50+ headcount. This range explains the wide salary spread.</p>
            <p><strong>Typical responsibilities:</strong> Quota ownership, team hiring and development, sales process optimization, cross-functional collaboration with marketing and customer success, executive reporting.</p>
            <p><strong>Career path:</strong> VP Sales typically leads to SVP Sales, CRO, or CEO roles, depending on company trajectory and individual goals.</p>
        """,
        'SVP': """
            <p>Senior Vice President of Sales roles typically involve broader organizational scope than VP roles, often including multiple sales teams, sales operations, and sometimes sales enablement or development.</p>
            <p><strong>Typical responsibilities:</strong> Multi-team leadership, strategic planning, board reporting, GTM strategy, executive hiring, large deal involvement.</p>
            <p><strong>Career path:</strong> SVP Sales commonly leads to CRO or President roles, with some transitioning to CEO positions, especially at sales-led organizations.</p>
        """,
        'C-Level': """
            <p>Chief Revenue Officer (CRO) roles encompass full revenue responsibility, typically including Sales, Customer Success, and sometimes Marketing and Partnerships. These are true executive roles with board exposure.</p>
            <p><strong>Typical responsibilities:</strong> Full P&L ownership, board presentations, strategic planning, executive team leadership, major customer relationships, investor relations support.</p>
            <p><strong>Key differentiator:</strong> CRO compensation often includes significant equity components and may include board observer or advisory roles.</p>
        """,
        'EVP': """
            <p>Executive Vice President roles sit between SVP and C-level, often found at larger organizations. These roles typically manage multiple SVPs or large regional organizations.</p>
            <p><strong>Typical scope:</strong> EVP Sales might oversee Americas, EMEA, or APAC regions, or manage both enterprise and commercial sales organizations.</p>
        """
    }

    context = seniority_contexts.get(seniority, f"<p>{seniority} level roles offer competitive compensation based on scope and company stage.</p>")

    return f"""
    <section class="seniority-context">
        <h2>{seniority} Sales Leadership Roles</h2>
        {context}
    </section>
    """

def generate_salary_page_v2(page_type, identifier, stats, all_pages, data):
    """Generate an enhanced salary page with full pSEO optimization."""

    count = stats.get('count', 0)
    if count < MIN_JOBS_FOR_PAGE:
        return None  # Skip thin content pages

    avg_min = stats.get('min_base_avg')
    avg_max = stats.get('max_base_avg')

    # Determine page title and slug
    if page_type == 'location':
        title = f"VP Sales Salary in {identifier}"
        slug = f"vp-sales-salary-{identifier.lower().replace(' ', '-')}"
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Salaries', 'url': '/salaries/'},
            {'name': 'By Location', 'url': '/salaries/by-location/'},
            {'name': identifier, 'url': f'/salaries/{slug}/'}
        ]
        context_html = generate_location_context(identifier, data)
        faqs = generate_salary_faqs(
            role_title="VP Sales",
            location=identifier,
            avg_min=avg_min,
            avg_max=avg_max,
            sample_count=count,
            comparison_data=get_national_averages(data)
        )
    elif page_type == 'stage':
        title = f"VP Sales Salary at {identifier} Companies"
        slug = f"vp-sales-salary-{identifier.lower().replace('/', '-').replace(' ', '-')}"
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Salaries', 'url': '/salaries/'},
            {'name': 'By Company Stage', 'url': '/salaries/by-stage/'},
            {'name': identifier, 'url': f'/salaries/{slug}/'}
        ]
        context_html = generate_stage_context(identifier, data)
        faqs = generate_salary_faqs(
            role_title="VP Sales",
            stage=identifier,
            avg_min=avg_min,
            avg_max=avg_max,
            sample_count=count
        )
    elif page_type == 'seniority':
        title = f"{identifier} Sales Salary Benchmarks"
        slug = f"{identifier.lower().replace('-', '-')}-sales-salary"
        breadcrumbs = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Salaries', 'url': '/salaries/'},
            {'name': 'By Seniority', 'url': '/salaries/by-seniority/'},
            {'name': identifier, 'url': f'/salaries/{slug}/'}
        ]
        context_html = generate_seniority_context(identifier, data)
        faqs = generate_salary_faqs(
            role_title=f"{identifier} Sales",
            avg_min=avg_min,
            avg_max=avg_max,
            sample_count=count
        )
    else:
        return None

    # Build page metadata
    page_data = {
        'type': page_type,
        'slug': slug,
        'title': title,
        'avg_min': avg_min,
        'avg_max': avg_max,
        'count': count
    }

    # Generate related pages
    related_pages = get_related_salary_pages(page_data, all_pages)

    # Generate schema markup
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)
    dataset_schema = generate_salary_dataset_schema(
        title=title,
        description=f"Salary benchmarks for {title.lower()} based on {count} job postings with disclosed compensation.",
        record_count=count,
        url=f"/salaries/{slug}/"
    )
    faq_html = generate_faq_html(faqs, include_schema=True)
    related_html = generate_related_pages_html(related_pages)

    # Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | The CRO Report</title>
    <meta name="description" content="{title}: {fmt_salary(avg_min)} - {fmt_salary(avg_max)} base salary based on {count} job postings. Updated {datetime.now().strftime('%B %Y')}.">
    <link rel="canonical" href="https://thecroreport.com/salaries/{slug}/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/styles.css">
    {breadcrumb_schema}
    {dataset_schema}
    <style>
        {get_seo_styles()}

        .salary-hero {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-medium) 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}

        .salary-hero h1 {{
            font-family: 'Fraunces', serif;
            font-size: 2.5rem;
            margin-bottom: 16px;
        }}

        .salary-range {{
            font-size: 2rem;
            font-weight: 700;
            margin: 24px 0;
        }}

        .salary-meta {{
            font-size: 0.95rem;
            opacity: 0.9;
        }}

        .content-section {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--navy);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--gray-600);
            margin-top: 8px;
        }}

        .location-context, .stage-context, .seniority-context {{
            background: var(--gray-50);
            border-radius: 12px;
            padding: 32px;
            margin: 40px 0;
        }}

        .location-context h2, .stage-context h2, .seniority-context h2 {{
            font-family: 'Fraunces', serif;
            font-size: 1.5rem;
            color: var(--navy-medium);
            margin-bottom: 16px;
        }}

        .location-context p, .stage-context p, .seniority-context p {{
            color: var(--gray-700);
            line-height: 1.7;
            margin-bottom: 12px;
        }}
    </style>
</head>
<body>
    <nav class="main-nav">
        <div class="nav-container">
            <a href="/" class="nav-logo">The CRO Report</a>
            <div class="nav-links">
                <a href="/jobs/">Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/tools/">Tools</a>
                <a href="/companies/">Companies</a>
            </div>
        </div>
    </nav>

    <header class="salary-hero">
        <h1>{title}</h1>
        <div class="salary-range">{fmt_salary(avg_min)} - {fmt_salary(avg_max)}</div>
        <p class="salary-meta">Based on {count} job postings with disclosed compensation • Updated {datetime.now().strftime('%B %Y')}</p>
    </header>

    <main class="content-section">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{fmt_salary(avg_min)}</div>
                <div class="stat-label">Average Minimum Base</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{fmt_salary(avg_max)}</div>
                <div class="stat-label">Average Maximum Base</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{fmt_salary((avg_min + avg_max) / 2 if avg_min and avg_max else 0)}</div>
                <div class="stat-label">Midpoint</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{count}</div>
                <div class="stat-label">Job Postings Analyzed</div>
            </div>
        </div>

        {context_html}

        {faq_html}

        {related_html}
    </main>

    <footer class="main-footer">
        <div class="footer-container">
            <p>&copy; {datetime.now().year} The CRO Report. Data updated weekly from job postings with disclosed compensation.</p>
        </div>
    </footer>
</body>
</html>"""

    return {'slug': slug, 'html': html, 'title': title, 'count': count}

def main():
    """Generate all enhanced salary pages."""
    data = load_comp_data()

    # Collect all page metadata for internal linking
    all_pages = []

    # Build page list for all categories
    for location, stats in data.get('by_metro', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_PAGE:
            all_pages.append({
                'type': 'location',
                'slug': f"vp-sales-salary-{location.lower().replace(' ', '-')}",
                'title': f"VP Sales Salary in {location}",
                'avg_max': stats.get('max_base_avg'),
                'count': stats.get('count')
            })

    for stage, stats in data.get('by_company_stage', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_PAGE:
            all_pages.append({
                'type': 'stage',
                'slug': f"vp-sales-salary-{stage.lower().replace('/', '-').replace(' ', '-')}",
                'title': f"VP Sales Salary at {stage} Companies",
                'avg_max': stats.get('max_base_avg'),
                'count': stats.get('count')
            })

    for seniority, stats in data.get('by_seniority', {}).items():
        if stats.get('count', 0) >= MIN_JOBS_FOR_PAGE:
            all_pages.append({
                'type': 'seniority',
                'slug': f"{seniority.lower()}-sales-salary",
                'title': f"{seniority} Sales Salary Benchmarks",
                'avg_max': stats.get('max_base_avg'),
                'count': stats.get('count')
            })

    generated = []

    # Generate location pages
    for location, stats in data.get('by_metro', {}).items():
        result = generate_salary_page_v2('location', location, stats, all_pages, data)
        if result:
            output_dir = f"site/salaries/{result['slug']}"
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/index.html", 'w') as f:
                f.write(result['html'])
            generated.append(result)
            print(f"Generated: /salaries/{result['slug']}/ ({result['count']} jobs)")

    # Generate company stage pages
    for stage, stats in data.get('by_company_stage', {}).items():
        result = generate_salary_page_v2('stage', stage, stats, all_pages, data)
        if result:
            output_dir = f"site/salaries/{result['slug']}"
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/index.html", 'w') as f:
                f.write(result['html'])
            generated.append(result)
            print(f"Generated: /salaries/{result['slug']}/ ({result['count']} jobs)")

    # Generate seniority pages
    for seniority, stats in data.get('by_seniority', {}).items():
        result = generate_salary_page_v2('seniority', seniority, stats, all_pages, data)
        if result:
            output_dir = f"site/salaries/{result['slug']}"
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/index.html", 'w') as f:
                f.write(result['html'])
            generated.append(result)
            print(f"Generated: /salaries/{result['slug']}/ ({result['count']} jobs)")

    print(f"\n✓ Generated {len(generated)} enhanced salary pages")
    return generated

if __name__ == "__main__":
    main()
