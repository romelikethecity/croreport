#!/usr/bin/env python3
"""
Enhanced Tools Page Generator v2 with pSEO optimizations:
- Schema.org markup (SoftwareApplication, FAQPage, BreadcrumbList)
- Data-driven FAQ sections
- Category hub pages
- Internal linking
"""

import json
import os
from datetime import datetime
from seo_core import (
    generate_breadcrumb_schema,
    generate_faq_schema,
    generate_tool_faqs,
    generate_faq_html,
    get_seo_styles
)

# Tool categories for hub pages
TOOL_CATEGORIES = {
    'ai-sdr': {
        'name': 'AI SDR Tools',
        'description': 'AI-powered sales development tools that automate prospecting, outreach, and meeting booking.',
        'keywords': ['AI SDR', 'automated prospecting', 'AI sales tools']
    },
    'data-enrichment': {
        'name': 'Data Enrichment Tools',
        'description': 'B2B data providers and enrichment platforms for contact and company information.',
        'keywords': ['data enrichment', 'B2B data', 'contact data']
    },
    'sales-engagement': {
        'name': 'Sales Engagement Platforms',
        'description': 'Multi-channel outreach platforms for email, phone, and social selling sequences.',
        'keywords': ['sales engagement', 'outreach platform', 'sales sequences']
    },
    'conversation-intelligence': {
        'name': 'Conversation Intelligence',
        'description': 'Call recording and analysis tools for sales coaching and deal intelligence.',
        'keywords': ['conversation intelligence', 'call recording', 'sales coaching']
    },
    'crm': {
        'name': 'CRM Platforms',
        'description': 'Customer relationship management systems for sales pipeline and customer data.',
        'keywords': ['CRM', 'sales CRM', 'pipeline management']
    },
    'forecasting': {
        'name': 'Revenue Forecasting',
        'description': 'AI-powered forecasting and pipeline analytics for sales leaders.',
        'keywords': ['revenue forecasting', 'sales forecasting', 'pipeline analytics']
    }
}

def load_tools_data():
    """Load tools data. In production, this would come from a database or JSON file."""
    # Sample tools data - in production, load from data/tools.json
    tools = [
        {
            'slug': '11x',
            'name': '11x',
            'category': 'ai-sdr',
            'tagline': 'AI-powered digital workers for sales development',
            'description': '11x provides AI digital workers that handle sales development tasks including prospecting, outreach, and meeting booking.',
            'pricing': 'Custom pricing, typically $1,000-5,000/month based on usage',
            'pros': ['Fully autonomous AI SDR', 'Works 24/7', 'Multi-language support', 'Handles full SDR workflow'],
            'cons': ['Premium pricing', 'Less control than human SDRs', 'Requires quality data inputs'],
            'best_for': 'Companies looking to scale outbound without hiring SDRs, or supplement existing teams',
            'alternatives': ['Artisan', 'Relevance AI', 'Regie.ai', 'Outreach']
        },
        {
            'slug': 'artisan',
            'name': 'Artisan',
            'category': 'ai-sdr',
            'tagline': 'AI employees for outbound sales',
            'description': 'Artisan creates AI employees (like Ava the AI BDR) that autonomously run outbound sales campaigns.',
            'pricing': 'Starting around $2,000/month for AI BDR',
            'pros': ['Named AI persona (Ava)', 'End-to-end automation', 'Built-in data enrichment'],
            'cons': ['Newer company', 'May need tuning for complex ICPs'],
            'best_for': 'Startups and SMBs wanting turnkey outbound automation',
            'alternatives': ['11x', 'Relevance AI', 'Apollo', 'Instantly']
        },
        {
            'slug': 'apollo',
            'name': 'Apollo.io',
            'category': 'data-enrichment',
            'tagline': 'Sales intelligence and engagement platform',
            'description': 'Apollo combines a B2B database of 275M+ contacts with sales engagement and analytics in one platform.',
            'pricing': 'Free tier available; paid plans from $49/user/month',
            'pros': ['Large contact database', 'All-in-one platform', 'Affordable pricing', 'Good data quality'],
            'cons': ['Can feel overwhelming', 'Email deliverability varies', 'Data gaps in some industries'],
            'best_for': 'SMBs and startups wanting an all-in-one prospecting solution',
            'alternatives': ['ZoomInfo', 'Lusha', 'Cognism', 'Clearbit']
        },
        {
            'slug': 'zoominfo',
            'name': 'ZoomInfo',
            'category': 'data-enrichment',
            'tagline': 'Enterprise B2B data and intelligence platform',
            'description': 'ZoomInfo is the market leader in B2B contact and company data, with deep integrations and intent data.',
            'pricing': 'Enterprise pricing, typically $15,000-50,000+/year',
            'pros': ['Largest B2B database', 'Intent data', 'Deep integrations', 'Enterprise-grade'],
            'cons': ['Expensive', 'Annual contracts', 'Complex pricing'],
            'best_for': 'Enterprise sales teams with budget for premium data',
            'alternatives': ['Apollo', 'Cognism', 'Lusha', '6sense']
        },
        {
            'slug': 'outreach',
            'name': 'Outreach',
            'category': 'sales-engagement',
            'tagline': 'Leading sales engagement platform',
            'description': 'Outreach is the category leader in sales engagement, powering multi-channel sequences and sales execution.',
            'pricing': 'Custom pricing, typically $100-150/user/month',
            'pros': ['Market leader', 'Robust features', 'Strong integrations', 'AI capabilities'],
            'cons': ['Premium pricing', 'Steep learning curve', 'Can be overkill for small teams'],
            'best_for': 'Mid-market and enterprise sales teams',
            'alternatives': ['Salesloft', 'Apollo', 'Groove', 'Mixmax']
        },
        {
            'slug': 'salesloft',
            'name': 'Salesloft',
            'category': 'sales-engagement',
            'tagline': 'Revenue workflow platform',
            'description': 'Salesloft combines sales engagement with conversation intelligence and forecasting in a unified platform.',
            'pricing': 'Custom pricing, similar to Outreach',
            'pros': ['Unified platform', 'Strong conversation intelligence', 'Good UX'],
            'cons': ['Premium pricing', 'Some features less mature than point solutions'],
            'best_for': 'Teams wanting engagement + conversation intel in one platform',
            'alternatives': ['Outreach', 'Gong', 'Clari', 'Apollo']
        },
        {
            'slug': 'gong',
            'name': 'Gong',
            'category': 'conversation-intelligence',
            'tagline': 'Revenue intelligence platform',
            'description': 'Gong captures and analyzes customer interactions to provide insights for sales coaching and deal intelligence.',
            'pricing': 'Custom pricing, typically $100-150/user/month',
            'pros': ['Best-in-class transcription', 'Deep analytics', 'Great for coaching', 'Deal intelligence'],
            'cons': ['Expensive', 'Requires call volume for value', 'Privacy considerations'],
            'best_for': 'Sales teams with significant call/meeting volume',
            'alternatives': ['Chorus', 'Clari', 'Salesloft', 'Fireflies']
        },
        {
            'slug': 'clari',
            'name': 'Clari',
            'category': 'forecasting',
            'tagline': 'Revenue platform for forecasting and pipeline',
            'description': 'Clari provides AI-powered revenue forecasting, pipeline management, and deal inspection for sales leaders.',
            'pricing': 'Custom enterprise pricing',
            'pros': ['Best-in-class forecasting', 'Pipeline analytics', 'CRO-level insights'],
            'cons': ['Enterprise pricing', 'Requires CRM data quality', 'Implementation time'],
            'best_for': 'Sales leaders needing accurate forecasting and pipeline visibility',
            'alternatives': ['Gong Forecast', 'Aviso', 'BoostUp', 'People.ai']
        }
    ]
    return tools

def generate_software_schema(tool):
    """Generate SoftwareApplication schema for a tool."""
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool['name'],
        "description": tool['description'],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "url": f"https://thecroreport.com/tools/{tool['slug']}/"
    }

    if tool.get('pricing'):
        schema["offers"] = {
            "@type": "Offer",
            "description": tool['pricing']
        }

    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'

def generate_tool_page_v2(tool):
    """Generate an enhanced tool page with full pSEO optimization."""

    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Tools', 'url': '/tools/'},
        {'name': TOOL_CATEGORIES.get(tool['category'], {}).get('name', 'Tools'), 'url': f"/tools/{tool['category']}/"},
        {'name': tool['name'], 'url': f"/tools/{tool['slug']}/"}
    ]

    # Generate schemas
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)
    software_schema = generate_software_schema(tool)

    # Generate FAQs
    faqs = generate_tool_faqs(
        tool_name=tool['name'],
        category=TOOL_CATEGORIES.get(tool['category'], {}).get('name', 'sales tool'),
        pricing=tool.get('pricing'),
        pros=tool.get('pros'),
        cons=tool.get('cons'),
        best_for=tool.get('best_for'),
        alternatives=tool.get('alternatives')
    )
    faq_html = generate_faq_html(faqs, include_schema=True)

    # Build pros/cons HTML
    pros_html = ""
    if tool.get('pros'):
        pros_html = "<ul class='pros-list'>" + "".join(f"<li>{p}</li>" for p in tool['pros']) + "</ul>"

    cons_html = ""
    if tool.get('cons'):
        cons_html = "<ul class='cons-list'>" + "".join(f"<li>{c}</li>" for c in tool['cons']) + "</ul>"

    # Build alternatives HTML
    alternatives_html = ""
    if tool.get('alternatives'):
        alt_links = []
        for alt in tool['alternatives']:
            alt_slug = alt.lower().replace('.', '').replace(' ', '-')
            alt_links.append(f'<a href="/tools/{alt_slug}/" class="alt-link">{alt}</a>')
        alternatives_html = f"""
        <section class="alternatives-section">
            <h2>{tool['name']} Alternatives</h2>
            <div class="alternatives-grid">
                {' '.join(alt_links)}
            </div>
        </section>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool['name']} Review: Pricing, Pros & Cons | The CRO Report</title>
    <meta name="description" content="{tool['name']} review: {tool['tagline']}. See pricing, pros/cons, and alternatives for {datetime.now().year}.">
    <link rel="canonical" href="https://thecroreport.com/tools/{tool['slug']}/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/styles.css">
    {breadcrumb_schema}
    {software_schema}
    <style>
        {get_seo_styles()}

        .tool-hero {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-medium) 100%);
            color: white;
            padding: 60px 20px;
        }}

        .tool-hero-content {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .tool-hero h1 {{
            font-family: 'Fraunces', serif;
            font-size: 2.5rem;
            margin-bottom: 12px;
        }}

        .tool-tagline {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }}

        .tool-category-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
        }}

        .tool-content {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .tool-section {{
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 32px;
            margin: 24px 0;
        }}

        .tool-section h2 {{
            font-family: 'Fraunces', serif;
            font-size: 1.5rem;
            color: var(--navy-medium);
            margin-bottom: 16px;
        }}

        .tool-section p {{
            color: var(--gray-700);
            line-height: 1.7;
        }}

        .pros-cons-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }}

        @media (max-width: 600px) {{
            .pros-cons-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .pros-section, .cons-section {{
            padding: 24px;
            border-radius: 8px;
        }}

        .pros-section {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
        }}

        .cons-section {{
            background: #fef2f2;
            border: 1px solid #fecaca;
        }}

        .pros-section h3 {{
            color: #166534;
            margin-bottom: 12px;
        }}

        .cons-section h3 {{
            color: #991b1b;
            margin-bottom: 12px;
        }}

        .pros-list, .cons-list {{
            margin: 0;
            padding-left: 20px;
        }}

        .pros-list li {{
            color: #166534;
            margin-bottom: 8px;
        }}

        .cons-list li {{
            color: #991b1b;
            margin-bottom: 8px;
        }}

        .pricing-box {{
            background: var(--gray-50);
            border-radius: 8px;
            padding: 24px;
            margin-top: 20px;
        }}

        .pricing-box h3 {{
            color: var(--navy);
            margin-bottom: 12px;
        }}

        .alternatives-section {{
            margin-top: 40px;
        }}

        .alternatives-section h2 {{
            font-family: 'Fraunces', serif;
            font-size: 1.5rem;
            color: var(--navy-medium);
            margin-bottom: 20px;
        }}

        .alternatives-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .alt-link {{
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            padding: 12px 20px;
            text-decoration: none;
            color: var(--navy);
            font-weight: 500;
            transition: all 0.2s;
        }}

        .alt-link:hover {{
            border-color: var(--navy-medium);
            background: var(--gray-50);
        }}

        .best-for-box {{
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}

        .best-for-box h3 {{
            color: #1e40af;
            margin-bottom: 8px;
        }}

        .best-for-box p {{
            color: #1e3a8a;
            margin: 0;
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

    <header class="tool-hero">
        <div class="tool-hero-content">
            <span class="tool-category-badge">{TOOL_CATEGORIES.get(tool['category'], {}).get('name', 'Sales Tool')}</span>
            <h1>{tool['name']}</h1>
            <p class="tool-tagline">{tool['tagline']}</p>
        </div>
    </header>

    <main class="tool-content">
        <section class="tool-section">
            <h2>Overview</h2>
            <p>{tool['description']}</p>

            {f'''<div class="best-for-box">
                <h3>Best For</h3>
                <p>{tool['best_for']}</p>
            </div>''' if tool.get('best_for') else ''}

            {f'''<div class="pricing-box">
                <h3>Pricing</h3>
                <p>{tool['pricing']}</p>
            </div>''' if tool.get('pricing') else ''}
        </section>

        <section class="tool-section">
            <h2>Pros and Cons</h2>
            <div class="pros-cons-grid">
                <div class="pros-section">
                    <h3>✓ Pros</h3>
                    {pros_html}
                </div>
                <div class="cons-section">
                    <h3>✗ Cons</h3>
                    {cons_html}
                </div>
            </div>
        </section>

        {faq_html}

        {alternatives_html}
    </main>

    <footer class="main-footer">
        <div class="footer-container">
            <p>&copy; {datetime.now().year} The CRO Report. Tool information updated regularly.</p>
        </div>
    </footer>
</body>
</html>"""

    return html

def generate_category_hub(category_slug, category_info, tools):
    """Generate a category hub page listing all tools in that category."""

    breadcrumbs = [
        {'name': 'Home', 'url': '/'},
        {'name': 'Tools', 'url': '/tools/'},
        {'name': category_info['name'], 'url': f"/tools/{category_slug}/"}
    ]
    breadcrumb_schema = generate_breadcrumb_schema(breadcrumbs)

    category_tools = [t for t in tools if t['category'] == category_slug]

    tools_html = ""
    for tool in category_tools:
        tools_html += f"""
        <a href="/tools/{tool['slug']}/" class="tool-card">
            <h3>{tool['name']}</h3>
            <p class="tool-tagline">{tool['tagline']}</p>
            {f'<p class="tool-pricing">{tool["pricing"]}</p>' if tool.get('pricing') else ''}
        </a>
        """

    # Generate ItemList schema
    itemlist_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": category_info['name'],
        "description": category_info['description'],
        "numberOfItems": len(category_tools),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": t['name'],
                "url": f"https://thecroreport.com/tools/{t['slug']}/"
            }
            for i, t in enumerate(category_tools)
        ]
    }
    itemlist_json = f'<script type="application/ld+json">{json.dumps(itemlist_schema, indent=2)}</script>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category_info['name']} - Best Tools for {datetime.now().year} | The CRO Report</title>
    <meta name="description" content="{category_info['description']} Compare {len(category_tools)}+ tools with pricing, pros/cons, and reviews.">
    <link rel="canonical" href="https://thecroreport.com/tools/{category_slug}/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/styles.css">
    {breadcrumb_schema}
    {itemlist_json}
    <style>
        {get_seo_styles()}

        .category-hero {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-medium) 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}

        .category-hero h1 {{
            font-family: 'Fraunces', serif;
            font-size: 2.5rem;
            margin-bottom: 16px;
        }}

        .category-hero p {{
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }}

        .category-content {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }}

        .tool-card {{
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            transition: all 0.2s;
        }}

        .tool-card:hover {{
            border-color: var(--navy-medium);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .tool-card h3 {{
            font-family: 'Fraunces', serif;
            font-size: 1.25rem;
            color: var(--navy);
            margin-bottom: 8px;
        }}

        .tool-card .tool-tagline {{
            color: var(--gray-600);
            font-size: 0.95rem;
            line-height: 1.5;
            margin-bottom: 12px;
        }}

        .tool-card .tool-pricing {{
            color: var(--gray-500);
            font-size: 0.85rem;
            margin: 0;
        }}

        .category-intro {{
            background: var(--gray-50);
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 40px;
        }}

        .category-intro h2 {{
            font-family: 'Fraunces', serif;
            color: var(--navy-medium);
            margin-bottom: 16px;
        }}

        .category-intro p {{
            color: var(--gray-700);
            line-height: 1.7;
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

    <header class="category-hero">
        <h1>{category_info['name']}</h1>
        <p>{category_info['description']}</p>
    </header>

    <main class="category-content">
        <div class="category-intro">
            <h2>About {category_info['name']}</h2>
            <p>{category_info['description']} Below you'll find our reviews of the top tools in this category, including pricing information, pros and cons, and recommendations for different team sizes and use cases.</p>
        </div>

        <div class="tools-grid">
            {tools_html}
        </div>
    </main>

    <footer class="main-footer">
        <div class="footer-container">
            <p>&copy; {datetime.now().year} The CRO Report. Tool information updated regularly.</p>
        </div>
    </footer>
</body>
</html>"""

    return html

def main():
    """Generate all enhanced tool pages."""
    tools = load_tools_data()
    generated = []

    # Generate individual tool pages
    for tool in tools:
        html = generate_tool_page_v2(tool)
        output_dir = f"site/tools/{tool['slug']}"
        os.makedirs(output_dir, exist_ok=True)
        with open(f"{output_dir}/index.html", 'w') as f:
            f.write(html)
        generated.append(f"/tools/{tool['slug']}/")
        print(f"Generated: /tools/{tool['slug']}/")

    # Generate category hub pages
    for category_slug, category_info in TOOL_CATEGORIES.items():
        category_tools = [t for t in tools if t['category'] == category_slug]
        if category_tools:
            html = generate_category_hub(category_slug, category_info, tools)
            output_dir = f"site/tools/{category_slug}"
            os.makedirs(output_dir, exist_ok=True)
            with open(f"{output_dir}/index.html", 'w') as f:
                f.write(html)
            generated.append(f"/tools/{category_slug}/")
            print(f"Generated: /tools/{category_slug}/ (category hub)")

    print(f"\n✓ Generated {len(generated)} tool pages")
    return generated

if __name__ == "__main__":
    main()
