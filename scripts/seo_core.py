#!/usr/bin/env python3
"""
SEO Core Module for CRO Report

Centralized SEO logic including:
- Schema.org JSON-LD generators (JobPosting, FAQPage, BreadcrumbList, Dataset)
- FAQ content generators with data-driven answers
- Internal linking engine
- Content enrichment utilities
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any


def generate_breadcrumb_schema(breadcrumbs: List[Dict[str, str]]) -> str:
    """Generate BreadcrumbList schema markup."""
    items = []
    for i, crumb in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": crumb['name'],
            "item": f"https://thecroreport.com{crumb['url']}"
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_faq_schema(faqs: List[Dict[str, str]]) -> str:
    """Generate FAQPage schema markup."""
    if not faqs:
        return ''

    main_entity = []
    for faq in faqs:
        main_entity.append({
            "@type": "Question",
            "name": faq['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['answer']
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_salary_dataset_schema(title: str, description: str, record_count: int, url: str, date_modified: str = None) -> str:
    """Generate Dataset schema for salary benchmark pages."""
    if date_modified is None:
        date_modified = datetime.now().strftime('%Y-%m-%d')

    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": description,
        "url": f"https://thecroreport.com{url}",
        "keywords": ["VP Sales salary", "CRO salary", "sales executive compensation"],
        "creator": {"@type": "Organization", "name": "The CRO Report", "url": "https://thecroreport.com"},
        "dateModified": date_modified,
        "temporalCoverage": str(datetime.now().year),
        "spatialCoverage": "United States"
    }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


def generate_salary_faqs(role_title: str, location: str = None, stage: str = None, avg_min: float = None, avg_max: float = None, median: float = None, sample_count: int = None, comparison_data: Dict = None) -> List[Dict[str, str]]:
    """Generate substantive FAQ content for salary pages based on actual data."""
    faqs = []

    def fmt_salary(amount):
        return f"${int(amount/1000)}K" if amount else "N/A"

    if avg_min and avg_max:
        range_spread = ((avg_max - avg_min) / avg_min) * 100

        if location:
            faqs.append({
                "question": f"What is the average {role_title} salary in {location}?",
                "answer": f"Based on {sample_count or 'our'} job postings with disclosed compensation, {role_title} roles in {location} pay between {fmt_salary(avg_min)} and {fmt_salary(avg_max)} base salary. The {int(range_spread)}% spread reflects differences in company stage, industry, and specific role scope. OTE typically adds 30-50% for revenue-carrying roles."
            })
        elif stage:
            equity_note = ""
            if "Seed" in stage or "Series A" in stage:
                equity_note = " Early-stage companies often compensate with larger equity grants (0.5-2%) to offset lower base."
            elif "Enterprise" in stage or "Public" in stage:
                equity_note = " Public companies typically offer RSUs worth 15-25% of base annually."

            faqs.append({
                "question": f"What do {role_title} roles pay at {stage} companies?",
                "answer": f"{stage} companies pay {role_title} roles between {fmt_salary(avg_min)} and {fmt_salary(avg_max)} base salary, based on {sample_count or 'analyzed'} job postings.{equity_note}"
            })
        else:
            faqs.append({
                "question": f"What is the average {role_title} salary?",
                "answer": f"The average {role_title} salary ranges from {fmt_salary(avg_min)} to {fmt_salary(avg_max)} base, based on {sample_count or 'analyzed'} job postings with disclosed compensation."
            })

        if range_spread > 30:
            faqs.append({
                "question": f"Why is the {role_title} salary range so wide ({fmt_salary(avg_min)} to {fmt_salary(avg_max)})?",
                "answer": f"The {int(range_spread)}% salary spread reflects real market variation. Key factors: (1) Company stage - Series A pays 20-30% less base but offers more equity; (2) Deal size responsibility - enterprise sales leaders ($500K+ ACV) command premiums; (3) Team size - managing 50+ reps vs 10 impacts compensation; (4) Industry - fintech and cybersecurity pay 15-20% above average. The 'right' salary depends on your specific situation."
            })

    if location and comparison_data:
        national_avg = comparison_data.get('national_avg_max')
        if national_avg and avg_max:
            diff_pct = ((avg_max - national_avg) / national_avg) * 100
            direction = "above" if diff_pct > 0 else "below"
            col_note = ""
            if location in ['San Francisco', 'New York']:
                col_note = f" However, cost of living in {location} is 40-60% higher than the national average, which affects real purchasing power."
            elif location == 'Remote':
                col_note = " Remote roles sometimes adjust pay based on candidate location (geographic pay bands)."

            faqs.append({
                "question": f"How do {location} {role_title} salaries compare to other markets?",
                "answer": f"{location} {role_title} salaries average {fmt_salary(avg_max)}, which is {abs(int(diff_pct))}% {direction} the national average of {fmt_salary(national_avg)}.{col_note}"
            })

    faqs.append({
        "question": f"Should I negotiate base salary or OTE for a {role_title} role?",
        "answer": "Focus on base salary for stability and comp benchmarking, but understand the full picture. At startups, negotiate equity vesting and acceleration clauses. At public companies, ask about RSU refresh grants. For OTE, clarify quota attainment rates (ask: 'What % of the team hit quota last year?') and whether targets are realistic. A high OTE with 20% attainment is worse than moderate OTE with 80% attainment."
    })

    if sample_count:
        faqs.append({
            "question": "How accurate is this salary data?",
            "answer": f"Our data comes from {sample_count} actual job postings with disclosed compensation ranges, not self-reported surveys (which typically skew 10-15% high). We track VP Sales, SVP Sales, and CRO roles weekly, filtering for executive-level positions. Limitations: not all companies disclose salary, and posted ranges may differ from final offers after negotiation."
        })

    return faqs


def generate_tool_faqs(tool_name: str, category: str, pricing: str = None, pros: List[str] = None, cons: List[str] = None, best_for: str = None, alternatives: List[str] = None) -> List[Dict[str, str]]:
    """Generate FAQ content for tool review pages."""
    faqs = []

    if pricing:
        faqs.append({
            "question": f"How much does {tool_name} cost?",
            "answer": f"{tool_name} pricing: {pricing}. Most {category} tools require annual contracts for the best rates. Request a custom quote based on your team size and usage needs."
        })

    if best_for:
        faqs.append({
            "question": f"Is {tool_name} right for my team?",
            "answer": f"{tool_name} is best for: {best_for}. Consider your team size, budget, and existing tech stack when evaluating. Most vendors offer trials or pilots."
        })

    if alternatives and len(alternatives) > 0:
        alt_list = ", ".join(alternatives[:4])
        faqs.append({
            "question": f"What are the best {tool_name} alternatives?",
            "answer": f"Top {tool_name} alternatives include: {alt_list}. The best choice depends on your specific needs - some prioritize features, others focus on pricing or ease of use. See our detailed comparison pages for head-to-head analysis."
        })

    if pros and cons:
        pros_text = "; ".join(pros[:3])
        cons_text = "; ".join(cons[:3])
        faqs.append({
            "question": f"What are the pros and cons of {tool_name}?",
            "answer": f"Pros: {pros_text}. Cons: {cons_text}. Every tool has tradeoffs - the key is finding the best fit for your team's workflow and budget."
        })

    return faqs


def get_related_salary_pages(current_page: Dict[str, Any], all_pages: List[Dict[str, Any]], max_links: int = 6) -> List[Dict[str, str]]:
    """Generate related page suggestions for internal linking."""
    related = []
    current_type = current_page.get('type')
    current_slug = current_page.get('slug')

    related.append({'title': 'All Salary Benchmarks', 'url': '/salaries/', 'context': 'View all salary data'})

    siblings = [p for p in all_pages if p.get('type') == current_type and p.get('slug') != current_slug]
    siblings.sort(key=lambda x: x.get('avg_max', 0), reverse=True)
    for sib in siblings[:3]:
        related.append({'title': sib.get('title'), 'url': f"/salaries/{sib.get('slug')}/", 'context': f"{sib.get('count', 0)} roles"})

    other_types = [p for p in all_pages if p.get('type') != current_type]
    for other in other_types[:2]:
        related.append({'title': other.get('title'), 'url': f"/salaries/{other.get('slug')}/", 'context': f"By {other.get('type', 'category')}"})

    return related[:max_links]


def generate_related_pages_html(related_pages: List[Dict[str, str]]) -> str:
    """Generate HTML for related pages section."""
    if not related_pages:
        return ''

    links_html = ''
    for page in related_pages:
        links_html += f'''
        <a href="{page['url']}" class="related-link">
            <span class="related-title">{page['title']}</span>
            <span class="related-context">{page.get('context', '')}</span>
        </a>
        '''

    return f'''
    <section class="related-pages">
        <h3>Related Salary Data</h3>
        <div class="related-links-grid">
            {links_html}
        </div>
    </section>
    '''


def generate_faq_html(faqs: List[Dict[str, str]], include_schema: bool = True) -> str:
    """Generate FAQ section HTML with optional schema markup."""
    if not faqs:
        return ''

    faq_items_html = ''
    for faq in faqs:
        faq_items_html += f'''
        <div class="faq-item">
            <h4 class="faq-question">{faq['question']}</h4>
            <p class="faq-answer">{faq['answer']}</p>
        </div>
        '''

    schema_html = generate_faq_schema(faqs) if include_schema else ''

    return f'''
    {schema_html}
    <section class="faq-section">
        <h2>Frequently Asked Questions</h2>
        {faq_items_html}
    </section>
    '''


SEO_CSS = '''
    /* FAQ Section */
    .faq-section {
        background: var(--white);
        border-radius: 12px;
        padding: 32px;
        margin: 40px 0;
    }

    .faq-section h2 {
        font-family: 'Fraunces', serif;
        font-size: 1.5rem;
        color: var(--navy-medium);
        margin-bottom: 24px;
    }

    .faq-item {
        border-bottom: 1px solid var(--gray-200);
        padding: 20px 0;
    }

    .faq-item:last-child { border-bottom: none; }

    .faq-question {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--navy);
        margin-bottom: 12px;
    }

    .faq-answer {
        font-size: 0.95rem;
        color: var(--gray-600);
        line-height: 1.7;
        margin: 0;
    }

    /* Related Pages Section */
    .related-pages {
        background: var(--gray-50);
        border-radius: 12px;
        padding: 32px;
        margin: 40px 0;
    }

    .related-pages h3 {
        font-family: 'Fraunces', serif;
        font-size: 1.25rem;
        color: var(--navy-medium);
        margin-bottom: 20px;
    }

    .related-links-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
    }

    .related-link {
        display: flex;
        flex-direction: column;
        background: var(--white);
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


def get_seo_styles() -> str:
    """Return CSS for SEO components"""
    return SEO_CSS
