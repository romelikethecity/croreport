import pandas as pd
from datetime import datetime
import glob
import json
import csv
import sys
sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

# ============================================================
# LOAD ENRICHED DATA
# ============================================================

print("="*70)
print("🌐 GENERATING INDEX.HTML FOR NETLIFY DEPLOYMENT")
print("="*70)

# Find most recent enriched data file
files = glob.glob("data/executive_sales_jobs_*.csv")
if not files:
    print("\n❌ ERROR: No enriched data files found.")
    print("👉 Please run enrich_and_analyze.py first.")
    exit(1)

latest_file = max(files)
print(f"\n📂 Loading: {latest_file}")

# Load enriched data using pandas (handles CSV properly)
df = pd.read_csv(latest_file)
print(f"📊 Loaded {len(df)} jobs")

# Calculate and save market stats
total_roles = len(df)
remote_count = df['is_remote'].sum() if 'is_remote' in df.columns else 0
remote_pct = round(100 * remote_count / total_roles, 1) if total_roles > 0 else 0

salary_df = df[df['max_amount'].notna() & (df['max_amount'] > 0)]
avg_max_salary = int(salary_df['max_amount'].mean()) if len(salary_df) > 0 else 0
avg_min_salary = int(salary_df['min_amount'].mean()) if len(salary_df) > 0 else 0
salary_disclosure_rate = round(100 * len(salary_df) / total_roles, 1) if total_roles > 0 else 0

unique_companies = df['company'].nunique()
seniority_counts = df['seniority'].value_counts().to_dict()

peak_roles = 162
vs_peak_pct = round(100 * (total_roles - peak_roles) / peak_roles)

market_stats = {
    "total_roles": total_roles,
    "unique_companies": unique_companies,
    "salary_disclosure_rate": salary_disclosure_rate,
    "by_seniority": {k: int(v) for k, v in seniority_counts.items()},
    "remote_pct": remote_pct,
    "avg_min_salary": avg_min_salary,
    "avg_max_salary": avg_max_salary,
    "date": datetime.now().strftime('%Y-%m-%d'),
    "wow_change": 0,
    "wow_change_pct": 0,
    "vs_peak_pct": vs_peak_pct,
    "peak_roles": peak_roles,
    "top_locations": [],
    "top_companies": []
}

with open('data/market_stats.json', 'w') as f:
    json.dump(market_stats, f, indent=2)
print(f"📈 Saved market stats: {total_roles} roles, {remote_pct}% remote, ${avg_max_salary:,} avg max")

# Convert DataFrame to JSON for reliable JavaScript parsing
# Only include columns needed for display (excludes problematic company_addresses with newlines)
display_cols = ['job_url_direct', 'title', 'company', 'location', 'date_posted', 
                'min_amount', 'max_amount', 'is_remote', 'seniority', 'is_tech', 'company_industry']
df_display = df[[c for c in display_cols if c in df.columns]].copy()

# Convert to JSON and clean NaN values
jobs_list = df_display.to_dict('records')
for job in jobs_list:
    for key in list(job.keys()):
        if pd.isna(job[key]):
            job[key] = ''

json_data = json.dumps(jobs_list)
# Escape for JavaScript template literal
csv_data_escaped = json_data.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

# Get update date
update_date = datetime.now().strftime('%B %d, %Y')

# Load and embed the CRO Report logo
import os
import base64

# Try to load logo from same directory as script
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = 'site/assets/logo.jpg'

if os.path.exists(logo_path):
    with open(logo_path, 'rb') as f:
        logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"✅ Loaded logo: {logo_path}")
else:
    # Fallback: simple SVG placeholder
    logo_base64 = ""
    print("⚠️  Warning: cro_minimal_zoomed.jpg not found in script directory")
    print(f"   Looking for: {logo_path}")

# ============================================================
# GENERATE HTML
# ============================================================

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Roles for Sales Executives | The CRO Report</title>
    <meta name="description" content="Curated VP+ sales executive jobs - CRO, SVP Sales, VP Sales positions updated weekly">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 0;
            box-shadow: none;
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .logo {{
            width: 150px;
            height: 150px;
            margin: 0 auto 20px;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}

        .update-badge {{
            display: inline-block;
            background: #f5a623;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
            font-weight: 600;
        }}

        .filters {{
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}

        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
        }}

        .filter-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #495057;
            font-size: 0.9em;
        }}

        .filter-group input,
        .filter-group select {{
            padding: 10px 12px;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.2s;
        }}

        .filter-group input:focus,
        .filter-group select:focus {{
            outline: none;
            border-color: #f5a623;
        }}

        .checkbox-filter {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
        }}

        .checkbox-filter input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
        }}

        .checkbox-filter label {{
            margin: 0;
            cursor: pointer;
            font-weight: 500;
        }}

        .stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 40px;
            background: white;
            border-bottom: 1px solid #e9ecef;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .stats-left {{
            font-size: 1.1em;
            color: #495057;
        }}

        .stats-left strong {{
            color: #f5a623;
            font-size: 1.3em;
        }}

        .clear-filters {{
            background: #f5a623;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }}

        .clear-filters:hover {{
            background: #e09517;
        }}

        .jobs-list {{
            padding: 20px 40px 40px;
        }}

        .job-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.2s;
            cursor: pointer;
        }}

        .job-card:hover {{
            border-color: #f5a623;
            box-shadow: 0 4px 12px rgba(245, 166, 35, 0.15);
            transform: translateY(-2px);
        }}

        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .job-title {{
            font-size: 1.4em;
            font-weight: 700;
            color: #212529;
            margin-bottom: 4px;
        }}

        .job-company {{
            font-size: 1.1em;
            color: #f5a623;
            font-weight: 600;
        }}

        .job-salary {{
            background: #1e3a5f;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            white-space: nowrap;
        }}

        .job-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 12px;
            color: #6c757d;
        }}

        .job-detail {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .job-detail svg {{
            width: 16px;
            height: 16px;
            fill: currentColor;
        }}

        .job-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}

        .job-tag {{
            background: #f8f9fa;
            color: #495057;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 500;
        }}

        .job-tag.remote {{
            background: #d4edda;
            color: #155724;
        }}

        .job-tag.seniority {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .apply-btn {{
            display: inline-block;
            background: #f5a623;
            color: white;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 12px;
            transition: background 0.2s;
        }}

        .apply-btn:hover {{
            background: #e09517;
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }}

        .no-results h2 {{
            font-size: 2em;
            margin-bottom: 12px;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            color: #6c757d;
            border-top: 2px solid #e9ecef;
        }}

        .footer a {{
            color: #f5a623;
            text-decoration: none;
            font-weight: 600;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .filter-grid {{
                grid-template-columns: 1fr;
            }}

            .stats {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .job-title {{
                font-size: 1.2em;
            }}
        }}

        /* Site Navigation */
        .site-nav {{
            background: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        .nav-logo {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            color: #1e3a5f;
            text-decoration: none;
            font-size: 1.1rem;
        }}
        .nav-logo img {{
            height: 36px;
        }}
        .nav-links {{
            display: flex;
            gap: 28px;
            align-items: center;
        }}
        .nav-links a {{
            color: #64748b;
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 500;
        }}
        .nav-links a:hover {{
            color: #1e3a5f;
        }}
        .nav-links .subscribe-btn {{
            background: #1e3a5f;
            color: white !important;
            padding: 10px 20px;
            border-radius: 6px;
        }}
        .nav-links .subscribe-btn:hover {{
            background: #2c5282;
        }}
    </style>
</head>
<body>
    <nav class="site-nav">
        <a href="/" class="nav-logo">
            <img src="/assets/logo.jpg" alt="The CRO Report">
            The CRO Report
        </a>
        <div class="nav-links">
            <a href="/jobs/">Jobs</a>
            <a href="/salaries/">Salaries</a>
            <a href="/insights/">Market Intel</a>
            <a href="https://croreport.substack.com/subscribe" class="subscribe-btn">Subscribe</a>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <img src="data:image/jpeg;base64,{logo_base64}" alt="The CRO Report Logo" class="logo" style="width: 200px; height: auto; background: white; padding: 20px; border-radius: 12px;">
            <h1>The CRO Report</h1>
            <p>Executive Sales Opportunities</p>
            <span class="update-badge">Updated {update_date}</span>
        </div>

        <div class="filters">
            <div class="filter-grid">
                <div class="filter-group">
                    <label for="searchInput">Search</label>
                    <input type="text" id="searchInput" placeholder="Job title or company...">
                </div>

                <div class="filter-group">
                    <label for="seniorityFilter">Seniority Level</label>
                    <select id="seniorityFilter">
                        <option value="">All Levels</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label for="locationFilter">Location</label>
                    <select id="locationFilter">
                        <option value="">All Locations</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label for="minSalary">Min Salary</label>
                    <input type="number" id="minSalary" placeholder="e.g., 150000">
                </div>

                <div class="filter-group">
                    <label for="maxSalary">Max Salary</label>
                    <input type="number" id="maxSalary" placeholder="e.g., 300000">
                </div>
            </div>

            <div class="checkbox-filter">
                <input type="checkbox" id="remoteOnly">
                <label for="remoteOnly">Remote positions only</label>
            </div>
        </div>

        <div class="stats">
            <div class="stats-left">
                Showing <strong id="jobCount">0</strong> executive sales roles
            </div>
            <button class="clear-filters" onclick="clearFilters()">Clear Filters</button>
        </div>

        <div class="jobs-list" id="jobsList">
            <!-- Jobs will be rendered here -->
        </div>

        <div class="footer">
            <p>Jobs updated weekly | <a href="mailto:contact@croreport.com">Contact</a></p>
            <p style="margin-top: 10px; font-size: 0.9em;">Curated opportunities for executive sales leaders</p>
        </div>
    </div>

    <script>
        // Embedded job data
        const jobsData = `{csv_data_escaped}`;

        let allJobs = [];
        let filteredJobs = [];

        // Initialize
        function init() {{
            allJobs = JSON.parse(jobsData);
            filteredJobs = [...allJobs];
            
            populateFilters();
            renderJobs();
            attachEventListeners();
        }}

        // Populate filter dropdowns
        function populateFilters() {{
            const locations = new Set();
            const seniorities = new Set();

            allJobs.forEach(job => {{
                if (job.location) locations.add(job.location);
                if (job.seniority) seniorities.add(job.seniority);
            }});

            populateSelect('locationFilter', Array.from(locations).sort());
            populateSelect('seniorityFilter', Array.from(seniorities).sort());
        }}

        function populateSelect(id, options) {{
            const select = document.getElementById(id);
            options.forEach(option => {{
                const opt = document.createElement('option');
                opt.value = option;
                opt.textContent = option;
                select.appendChild(opt);
            }});
        }}

        // Apply filters
        function applyFilters() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const seniority = document.getElementById('seniorityFilter').value;
            const location = document.getElementById('locationFilter').value;
            const minSalary = document.getElementById('minSalary').value;
            const maxSalary = document.getElementById('maxSalary').value;
            const remoteOnly = document.getElementById('remoteOnly').checked;

            filteredJobs = allJobs.filter(job => {{
                // Search filter
                if (searchTerm) {{
                    const searchableText = `${{job.title}} ${{job.company}}`.toLowerCase();
                    if (!searchableText.includes(searchTerm)) return false;
                }}

                // Seniority filter
                if (seniority && job.seniority !== seniority) return false;

                // Location filter
                if (location && job.location !== location) return false;

                // Salary filters
                const jobMinSalary = parseFloat(job.min_amount) || 0;
                const jobMaxSalary = parseFloat(job.max_amount) || Infinity;
                
                if (minSalary && jobMaxSalary < parseFloat(minSalary)) return false;
                if (maxSalary && jobMinSalary > parseFloat(maxSalary)) return false;

                // Remote filter
                if (remoteOnly && job.is_remote !== 'True') return false;

                return true;
            }});

            renderJobs();
        }}

        // Render jobs
        function renderJobs() {{
            const jobsList = document.getElementById('jobsList');
            const jobCount = document.getElementById('jobCount');
            
            jobCount.textContent = filteredJobs.length;

            if (filteredJobs.length === 0) {{
                jobsList.innerHTML = `
                    <div class="no-results">
                        <h2>No jobs found</h2>
                        <p>Try adjusting your filters to see more results</p>
                    </div>
                `;
                return;
            }}

            jobsList.innerHTML = filteredJobs.map(job => {{
                // Skip jobs with no title or company
                if (!job.title || !job.company) return '';
                
                // Get job URL - try multiple fields with validation
                let jobUrl = job.job_url_direct || job.job_url || '';
                
                // Validate URL
                if (!jobUrl || jobUrl.length < 10 || !jobUrl.startsWith('http')) {{
                    console.warn('Invalid job URL for:', job.title, 'URL:', jobUrl);
                    jobUrl = '#';  // Fallback to prevent broken links
                }}
                
                const salary = formatSalary(job.min_amount, job.max_amount);
                const isRemote = job.is_remote === 'True';
                
                return `
                    <div class="job-card" onclick="if('${{jobUrl}}' !== '#') window.open('${{jobUrl}}', '_blank')">
                        <div class="job-header">
                            <div>
                                <div class="job-title">${{escapeHtml(job.title)}}</div>
                                <div class="job-company">${{escapeHtml(job.company)}}</div>
                            </div>
                            ${{salary ? `<div class="job-salary">${{salary}}</div>` : ''}}
                        </div>
                        
                        <div class="job-details">
                            ${{job.location ? `
                                <div class="job-detail">
                                    <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                                    ${{escapeHtml(job.location)}}
                                </div>
                            ` : ''}}
                            
                            ${{job.date_posted ? `
                                <div class="job-detail">
                                    <svg viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"/></svg>
                                    ${{formatDate(job.date_posted)}}
                                </div>
                            ` : ''}}
                        </div>
                        
                        <div class="job-tags">
                            ${{isRemote ? '<span class="job-tag remote">🏠 Remote</span>' : ''}}
                            ${{job.seniority ? `<span class="job-tag seniority">${{escapeHtml(job.seniority)}}</span>` : ''}}
                            ${{job.is_tech === 'True' ? '<span class="job-tag">💻 Tech Company</span>' : ''}}
                            ${{job.company_industry ? `<span class="job-tag">${{escapeHtml(job.company_industry)}}</span>` : ''}}
                        </div>
                        
                        ${{jobUrl !== '#' ? `
                            <a href="${{jobUrl}}" class="apply-btn" target="_blank" onclick="event.stopPropagation()">
                                Apply Now →
                            </a>
                        ` : `
                            <div class="apply-btn" style="opacity: 0.5; cursor: not-allowed;" title="Job URL not available">
                                URL Not Available
                            </div>
                        `}}
                    </div>
                `;
            }}).filter(html => html).join(''); // Filter out empty strings
        }}

        // Helper functions
        function escapeHtml(text) {{
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        function formatSalary(min, max) {{
            if (!min && !max) return '';
            
            const formatNum = (num) => {{
                if (!num) return '';
                const n = parseFloat(num);
                if (n >= 1000) {{
                    return '$' + (n / 1000).toFixed(0) + 'K';
                }}
                return '$' + n.toLocaleString();
            }};

            if (min && max) {{
                return `${{formatNum(min)}} - ${{formatNum(max)}}`;
            }} else if (min) {{
                return `${{formatNum(min)}}+`;
            }} else {{
                return `Up to ${{formatNum(max)}}`;
            }}
        }}

        function formatDate(dateStr) {{
            const date = new Date(dateStr);
            const today = new Date();
            const diffTime = Math.abs(today - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${{diffDays}} days ago`;
            if (diffDays < 30) return `${{Math.floor(diffDays / 7)}} weeks ago`;
            return date.toLocaleDateString();
        }}

        function clearFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('seniorityFilter').value = '';
            document.getElementById('locationFilter').value = '';
            document.getElementById('minSalary').value = '';
            document.getElementById('maxSalary').value = '';
            document.getElementById('remoteOnly').checked = false;
            applyFilters();
        }}

        // Event listeners
        function attachEventListeners() {{
            document.getElementById('searchInput').addEventListener('input', applyFilters);
            document.getElementById('seniorityFilter').addEventListener('change', applyFilters);
            document.getElementById('locationFilter').addEventListener('change', applyFilters);
            document.getElementById('minSalary').addEventListener('input', applyFilters);
            document.getElementById('maxSalary').addEventListener('input', applyFilters);
            document.getElementById('remoteOnly').addEventListener('change', applyFilters);
        }}

        // Start the app
        init();
    </script>
</body>
</html>'''

# ============================================================
# SAVE HTML FILE
# ============================================================

output_filename = "site/jobs/index.html"
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n" + "="*70)
print("✅ INDEX.HTML GENERATED!")
print("="*70)
print(f"📁 File: {output_filename}")
print(f"📊 Jobs embedded: {len(df)}")
print(f"📅 Update date: {update_date}")
print("\n🚀 READY FOR NETLIFY DEPLOYMENT")
print("="*70)
print("\nNext steps:")
print("1. Upload index.html to Netlify")
print("2. Or drag & drop the file to netlify.com/drop")
print("3. Your job board will be live!")
print("="*70)
