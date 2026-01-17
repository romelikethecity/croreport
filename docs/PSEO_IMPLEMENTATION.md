# Programmatic SEO Implementation Guide

## Overview

This document describes the pSEO architecture implemented for The CRO Report, based on best practices for scaling to 100k+ pages while avoiding thin content penalties.

## Architecture

### Hub-and-Spoke Model

```
/salaries/                    (main hub)
├── by-location/              (category hub)
│   ├── vp-sales-salary-san-francisco/
│   ├── vp-sales-salary-new-york/
│   └── ...
├── by-stage/                 (category hub)
│   ├── vp-sales-salary-seed-series-a/
│   ├── vp-sales-salary-series-c-d/
│   └── ...
├── by-seniority/             (category hub)
│   ├── c-level-sales-salary/
│   ├── svp-sales-salary/
│   └── vp-sales-salary/
└── [individual pages]

/tools/                       (main hub)
├── ai-sdr/                   (category hub)
│   ├── 11x/
│   ├── artisan/
│   └── ...
├── data-enrichment/          (category hub)
├── sales-engagement/         (category hub)
└── ...

/trends/                      (standalone page)
```

### Key Files

| File | Purpose |
|------|---------|
| `scripts/seo_core.py` | Centralized SEO utilities (schema generators, FAQ builders, CSS) |
| `scripts/generate_salary_pages_v2.py` | Enhanced salary pages with schema + FAQs |
| `scripts/generate_hub_pages.py` | Hub/index pages for categories |
| `scripts/generate_tools_pages_v2.py` | Enhanced tool pages with schema + FAQs |

## Schema Markup

### Implemented Schema Types

1. **BreadcrumbList** - Navigation hierarchy on all pages
2. **FAQPage** - Data-driven FAQ sections
3. **Dataset** - Salary benchmark pages (for Google Dataset Search)
4. **SoftwareApplication** - Tool review pages
5. **ItemList** - Category hub pages listing tools

### Example: BreadcrumbList

```python
from seo_core import generate_breadcrumb_schema

breadcrumbs = [
    {'name': 'Home', 'url': '/'},
    {'name': 'Salaries', 'url': '/salaries/'},
    {'name': 'By Location', 'url': '/salaries/by-location/'},
    {'name': 'San Francisco', 'url': '/salaries/vp-sales-salary-san-francisco/'}
]
schema_html = generate_breadcrumb_schema(breadcrumbs)
```

### Example: FAQPage with Data-Driven Content

```python
from seo_core import generate_salary_faqs, generate_faq_html

faqs = generate_salary_faqs(
    role_title="VP Sales",
    location="San Francisco",
    avg_min=244452,
    avg_max=347218,
    sample_count=18,
    comparison_data={'national_avg_max': 256000}
)
faq_html = generate_faq_html(faqs, include_schema=True)
```

## Content Quality Guidelines

### Avoiding Thin Content

1. **Minimum threshold**: Pages require 5+ job postings (`MIN_JOBS_FOR_PAGE = 5`)
2. **Contextual enrichment**: Each page type has unique context sections
3. **Data-driven FAQs**: Questions and answers use actual data, not generic templates

### Location Context Example

San Francisco pages include:
> "San Francisco remains the highest-paying market for sales leadership, driven by the concentration of well-funded startups and enterprise tech companies. Competition for talent is fierce, with many companies offering premium packages to attract proven leaders."

### Company Stage Context Example

Seed/Series A pages include:
> "Early-stage companies (Seed through Series A) typically offer lower base salaries but compensate with significant equity grants. Expect 0.5-2% equity for VP-level hires..."

## FAQ Generation Logic

FAQs are generated based on available data:

| Condition | FAQ Generated |
|-----------|---------------|
| Location + salary data | "What is the average VP Sales salary in {location}?" |
| Salary range > 30% spread | "Why is the salary range so wide?" |
| Location + national comparison | "How do {location} salaries compare to other markets?" |
| Sample count available | "How accurate is this salary data?" |
| Always included | "Should I negotiate base salary or OTE?" |

## Internal Linking

### Related Pages Engine

```python
from seo_core import get_related_salary_pages, generate_related_pages_html

related = get_related_salary_pages(current_page, all_pages, max_links=6)
html = generate_related_pages_html(related)
```

Links include:
- Parent hub page
- Sibling pages (same category, sorted by data volume)
- Cross-category pages (different dimension)

## Running the Generators

```bash
# Generate all enhanced salary pages
python3 scripts/generate_salary_pages_v2.py

# Generate hub pages
python3 scripts/generate_hub_pages.py

# Generate enhanced tool pages
python3 scripts/generate_tools_pages_v2.py
```

## Page Inventory

### Salary Pages (20 total)
- 11 location pages (San Francisco, New York, Boston, etc.)
- 6 company stage pages (Seed/Series A through Enterprise/Public)
- 3 seniority pages (VP, SVP, C-Level)

### Hub Pages (4 total)
- `/salaries/by-location/`
- `/salaries/by-stage/`
- `/salaries/by-seniority/`
- `/trends/`

### Tool Pages (13 total)
- 8 individual tool pages
- 5 category hub pages

## Data Sources

- **Salary data**: `data/comp_analysis.json` (656 executive records, 59.6% disclosure rate)
- **Tool data**: Hardcoded in `generate_tools_pages_v2.py` (can be externalized to JSON)

## Future Enhancements

1. **Externalize tool data** to `data/tools.json` for easier updates
2. **Add industry dimension** to salary pages when data available
3. **Implement comparison pages** (e.g., "SF vs NYC VP Sales Salary")
4. **Add structured data testing** with Google Rich Results Test
5. **Split sitemaps** by category when page count exceeds 10k

## CSS Styles

SEO component styles are centralized in `seo_core.py`:

```python
from seo_core import get_seo_styles

# Include in page <style> tag
styles = get_seo_styles()
```

Includes styles for:
- `.faq-section`, `.faq-item`, `.faq-question`, `.faq-answer`
- `.related-pages`, `.related-links-grid`, `.related-link`

## References

- Original pSEO architecture article (analyzed for this implementation)
- Verum website patterns (content depth, FAQ structure)
- Google's guidance on programmatic content quality
