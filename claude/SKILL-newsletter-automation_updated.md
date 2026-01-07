---
name: newsletter-automation
description: Automated workflow for generating The CRO Report weekly newsletter. Use when Rome asks to write or draft the weekly newsletter. Pulls data directly from GitHub repo, analyzes jobs, researches executive movements, and generates complete newsletter draft.
---

# CRO Report Newsletter Automation

## Trigger Phrases

Use this workflow when you hear:
- "Write this week's newsletter"
- "Draft the CRO Report"
- "Generate the weekly edition"
- "Create the newsletter for [date]"

## Data Sources

All data lives in the GitHub repo. Fetch directly—no manual uploads needed.

### Primary Data Files

```bash
# Clone or fetch latest from repo
git clone https://github.com/romelikethecity/croreport.git /home/claude/croreport

# Or if already cloned, pull latest
cd /home/claude/croreport && git pull
```

**Key files to read:**

| File | Location | Purpose |
|------|----------|---------|
| Weekly jobs | `data/executive_sales_jobs_YYYYMMDD.csv` | Current week's enriched job data |
| Historical trend | `data/Sales_Exec_Openings.csv` | Week-over-week tracking |
| Master database | `data/master_jobs_database.csv` | All historical jobs for context |
| 90-day graph | `site/assets/trend_90_days.png` | For newsletter image |
| All-time graph | `site/assets/trend_all_time.png` | For newsletter image |
| Buzzwords chart | `site/assets/buzzwords_chart.png` | What Employers Want section (PAID) |
| Industry chart | `site/assets/industry_chart.png` | What Employers Want section (PAID) |
| Methodology chart | `site/assets/methodology_chart.png` | What Employers Want section (PAID) |
| Tools chart | `site/assets/tools_chart.png` | What Employers Want section (PAID) |

### Finding the Latest Data

```python
import glob
import os

# Get most recent enriched jobs file
data_dir = '/home/claude/croreport/data'
files = glob.glob(f'{data_dir}/executive_sales_jobs_*.csv')
latest_jobs = max(files, key=os.path.getctime)
```

## Workflow Steps

### Step 1: Fetch Data

```bash
cd /home/claude
git clone https://github.com/romelikethecity/croreport.git 2>/dev/null || (cd croreport && git pull)
```

### Step 2: Analyze Market Data

Read `Sales_Exec_Openings.csv` and calculate:
- Current week's openings
- Previous week's openings
- Week-over-week change (number and percentage)
- Comparison to 2022 peak (162 openings)
- 90-day trend direction

### Step 3: Analyze This Week's Jobs

Read the latest `executive_sales_jobs_*.csv` and identify:

**For spotlight candidates (pick 3-5):**
- Unusual compensation (top 5% or bottom 20%)
- Interesting company stories (acquisitions, IPOs, turnarounds)
- High-profile companies
- Companies with multiple postings (expansion signal)
- Red flag patterns worth discussing

**For "Skip These Roles":**
- Below-market compensation (40%+ under benchmark)
- Title inflation (VP at <$120K, CRO at <$200K)
- Contractor/consultant roles disguised as full-time
- Zero salary disclosure in California (compliance issue)
- Spam postings (10+ identical roles from one company)

**For compensation analysis:**
- Count of roles with disclosed salary
- Average/median by seniority (VP, SVP, C-Level)
- Geographic breakdown (SF, NYC, Remote, etc.)
- Top 5 highest-paying roles

### Step 4: Analyze Market Requirements (What Employers Want)

Read `master_jobs_database.csv` and analyze the `description` field for keyword frequencies. This powers the PAID "What Employers Want" section.

**Buzzwords & Trends** (search descriptions for):
- Scale/Scalable: `\b(scale|scalable|scaling)\b`
- Go-to-Market/GTM: `\b(go-to-market|gtm|go to market)\b`
- AI/Machine Learning: `\b(ai|artificial intelligence|machine learning|ml)\b`
- Data-Driven: `\b(data-driven|data driven)\b`
- SaaS: `\bsaas\b`
- Cloud: `\bcloud\b`
- Customer Success: `\bcustomer success\b`
- Recurring Revenue/ARR: `\b(arr|recurring revenue|mrr)\b`
- GenAI: `\b(genai|generative ai|gen ai)\b`

**Sales Methodologies** (search for):
- Consultative Selling: `\bconsultative\b`
- Enterprise Sales: `\benterprise sales\b`
- Channel/Partner: `\b(channel|partner sales|partnerships)\b`
- MEDDIC/MEDDPICC: `\bmedd[ip]*c+\b`
- PLG/Product-Led: `\b(plg|product-led|product led)\b`
- Challenger: `\bchallenger\b`
- Value Selling: `\bvalue selling\b`
- Account-Based/ABM: `\b(abm|account-based|account based)\b`

**Tools in Demand** (search for):
- Salesforce, Outreach, HubSpot, Tableau, ZoomInfo, Gong, LinkedIn Sales Nav, Clari

**Industry Focus**: Use the `company_industry` field from the database.

**Output**: Reference the pre-generated charts (buzzwords_chart.png, industry_chart.png, methodology_chart.png, tools_chart.png). Write 2-3 sentence analysis per chart focusing on positioning implications for job seekers.

**Free Teaser**: Pick ONE compelling stat for the Market Intelligence section with "Full breakdown for paid subscribers."

### Step 5: Research Executive Movements

Search the web for recent appointments:
```
"Chief Revenue Officer" appointed [current month] [year]
"CRO" hired [current month] [year]
"VP Sales" appointed [current month] [year]
```

Select the most interesting appointment based on:
- Company profile (funding, stage, industry)
- Executive pedigree (prior companies, track record)
- Strategic significance (why now? what's the bet?)

Research the selected executive:
- LinkedIn career history
- Previous company performance
- New company context and challenges
- Why this hire matters

### Step 6: Research Spotlight Company

Once Rome selects a company (or you recommend top candidates):

1. **Company fundamentals**: Funding, revenue, employee count, growth
2. **The role**: Comp, location, reporting structure, scope
3. **Predecessor intel**: Who had this role before? Why did they leave?
4. **Board composition**: Who controls the company? Any sales expertise on board?
5. **Red flags**: Glassdoor reviews, layoff history, leadership turnover
6. **Why compelling**: What makes this worth considering?

### Step 7: Generate Newsletter

Follow `SKILL-croreport_writing.md` for voice and structure.

**Section order:**
1. 📊 The Sales Executive Market (90-day + 5-year context)
2. What This Means (4 lines only—employed, seekers, hiring, signal)
3. 🚀 Who's Moving (2-line preview)
4. 🎯 Company Deep-Dive (3-line preview)
5. 💼 This Week's Board Update
6. 🚀 Complete Movement Analysis (full)
7. 🎯 Company Deep-Dive (full with all subsections)
8. 🚫 Skip These Roles This Week (3-5 roles)
9. 💰 Compensation Benchmarking
10. 📋 What Employers Want (PAID ONLY - 4 charts with analysis)
11. 📊 Market Intelligence (4-5 observations + one free teaser from What Employers Want)
12. Closing CTA

### Step 8: Output

Save newsletter to `/mnt/user-data/outputs/cro_report_YYYYMMDD.md`

Copy trend images:
```bash
cp /home/claude/croreport/site/assets/trend_90_days.png /mnt/user-data/outputs/
cp /home/claude/croreport/site/assets/trend_all_time.png /mnt/user-data/outputs/
```

Copy What Employers Want charts (for paid section):
```bash
cp /home/claude/croreport/site/assets/buzzwords_chart.png /mnt/user-data/outputs/
cp /home/claude/croreport/site/assets/industry_chart.png /mnt/user-data/outputs/
cp /home/claude/croreport/site/assets/methodology_chart.png /mnt/user-data/outputs/
cp /home/claude/croreport/site/assets/tools_chart.png /mnt/user-data/outputs/
```

**Note:** If any chart files are missing, skip that subsection in the What Employers Want section rather than fabricating data.

## Example Prompt to Claude Code

Rome just needs to say:

> "Write this week's CRO Report newsletter. I'm thinking [Company X] for the spotlight, but open to other suggestions."

Or even simpler:

> "Write this week's newsletter."

Claude Code will:
1. Pull latest data from GitHub
2. Analyze jobs and trends
3. Identify spotlight candidates (ask Rome to pick if not specified)
4. Analyze market requirements for What Employers Want section
5. Research executive movements
6. Research spotlight company
7. Generate full newsletter draft
8. Output markdown + images (including What Employers Want charts)

## Benchmarks for Analysis

**Compensation red flags:**
- VP Sales: <$150K base is concerning
- SVP Sales: <$200K base is concerning
- C-Level (CRO/CSO): <$250K base is concerning

**Title inflation indicators:**
- "VP" at <$120K = likely IC role
- "CRO" at <$150K = likely VP-level scope
- "CSO" at <$100K = definitely not C-suite

**Geographic adjustments:**
- SF/NYC: +15-25% vs national
- Remote: -10-15% vs NYC

**Company stage compensation norms:**
- Seed/Series A: Lower base, higher equity
- Series B/C: $175K-$250K VP base typical
- Public/Enterprise: $250K-$400K VP base typical

## Notes

- Always check the most recent CSV date—don't use stale data
- If GitHub clone fails, ask Rome to confirm repo access
- The newsletter images (trend graphs) are regenerated by GitHub Actions when new data is pushed
- Predecessor intel and board composition are REQUIRED sections—never skip them
