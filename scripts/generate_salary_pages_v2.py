#!/usr/bin/env python3
"""
Enhanced Salary Page Generator v2 with pSEO optimizations:
- Schema.org markup (Dataset, FAQPage, BreadcrumbList)
- Data-driven FAQ sections
- Internal linking engine
- Content enrichment based on actual data

Uses templates.py for consistent site design.
"""

import json
import os
from datetime import datetime

# Import shared templates and utilities
from templates import (
    get_html_head,
    get_nav_html,
    get_footer_html,
    generate_cta_section,
    generate_faq_html,
    fmt_salary,
    load_json_data,
    write_page,
    CSS_VARIABLES,
    CSS_NAV,
    CSS_LAYOUT,
    CSS_CARDS,
    CSS_CTA,
    CSS_FOOTER,
    CSS_PAGE_HEADER,
    CSS_CTA_SECTION,
    CSS_FAQ_SECTION,
    CSS_STAT_CARDS,
)
from seo_core import (
    generate_breadcrumb_schema,
    generate_salary_dataset_schema,
    generate_salary_faqs,
    get_related_salary_pages,
)

# Minimum jobs required to create a page (avoid thin content)
MIN_JOBS_FOR_PAGE = 5


def load_comp_data():
    """Load compensation analysis data."""
    return load_json_data('comp_analysis.json')

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
    return context

def generate_stage_context(stage, data):
    """Generate contextual content for a company stage."""
    stage_contexts = {
        'Seed/Series A': (
            "Early-stage companies (Seed through Series A) typically offer lower base salaries but compensate with significant equity grants. "
            "Expect 0.5-2% equity for VP-level hires, with 4-year vesting and 1-year cliff standard.",
            "Evaluate equity value realistically—most startups don't reach IPO. Focus on the team, market opportunity, and your ability to influence outcomes. "
            "Cash runway matters: ensure the company can pay your salary for 18+ months."
        ),
        'Series A/B': (
            "Series A/B companies are typically finding product-market fit and scaling initial go-to-market. "
            "Sales leaders at this stage often build the foundational sales playbook and hire the first dedicated sales team.",
            "Equity grants range from 0.25-1%. Look for clear paths to the next funding round and realistic revenue targets. "
            "Your impact on company trajectory is significant at this stage."
        ),
        'Series B/C': (
            "Series B/C companies are scaling proven go-to-market motions. Sales leadership roles focus on building repeatable processes, "
            "expanding into new segments, and professionalizing the sales organization.",
            "Equity grants of 0.1-0.5% are typical. Evaluate the path to profitability or IPO. "
            "These companies offer a balance of growth potential and relative stability."
        ),
        'Series C/D': (
            "Late-stage private companies (Series C/D) often pay near-public-company rates while still offering meaningful equity upside. "
            "These roles typically involve managing larger teams and more complex go-to-market strategies.",
            "Equity grants may be 0.05-0.25%. Assess secondary sale opportunities and realistic IPO/acquisition timelines. "
            "Many offer competitive benefits packages."
        ),
        'Late Stage': (
            "Late-stage companies preparing for IPO or acquisition offer the most predictable compensation. "
            "Base salaries are competitive with public companies, and equity has clearer near-term liquidity potential.",
            "Evaluate lockup periods post-IPO and understand the stock's likely trading dynamics. "
            "These roles suit leaders who want upside with reduced early-stage risk."
        ),
        'Enterprise/Public': (
            "Public and large enterprise companies offer the highest base salaries and most comprehensive benefits. "
            "Compensation is more standardized with clear bands and annual refresh grants.",
            "RSU grants typically vest over 4 years with annual refreshes. Total compensation is more predictable but upside is limited "
            "compared to pre-IPO companies. Focus on scope, title progression, and team size."
        )
    }

    return stage_contexts.get(stage, (
        f"{stage} companies offer varying compensation based on their specific situation and growth trajectory.",
        "Consider the full compensation package including base, bonus, and equity when evaluating opportunities."
    ))

def generate_seniority_context(seniority, data):
    """Generate contextual content for a seniority level."""
    seniority_contexts = {
        'VP': (
            "Vice President of Sales roles vary significantly in scope—from managing a single team of 5-10 reps to overseeing multiple sales functions with 50+ headcount. This range explains the wide salary spread.",
            "Typical responsibilities include quota ownership, team hiring and development, sales process optimization, cross-functional collaboration with marketing and customer success, and executive reporting.",
            "VP Sales typically leads to SVP Sales, CRO, or CEO roles, depending on company trajectory and individual goals."
        ),
        'SVP': (
            "Senior Vice President of Sales roles typically involve broader organizational scope than VP roles, often including multiple sales teams, sales operations, and sometimes sales enablement or development.",
            "Typical responsibilities include multi-team leadership, strategic planning, board reporting, GTM strategy, executive hiring, and large deal involvement.",
            "SVP Sales commonly leads to CRO or President roles, with some transitioning to CEO positions, especially at sales-led organizations."
        ),
        'C-Level': (
            "Chief Revenue Officer (CRO) roles encompass full revenue responsibility, typically including Sales, Customer Success, and sometimes Marketing and Partnerships. These are true executive roles with board exposure.",
            "Typical responsibilities include full P&L ownership, board presentations, strategic planning, executive team leadership, major customer relationships, and investor relations support.",
            "CRO compensation often includes significant equity components and may include board observer or advisory roles."
        ),
        'EVP': (
            "Executive Vice President roles sit between SVP and C-level, often found at larger organizations. These roles typically manage multiple SVPs or large regional organizations.",
            "EVP Sales might oversee Americas, EMEA, or APAC regions, or manage both enterprise and commercial sales organizations.",
            "EVP roles often lead to CRO or Chief Commercial Officer positions at the same or larger organizations."
        )
    }

    return seniority_contexts.get(seniority, (
        f"{seniority} level roles offer competitive compensation based on scope and company stage.",
        "Responsibilities and compensation vary significantly based on company size and industry.",
        "Career progression depends on individual goals and market opportunities."
    ))

# Page-specific CSS (unique to salary pages, uses shared components from templates.py)
SALARY_PAGE_CSS = '''
    /* Stats Grid - specific layout for salary pages */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: -40px auto 40px;
        max-width: 900px;
        padding: 0 20px;
        position: relative;
        z-index: 10;
    }
    @media (max-width: 600px) { .stats-grid { grid-template-columns: 1fr; } }

    /* Section */
    .section { padding: 40px 0; }
    .section h2 { font-family: 'Fraunces', serif; font-size: 1.5rem; color: var(--navy-medium); margin-bottom: 20px; }

    /* Context Box */
    .context-box {
        background: white;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 32px;
    }
    .context-box h2 {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        color: var(--navy-medium);
        margin-bottom: 16px;
    }
    .context-box p {
        color: var(--gray-700);
        line-height: 1.7;
        margin-bottom: 12px;
    }
    .context-box p:last-child { margin-bottom: 0; }

    /* Related Pages */
    .related-section {
        background: var(--gray-50);
        border-radius: 12px;
        padding: 32px;
        margin: 32px 0;
    }
    .related-section h3 {
        font-family: 'Fraunces', serif;
        font-size: 1.25rem;
        color: var(--navy-medium);
        margin-bottom: 20px;
    }
    .related-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
    }
    .related-link {
        display: flex;
        flex-direction: column;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 8px;
        padding: 16px;
        text-decoration: none;
        transition: all 0.2s;
    }
    .related-link:hover {
        border-color: var(--navy-medium);
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .related-title {
        font-weight: 600;
        color: var(--navy);
        font-size: 0.95rem;
    }
    .related-context {
        font-size: 0.8rem;
        color: var(--gray-500);
        margin-top: 4px;
    }
'''

def generate_salary_page_v2(page_type, identifier, stats, all_pages, data):
    """Generate an enhanced salary page with full pSEO optimization."""

    count = stats.get('count', 0)
    if count < MIN_JOBS_FOR_PAGE:
        return None  # Skip thin content pages

    avg_min = stats.get('min_base_avg')
    avg_max = stats.get('max_base_avg')
    midpoint = (avg_min + avg_max) / 2 if avg_min and avg_max else 0

    # Determine page title, slug, and content
    if page_type == 'location':
        title = f"VP Sales {identifier} Salary"
        slug = f"vp-sales-salary-{identifier.lower().replace(' ', '-')}"
        page_path = f"salaries/{slug}/"
        description = f"VP Sales salary data for {identifier}: {fmt_salary(avg_min)} - {fmt_salary(avg_max)} base. Based on {count} job postings. Updated {datetime.now().strftime('%B %Y')}."
        eyebrow = "Salary by Location"
        context_title = f"Sales Leadership Market: {identifier}"
        context_text = generate_location_context(identifier, data)
        breadcrumb_html = f'<a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {identifier}'
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
        page_path = f"salaries/{slug}/"
        description = f"VP Sales compensation at {identifier} companies: {fmt_salary(avg_min)} - {fmt_salary(avg_max)} base. Based on {count} job postings."
        eyebrow = "Salary by Company Stage"
        context_title = f"Compensation at {identifier} Companies"
        context_parts = generate_stage_context(identifier, data)
        context_text = context_parts[0] if isinstance(context_parts, tuple) else context_parts
        context_extra = context_parts[1] if isinstance(context_parts, tuple) and len(context_parts) > 1 else ""
        breadcrumb_html = f'<a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {identifier}'
        faqs = generate_salary_faqs(
            role_title="VP Sales",
            stage=identifier,
            avg_min=avg_min,
            avg_max=avg_max,
            sample_count=count
        )

    elif page_type == 'seniority':
        title = f"{identifier} Sales Salary Benchmarks"
        slug = f"{identifier.lower()}-sales-salary"
        page_path = f"salaries/{slug}/"
        description = f"{identifier} Sales salary data: {fmt_salary(avg_min)} - {fmt_salary(avg_max)} base. Based on {count} job postings."
        eyebrow = "Salary by Seniority"
        context_title = f"{identifier} Sales Leadership Roles"
        context_parts = generate_seniority_context(identifier, data)
        context_text = context_parts[0] if isinstance(context_parts, tuple) else context_parts
        breadcrumb_html = f'<a href="/">Home</a> → <a href="/salaries/">Salaries</a> → {identifier}'
        faqs = generate_salary_faqs(
            role_title=f"{identifier} Sales",
            avg_min=avg_min,
            avg_max=avg_max,
            sample_count=count
        )
    else:
        return None

    # Build page metadata for internal linking
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
    breadcrumbs_for_schema = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Salaries', 'url': '/salaries/'},
        {'name': identifier, 'url': f'/salaries/{slug}/'}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs_for_schema)
    dataset_schema = generate_salary_dataset_schema(
        title=title,
        description=f"Salary benchmarks for {title.lower()} based on {count} job postings with disclosed compensation.",
        record_count=count,
        url=f"/salaries/{slug}/"
    )

    # Build FAQ HTML using shared utility
    faq_section_html = generate_faq_html(faqs, include_schema=True)

    # Build related pages HTML
    related_links_html = ''
    for page in related_pages:
        related_links_html += f'''
            <a href="{page['url']}" class="related-link">
                <span class="related-title">{page['title']}</span>
                <span class="related-context">{page.get('context', '')}</span>
            </a>
        '''

    related_section_html = f'''
        <section class="related-section">
            <h3>Related Salary Data</h3>
            <div class="related-grid">
                {related_links_html}
            </div>
        </section>
    ''' if related_pages else ''

    # Build context section
    context_html = f'''
        <div class="context-box">
            <h2>{context_title}</h2>
            <p>{context_text}</p>
            {"<p><strong>Key considerations:</strong> " + context_extra + "</p>" if page_type == 'stage' and 'context_extra' in dir() and context_extra else ""}
        </div>
    '''

    # Use templates.py for head (but we need custom styles, so include_styles=False and add our own)
    html_head = get_html_head(title, description, page_path, include_styles=False)

    # Build full HTML using shared CSS constants
    html = f'''{html_head}
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
        {CSS_PAGE_HEADER}
        {CSS_CTA_SECTION}
        {CSS_FAQ_SECTION}
        {CSS_STAT_CARDS}
        {SALARY_PAGE_CSS}
    </style>
    {breadcrumb_schema}
    {dataset_schema}

{get_nav_html('salaries')}

    <div class="header">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>Current salary data based on {count} job postings with disclosed compensation.</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">Average Range</div>
            <div class="value">{fmt_salary(avg_min)} - {fmt_salary(avg_max)}</div>
            <div class="sublabel">Base salary</div>
        </div>
        <div class="stat-card">
            <div class="label">Midpoint</div>
            <div class="value">{fmt_salary(midpoint)}</div>
            <div class="sublabel">Average base</div>
        </div>
        <div class="stat-card">
            <div class="label">Sample Size</div>
            <div class="value">{count}</div>
            <div class="sublabel">Job postings</div>
        </div>
    </div>

    <div class="container" style="max-width: 900px; padding: 0 20px;">
        <nav class="breadcrumb" style="padding: 16px 0; font-size: 0.85rem; color: var(--gray-500);">
            {breadcrumb_html}
        </nav>

        {context_html}

        {faq_section_html}

        {related_section_html}

        <div class="cta-section">
            <h2>Get Full Compensation Intelligence</h2>
            <p>Weekly analysis of compensation trends, red flags, and negotiation insights for VP Sales and CRO roles.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </div>

{get_footer_html()}'''

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
