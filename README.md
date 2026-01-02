# The CRO Report - Website & Automation

[![Build and Deploy](https://github.com/romelikethecity/croreport/actions/workflows/build-site.yml/badge.svg)](https://github.com/romelikethecity/croreport/actions/workflows/build-site.yml)

Weekly intelligence for VP Sales and CRO leaders. This repo powers:
- **Homepage** with Market Pulse and Who's Moving teasers
- **Free Job Board** with 150+ executive sales roles
- **Salary Benchmark Pages** for programmatic SEO
- **Automated generation** via GitHub Actions

Live site: https://romelikethecity.github.io/croreport/

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      YOUR WEEKLY FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Run scraper locally (~2 hours)                          │
│     python scraper/scrape_jobs_maximum_coverage.py          │
│                                                              │
│  2. Copy raw_jobs_YYYYMMDD.csv to data/                     │
│                                                              │
│  3. git push → GitHub Actions runs automatically:           │
│     • Enrichment & filtering                                │
│     • Job board generation                                  │
│     • Salary pages (SEO)                                    │
│     • Trend graphs                                          │
│     • Homepage with Market Pulse                            │
│                                                              │
│  4. Site deploys to GitHub Pages (~5 minutes)               │
│                                                              │
│  5. Write newsletter in Claude (using generated stats)      │
│                                                              │
│  6. After publishing: add Who's Moving to data/moves.json   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
croreport/
├── .github/
│   └── workflows/
│       └── build-site.yml      # GitHub Actions workflow
├── data/
│   ├── raw_jobs_YYYYMMDD.csv   # Raw scraped data (you add this)
│   ├── executive_sales_jobs_*.csv  # Enriched data (generated)
│   ├── Sales_Exec_Openings.csv # Historical tracking
│   ├── market_stats.json       # Stats for homepage (generated)
│   └── moves.json              # Executive moves (you update)
├── scripts/
│   ├── enrich_and_analyze.py   # Filter & enrich jobs
│   ├── generate_graphs.py      # Trend visualizations
│   ├── generate_job_board.py   # Free job board page
│   ├── generate_salary_pages.py # SEO salary pages
│   └── generate_homepage.py    # Main homepage
├── scraper/
│   └── scrape_jobs_maximum_coverage.py  # Run locally only
├── site/                       # Generated site (don't edit)
│   ├── index.html
│   ├── jobs/
│   ├── salaries/
│   └── assets/
└── README.md
```

## 🚀 Initial Setup

### 1. Create the GitHub Repository

```bash
# Create new repo at github.com/romelikethecity/croreport
# Then clone and add files:

git clone https://github.com/romelikethecity/croreport.git
cd croreport

# Copy all files from this template
# (or download and extract the zip)
```

### 2. Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **GitHub Actions**
3. Save

### 3. Add Your Historical Data

Copy your existing files to `data/`:
- `Sales_Exec_Openings.csv` (historical tracking)
- Latest `executive_sales_jobs_*.csv` (current jobs)

### 4. First Deploy

```bash
git add .
git commit -m "Initial setup"
git push
```

GitHub Actions will build and deploy. Check the Actions tab for progress.

## 📅 Weekly Workflow

### Step 1: Run Scraper (Local, ~2 hours)

```bash
# From the scraper directory on your local machine
cd scraper
python scrape_jobs_maximum_coverage.py

# This creates: raw_jobs_YYYYMMDD_HHMM.csv
```

### Step 2: Push to GitHub

```bash
# Copy the raw file to data/
cp raw_jobs_*.csv ../data/

# Push
cd ..
git add data/raw_jobs_*.csv
git commit -m "Week of [date] - raw job data"
git push
```

### Step 3: Wait for Build (~5 minutes)

GitHub Actions automatically:
1. Runs enrichment (filters to VP+ sales roles, preserves descriptions)
2. Merges new jobs into master_jobs_database.csv
3. Generates all site pages (jobs, salaries, insights, tools)
4. Updates trend graphs
5. Deploys to GitHub Pages

### Step 4: Write Newsletter

Use the generated stats in `data/market_stats.json` and `data/market_intelligence.json` for your newsletter.

### Step 5: Update Who's Moving (After Publishing)

Edit `data/moves.json` to add the executive move you covered:

```json
{
  "moves": [
    {
      "name": "New Person",
      "new_role": "Chief Revenue Officer",
      "new_company": "Company Name",
      "previous": "Previous role at Previous Company",
      "date": "2025-01-02"
    },
    // ... existing moves (keep latest 4-5)
  ]
}
```

Then push:

```bash
git add data/moves.json
git commit -m "Add [Name] move"
git push
```

## 📊 Master Database

The `master_jobs_database.csv` accumulates all historical job data including full descriptions. This enables:

- **Trend analysis**: "AI mentions up 15% vs last quarter"
- **Historical lookback**: What was [Company] hiring for 6 months ago?
- **Methodology tracking**: MEDDIC requirements over time
- **Content**: Quarterly "State of Sales Hiring" reports

The database grows ~50MB/year (manageable) and preserves all job description text for analysis.

## 🔧 Manual Trigger

You can manually trigger a rebuild without new data:

1. Go to **Actions** tab
2. Select "Build and Deploy CRO Report Site"
3. Click **Run workflow**

## 📊 Generated Pages

After each build, **820+ pages** are created:

| Section | Pages | SEO Target |
|---------|-------|------------|
| Homepage | 1 | Brand |
| Job Board | 1 | "executive sales jobs" |
| **Individual Job Pages** | 785+ | "[Company] VP Sales job" |
| Salary Pages | 14 | "VP Sales salary NYC" |
| Tools Pages | 20 | "Outreach alternatives" |

### Key URLs:

- `/` — Homepage with Market Pulse
- `/jobs/` — Filterable job board
- `/jobs/[company]-[role]-[hash]/` — Individual job pages
- `/salaries/` — Salary benchmarks index
- `/salaries/new-york/` — NYC salary data
- `/salaries/san-francisco/` — SF salary data
- `/tools/` — GTM tools index
- `/tools/outreach-alternatives/` — Alternatives pages
- `/tools/outreach-vs-salesloft/` — Comparison pages

## 🔗 Connecting Your Domain

To use a custom domain (e.g., `croreport.com`):

1. Go to **Settings** → **Pages**
2. Under "Custom domain", enter your domain
3. Add DNS records at your registrar:
   - **A records** pointing to GitHub's IPs:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```
   - Or **CNAME** record: `romelikethecity.github.io`
4. Wait for DNS propagation (~24 hours)
5. Enable "Enforce HTTPS"

## 📈 SEO Notes

The salary pages are designed for programmatic SEO:
- Target keywords: "VP Sales salary NYC", "CRO compensation San Francisco", etc.
- Each page has unique title, meta description, and canonical URL
- Schema markup can be added for richer search results

## 🛠️ Troubleshooting

### Build Failed
- Check the Actions tab for error logs
- Most common: CSV parsing errors (check for special characters)

### Data Not Updating
- Ensure raw_jobs file is in `data/` directory
- Check that file naming matches pattern: `raw_jobs_*.csv`

### Scraper Blocked
- Indeed blocks datacenter IPs; scraper must run locally
- Try increasing wait time in scraper (currently 120 seconds)

## 📝 License

Private repository - The CRO Report © 2025
