# SEO Audit Report - thecroreport.com

**Audit Date:** January 25, 2026
**Total Pages Analyzed:** 1,356 HTML files
**Reference:** [SEO Best Practices Guide](./SEO_BEST_PRACTICES.md)

---

## Executive Summary

The site has **strong SEO foundations** on well-maintained pages (homepage, tool reviews, salary pages) but has **significant gaps** across job listings and several tool pages. The main issues are:

### Technical SEO Issues

| Issue | Count | Severity |
|-------|-------|----------|
| Missing Open Graph tags | 1,060 pages | HIGH |
| Missing Twitter Card tags | 1,069 pages | HIGH |
| Title tags over 60 chars | 1,191 pages | HIGH |
| Missing `<main>` landmark | 1,326 pages | MEDIUM |
| Missing BreadcrumbList schema | 1,327 pages | MEDIUM |
| Meta descriptions over 160 chars | 51 pages | MEDIUM |
| Missing H1 tag | 21 pages | MEDIUM |
| Images missing width/height | 111 instances | MEDIUM |
| Missing canonical tag | 3 pages | HIGH |
| Missing Google Analytics | 3 pages | HIGH |

### Content Quality Issues (E-E-A-T)

| Issue | Count | Severity |
|-------|-------|----------|
| **Missing related links sections** | 1,356 pages (ALL) | HIGH |
| **No authoritative source citations** | ~50 tool pages | HIGH |
| **Duplicate title tags** | 77+ job pages | HIGH |
| **Duplicate meta descriptions** | 43+ job pages | HIGH |
| **Thin content (<1,000 words)** | 3 tool pages | MEDIUM |

---

## Critical Issues (Immediate Fix Required)

### 1. Missing Canonical Tags (3 pages)

**Impact:** Duplicate content issues, diluted rankings

**Affected pages:**
- `site/tools/linkedin-sales-navigator/index.html`
- `site/tools/cognism/index.html`
- `site/tools/gong-vs-chorus/index.html`

**Fix:** Add canonical tag to each page:
```html
<link rel="canonical" href="https://thecroreport.com/tools/{page-path}/">
```

### 2. Missing Open Graph & Twitter Cards (1,060+ pages)

**Impact:** Poor social sharing appearance, missed traffic from social platforms

**Affected sections:**
- All job listing pages (`site/jobs/*/index.html`) - ~1,000+ pages
- Newsletter page (`site/newsletter/index.html`)
- Several tool pages (warmly, unify, demandbase, cloudingo, etc.)
- Assessment page (`site/assessment/index.html`)

**Fix:** Add to each page `<head>`:
```html
<!-- Open Graph Tags -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://thecroreport.com/{path}/">
<meta property="og:title" content="{Page Title} | The CRO Report">
<meta property="og:description" content="{Same as meta description}">
<meta property="og:site_name" content="The CRO Report">
<meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">

<!-- Twitter Card Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Page Title} | The CRO Report">
<meta name="twitter:description" content="{Same as meta description}">
<meta property="twitter:image" content="https://thecroreport.com/assets/social-preview.png">
```

### 3. Missing Google Analytics (3 pages)

**Impact:** No tracking data for these pages

**Affected pages:**
- `site/tools/linkedin-sales-navigator/index.html`
- `site/tools/cognism/index.html`
- `site/tools/gong-vs-chorus/index.html`

**Fix:** Add GA4 tracking code after `<head>`:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3119XDMC12"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-3119XDMC12');
</script>
```

---

## High Priority Issues

### 4. Meta Descriptions Over 160 Characters (51 pages)

**Impact:** Truncated descriptions in search results

**Sample affected pages with lengths:**
| Page | Length |
|------|--------|
| `tools/apollo/index.html` | 211 chars |
| `tools/artisan/index.html` | 206 chars |
| `tools/clari/index.html` | 192 chars |
| `tools/gong/index.html` | 185 chars |
| `tools/unify/index.html` | 178 chars |
| `tools/zoominfo/index.html` | 177 chars |
| `tools/regie/index.html` | 175 chars |
| `tools/zoominfo-vs-apollo/index.html` | 173 chars |
| `tools/warmly/index.html` | 172 chars |
| `tools/leandata/index.html` | 172 chars |
| `tools/gong-vs-clari/index.html` | 172 chars |
| ... and 40 more |

**Fix:** Trim descriptions to 150-160 characters. Example:

**Before (Apollo - 211 chars):**
```
Apollo.io review for 2026. The best value B2B data + engagement platform starting at $49/user/month with a free tier. Great for SMB/mid-market, but data quality isn't ZoomInfo-level. Here's the honest breakdown.
```

**After (158 chars):**
```
Apollo.io review 2026: Best value B2B data + engagement platform from $49/user. Great for SMB, but data quality trails ZoomInfo. Honest breakdown inside.
```

### 5. Missing H1 Tags (21 pages)

**Impact:** Poor heading hierarchy, accessibility issues

**Affected pages:**
- All salary location pages (`site/salaries/vp-sales-salary-*/index.html`)
- Newsletter page (`site/newsletter/index.html`)

**Fix:** Add proper H1 tag as the main page heading:
```html
<h1>VP Sales Salary in Boston</h1>
```

---

## Medium Priority Issues

### 6. Missing `<main>` Landmark (1,326 pages)

**Impact:** Accessibility issues, poor Core Web Vitals (SEO score deduction)

**Affected:** Nearly all pages lack the `<main>` wrapper

**Fix:** Wrap page content between header and footer:
```html
<header class="site-header">...</header>
<main>
    <!-- All page content here -->
</main>
<footer class="site-footer">...</footer>
```

### 7. Missing BreadcrumbList Schema (1,327 pages)

**Impact:** Missing rich snippets in Google, reduced click-through rates

**Good example (already has schema):**
- `site/salaries/vp-sales-salary/index.html` - has BreadcrumbList JSON-LD

**Needs schema (missing):**
- All job listing pages
- Most tool pages
- All salary location pages

**Fix:** Add JSON-LD to `<head>`:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://thecroreport.com/"},
    {"@type": "ListItem", "position": 2, "name": "Jobs", "item": "https://thecroreport.com/jobs/"},
    {"@type": "ListItem", "position": 3, "name": "{Job Title}"}
  ]
}
</script>
```

### 8. Images Missing Width/Height Attributes (111 instances)

**Impact:** Layout shift (poor CLS), SEO score deduction

**Affected pages:**
- `site/tools/index.html` - multiple logo images
- `site/tools/aisdr/index.html`
- `site/tools/zoominfo-vs-apollo/index.html`
- `site/tools/salesloft/index.html`
- Various other tool pages

**Fix:** Add explicit dimensions to all `<img>` tags:
```html
<!-- Before -->
<img src="/assets/logos/Apollo.io_logo.png" alt="Apollo Logo">

<!-- After -->
<img src="/assets/logos/Apollo.io_logo.png" alt="Apollo Logo" width="56" height="56">
```

---

## Content Quality Issues (E-E-A-T)

### 9. Title Tags Over 60 Characters (1,191 pages)

**Impact:** Truncated titles in search results, poor click-through rates

**Sample affected pages:**
| Page | Length |
|------|--------|
| `tools/cloudingo/index.html` | 95 chars |
| `tools/salesloft/index.html` | 91 chars |
| `tools/leandata/index.html` | 91 chars |
| `tools/openprise/index.html` | 89 chars |
| `tools/chorus/index.html` | 89 chars |
| `tools/demandbase/index.html` | 84 chars |
| `tools/warmly/index.html` | 84 chars |
| ... and 1,183 more |

**Fix:** Keep titles under 60 characters. Example:

**Before (Salesloft - 91 chars):**
```
Salesloft Review 2026: Enterprise Sales Engagement with AI Meeting Insights | The CRO Report
```

**After (58 chars):**
```
Salesloft Review 2026: Enterprise Sales Engagement | CRO
```

### 10. Missing Related Links Sections (ALL 1,356 pages)

**Impact:** Poor internal linking, missed "link juice" distribution, reduced crawlability

**Per your SEO best practices (line 301-312):**
> "Every content page should have related links... Link to 3-4 related pages within the same category"

**Current state:** Zero pages have a related links section.

**Fix:** Add to bottom of each page's content:
```html
<p class="related-links">
  Related:
  <a href="/tools/apollo/">Apollo Review</a> |
  <a href="/tools/zoominfo/">ZoomInfo Review</a> |
  <a href="/salaries/vp-sales-salary/">VP Sales Salary Data</a>
</p>
```

### 11. No Authoritative Source Citations (E-E-A-T Issue)

**Impact:** Lower trust signals for Google, reduced E-E-A-T score, less credibility

**Per your SEO best practices (line 333-348):**
> "Statistics should be cited with authoritative sources: BLS, Census, Gartner, Forrester, McKinsey, HBR"

**Current state:** Tool pages cite user reviews (G2, Reddit) but make statistical claims without authoritative sources:
- "80% of ZoomInfo's value at 20% of the cost" — no source
- "raised over $250M" — no source linked
- "serves over 1 million users" — no source linked
- "30-40% bounce rates" — anecdotal, no industry benchmark

**Recommended citations to add:**
| Claim Type | Authoritative Source |
|------------|---------------------|
| Data decay rates | Bureau of Labor Statistics (job tenure data) |
| Sales productivity stats | Gartner, Forrester |
| B2B market size | McKinsey, CB Insights |
| Company funding/valuation | Crunchbase, PitchBook |
| Tool pricing comparisons | Vendr (already using), G2 |

**Fix example:**
```html
<!-- Before -->
<p>B2B databases decay at 25-30% annually.</p>

<!-- After -->
<p>B2B databases decay at 25-30% annually, according to
<a href="https://www.bls.gov/news.release/tenure.nr0.htm" target="_blank" rel="noopener">
Bureau of Labor Statistics</a> data on average job tenure.</p>
```

### 12. Duplicate Titles and Descriptions (Job Pages)

**Impact:** Duplicate content signals, confused indexing, diluted rankings

**Duplicate titles found:**
| Title | Occurrences |
|-------|-------------|
| "VP of Sales (OTE $300,000/year USD), @CXT Software..." | 77 pages |
| "Sales Vice President at Accenture Sap Regional..." | 43 pages |
| "Vice President Of Sales at Wfs Group..." | 31 pages |

**Duplicate descriptions found:**
| Description Pattern | Occurrences |
|--------------------|-------------|
| "This [Job Title] position at [Company] is no longer available..." | 43+ pages |

**Root cause:** Job pages for filled positions share identical templates without unique identifiers.

**Fix:** Make each title/description unique:
```html
<!-- Before (duplicate) -->
<title>VP of Sales at Accenture - Position Filled | The CRO Report</title>

<!-- After (unique with location/date) -->
<title>VP of Sales at Accenture (NYC) - Filled Jan 2026 | The CRO Report</title>
```

### 13. Thin Content (3 tool pages)

**Impact:** Low ranking potential, perceived as low-quality

**Pages under 1,000 words:**
| Page | Word Count |
|------|------------|
| `tools/cognism/index.html` | 639 words |
| `tools/linkedin-sales-navigator/index.html` | 646 words |
| `tools/gong-vs-chorus/index.html` | 876 words |

**Note:** These are the same 3 pages missing canonical tags and GA tracking — they appear to be incomplete drafts.

**For comparison, well-performing pages:**
| Page | Word Count |
|------|------------|
| `tools/salesforce/index.html` | 4,264 words |
| `tools/hubspot/index.html` | 4,081 words |
| `tools/11x/index.html` | 4,011 words |
| `tools/apollo/index.html` | 3,492 words |

**Fix:** Expand thin pages to 2,500-3,500+ words with:
- Pricing breakdown section
- Pros/cons analysis
- User quotes from G2/Reddit
- Comparison tables
- Bottom line verdict

---

## Pages with Good SEO (Use as Templates)

These pages follow best practices and can serve as templates:

1. **Homepage** (`site/index.html`)
   - Has: canonical, OG tags, Twitter cards, GA4, Clarity, proper heading hierarchy
   - Missing: BreadcrumbList (not needed for homepage), `<main>` landmark

2. **Apollo Tool Review** (`site/tools/apollo/index.html`)
   - Has: canonical, OG tags, Twitter cards, Article schema, proper H1
   - Missing: `<main>` landmark
   - Issue: Meta description too long (211 chars)

3. **VP Sales Salary** (`site/salaries/vp-sales-salary/index.html`)
   - Has: canonical, OG tags, Twitter cards, BreadcrumbList, Dataset schema
   - Missing: `<main>` landmark, H1 tag
   - Note: Best structured data implementation

---

## Recommended Fixes by Priority

### Phase 1: Critical (This Week)
1. Fix 3 incomplete tool pages (cognism, linkedin-sales-navigator, gong-vs-chorus):
   - Add canonical tags
   - Add Google Analytics
   - Expand content to 2,500+ words
2. Add OG/Twitter tags to newsletter and assessment pages

### Phase 2: High Priority (Next 2 Weeks)
1. **Shorten all title tags to under 60 characters** (1,191 pages)
2. Trim all 51 meta descriptions to under 160 characters
3. Add H1 tags to 21 affected pages
4. Add `<main>` landmark to all pages (template update)
5. **Fix duplicate titles/descriptions on job pages** (add location/date identifiers)

### Phase 3: Content Quality (Next Month)
1. **Add related links sections to ALL pages** (critical for internal linking)
2. **Add authoritative source citations to tool pages:**
   - Link funding claims to Crunchbase/PitchBook
   - Link market stats to Gartner/Forrester/McKinsey
   - Link industry data to BLS/Census
3. Add OG/Twitter tags to all ~1,000 job pages (template update)
4. Add BreadcrumbList schema to all pages (template update)
5. Add width/height to all images

### Phase 4: Ongoing
1. Run PageSpeed Insights on key pages monthly
2. Validate new pages against SEO checklist before publishing
3. Test social previews with Facebook/Twitter debuggers
4. **Audit new content for E-E-A-T compliance:**
   - Stats must have authoritative sources
   - Related links must be included
   - Word count minimum 2,500 for tool reviews

---

## Scripts to Find Issues

Add these to your workflow for ongoing audits:

```bash
# Find pages missing canonical tag
find site -name "*.html" | xargs grep -L 'rel="canonical"'

# Find pages missing OG tags
find site -name "*.html" | xargs grep -L 'og:title'

# Find meta descriptions over 160 chars
for f in $(find site -name "*.html"); do
  desc=$(grep -o 'meta name="description" content="[^"]*"' "$f" 2>/dev/null | head -1 | sed 's/.*content="\(.*\)"/\1/')
  if [ -n "$desc" ] && [ ${#desc} -gt 160 ]; then
    echo "${#desc} chars: $f"
  fi
done

# Find pages missing main landmark
find site -name "*.html" | xargs grep -L '<main'

# Find images missing width attribute
grep -r '<img ' site --include="*.html" | grep -v 'width='
```

---

## Suggested Template Updates

To fix issues at scale, update the page generation scripts/templates to include:

1. **All pages should have:**
   - `<main>` wrapper around content
   - Complete OG and Twitter Card meta tags
   - Canonical URL
   - BreadcrumbList JSON-LD (except homepage)

2. **Job page template should add:**
   - OG tags with job title and company
   - Twitter cards
   - JobPosting schema (for rich results)
   - BreadcrumbList

3. **Tool page template should add:**
   - `<main>` landmark
   - Width/height on logo images
   - Verify meta description length < 160

---

*Generated by SEO Audit Tool - January 25, 2026*
