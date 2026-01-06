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
- **Logos**: Check `/site/assets/logos/` for existing tool logos
- **Workflow**: Generated pages must be included in git add for GitHub Actions to deploy

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

## Style Reminders

- Use contractions (it's, don't, won't)
- Vary sentence length dramatically
- No AI tells (robust, leverage, navigate, cutting-edge)
- Source every claim with links
- Be honest about red flags even for tools with affiliate potential
