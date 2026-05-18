import asyncio, xml.etree.ElementTree as ET, re
from playwright.async_api import async_playwright

with open('/tmp/feed.xml', 'rb') as f:
    content = f.read()

root = ET.fromstring(content)
ns = {'g': 'http://base.google.com/ns/1.0'}
items = root.findall('.//item')

# Grab first 50 products
products = []
for item in items[:50]:
    link = item.find('link')
    price_el = item.find('g:price', ns)
    title_el = item.find('title')
    if link is None or price_el is None:
        continue
    url = link.text.strip()
    name = (title_el.text[:50] if title_el is not None else url[:50])
    price_str = price_el.text.strip().replace(' RON', '').replace(',', '.')
    try:
        feed_price = float(price_str)
    except:
        continue
    products.append({'url': url, 'name': name, 'feed_price': feed_price})

async def main():
    mismatches = []
    ok = []
    errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for prod in products:
            try:
                page = await context.new_page()
                await page.goto(prod['url'], wait_until='domcontentloaded', timeout=20000)
                html = await page.content()
                await page.close()

                # Try JSON-LD price first
                prices = re.findall(r'"price"\s*:\s*"?([0-9]+(?:[.,][0-9]+)?)"?', html)
                if not prices:
                    errors.append(f'{prod["name"]}: no price found')
                    continue

                site_price = float(prices[0].replace(',', '.'))
                diff = abs(prod['feed_price'] - site_price)
                diff_pct = diff / site_price * 100 if site_price > 0 else 0

                if diff > 1.0:
                    mismatches.append({
                        'name': prod['name'],
                        'feed': prod['feed_price'],
                        'site': site_price,
                        'diff': diff,
                        'pct': diff_pct,
                        'url': prod['url']
                    })
                else:
                    ok.append(prod['name'])

            except Exception as e:
                errors.append(f'{prod["name"]}: {e}')

        await browser.close()

    print(f'=== PRICE CHECK (50 produse) ===')
    print(f'OK: {len(ok)} | Mismatch: {len(mismatches)} | Erori: {len(errors)}\n')

    if mismatches:
        print('PRETURI DIFERITE:')
        for m in mismatches:
            print(f'  Feed: {m["feed"]:.0f} RON | Site: {m["site"]:.0f} RON | Diff: {m["pct"]:.1f}% | {m["name"]}')
            print(f'    {m["url"]}')

    if errors:
        print(f'\nErori ({len(errors)}):')
        for e in errors[:5]:
            print(f'  {e}')

asyncio.run(main())
