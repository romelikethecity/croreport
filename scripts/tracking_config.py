# Analytics Configuration

# Google Analytics 4
GA4_MEASUREMENT_ID = "G-3119XDMC12"

# Microsoft Clarity
CLARITY_PROJECT_ID = "uvbemaajqm"

def get_tracking_code():
    """Returns the tracking code snippet to add to <head>

    Analytics are deferred until after page is interactive to improve TBT/LCP.
    Uses requestIdleCallback with setTimeout fallback.
    """
    code = ""

    if GA4_MEASUREMENT_ID or CLARITY_PROJECT_ID:
        code += '''
    <!-- Deferred Analytics - loads after page is interactive -->
    <script>
        (function() {
            function loadAnalytics() {'''

        if GA4_MEASUREMENT_ID:
            code += f'''
                // Google Analytics 4
                var ga = document.createElement('script');
                ga.src = 'https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}';
                ga.async = true;
                document.head.appendChild(ga);
                window.dataLayer = window.dataLayer || [];
                function gtag(){{dataLayer.push(arguments);}}
                gtag('js', new Date());
                gtag('config', '{GA4_MEASUREMENT_ID}');'''

        if CLARITY_PROJECT_ID:
            code += f'''
                // Microsoft Clarity
                (function(c,l,a,r,i,t,y){{
                    c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
                    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
                }})(window, document, "clarity", "script", "{CLARITY_PROJECT_ID}");'''

        code += '''
            }
            // Defer until browser is idle, or after 3s max
            if ('requestIdleCallback' in window) {
                requestIdleCallback(loadAnalytics, { timeout: 3000 });
            } else {
                setTimeout(loadAnalytics, 2000);
            }
        })();
    </script>
'''

    return code
