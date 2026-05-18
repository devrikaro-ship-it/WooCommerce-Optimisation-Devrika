import asyncio
import json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

async def fetch_page(page, offset, per_page=100):
    result = await page.evaluate(f"""async () => {{
        const nonce = window.wpApiSettings?.nonce || '';
        const res = await fetch('/wp-json/wc/v3/products?per_page={per_page}&offset={offset}&orderby=id&order=asc&status=publish', {{
            headers: {{'X-WP-Nonce': nonce}}
        }});
        return await res.text();
    }}""")
    data = json.loads(result)
    return data if isinstance(data, list) else []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        all_products = []
        offset = 0
        while True:
            batch = await fetch_page(page, offset, 100)
            if not batch:
                break
            all_products.extend(batch)
            print(f'  Fetched {len(all_products)} produse...')
            if len(batch) < 100:
                break
            offset += 100

        print(f'\nTotal produse: {len(all_products)}')

        empty_desc = []
        short_desc = []
        ok_desc = []

        for prod in all_products:
            name = prod.get('name', '?')[:50]
            desc_html = prod.get('description', '')
            desc_text = re.sub(r'<[^>]+>', ' ', desc_html).strip()
            desc_text = re.sub(r'\s+', ' ', desc_text)
            words = len(desc_text.split()) if desc_text else 0

            if words == 0:
                empty_desc.append((name, prod.get('id')))
            elif words < 100:
                short_desc.append((name, words, prod.get('id')))
            else:
                ok_desc.append(words)

        print(f'\n=== STATISTICI DESCRIERI ===')
        print(f'Fara descriere (0 cuvinte): {len(empty_desc)}')
        print(f'Descriere scurta (<100w):   {len(short_desc)}')
        print(f'Descriere OK (100w+):       {len(ok_desc)}')
        if ok_desc:
            print(f'  Media: {sum(ok_desc)//len(ok_desc)}w | Min: {min(ok_desc)}w | Max: {max(ok_desc)}w')

        if empty_desc[:10]:
            print(f'\nPrime 10 produse FARA descriere:')
            for name, pid in empty_desc[:10]:
                print(f'  ID {pid}: {name}')

        if short_desc[:10]:
            print(f'\nPrime 10 produse cu descriere SCURTA:')
            for name, words, pid in short_desc[:10]:
                print(f'  ID {pid} [{words}w]: {name}')

        await browser.close()

asyncio.run(main())
