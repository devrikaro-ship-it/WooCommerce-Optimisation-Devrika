import re

with open('/tmp/puria_home.html', 'r', errors='ignore') as f:
    html = f.read()

gtag = re.findall(r'gtag\s*\(|googletagmanager\.com|gtag\.js', html)
print(f'GTM/gtag mentions: {len(gtag)}')
for m in gtag[:8]:
    idx = html.find(m)
    print(f'  {html[max(0,idx-40):idx+70].strip()[:110]}')

print()
fonts = re.findall(r'fonts\.googleapis\.com[^\"\'\s>]+', html)
print(f'Google Fonts requests: {len(fonts)}')
for f in fonts[:10]:
    print(f'  {f[:100]}')

print()
fb = re.findall(r'fbevents\.js|connect\.facebook\.net', html)
print(f'Facebook pixel: {len(fb)}')

chaty = re.findall(r'chaty|chative', html, re.IGNORECASE)
print(f'Chaty: {len(chaty)}')

scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
external = [s for s in scripts if s.startswith('http') and 'puria.ro' not in s]
print(f'\nExternal scripts ({len(external)}):')
for s in external:
    print(f'  {s[:90]}')

print()
# WP Rocket delay JS markers
rocket = re.findall(r'data-rocketlazyloadscript|rocket-loader|data-rocket-defer', html, re.IGNORECASE)
print(f'WP Rocket lazy/defer markers: {len(rocket)}')
