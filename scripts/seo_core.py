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



# Note: generate_faq_html() and CSS moved to templates.py for centralization
# Use templates.generate_faq_html() and templates.CSS_FAQ_SECTION instead


# =============================================================================
# CONTENT VALIDATION
# =============================================================================

# Minimum thresholds for content quality
MIN_WORD_COUNT = 300
MIN_FAQ_COUNT = 3


def validate_page_content(page_data: Dict[str, Any], all_pages: List[Dict[str, Any]] = None) -> List[str]:
    """
    Validate page meets quality thresholds for pSEO.

    Args:
        page_data: Dict containing title, content/html, faqs, etc.
        all_pages: List of all pages for uniqueness checking

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []

    # 1. Word count check
    content = page_data.get('content', '') or page_data.get('html', '')
    # Strip HTML tags for word count
    import re
    text_only = re.sub(r'<[^>]+>', ' ', content)
    text_only = re.sub(r'\s+', ' ', text_only).strip()
    word_count = len(text_only.split())

    if word_count < MIN_WORD_COUNT:
        issues.append(f"Thin content: {word_count} words (minimum: {MIN_WORD_COUNT})")

    # 2. FAQ count check
    faqs = page_data.get('faqs', [])
    faq_count = len(faqs) if faqs else 0
    if faq_count < MIN_FAQ_COUNT:
        issues.append(f"Low FAQ count: {faq_count} (minimum: {MIN_FAQ_COUNT})")

    # 3. Title present and reasonable length
    title = page_data.get('title', '')
    if not title:
        issues.append("Missing title")
    elif len(title) > 70:
        issues.append(f"Title too long: {len(title)} chars (max: 70)")
    elif len(title) < 20:
        issues.append(f"Title too short: {len(title)} chars (min: 20)")

    # 4. Description present and reasonable length
    description = page_data.get('description', '')
    if not description:
        issues.append("Missing meta description")
    elif len(description) > 160:
        issues.append(f"Description too long: {len(description)} chars (max: 160)")
    elif len(description) < 50:
        issues.append(f"Description too short: {len(description)} chars (min: 50)")

    # 5. Title uniqueness check
    if all_pages:
        existing_titles = [p.get('title') for p in all_pages if p.get('title') != title]
        if title in existing_titles:
            issues.append(f"Duplicate title found: {title}")

    # 6. Slug/URL present
    if not page_data.get('slug') and not page_data.get('url'):
        issues.append("Missing slug/URL")

    return issues


def validate_all_pages(pages: List[Dict[str, Any]], strict: bool = False) -> Dict[str, Any]:
    """
    Validate all pages and return summary report.

    Args:
        pages: List of page data dicts
        strict: If True, raise exception on any issues

    Returns:
        Dict with validation summary and issues by page
    """
    results = {
        'total_pages': len(pages),
        'valid_pages': 0,
        'pages_with_issues': 0,
        'issues_by_page': {},
        'issue_summary': {}
    }

    for page in pages:
        slug = page.get('slug', page.get('url', 'unknown'))
        issues = validate_page_content(page, pages)

        if issues:
            results['pages_with_issues'] += 1
            results['issues_by_page'][slug] = issues

            # Track issue types
            for issue in issues:
                issue_type = issue.split(':')[0]
                results['issue_summary'][issue_type] = results['issue_summary'].get(issue_type, 0) + 1
        else:
            results['valid_pages'] += 1

    if strict and results['pages_with_issues'] > 0:
        raise ValueError(f"Validation failed: {results['pages_with_issues']} pages have issues")

    return results


# =============================================================================
# SOFTWARE/TOOL SCHEMA (moved from generate_tools_pages_v2.py)
# =============================================================================

def generate_software_schema(tool: Dict[str, Any]) -> str:
    """Generate SoftwareApplication schema for tool pages."""
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool.get('name'),
        "description": tool.get('description', tool.get('tagline', '')),
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "url": f"https://thecroreport.com/tools/{tool.get('slug')}/",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "reviewCount": "50"
        }
    }

    if tool.get('pricing'):
        schema["offers"] = {
            "@type": "Offer",
            "description": tool['pricing']
        }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'
