#!/usr/bin/env python3
"""
Generate Company Intelligence Database

Extracts technographics, sales methodologies, and business signals from job postings
into a SQLite database ready for Datasette.

Usage:
    python scripts/generate_company_intel.py              # Generate database
    python scripts/generate_company_intel.py --discover   # Find new tools
"""

import pandas as pd
import sqlite3
import json
import re
import argparse
from collections import defaultdict
from datetime import datetime
import os

DATA_DIR = "data"
CONFIG_FILE = f"{DATA_DIR}/signal_config.json"
DB_FILE = f"{DATA_DIR}/company_intelligence.db"
MASTER_CSV = f"{DATA_DIR}/master_jobs_database.csv"
DISCOVERED_FILE = f"{DATA_DIR}/discovered_tools.json"


def load_config():
    """Load signal configuration from JSON file."""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_all_text(row):
    """Combine all text fields for analysis."""
    text = ""
    for col in ['description', 'title', 'company_description', 'skills']:
        if col in row.index and pd.notna(row[col]):
            text += " " + str(row[col])
    return text.lower()


def extract_tools(text, config):
    """Extract all matching tools from text."""
    matches = []
    for category, tools in config.get('technographics', {}).items():
        for tool_id, pattern in tools.items():
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append({
                        'tool_id': tool_id,
                        'tool_name': tool_id.replace('_', ' ').title(),
                        'category': category.replace('_', ' ')
                    })
            except re.error:
                continue
    return matches


def extract_signals(text, config):
    """Extract all matching signals from text."""
    matches = []
    for signal_type, signals in config.get('signals', {}).items():
        for signal_id, pattern in signals.items():
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append({
                        'signal_type': signal_type,
                        'signal_id': signal_id,
                        'signal_value': signal_id.replace('_', ' ').title()
                    })
            except re.error:
                continue
    return matches


def process_companies(df, config):
    """Aggregate data by company."""
    companies = {}
    company_tools = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'last_seen': None, 'category': None}))
    company_signals = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'last_seen': None, 'type': None}))

    for idx, row in df.iterrows():
        company_name = row.get('company')
        if pd.isna(company_name) or not company_name:
            continue

        company_name = str(company_name).strip()
        all_text = get_all_text(row)
        date_posted = row.get('date_posted') or row.get('import_date')

        # Initialize or update company record
        if company_name not in companies:
            companies[company_name] = {
                'name': company_name,
                'url': row.get('company_url_direct') or row.get('company_url'),
                'industry': row.get('company_industry'),
                'stage': row.get('company_stage'),
                'size': row.get('company_num_employees'),
                'revenue': row.get('company_revenue'),
                'total_job_postings': 0,
                'salary_min_sum': 0,
                'salary_max_sum': 0,
                'salary_count': 0,
                'last_seen': date_posted
            }

        companies[company_name]['total_job_postings'] += 1

        # Track salary data
        if pd.notna(row.get('min_amount')) and pd.notna(row.get('max_amount')):
            companies[company_name]['salary_min_sum'] += float(row['min_amount'])
            companies[company_name]['salary_max_sum'] += float(row['max_amount'])
            companies[company_name]['salary_count'] += 1

        # Update last_seen
        if date_posted and (not companies[company_name]['last_seen'] or date_posted > companies[company_name]['last_seen']):
            companies[company_name]['last_seen'] = date_posted

        # Extract and count tools
        tools = extract_tools(all_text, config)
        for tool in tools:
            key = tool['tool_id']
            company_tools[company_name][key]['count'] += 1
            company_tools[company_name][key]['category'] = tool['category']
            company_tools[company_name][key]['name'] = tool['tool_name']
            if date_posted:
                company_tools[company_name][key]['last_seen'] = date_posted

        # Extract and count signals
        signals = extract_signals(all_text, config)
        for signal in signals:
            key = f"{signal['signal_type']}:{signal['signal_id']}"
            company_signals[company_name][key]['count'] += 1
            company_signals[company_name][key]['type'] = signal['signal_type']
            company_signals[company_name][key]['value'] = signal['signal_value']
            if date_posted:
                company_signals[company_name][key]['last_seen'] = date_posted

    # Calculate averages
    for company_name, data in companies.items():
        if data['salary_count'] > 0:
            data['avg_salary_min'] = int(data['salary_min_sum'] / data['salary_count'])
            data['avg_salary_max'] = int(data['salary_max_sum'] / data['salary_count'])
        else:
            data['avg_salary_min'] = None
            data['avg_salary_max'] = None
        del data['salary_min_sum']
        del data['salary_max_sum']
        del data['salary_count']

    return companies, company_tools, company_signals


def write_database(companies, company_tools, company_signals):
    """Write data to SQLite database."""
    # Remove existing database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create companies table
    cursor.execute('''
        CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            url TEXT,
            industry TEXT,
            stage TEXT,
            size TEXT,
            revenue TEXT,
            total_job_postings INTEGER,
            avg_salary_min INTEGER,
            avg_salary_max INTEGER,
            last_seen TEXT
        )
    ''')

    # Create company_tools table
    cursor.execute('''
        CREATE TABLE company_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT,
            tool_id TEXT,
            tool_name TEXT,
            tool_category TEXT,
            mention_count INTEGER,
            last_seen TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')

    # Create company_signals table
    cursor.execute('''
        CREATE TABLE company_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT,
            signal_type TEXT,
            signal_value TEXT,
            mention_count INTEGER,
            last_seen TEXT,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')

    # Insert companies
    company_id_map = {}
    for company_name, data in companies.items():
        cursor.execute('''
            INSERT INTO companies (name, url, industry, stage, size, revenue,
                                   total_job_postings, avg_salary_min, avg_salary_max, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['url'],
            data['industry'],
            data['stage'],
            data['size'],
            data['revenue'],
            data['total_job_postings'],
            data['avg_salary_min'],
            data['avg_salary_max'],
            data['last_seen']
        ))
        company_id_map[company_name] = cursor.lastrowid

    # Insert tools
    for company_name, tools in company_tools.items():
        company_id = company_id_map.get(company_name)
        if not company_id:
            continue
        for tool_id, tool_data in tools.items():
            cursor.execute('''
                INSERT INTO company_tools (company_id, company_name, tool_id, tool_name,
                                          tool_category, mention_count, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_id,
                company_name,
                tool_id,
                tool_data.get('name', tool_id),
                tool_data['category'],
                tool_data['count'],
                tool_data['last_seen']
            ))

    # Insert signals
    for company_name, signals in company_signals.items():
        company_id = company_id_map.get(company_name)
        if not company_id:
            continue
        for signal_key, signal_data in signals.items():
            cursor.execute('''
                INSERT INTO company_signals (company_id, company_name, signal_type,
                                            signal_value, mention_count, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                company_id,
                company_name,
                signal_data['type'],
                signal_data.get('value', signal_key),
                signal_data['count'],
                signal_data['last_seen']
            ))

    # Create indexes for faster queries
    cursor.execute('CREATE INDEX idx_tools_company ON company_tools(company_id)')
    cursor.execute('CREATE INDEX idx_tools_category ON company_tools(tool_category)')
    cursor.execute('CREATE INDEX idx_tools_name ON company_tools(tool_name)')
    cursor.execute('CREATE INDEX idx_signals_company ON company_signals(company_id)')
    cursor.execute('CREATE INDEX idx_signals_type ON company_signals(signal_type)')
    cursor.execute('CREATE INDEX idx_companies_stage ON companies(stage)')
    cursor.execute('CREATE INDEX idx_companies_industry ON companies(industry)')

    conn.commit()
    conn.close()

    return len(companies)


def discover_new_tools(df, config):
    """Scan for potential new tools not in the config."""
    known_tools = set()
    for category, tools in config.get('technographics', {}).items():
        known_tools.update(tools.keys())

    # Patterns that might indicate tool names
    tool_patterns = [
        r'\b([A-Z][a-z]+(?:\.(?:io|ai|com))?)\b',  # CamelCase or domain
        r'\b([A-Z]{2,})\b',  # Acronyms
    ]

    potential_tools = defaultdict(int)

    for idx, row in df.iterrows():
        all_text = get_all_text(row)

        for pattern in tool_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower()
                if match_lower not in known_tools and len(match) > 2:
                    potential_tools[match] += 1

    # Filter to tools mentioned at least 3 times
    significant_tools = {k: v for k, v in potential_tools.items() if v >= 3}

    # Sort by frequency
    sorted_tools = sorted(significant_tools.items(), key=lambda x: x[1], reverse=True)

    # Save to file
    discovered = {
        'generated_at': datetime.now().isoformat(),
        'potential_tools': [{'name': name, 'mentions': count} for name, count in sorted_tools[:100]]
    }

    with open(DISCOVERED_FILE, 'w') as f:
        json.dump(discovered, f, indent=2)

    return sorted_tools[:50]


def main():
    parser = argparse.ArgumentParser(description='Generate Company Intelligence Database')
    parser.add_argument('--discover', action='store_true', help='Run tool discovery mode')
    args = parser.parse_args()

    print("=" * 70)
    print("COMPANY INTELLIGENCE GENERATOR")
    print("=" * 70)

    # Load config
    print(f"\nLoading config from {CONFIG_FILE}...")
    config = load_config()

    # Count configured tools
    tool_count = sum(len(tools) for tools in config.get('technographics', {}).values())
    signal_count = sum(len(signals) for signals in config.get('signals', {}).values())
    print(f"  Configured tools: {tool_count}")
    print(f"  Configured signals: {signal_count}")

    # Load data
    print(f"\nLoading data from {MASTER_CSV}...")
    df = pd.read_csv(MASTER_CSV)
    print(f"  Total records: {len(df)}")
    print(f"  Unique companies: {df['company'].nunique()}")

    if args.discover:
        print("\n" + "=" * 70)
        print("DISCOVERY MODE")
        print("=" * 70)
        discovered = discover_new_tools(df, config)
        print(f"\nTop potential new tools (saved to {DISCOVERED_FILE}):")
        for name, count in discovered[:20]:
            print(f"  {name}: {count} mentions")
        return

    # Process companies
    print("\nProcessing companies...")
    companies, company_tools, company_signals = process_companies(df, config)

    # Count statistics
    total_tools_found = sum(len(tools) for tools in company_tools.values())
    total_signals_found = sum(len(signals) for signals in company_signals.values())
    companies_with_tools = sum(1 for tools in company_tools.values() if tools)
    companies_with_signals = sum(1 for signals in company_signals.values() if signals)

    print(f"\n  Companies processed: {len(companies)}")
    print(f"  Companies with tools: {companies_with_tools}")
    print(f"  Companies with signals: {companies_with_signals}")
    print(f"  Total tool mentions: {total_tools_found}")
    print(f"  Total signal mentions: {total_signals_found}")

    # Write to database
    print(f"\nWriting to {DB_FILE}...")
    num_companies = write_database(companies, company_tools, company_signals)

    print(f"\n{'=' * 70}")
    print(f"DATABASE CREATED: {DB_FILE}")
    print(f"  Companies: {num_companies}")
    print(f"  Tool records: {total_tools_found}")
    print(f"  Signal records: {total_signals_found}")
    print(f"\nTo explore with Datasette:")
    print(f"  pip install datasette")
    print(f"  datasette {DB_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
