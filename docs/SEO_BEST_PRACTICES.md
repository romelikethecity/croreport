# SEO Best Practices Guide

A portable guide for implementing SEO best practices across any website. Replace placeholders with your site-specific values.

---

## Configuration Placeholders

Replace these throughout your implementation:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{DOMAIN}` | Your canonical domain | `example.com` |
| `{SITE_NAME}` | Your brand/site name | `Example Inc` |
| `{GA_ID}` | Google Analytics 4 ID | `G-XXXXXXXXXX` |
| `{CLARITY_ID}` | Microsoft Clarity ID | `xxxxxxxxxx` |
| `{SOCIAL_IMAGE}` | Social preview image path | `/assets/social-preview.png` |

---

## Meta Tags (Required on Every Page)

```html
<!-- Basic -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{Page Title} | {SITE_NAME}</title>
<meta name="description" content="{120-160 characters}">
<meta name="keywords" content="{keyword1}, {keyword2}, {keyword3}">

<!-- Canonical (CRITICAL) -->
<link rel="canonical" href="https://{DOMAIN}/{path}/">

<!-- Favicon -->
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://{DOMAIN}/{path}/">
<meta property="og:title" content="{Page Title} | {SITE_NAME}">
<meta property="og:description" content="{Same as meta description}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:image" content="https://{DOMAIN}{SOCIAL_IMAGE}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Page Title} | {SITE_NAME}">
<meta name="twitter:description" content="{Same as meta description}">
<meta name="twitter:image" content="https://{DOMAIN}{SOCIAL_IMAGE}">
```

---

## Meta Description Guidelines

### Length Requirements
- **Minimum:** 120 characters
- **Maximum:** 160 characters (Google truncates longer descriptions)
- **Optimal:** 150-160 characters

### Templates by Page Type

**Product/Service Pages:**
```
{Service} for {audience}. {Key benefit}. {Differentiator or CTA}.
```
Example: "Data enrichment for B2B companies. Firmographics, contacts, and technographics. Human-verified quality." (103 chars)

**Resource/Guide Pages:**
```
{Topic} for {audience}. {Key benefit or use case}.
```
Example: "Data enrichment for financial services. KYC automation, compliance, and customer data management." (97 chars)

**Category/Directory Pages:**
```
Find {item type} with {key feature}. {What's included}.
```
Example: "Find dental practices with verified contact data. Owner contacts, NPI numbers, and practice details." (100 chars)

### Common Mistakes to Avoid
- Descriptions over 160 characters (get truncated)
- Duplicate descriptions across pages
- Empty or placeholder descriptions
- Starting with "Welcome to..." or similar generic text

---

## CSS Cache-Busting

**Always include version parameter on CSS links:**
```html
<link rel="stylesheet" href="/css/styles.css?v=1">
```

**When to increment:**
- After any CSS changes
- When deploying significant updates

**Why this matters:** CDNs and browsers cache CSS. Without version params, users see stale styles.

---

## Tracking Code Setup

### Google Analytics 4

```html
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
```

### Microsoft Clarity (Optional but Recommended)

```html
<script type="text/javascript">
  (function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", "{CLARITY_ID}");
</script>
```

**Important:** Never use placeholder IDs like `G-XXXXXXXXXX` in production.

---

## Structured Data (JSON-LD)

### Organization Schema (Homepage)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{SITE_NAME}",
  "url": "https://{DOMAIN}",
  "logo": "https://{DOMAIN}/assets/logo.svg",
  "description": "{Company description}",
  "sameAs": [
    "https://www.linkedin.com/company/{company}/",
    "https://twitter.com/{handle}"
  ]
}
</script>
```

### BreadcrumbList Schema (All Inner Pages)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://{DOMAIN}/"},
    {"@type": "ListItem", "position": 2, "name": "{Category}", "item": "https://{DOMAIN}/{category}/"},
    {"@type": "ListItem", "position": 3, "name": "{Page Title}"}
  ]
}
</script>
```

### Service Schema (Service/Product Pages)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "{Service Name}",
  "provider": {
    "@type": "Organization",
    "name": "{SITE_NAME}"
  },
  "description": "{Service description under 200 chars}",
  "serviceType": "{Service Type}"
}
</script>
```

### FAQPage Schema (Pages with FAQ Sections)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question 1?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer 1."
      }
    },
    {
      "@type": "Question",
      "name": "Question 2?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer 2."
      }
    }
  ]
}
</script>
```

**Important:** FAQ schema questions must match visible FAQ content on the page.

### Article Schema (Blog/Resource Pages)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{Article Title}",
  "author": {"@type": "Organization", "name": "{SITE_NAME}"},
  "publisher": {"@type": "Organization", "name": "{SITE_NAME}"},
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD"
}
</script>
```

### Schema Validation
- Test with Google's Rich Results Test: https://search.google.com/test/rich-results
- Ensure all JSON-LD blocks are complete (no unclosed braces)
- Never leave incomplete schema blocks

---

## Social Preview Image

**Requirements:**
- **Dimensions:** 1200 x 630 pixels
- **Format:** PNG or JPG
- **Content:** Brand logo, key message, clear on dark and light backgrounds

**Testing:**
- Facebook: https://developers.facebook.com/tools/debug/
- Twitter: https://cards-dev.twitter.com/validator
- LinkedIn: https://www.linkedin.com/post-inspector/

---

## PageSpeed & Core Web Vitals

### Target Scores
| Metric | Target |
|--------|--------|
| Performance | 90+ |
| Accessibility | 90+ |
| Best Practices | 90+ |
| SEO | 100 |

### Core Web Vitals Targets
| Metric | Target | Description |
|--------|--------|-------------|
| LCP (Largest Contentful Paint) | < 2.5s | Main content load time |
| FCP (First Contentful Paint) | < 1.8s | Time to first visible content |
| CLS (Cumulative Layout Shift) | < 0.1 | Visual stability |
| TBT (Total Blocking Time) | < 200ms | Main thread responsiveness |

### HTML Best Practices

**1. Always wrap page content in `<main>` landmark:**
```html
<header id="site-header"></header>
<main>
  <!-- All page content here -->
</main>
<footer id="site-footer"></footer>
```

**2. Always add width/height to images:**
```html
<!-- Prevents layout shift (CLS) -->
<img src="/path/to/image.png" alt="Description" width="200" height="100">
```

**3. Heading hierarchy:**
Use headings in sequential order: h1 → h2 → h3. Don't skip levels.

**4. Font loading:**
Use `display=swap` with web fonts to prevent invisible text.

---

## Internal Linking

**Every content page should have related links:**
```html
<p class="related-links">Related: <a href="/path1/">Link 1</a> | <a href="/path2/">Link 2</a> | <a href="/path3/">Link 3</a></p>
```

**Guidelines:**
- Link to 3-4 related pages within the same category
- Include at least 1 link to a different but relevant category
- Link to key service/product pages when appropriate

---

## Sitemap & Robots.txt

### robots.txt

```
User-agent: *
Allow: /

Sitemap: https://{DOMAIN}/sitemap.xml
```

### Sitemap Guidelines
- Generate XML sitemap for all indexable pages
- Submit to Google Search Console after major changes
- Include `<lastmod>` dates for frequently updated pages

---

## Citation Requirements (E-E-A-T)

**Statistics should be cited with authoritative sources:**

```html
<p>B2B databases decay at 25-30% annually, according to
<a href="https://www.bls.gov/news.release/tenure.nr0.htm" target="_blank" rel="noopener">Bureau of Labor Statistics</a>
data on average job tenure.</p>
```

**Authoritative sources by category:**
- **Government:** BLS, Census, Federal Reserve, SEC
- **Research:** Gartner, Forrester, McKinsey, HBR
- **Industry:** Salesforce, HubSpot, relevant trade associations
- **Platform docs:** Official documentation for any tools mentioned

---

## Pre-Commit SEO Checklist

Before publishing any new or modified page:

- [ ] Title tag is unique and under 60 characters
- [ ] Meta description is 120-160 characters
- [ ] Canonical URL is set correctly
- [ ] CSS link includes version parameter
- [ ] Open Graph tags present
- [ ] Twitter Card tags present
- [ ] BreadcrumbList schema present (inner pages)
- [ ] All JSON-LD blocks are complete and valid
- [ ] H1 tag is present and unique
- [ ] Images have width/height attributes
- [ ] Images have descriptive alt text
- [ ] Related links section present
- [ ] Tracking codes present with correct IDs
- [ ] No placeholder values anywhere
- [ ] Page added to sitemap

---

## Quick SEO Audit Commands

Run these periodically to catch issues:

```bash
# Count pages with meta descriptions over 160 characters
for f in $(find . -name "*.html" -type f | grep -v node_modules); do
  desc=$(grep -o 'meta name="description" content="[^"]*"' "$f" 2>/dev/null | head -1 | sed 's/.*content="\(.*\)"/\1/')
  if [ -n "$desc" ] && [ ${#desc} -gt 160 ]; then
    echo "${#desc} chars: $f"
  fi
done

# Find pages missing BreadcrumbList schema
find . -name "*.html" -type f | xargs grep -L 'BreadcrumbList' | grep -v 'index.html$'

# Find pages missing CSS version parameter
grep -r 'href="/css/styles.css"' --include="*.html" | grep -v 'styles.css?v='

# Find pages missing canonical tag
find . -name "*.html" -type f | xargs grep -L 'rel="canonical"'

# Find pages missing Open Graph tags
find . -name "*.html" -type f | xargs grep -L 'og:title'

# Find pages with placeholder tracking IDs
grep -r "G-XXXXXXXXXX" --include="*.html"
grep -r "XXXXXXXXXX" --include="*.html"
```

---

## Full Page Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Page Title} | {SITE_NAME}</title>
  <meta name="description" content="{120-160 char description}">
  <meta name="keywords" content="{keyword1}, {keyword2}, {keyword3}">

  <link rel="canonical" href="https://{DOMAIN}/{path}/">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/styles.css?v=1">

  <meta property="og:type" content="website">
  <meta property="og:url" content="https://{DOMAIN}/{path}/">
  <meta property="og:title" content="{Page Title} | {SITE_NAME}">
  <meta property="og:description" content="{Same as meta description}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:image" content="https://{DOMAIN}{SOCIAL_IMAGE}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{Page Title} | {SITE_NAME}">
  <meta name="twitter:description" content="{Same as meta description}">
  <meta name="twitter:image" content="https://{DOMAIN}{SOCIAL_IMAGE}">

  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{GA_ID}');
  </script>

  <!-- Microsoft Clarity (optional) -->
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "{CLARITY_ID}");
  </script>

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://{DOMAIN}/"},
      {"@type": "ListItem", "position": 2, "name": "{Category}", "item": "https://{DOMAIN}/{category}/"},
      {"@type": "ListItem", "position": 3, "name": "{Page Title}"}
    ]
  }
  </script>
</head>
<body>
  <header id="site-header"></header>

  <main>
    <section class="page-hero">
      <div class="container">
        <h1>{Page Title}</h1>
        <p>{Subtitle}</p>
      </div>
    </section>

    <section class="content">
      <div class="container">
        <!-- Page content here -->

        <p class="related-links">Related: <a href="/path1/">Link 1</a> | <a href="/path2/">Link 2</a> | <a href="/path3/">Link 3</a></p>
      </div>
    </section>
  </main>

  <footer id="site-footer"></footer>
</body>
</html>
```

---

## Common Issues to Avoid

| Issue | Impact | Fix |
|-------|--------|-----|
| Wrong canonical domain | Duplicate content, diluted rankings | Always use production domain |
| Missing OG tags | Poor social previews | Add all required OG tags |
| Duplicate content | Confused indexing | Unique title/description per page |
| Broken internal links | Poor crawlability, bad UX | Test links after changes |
| Missing tracking | No analytics data | Add GA4 to every page |
| Meta descriptions >160 chars | Truncated in search results | Keep under 160 characters |
| Missing alt text on images | Accessibility issues, missed SEO | Add descriptive alt text |
| Skipped heading levels | Accessibility issues | Use h1 → h2 → h3 in order |
| Images without dimensions | Layout shift (poor CLS) | Add width/height attributes |
| Incomplete JSON-LD | Schema errors | Validate with Google's tool |

---

## Resources

- **PageSpeed Insights:** https://pagespeed.web.dev/
- **Rich Results Test:** https://search.google.com/test/rich-results
- **Mobile-Friendly Test:** https://search.google.com/test/mobile-friendly
- **Google Search Console:** https://search.google.com/search-console
- **Schema.org Documentation:** https://schema.org/
- **Facebook Debugger:** https://developers.facebook.com/tools/debug/
- **Twitter Card Validator:** https://cards-dev.twitter.com/validator
