# Analytics Configuration

# Google Analytics 4
GA4_MEASUREMENT_ID = "G-3119XDMC12"

# Microsoft Clarity
CLARITY_PROJECT_ID = "uvbemaajqm"

def get_tracking_code():
    """Returns the tracking code snippet to add to <head>"""
    code = ""

    if GA4_MEASUREMENT_ID:
        code += f'''
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA4_MEASUREMENT_ID}');
    </script>
'''

    if CLARITY_PROJECT_ID:
        code += f'''
    <!-- Microsoft Clarity -->
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){{
            c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        }})(window, document, "clarity", "script", "{CLARITY_PROJECT_ID}");
    </script>
'''

    return code
