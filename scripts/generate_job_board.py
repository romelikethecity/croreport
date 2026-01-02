#!/usr/bin/env python3
"""
Generate the free job board for GitHub Pages
This is the lead magnet - job listings are free, analysis is paid
"""

import pandas as pd
from datetime import datetime
import glob
import os
import csv
from io import StringIO

DATA_DIR = 'data'
SITE_DIR = 'site'

print("="*70)
print("🌐 GENERATING JOB BOARD")
print("="*70)

os.makedirs(f'{SITE_DIR}/jobs', exist_ok=True)

# Find most recent enriched data
files = glob.glob(f"{DATA_DIR}/executive_sales_jobs_*.csv")
if not files:
    print("❌ No enriched data found")
    exit(1)

latest_file = max(files)
print(f"📂 Loading: {latest_file}")

df = pd.read_csv(latest_file)
print(f"📊 Loaded {len(df)} jobs")

# Convert to CSV string for embedding
output = StringIO()
df.to_csv(output, index=False, quoting=csv.QUOTE_ALL)
csv_data = output.getvalue()
csv_data_escaped = csv_data.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

update_date = datetime.now().strftime('%B %d, %Y')

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Sales Jobs | VP Sales, CRO Roles | The CRO Report</title>
    <meta name="description" content="Browse {len(df)}+ VP Sales, CRO, and executive sales leadership positions. Salary data included. Updated weekly.">
    <link rel="canonical" href="https://romelikethecity.github.io/croreport/jobs/">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2rem; margin-bottom: 8px; }}
        .header p {{ opacity: 0.9; font-size: 1.1rem; }}
        .update-badge {{
            display: inline-block;
            background: #d97706;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 12px;
            font-weight: 600;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        
        .filters {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            margin: -30px auto 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: relative;
            z-index: 10;
        }}
        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .filter-group label {{
            display: block;
            font-weight: 600;
            margin-bottom: 6px;
            font-size: 0.85rem;
            color: #475569;
        }}
        .filter-group input, .filter-group select {{
            width: 100%;
            padding: 10px 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
        }}
        .filter-group input:focus, .filter-group select:focus {{
            outline: none;
            border-color: #1e3a5f;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            margin-bottom: 16px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .stats-left {{ font-size: 1rem; color: #475569; }}
        .stats-left strong {{ color: #d97706; font-size: 1.2rem; }}
        
        .clear-btn {{
            background: #1e3a5f;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }}
        .clear-btn:hover {{ background: #2d4a6f; }}
        
        .jobs-grid {{
            display: grid;
            gap: 16px;
        }}
        
        .job-card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
            cursor: pointer;
        }}
        .job-card:hover {{
            border-color: #1e3a5f;
            box-shadow: 0 4px 16px rgba(30,58,95,0.12);
            transform: translateY(-2px);
        }}
        
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 12px;
        }}
        .job-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 4px;
        }}
        .job-company {{
            color: #1e3a5f;
            font-weight: 500;
        }}
        .job-salary {{
            background: #f0fdf4;
            color: #166534;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 600;
            white-space: nowrap;
        }}
        
        .job-meta {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 12px;
            font-size: 0.9rem;
            color: #64748b;
        }}
        .job-meta span {{ display: flex; align-items: center; gap: 4px; }}
        
        .job-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tag {{
            background: #f1f5f9;
            color: #475569;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .tag.remote {{ background: #dbeafe; color: #1d4ed8; }}
        .tag.seniority {{ background: #fef3c7; color: #92400e; }}
        
        .apply-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 16px;
            transition: background 0.2s;
        }}
        .apply-btn:hover {{ background: #b45309; }}
        
        .cta-banner {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6f 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
            margin: 40px 0;
        }}
        .cta-banner h2 {{ margin-bottom: 12px; }}
        .cta-banner p {{ opacity: 0.9; margin-bottom: 20px; max-width: 500px; margin-left: auto; margin-right: auto; }}
        .cta-btn {{
            display: inline-block;
            background: #d97706;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
        }}
        .cta-btn:hover {{ background: #b45309; }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }}
        .no-results h2 {{ color: #0f172a; margin-bottom: 8px; }}
        
        .footer {{
            background: #1e3a5f;
            color: #94a3b8;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }}
        .footer a {{ color: #d97706; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>Executive Sales Jobs</h1>
        <p>VP Sales, CRO, and sales leadership positions</p>
        <span class="update-badge">Updated {update_date}</span>
    </header>
    
    <div class="container">
        <div class="filters">
            <div class="filter-grid">
                <div class="filter-group">
                    <label>Search</label>
                    <input type="text" id="searchInput" placeholder="Title or company...">
                </div>
                <div class="filter-group">
                    <label>Seniority</label>
                    <select id="seniorityFilter">
                        <option value="">All Levels</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Location</label>
                    <select id="metroFilter">
                        <option value="">All Locations</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Min Salary</label>
                    <input type="number" id="minSalary" placeholder="e.g. 200000">
                </div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stats-left">
                Showing <strong id="jobCount">{len(df)}</strong> roles
            </div>
            <button class="clear-btn" onclick="clearFilters()">Clear Filters</button>
        </div>
        
        <div class="jobs-grid" id="jobsList"></div>
        
        <div class="cta-banner">
            <h2>Want the full intelligence?</h2>
            <p>Get red flags, predecessor intel, company deep-dives, and "skip these roles" analysis every week.</p>
            <a href="https://croreport.substack.com/subscribe" class="cta-btn">Subscribe to The CRO Report →</a>
        </div>
    </div>
    
    <footer class="footer">
        <p>© 2025 <a href="/">The CRO Report</a> · <a href="https://croreport.substack.com">Newsletter</a></p>
    </footer>
    
    <script>
        const csvData = `{csv_data_escaped}`;
        let allJobs = [];
        let filteredJobs = [];
        
        function parseCSV(csv) {{
            const lines = csv.trim().split('\\n');
            const headers = parseCSVLine(lines[0]);
            return lines.slice(1).map(line => {{
                const values = parseCSVLine(line);
                const obj = {{}};
                headers.forEach((h, i) => obj[h] = values[i] || '');
                return obj;
            }});
        }}
        
        function parseCSVLine(line) {{
            const result = [];
            let current = '';
            let inQuotes = false;
            for (let i = 0; i < line.length; i++) {{
                const char = line[i];
                if (char === '"') {{
                    if (inQuotes && line[i+1] === '"') {{
                        current += '"';
                        i++;
                    }} else {{
                        inQuotes = !inQuotes;
                    }}
                }} else if (char === ',' && !inQuotes) {{
                    result.push(current);
                    current = '';
                }} else {{
                    current += char;
                }}
            }}
            result.push(current);
            return result;
        }}
        
        function init() {{
            allJobs = parseCSV(csvData);
            filteredJobs = [...allJobs];
            populateFilters();
            attachListeners();
            renderJobs();
        }}
        
        function populateFilters() {{
            const seniorities = new Set();
            const metros = new Set();
            allJobs.forEach(job => {{
                if (job.seniority) seniorities.add(job.seniority);
                if (job.metro) metros.add(job.metro);
            }});
            
            const senioritySelect = document.getElementById('seniorityFilter');
            Array.from(seniorities).sort().forEach(s => {{
                senioritySelect.innerHTML += `<option value="${{s}}">${{s}}</option>`;
            }});
            
            const metroSelect = document.getElementById('metroFilter');
            Array.from(metros).sort().forEach(m => {{
                metroSelect.innerHTML += `<option value="${{m}}">${{m}}</option>`;
            }});
        }}
        
        function applyFilters() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const seniority = document.getElementById('seniorityFilter').value;
            const metro = document.getElementById('metroFilter').value;
            const minSalary = parseFloat(document.getElementById('minSalary').value) || 0;
            
            filteredJobs = allJobs.filter(job => {{
                if (search && !`${{job.title}} ${{job.company}}`.toLowerCase().includes(search)) return false;
                if (seniority && job.seniority !== seniority) return false;
                if (metro && job.metro !== metro) return false;
                if (minSalary && (parseFloat(job.max_amount) || 0) < minSalary) return false;
                return true;
            }});
            
            renderJobs();
        }}
        
        function renderJobs() {{
            const container = document.getElementById('jobsList');
            document.getElementById('jobCount').textContent = filteredJobs.length;
            
            if (filteredJobs.length === 0) {{
                container.innerHTML = '<div class="no-results"><h2>No jobs found</h2><p>Try adjusting your filters</p></div>';
                return;
            }}
            
            container.innerHTML = filteredJobs.map(job => {{
                if (!job.title) return '';
                const url = job.job_url_direct || '#';
                const salary = formatSalary(job.min_amount, job.max_amount);
                const isRemote = job.is_remote === 'True';
                
                return `
                    <div class="job-card" onclick="window.open('${{url}}', '_blank')">
                        <div class="job-header">
                            <div>
                                <div class="job-title">${{escapeHtml(job.title)}}</div>
                                <div class="job-company">${{escapeHtml(job.company)}}</div>
                            </div>
                            ${{salary ? `<div class="job-salary">${{salary}}</div>` : ''}}
                        </div>
                        <div class="job-meta">
                            ${{job.location ? `<span>📍 ${{escapeHtml(job.location)}}</span>` : ''}}
                            ${{job.date_posted ? `<span>📅 ${{formatDate(job.date_posted)}}</span>` : ''}}
                        </div>
                        <div class="job-tags">
                            ${{isRemote ? '<span class="tag remote">🏠 Remote</span>' : ''}}
                            ${{job.seniority ? `<span class="tag seniority">${{job.seniority}}</span>` : ''}}
                        </div>
                        <a href="${{url}}" class="apply-btn" target="_blank" onclick="event.stopPropagation()">Apply →</a>
                    </div>
                `;
            }}).join('');
        }}
        
        function escapeHtml(text) {{
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        function formatSalary(min, max) {{
            if (!min && !max) return '';
            const fmt = n => n >= 1000 ? '$' + (n/1000).toFixed(0) + 'K' : '$' + n;
            if (min && max) return fmt(parseFloat(min)) + ' - ' + fmt(parseFloat(max));
            if (min) return fmt(parseFloat(min)) + '+';
            return 'Up to ' + fmt(parseFloat(max));
        }}
        
        function formatDate(d) {{
            const date = new Date(d);
            const days = Math.ceil((new Date() - date) / (1000*60*60*24));
            if (days <= 1) return 'Today';
            if (days <= 7) return days + ' days ago';
            return date.toLocaleDateString();
        }}
        
        function clearFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('seniorityFilter').value = '';
            document.getElementById('metroFilter').value = '';
            document.getElementById('minSalary').value = '';
            applyFilters();
        }}
        
        function attachListeners() {{
            document.getElementById('searchInput').addEventListener('input', applyFilters);
            document.getElementById('seniorityFilter').addEventListener('change', applyFilters);
            document.getElementById('metroFilter').addEventListener('change', applyFilters);
            document.getElementById('minSalary').addEventListener('input', applyFilters);
        }}
        
        init();
    </script>
</body>
</html>'''

# Save job board
output_path = f'{SITE_DIR}/jobs/index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Saved job board: {output_path}")
print(f"📊 {len(df)} jobs embedded")
