---
name: thecroreport-seo
description: SEO and page generation standards for thecroreport.com. Use when creating new pages, scripts, sections, or programmatic page generators for The CRO Report website. Ensures correct canonical URLs (thecroreport.com, NOT GitHub Pages), proper Open Graph tags, tracking code, and JobPosting schema. Critical for any work involving generate_*.py scripts, new HTML templates, or site/ directory modifications.
---

# The CRO Report SEO Standards

Standards for all page generation on thecroreport.com to ensure proper SEO, social sharing, and analytics.

## Critical: Domain Configuration

**ALWAYS use `thecroreport.com` as the canonical domain.**

```python
# CORRECT
BASE_URL = 'https://thecroreport.com'
canonical_url = f"{BASE_URL}/jobs/{slug}/"

# WRONG - Never use GitHub Pages URL
BASE_URL = 'https://romelikethecity.github.io/croreport'  # âŒ NEVER
```

The site is hosted on GitHub Pages but uses a custom domain. All canonical URLs, OG tags, and sitemaps must reference `thecroreport.com`.

## Required Elements for Every Page

### 1. Tracking Code

Import and inject at the start of `<head>`:

```python
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

# In HTML template:
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    ...
'''
```

### 2. Canonical URL

Always include, always use thecroreport.com:

```html
<link rel="canonical" href="https://thecroreport.com/{page_path}/">
```

### 3. Open Graph Tags

Required for LinkedIn sharing (primary distribution channel):

```html
<!-- Open Graph Tags -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://thecroreport.com/{page_path}/">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{description}">
<meta property="og:site_name" content="The CRO Report">
<meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">

<!-- Twitter Card Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">
```

### 4. JobPosting Schema (Job Pages Only)

For individual job pages, include JSON-LD:

```html
<!-- JobPosting Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "JobPosting",
  "title": "{title}",
  "description": "{description}",
  "datePosted": "{date_posted}",
  "employmentType": "FULL_TIME",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "{company}"
  },
  "jobLocation": {
    "@type": "Place",
    "address": "{location}"
  },
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "USD",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": {min_salary},
      "maxValue": {max_salary},
      "unitText": "YEAR"
    }
  }
}
</script>
```

## Complete Head Template

```python
head_template = f'''<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | The CRO Report</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="https://thecroreport.com/{page_path}/">
    
    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://thecroreport.com/{page_path}/">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">
    
    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">
    
    <link rel="icon" type="image/jpeg" href="/assets/logo.jpg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    ...
</head>'''
```

## File Structure

```
site/
â”œâ”€â”€ index.html           # Homepage
â”œâ”€â”€ assets/
â”‚   â”œâ”€â”€ logo.jpg
â”‚   â””â”€â”€ social-preview.png  # 1200x630px for OG image
â”œâ”€â”€ jobs/
â”‚   â”œâ”€â”€ index.html       # Job board listing
â”‚   â””â”€â”€ {slug}/          # Individual job pages
â”‚       â””â”€â”€ index.html
â”œâ”€â”€ salaries/
â”‚   â”œâ”€â”€ index.html
â”‚   â””â”€â”€ {location}/
â”œâ”€â”€ companies/
â”‚   â”œâ”€â”€ index.html
â”‚   â””â”€â”€ {slug}/
â”œâ”€â”€ insights/
â”‚   â””â”€â”€ index.html
â”œâ”€â”€ tools/
â”‚   â””â”€â”€ index.html
â”œâ”€â”€ robots.txt
â””â”€â”€ sitemap.xml
```

## Workflow Requirement

The GitHub Actions workflow must commit generated pages. Ensure `build-site.yml` includes:

```yaml
- name: Commit updated data files
  run: |
    git add data/*.csv data/*.json data/*.md site/
    git diff --staged --quiet || git commit -m "Update data and assets [skip ci]"
    git push || true
```

Note: `site/` must be included in `git add` for generated pages to deploy.

## Checklist for New Page Generators

When creating any new `generate_*.py` script:

- [ ] `BASE_URL = 'https://thecroreport.com'` (never GitHub Pages)
- [ ] Import and inject tracking code
- [ ] Include canonical URL with thecroreport.com domain
- [ ] Include Open Graph tags
- [ ] Include Twitter Card tags
- [ ] For job pages: Include JobPosting JSON-LD schema
- [ ] Output to correct `site/` subdirectory
- [ ] Add to sitemap generation if needed
- [ ] Verify workflow commits the new pages

## Common Mistakes to Avoid

1. **Wrong canonical domain**: Using `romelikethecity.github.io/croreport` instead of `thecroreport.com`
2. **Missing OG tags**: Pages won't preview correctly on LinkedIn
3. **Missing tracking code**: Traffic won't be measured
4. **Pages not committed**: Generated pages need `site/` in the git add command
5. **Hardcoded GitHub Pages URLs**: Search for `github.io` in any new code
