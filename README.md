# CRO Report GitHub Scripts Update

## What's Included

### scripts/ (copy to your GitHub repo)
- **enrich_and_analyze.py** - Processes raw_jobs CSVs into enriched executive sales data
- **generate_graphs.py** - Creates ALL 5 trend charts (30d, 90d, 6mo, 12mo, all-time) + social preview
- **cro_comp_aggregator.py** - Generates comp benchmark charts and newsletter markdown
- **merge_to_master.py** - Merges weekly data into master database

### .github/workflows/ (copy to your GitHub repo)
- **build-site.yml** - Updated workflow that runs all scripts in correct order

### scraper/ (keep locally, don't put in GitHub)
- **scrape_jobs_maximum_coverage.py** - Updated scraper with auto-push to GitHub

## Installation

1. **Replace GitHub scripts:**
   ```bash
   cd ~/Downloads/croreport-github
   # Backup existing scripts
   mv scripts scripts_backup
   # Extract new scripts
   unzip github_scripts_update.zip
   # Copy scripts to repo
   cp -r scripts/* scripts/
   cp -r .github/* .github/
   ```

2. **Update your local scraper:**
   ```bash
   cp scraper/scrape_jobs_maximum_coverage.py ~/Documents/Job-Scraper/
   ```

3. **Push to GitHub:**
   ```bash
   cd ~/Downloads/croreport-github
   git add .
   git commit -m "Update all scripts for proper image generation"
   git push
   ```

## What Gets Generated

After the workflow runs, your site/assets/ folder will have:
- `trend_all_time.png` - Complete history chart
- `trend_12_months.png` - Last 12 months
- `trend_6_months.png` - Last 6 months
- `trend_90_days.png` - Last 90 days
- `trend_30_days.png` - Last 30 days
- `social_preview.png` - Substack preview image
- `comp_by_seniority.png` - Compensation by VP/SVP/EVP/C-Level
- `comp_by_stage.png` - Compensation by company stage
- `comp_by_location.png` - Compensation by metro area

And your data/ folder will have:
- `comp_newsletter_section.md` - Ready-to-use markdown for newsletter
- `comp_analysis.json` - Full analysis data

## Weekly Workflow

1. Run scraper: `python3 scrape_jobs_maximum_coverage.py`
2. Wait for GitHub Actions to complete (~5 min)
3. Check site at https://thecroreport.com
4. Copy images and markdown for your Substack newsletter
