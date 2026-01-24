# The CRO Report - Claude Code Instructions

This repo powers thecroreport.com (GitHub Pages with custom domain).

## When Writing GTM Tool Reviews

1. Read `.claude/gtm-tool-comparison.md` FIRST
2. Follow `.claude/seo-standards.md` for HTML structure
3. Follow `.claude/writing-style.md` for voice
4. Output to: `site/tools/{category}/{tool-slug}/index.html`

## Key Technical Requirements

- **Canonical URLs**: Always use `thecroreport.com` (NEVER `romelikethecity.github.io`)
- **Tracking**: Import from `scripts/tracking_config.py`
- **Navigation**: Import from `scripts/nav_config.py` (single source of truth)
- **Logos**: Check `/site/assets/logos/` for existing tool logos
- **Workflow**: Generated pages must be included in git add for GitHub Actions to deploy

## Navigation Config (scripts/nav_config.py)

**To update site-wide navigation**, edit `scripts/nav_config.py`:
- `NAV_ITEMS`: Main nav links (Jobs, Salaries, Tools, Market Intel, AI Assessment, About)
- `FOOTER_ITEMS`: Footer links (includes Newsletter)
- `SUBSCRIBE_LINK`: Subscribe button destination (/newsletter/)

After editing, regenerate all pages:
```bash
python3 scripts/generate_job_pages.py
python3 scripts/generate_category_pages.py
python3 scripts/generate_job_board.py
python3 scripts/generate_insights_page.py
python3 scripts/generate_newsletter_archive.py
```

## Page Generators Overview

| Generator | Output | Notes |
|-----------|--------|-------|
| `generate_job_pages.py` | `/jobs/{slug}/` | Individual job pages + stale job handling |
| `generate_job_board.py` | `/jobs/index.html` | Main job listing page |
| `generate_category_pages.py` | `/jobs/vp-sales/`, `/jobs/remote/`, etc. | Filter pages by role/location |
| `generate_salary_pages.py` | `/salaries/` | Salary data pages |
| `generate_company_pages.py` | `/companies/` | Company profile pages |
| `generate_tools_pages.py` | `/tools/` | GTM tools hub and pages |
| `generate_insights_page.py` | `/insights/` | Market intelligence page |
| `generate_newsletter_archive.py` | `/newsletter/` | Newsletter archive |
| `generate_homepage.py` | `/index.html` | Homepage |

## Stale Job Handling

When jobs expire (no longer in current data CSV), `generate_job_pages.py`:
1. Detects stale pages (exist on disk but not in current data)
2. Replaces "Apply Now" with "Position Filled" badge (orange #d97706)
3. Shows 5 similar live job recommendations
4. Adds `noindex` meta tag to remove from Google
5. Keeps page accessible for users who land on it from old links

## Tool Review Priority

**AI SDR Comparisons:**
1. 11x vs Artisan ✅ (done)
2. Artisan vs AiSDR
3. 11x vs AiSDR
4. Best AI SDR Tools 2026

**Data Enrichment Comparisons:**
1. Clay vs Apollo ✅ (done)

**Individual Reviews (after comparisons):**
- 11x, Artisan, AiSDR, Clay, Apollo, Regie.ai, Lavender, Gong, Clari, Unify, Warmly

## File Structure

```
site/
├── tools/
│   ├── index.html           # Tools hub
│   ├── ai-sdr/
│   │   ├── 11x-vs-artisan/
│   │   ├── artisan-vs-aisdr/
│   │   └── ...
│   └── data-enrichment/
│       ├── clay-vs-apollo/
│       └── ...
```

## Newsletter Writing

When creating newsletter markdown files in `/newsletters/`:

**Image Paths:** Always use `../` prefix for image references since images live in the project root, not the newsletters folder:
- `![90-Day Trend Chart](../trend_90_days.png)`
- `![5-Year Trend Chart](../trend_all_time.png)`
- `![Compensation by Seniority](../comp_by_seniority.png)`
- `![Compensation by Stage](../comp_by_stage.png)`
- `![Compensation by Location](../comp_by_location.png)`
- `![Buzzwords & Trends](../insights_buzzwords.png)`
- `![Industry Focus](../insights_industries.png)`
- `![Sales Methodologies Required](../insights_methodologies.png)`
- `![Tools & Platforms in Demand](../insights_tools.png)`

**Required Emoji Section Headers:**
- `## 📊 The Sales Executive Market`
- `## 🚀 Who's Moving`
- `## 💼 This Week's Board Update`
- `## 🎯 Company Deep-Dive` (or `## 🎯 Three Roles Worth Watching`)
- `## 🚫 Skip These Roles This Week`
- `## 💰 Compensation Benchmarking`
- `## 📋 What Employers Want`
- `## 📊 Market Intelligence`

**Front Matter:** Include YAML front matter with title, date, excerpt, substack_url, and moves array.

## Style Reminders

- Use contractions (it's, don't, won't)
- Vary sentence length dramatically
- No AI tells (robust, leverage, navigate, cutting-edge)
- Source every claim with links
- Be honest about red flags even for tools with affiliate potential

## Performance Optimization

See `claude/PERFORMANCE-GUIDE.md` for comprehensive PageSpeed optimization guide.

**Key optimizations implemented (Jan 2026):**

| Optimization | Impact | File(s) Changed |
|-------------|--------|-----------------|
| Logo compression (1.4MB → 14KB) | LCP: 10.1s → 2.3s | `site/assets/logo.jpg` |
| Async Google Fonts | FCP: 2.9s → 1.5s | All generators |
| Chart DPI reduction (300 → 150) | -55% file size | `generate_graphs.py` |
| Image dimensions (width/height) | Prevents CLS | All generators |
| Lazy iframe loading | Reduces initial load | `generate_homepage.py` |

**Current Performance (Jan 2026):** 77-80 on PageSpeed Insights (mobile)

**Analytics placement:** Keep GA4 + Clarity in `<head>` per Google's recommendation. Moving to `</body>` improves PageSpeed but hurts tracking accuracy.
