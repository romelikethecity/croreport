#!/usr/bin/env python3
"""
Shared HTML components for The CRO Report site generation.

Usage:
    from shared_components import get_nav, get_footer, get_nav_styles

This module loads HTML includes from templates/includes/ so that
navigation and footer can be updated in one place.
"""

import os

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'includes')

def _read_include(filename):
    """Read an include file and return its contents."""
    filepath = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    else:
        print(f"Warning: Include file not found: {filepath}")
        return ""

def get_nav():
    """Return the shared navigation HTML."""
    return _read_include('nav.html')

def get_footer():
    """Return the shared footer HTML."""
    return _read_include('footer.html')

def get_nav_styles():
    """Return the shared navigation CSS."""
    return _read_include('nav-styles.css')

def get_head_common():
    """Return common head elements (fonts, tracking, etc.)."""
    return '''
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3119XDMC12"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-3119XDMC12');
    </script>

    <!-- Microsoft Clarity -->
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        })(window, document, "clarity", "script", "uvbemaajqm");
    </script>

    <!-- Favicons -->
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
'''

# For backwards compatibility, also provide inline versions
# that can be embedded in Python f-strings (escaped braces)
def get_nav_styles_escaped():
    """Return nav styles with escaped braces for f-string use."""
    return get_nav_styles().replace('{', '{{').replace('}', '}}')


if __name__ == '__main__':
    # Test the includes
    print("Testing shared components...")
    print(f"Nav length: {len(get_nav())} chars")
    print(f"Footer length: {len(get_footer())} chars")
    print(f"Styles length: {len(get_nav_styles())} chars")
    print("Done!")
