#!/usr/bin/env python3
"""
Sync executive moves from newsletter frontmatter to moves.json

Newsletters should include moves in frontmatter like:
---
title: "..."
date: 2026-01-07
moves:
  - name: Bobby Condon
    new_role: Chief Revenue Officer
    new_company: Forward Networks
    previous: CRO-level leadership at Fastly (scaled revenue from $2M to $480M)
---

This script reads all newsletters, extracts moves, and updates data/moves.json
"""

import os
import json
import yaml
import glob
from datetime import datetime

NEWSLETTERS_DIR = 'newsletters'
DATA_DIR = 'data'
MOVES_FILE = f'{DATA_DIR}/moves.json'

def parse_frontmatter(filepath):
    """Extract YAML frontmatter from markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    # Find the closing ---
    end = content.find('---', 3)
    if end == -1:
        return None

    frontmatter = content[3:end].strip()
    try:
        return yaml.safe_load(frontmatter)
    except yaml.YAMLError:
        return None

def get_all_moves():
    """Extract moves from all newsletters"""
    all_moves = []

    # Get all newsletter files
    pattern = f"{NEWSLETTERS_DIR}/*.md"
    files = glob.glob(pattern)

    for filepath in files:
        frontmatter = parse_frontmatter(filepath)
        if not frontmatter:
            continue

        date = frontmatter.get('date')
        moves = frontmatter.get('moves', [])

        if not moves:
            continue

        # Convert date to string if it's a date object
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        elif hasattr(date, 'isoformat'):
            date_str = date.isoformat()
        else:
            date_str = str(date)

        for move in moves:
            move['date'] = date_str
            all_moves.append(move)

    # Sort by date descending (most recent first)
    all_moves.sort(key=lambda x: x.get('date', ''), reverse=True)

    return all_moves

def main():
    print("=" * 70)
    print("🔄 SYNCING MOVES FROM NEWSLETTERS")
    print("=" * 70)

    moves = get_all_moves()

    if not moves:
        print("⚠️  No moves found in newsletter frontmatter")
        print("   Add moves to newsletter frontmatter like:")
        print("   ---")
        print("   moves:")
        print("     - name: Bobby Condon")
        print("       new_role: Chief Revenue Officer")
        print("       new_company: Forward Networks")
        print("       previous: CRO at Fastly")
        print("   ---")
        return

    # Create output
    output = {
        "moves": moves,
        "last_updated": datetime.now().strftime('%Y-%m-%d')
    }

    # Save to moves.json
    with open(MOVES_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Found {len(moves)} moves across newsletters")
    print(f"✅ Saved to {MOVES_FILE}")

    # Show latest moves
    print("\n📋 Latest moves:")
    for move in moves[:5]:
        print(f"   • {move['name']} → {move['new_role']} at {move['new_company']}")

if __name__ == '__main__':
    main()
