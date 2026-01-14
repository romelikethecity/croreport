# PageSpeed Performance Optimization Guide

A comprehensive guide for optimizing static sites for PageSpeed Insights, based on optimizations performed on thecroreport.com (Jan 2026).

## Quick Reference: Target Metrics

| Metric | Target | What It Measures |
|--------|--------|------------------|
| Performance Score | 90+ (green) | Overall score |
| FCP (First Contentful Paint) | < 1.8s | Time to first text/image |
| LCP (Largest Contentful Paint) | < 2.5s | Time to largest element |
| TBT (Total Blocking Time) | < 200ms | Main thread blocking |
| CLS (Cumulative Layout Shift) | < 0.1 | Visual stability |

## The Big Wins (Highest Impact)

### 1. Image Optimization

**Problem:** Large images are the #1 cause of slow LCP.

**Solution:**
```bash
# Check image sizes
ls -la site/assets/*.jpg site/assets/*.png

# Compress with ImageMagick (macOS: brew install imagemagick)
convert large-image.jpg -resize 200x200 -quality 85 optimized.jpg
```

**Guidelines:**
- Logo images: 200x200px max (displayed at 40x40, 2x for retina)
- Hero images: 1200px wide max
- Always add `width` and `height` attributes to prevent CLS:
```html
<img src="/assets/logo.jpg" alt="Logo" width="40" height="40">
```

### 2. Google Fonts (Non-Blocking)

**Problem:** Default Google Fonts loading blocks render (~2000ms penalty).

**Bad (blocks render):**
```html
<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
```

**Good (non-blocking):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap"></noscript>
```

**Never use `@import` in CSS** - it's render-blocking:
```css
/* BAD - blocks render */
@import url('https://fonts.googleapis.com/css2?family=Inter');
```

### 3. Chart/Graph DPI

**Problem:** Matplotlib defaults to 300 DPI (print quality), web only needs 72-150.

**Fix in Python:**
```python
# Bad
plt.savefig(output_path, dpi=300, ...)

# Good
plt.savefig(output_path, dpi=150, ...)
```

This typically reduces chart file sizes by 50-60%.

### 4. Lazy Loading

**For images below the fold:**
```html
<img src="chart.png" loading="lazy" width="800" height="400" alt="...">
```

**For iframes (embeds, videos):**
```html
<iframe src="https://example.com/embed" loading="lazy" title="Description"></iframe>
```

Note: Don't lazy-load above-the-fold content (logo, hero image).

## Analytics Placement

### Google's Recommendation
Place analytics in `<head>` immediately after `<meta charset>`:

```html
<head>
    <meta charset="UTF-8">
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXX');
    </script>
    <!-- Rest of head -->
</head>
```

### Trade-offs

| Placement | PageSpeed | Data Accuracy |
|-----------|-----------|---------------|
| `<head>` (recommended) | Lower score | Complete tracking |
| `</body>` | Higher score | May miss fast-bouncing users |

**Recommendation:** Keep in `<head>`. The async attribute prevents blocking, and data accuracy is more valuable than a few PageSpeed points.

### Microsoft Clarity

Clarity is lightweight (~25KB) and async. It's not a significant performance concern despite what PageSpeed's "unused JavaScript" warning suggests.

```html
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "YOUR_PROJECT_ID");
</script>
```

## What NOT to Do

### Don't Defer Analytics with requestIdleCallback

This approach caused "Forced reflow" issues and tanked performance from 79 to 32:

```javascript
// DON'T DO THIS - causes forced reflow
if ('requestIdleCallback' in window) {
    requestIdleCallback(loadAnalytics, { timeout: 3000 });
} else {
    setTimeout(loadAnalytics, 2000);
}
```

### Don't Remove Analytics for PageSpeed

The "unused JavaScript" warning (1,200+ KiB) is primarily GA4's gtag.js library. This is a known trade-off - you can't have GA4 without its code.

## PageSpeed Test Variance

**Important:** PageSpeed Insights has significant test-to-test variance (±10-15 points is normal).

Our actual test results (same site, same code):
- Test 1: Score 30 (outlier with "Forced reflow")
- Test 2: Score 80
- Test 3: Score 77

**Best practice:** Run 3-5 tests and take the median/average. Ignore outliers.

The "Forced reflow" issue is an intermittent race condition with third-party scripts that can't be reliably prevented.

## Checklist for New Sites

### Before Launch
- [ ] Compress all images (target <100KB for logos, <500KB for hero)
- [ ] Add `width` and `height` to all `<img>` tags
- [ ] Use async Google Fonts (media="print" onload trick)
- [ ] Set chart DPI to 150 (not 300)
- [ ] Add `loading="lazy"` to below-fold images and iframes
- [ ] Add `title` attribute to all iframes (accessibility)

### Analytics Setup
- [ ] Place GA4 in `<head>` after `<meta charset>`
- [ ] Use `async` attribute on gtag.js script
- [ ] Clarity: use standard async snippet

### Testing
- [ ] Run PageSpeed 3-5 times, take median score
- [ ] Check both Mobile and Desktop tabs
- [ ] Verify no "Eliminate render-blocking resources" for fonts

## File Reference (thecroreport.com)

| File | Purpose |
|------|---------|
| `scripts/tracking_config.py` | GA4 + Clarity snippets |
| `scripts/templates.py` | Shared HTML head with async fonts |
| `scripts/generate_graphs.py` | Chart generation (DPI setting) |
| `scripts/generate_homepage.py` | Homepage with lazy iframe |

## Results Summary

Starting point (Jan 2026): **Score 57**
After optimizations: **Score 77-80**

| Change | Before | After |
|--------|--------|-------|
| Logo size | 1.4MB | 14KB |
| LCP | 10.1s | 2.3s |
| FCP | 2.9s | 1.5s |
| Accessibility | 91 | 96 |

The remaining "unused JavaScript" (~1,200KB) is GA4's library - an unavoidable trade-off for analytics functionality.
