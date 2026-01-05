# The CRO Report - SEO Script Updates

## Summary of Changes

### Critical Fix: generate_job_pages.py
**Issue:** Canonical URL was pointing to `romelikethecity.github.io/croreport` instead of `thecroreport.com`
- This was splitting your SEO authority between two domains
- Google was indexing the wrong domain

**Fixed in this update:**
- ✅ Correct canonical URL (`https://thecroreport.com/jobs/{slug}/`)
- ✅ SEO-optimized titles with salary/location: `VP Sales at Acme Corp - $200K-$300K (Remote) | The CRO Report`
- ✅ Open Graph tags for LinkedIn sharing
- ✅ Twitter card tags
- ✅ JobPosting JSON-LD schema (enables Google rich results with salary, location, and apply button)

### Critical Fix: generate_job_board.py
**Issue:** Missing tracking code entirely (GA4 + Clarity not firing on `/jobs/` index page)

**Fixed in this update:**
- ✅ Added tracking code import and injection
- ✅ Added Open Graph tags
- ✅ Added Twitter card tags
- ✅ Added canonical URL
- ✅ Better page title with job count

## Installation

1. **Backup your existing scripts:**
```bash
cd ~/your-repo-path
cp scripts/generate_job_pages.py scripts/generate_job_pages.py.bak
cp scripts/generate_job_board.py scripts/generate_job_board.py.bak
```

2. **Copy new scripts to your repo:**
```bash
cp ~/Downloads/updated_scripts/generate_job_pages.py scripts/
cp ~/Downloads/updated_scripts/generate_job_board.py scripts/
```

3. **Commit and push:**
```bash
git add scripts/
git commit -m "SEO improvements: fix canonical URLs, add OG tags, add JobPosting schema"
git push
```

4. **Wait for GitHub Actions to complete** (~5 min)

5. **Verify the fix:**
   - Go to https://thecroreport.com/jobs/
   - View source (Cmd+U)
   - Search for `canonical` - should show `https://thecroreport.com/jobs/`
   - Search for `og:` - should see Open Graph tags

## What You'll See After Deployment

### In Google Search Console (after 1-2 weeks):
- Pages indexed under thecroreport.com instead of github.io
- JobPosting rich results appearing for individual job pages

### On LinkedIn/Twitter shares:
- Proper preview cards with title, description, and image
- Consistent branding across social platforms

### In Google Analytics:
- `/jobs/` page traffic now tracked (it wasn't before!)

## Other Scripts to Update (Lower Priority)

These scripts work but are missing OG tags. Update when you have time:

| Script | Missing |
|--------|---------|
| generate_company_pages.py | OG tags, Twitter cards |
| generate_category_pages.py | OG tags, Twitter cards |
| generate_salary_pages.py | OG tags, Twitter cards |
| generate_homepage.py | OG tags, Twitter cards |
| generate_insights_page.py | Canonical, OG tags |
| generate_tools_pages.py | Canonical, OG tags |

The pattern to add to each `<head>` section:

```html
<!-- Open Graph Tags -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://thecroreport.com/PAGE_PATH/">
<meta property="og:title" content="PAGE TITLE">
<meta property="og:description" content="PAGE DESCRIPTION">
<meta property="og:site_name" content="The CRO Report">
<meta property="og:image" content="https://thecroreport.com/assets/social-preview.png">

<!-- Twitter Card Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="PAGE TITLE">
<meta name="twitter:description" content="PAGE DESCRIPTION">
<meta name="twitter:image" content="https://thecroreport.com/assets/social-preview.png">
```

## Social Preview Image

Make sure you have `/assets/social-preview.png` on your site. If not:
1. Create a 1200x630px image with your logo and tagline
2. Save as `site/assets/social-preview.png`

## Questions?

The most important fix is the canonical URL in generate_job_pages.py - that's actively hurting your SEO right now by splitting authority to the wrong domain.
