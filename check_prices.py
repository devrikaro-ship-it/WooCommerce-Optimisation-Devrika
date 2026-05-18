import sys, xml.etree.ElementTree as ET, urllib.request, re, ssl

with open('/tmp/feed.xml', 'rb') as f:
    content = f.read()

root = ET.fromstring(content)
ns = {'g': 'http://base.google.com/ns/1.0'}
items = root.findall('.//item')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

mismatches = []
ok = []
errors = []

for item in items[:40]:
    link = item.find('link')
    price_el = item.find('g:price', ns)
    title_el = item.find('title')
    if not link or not price_el: continue

    url = link.text.strip()
    name = title_el.text[:45] if title_el is not None else url[:45]
    feed_price_str = price_el.text.strip().replace(' RON','').replace(',','.')
    try:
        feed_price = float(feed_price_str)
    except:
        continue

    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        html = urllib.request.urlopen(req, timeout=10, context=ctx).read().decode('utf-8','ignore')
    except Exception as e:
        errors.append(f'{name}: {e}')
        continue

    site_prices = re.findall(r'"price":"([^"]+)"', html)
    if not site_prices:
        errors.append(f'{name}: no price found on page')
        continue

    try:
        site_price = float(site_prices[0])
    except:
        continue

    diff = abs(feed_price - site_price)
    diff_pct = diff / site_price * 100 if site_price > 0 else 0

    if diff > 1.0:
        mismatches.append((name, feed_price, site_price, diff_pct))
    else:
        ok.append(name)

print(f'=== REZULTATE (40 produse) ===')
print(f'OK: {len(ok)} | Mismatch: {len(mismatches)} | Erori fetch: {len(errors)}\n')

if mismatches:
    print('❌ PRETURI DIFERITE:')
    for name, fp, sp, pct in mismatches:
        print(f'  Feed: {fp:.0f} RON | Site: {sp:.0f} RON | Diff: {pct:.1f}% | {name}')

if ok:
    print(f'\n✅ OK (primele 5): {ok[:5]}')
