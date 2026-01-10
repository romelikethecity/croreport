#!/usr/bin/env python3
"""
Shared templates and utilities for CRO Report page generators.

This module consolidates common HTML, CSS, and utility functions used across
multiple page generators to eliminate duplication and centralize maintenance.
"""

import re
import pandas as pd
import sys

sys.path.insert(0, 'scripts')
try:
    from tracking_config import get_tracking_code
    TRACKING_CODE = get_tracking_code()
except:
    TRACKING_CODE = ""

# SEO: Always use thecroreport.com as canonical domain
BASE_URL = 'https://thecroreport.com'


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def slugify(text, max_length=60):
    """Convert text to URL-safe slug"""
    if pd.isna(text) or not text:
        return None
    slug = str(text).lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug[:max_length] if slug else None


def format_salary(min_amount, max_amount):
    """Format salary range for display"""
    try:
        min_sal = float(min_amount) if pd.notna(min_amount) else 0
        max_sal = float(max_amount) if pd.notna(max_amount) else 0
    except (ValueError, TypeError):
        return ""

    if min_sal > 0 and max_sal > 0:
        return f"${int(min_sal/1000)}K - ${int(max_sal/1000)}K"
    elif max_sal > 0:
        return f"Up to ${int(max_sal/1000)}K"
    elif min_sal > 0:
        return f"${int(min_sal/1000)}K+"
    return ""


def is_remote(job_data):
    """Check if job is remote based on job data dict or series"""
    if isinstance(job_data, dict):
        if job_data.get('is_remote'):
            return True
        location = job_data.get('location', '')
    else:
        # pandas Series
        if 'is_remote' in job_data and job_data['is_remote']:
            return True
        location = job_data.get('location', '')

    if pd.notna(location):
        return 'remote' in str(location).lower()
    return False


# =============================================================================
# CSS CONSTANTS
# =============================================================================

CSS_VARIABLES = '''
    :root {
        --navy: #0a1628;
        --navy-light: #132038;
        --navy-medium: #1e3a5f;
        --navy-hover: #2d4a6f;
        --gold: #d4a853;
        --gold-muted: #b8956a;
        --gold-dark: #d97706;
        --red: #dc3545;
        --green: #28a745;
        --green-dark: #166534;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --white: #ffffff;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--gray-50);
        color: var(--gray-800);
        line-height: 1.6;
    }
'''

CSS_NAV = '''
    /* Navigation */
    .site-header {
        background: var(--white);
        border-bottom: 1px solid var(--gray-200);
        padding: 16px 0;
        position: sticky;
        top: 0;
        z-index: 100;
    }

    .header-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
        color: var(--navy-medium);
        font-weight: 700;
        font-size: 1.1rem;
    }

    .logo img, .logo-img {
        width: 40px;
        height: 40px;
        border-radius: 8px;
    }

    .nav, .nav-links {
        display: flex;
        gap: 24px;
        align-items: center;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .nav a, .nav-links a {
        color: var(--gray-600);
        text-decoration: none;
        font-size: 0.95rem;
        font-weight: 500;
        transition: color 0.2s;
    }

    .nav a:hover, .nav-links a:hover { color: var(--navy-medium); }
    .nav a.active { color: var(--navy-medium); font-weight: 600; }

    .nav-cta, .btn-subscribe {
        background: var(--navy-medium) !important;
        color: var(--white) !important;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
    }
    .nav-cta:hover, .btn-subscribe:hover {
        background: var(--navy-hover) !important;
    }

    /* Mobile Navigation */
    .mobile-menu-btn {
        display: none;
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--navy-medium);
    }
    .mobile-nav-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .mobile-nav-overlay.active { opacity: 1; }
    .mobile-nav {
        position: fixed;
        top: 0;
        right: -100%;
        width: 280px;
        max-width: 85%;
        height: 100vh;
        background: var(--white);
        z-index: 1000;
        padding: 1.5rem;
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
        transition: right 0.3s ease;
        overflow-y: auto;
    }
    .mobile-nav.active { right: 0; }
    .mobile-nav-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--gray-200);
    }
    .mobile-nav-header .logo-text {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--navy-medium);
    }
    .mobile-nav-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--gray-500);
    }
    .mobile-nav-links {
        list-style: none;
        margin: 0 0 2rem 0;
        padding: 0;
    }
    .mobile-nav-links li { border-bottom: 1px solid var(--gray-100); }
    .mobile-nav-links a {
        display: block;
        padding: 1rem 0;
        font-size: 1rem;
        font-weight: 500;
        color: var(--gray-600);
        text-decoration: none;
    }
    .mobile-nav-subscribe {
        display: block;
        width: 100%;
        padding: 1rem;
        background: var(--navy-medium);
        color: var(--white);
        text-align: center;
        font-weight: 600;
        border-radius: 8px;
        text-decoration: none;
    }

    @media (max-width: 768px) {
        .nav, .nav-links { display: none; }
        .mobile-menu-btn { display: block; }
        .mobile-nav-overlay { display: block; pointer-events: none; }
        .mobile-nav-overlay.active { pointer-events: auto; }
    }
'''

CSS_LAYOUT = '''
    /* Layout */
    .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    .container-narrow { max-width: 900px; margin: 0 auto; padding: 0 24px; }

    main { padding: 48px 0; }
    .section { margin-bottom: 56px; }

    /* Page Header */
    .page-header {
        background: var(--white);
        padding: 48px 0 40px;
        border-bottom: 1px solid var(--gray-200);
    }

    .breadcrumb {
        font-size: 0.85rem;
        color: var(--gray-500);
        margin-bottom: 16px;
    }
    .breadcrumb a { color: var(--gold-muted); text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }

    .page-label {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--gold-muted);
        margin-bottom: 12px;
    }

    .page-header h1 {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 12px;
    }

    .page-header .lead {
        font-size: 1.1rem;
        color: var(--gray-600);
        max-width: 700px;
        line-height: 1.7;
    }
'''

CSS_CARDS = '''
    /* Cards */
    .tool-card, .job-card, .company-card, .salary-card {
        background: var(--white);
        border: 1px solid var(--gray-200);
        border-radius: 12px;
        padding: 24px;
        text-decoration: none;
        color: inherit;
        transition: all 0.2s;
    }

    .tool-card:hover, .job-card:hover, .company-card:hover, .salary-card:hover {
        border-color: var(--gold);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }

    .card-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 14px;
        width: fit-content;
    }

    .badge-live { background: rgba(40, 167, 69, 0.12); color: var(--green); }
    .badge-soon { background: rgba(100, 116, 139, 0.12); color: var(--gray-500); }
    .badge-comparison { background: rgba(212, 168, 83, 0.15); color: var(--gold-muted); }
    .badge-remote { background: #dcfce7; color: var(--green-dark); }

    /* Stats */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 32px;
    }

    @media (max-width: 768px) { .stats-row { grid-template-columns: repeat(2, 1fr); } }

    .stat-box {
        background: var(--gray-50);
        border: 1px solid var(--gray-200);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
    }

    .stat-number {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--navy);
        line-height: 1;
    }

    .stat-number.gold { color: var(--gold-muted); }
    .stat-number.red { color: var(--red); }
    .stat-number.green { color: var(--green); }

    .stat-label {
        font-size: 0.75rem;
        color: var(--gray-500);
        margin-top: 6px;
    }
'''

CSS_CTA = '''
    /* CTA Box */
    .cta-box {
        background: var(--navy);
        color: var(--white);
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        margin: 40px 0;
    }

    .cta-box h3 {
        font-size: 1.25rem;
        margin-bottom: 10px;
    }

    .cta-box p {
        color: var(--gray-300);
        margin-bottom: 20px;
    }

    .btn {
        display: inline-block;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.95rem;
    }

    .btn-gold { background: var(--gold); color: var(--navy); }
    .btn-gold:hover { background: var(--gold-muted); }
'''

CSS_FOOTER = '''
    /* Footer */
    .site-footer, .footer {
        background: var(--white);
        border-top: 1px solid var(--gray-200);
        padding: 24px 0;
        margin-top: 48px;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        color: var(--gray-500);
    }

    .footer-content a, .footer a { color: var(--gray-600); text-decoration: none; }
    .footer-links a { margin-left: 24px; }
    .footer-links a:hover { color: var(--navy); }

    @media (max-width: 768px) {
        .footer-content { flex-direction: column; gap: 12px; text-align: center; }
        .footer-links a { margin: 0 12px; }
    }
'''


def get_base_styles():
    """Get all base CSS styles"""
    return f'''
    <style>
        {CSS_VARIABLES}
        {CSS_NAV}
        {CSS_LAYOUT}
        {CSS_CARDS}
        {CSS_CTA}
        {CSS_FOOTER}
    </style>
'''


# =============================================================================
# HTML GENERATORS
# =============================================================================

def get_html_head(title, description, page_path, include_styles=True):
    """Generate SEO-compliant head section"""
    styles = get_base_styles() if include_styles else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">{TRACKING_CODE}
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | The CRO Report</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{BASE_URL}/{page_path}">

    <!-- Open Graph Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{BASE_URL}/{page_path}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="The CRO Report">
    <meta property="og:image" content="{BASE_URL}/assets/social-preview.png">

    <!-- Twitter Card Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{BASE_URL}/assets/social-preview.png">

    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    {styles}
</head>
'''


def get_nav_html(active_page=None):
    """Generate site navigation including mobile nav and JS"""
    def active_class(page):
        return ' class="active"' if page == active_page else ''

    return f'''
<body>
    <header class="site-header">
        <div class="header-container">
            <a href="/" class="logo">
                <img src="/assets/logo.jpg" alt="The CRO Report">
                The CRO Report
            </a>
            <nav class="nav">
                <a href="/jobs/"{active_class('jobs')}>Jobs</a>
                <a href="/salaries/"{active_class('salaries')}>Salaries</a>
                <a href="/tools/"{active_class('tools')}>Tools</a>
                <a href="/insights/"{active_class('insights')}>Market Intel</a>
                <a href="/about/"{active_class('about')}>About</a>
                <a href="/newsletter/"{active_class('newsletter')}>Newsletter</a>
                <a href="https://croreport.substack.com/subscribe" class="nav-cta">Subscribe</a>
            </nav>
            <button class="mobile-menu-btn" aria-label="Open menu">☰</button>
        </div>
    </header>

    <!-- Mobile Navigation -->
    <div class="mobile-nav-overlay"></div>
    <nav class="mobile-nav">
        <div class="mobile-nav-header">
            <span class="logo-text">The CRO Report</span>
            <button class="mobile-nav-close" aria-label="Close menu">✕</button>
        </div>
        <ul class="mobile-nav-links">
            <li><a href="/jobs/">Jobs</a></li>
            <li><a href="/salaries/">Salaries</a></li>
            <li><a href="/tools/">Tools</a></li>
            <li><a href="/insights/">Market Intel</a></li>
            <li><a href="/about/">About</a></li>
            <li><a href="/newsletter/">Newsletter</a></li>
        </ul>
        <a href="https://croreport.substack.com/subscribe" class="mobile-nav-subscribe">Subscribe</a>
    </nav>

    <script>
        (function() {{
            const menuBtn = document.querySelector('.mobile-menu-btn');
            const closeBtn = document.querySelector('.mobile-nav-close');
            const overlay = document.querySelector('.mobile-nav-overlay');
            const mobileNav = document.querySelector('.mobile-nav');
            const mobileLinks = document.querySelectorAll('.mobile-nav-links a, .mobile-nav-subscribe');
            function openMenu() {{
                mobileNav.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }}
            function closeMenu() {{
                mobileNav.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }}
            menuBtn.addEventListener('click', openMenu);
            closeBtn.addEventListener('click', closeMenu);
            overlay.addEventListener('click', closeMenu);
            mobileLinks.forEach(link => {{ link.addEventListener('click', closeMenu); }});
        }})();
    </script>
'''


def get_footer_html():
    """Generate site footer"""
    return '''
    <footer class="site-footer">
        <div class="footer-content">
            <span>&copy; 2025 <a href="/">The CRO Report</a></span>
            <div class="footer-links">
                <a href="/jobs/">Jobs</a>
                <a href="/salaries/">Salaries</a>
                <a href="/tools/">Tools</a>
                <a href="/insights/">Market Intel</a>
                <a href="/about/">About</a>
                <a href="https://croreport.substack.com">Newsletter</a>
            </div>
        </div>
    </footer>
</body>
</html>
'''


def get_cta_box(title="Get Weekly Market Intelligence",
                description="Join 500+ sales executives getting compensation data, executive movements, and opportunity analysis.",
                button_text="Subscribe Free",
                button_url="https://croreport.substack.com/subscribe"):
    """Generate a CTA box"""
    return f'''
    <div class="cta-box">
        <h3>{title}</h3>
        <p>{description}</p>
        <a href="{button_url}" class="btn btn-gold">{button_text} →</a>
    </div>
'''
