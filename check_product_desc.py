import asyncio
import json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

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

        # Get 10 products spread across categories
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wc/v3/products?per_page=15&orderby=id&order=desc&status=publish', {
                headers: {'X-WP-Nonce': nonce}
            });
            return await res.text();
        }""")

        products = json.loads(result)
        if not isinstance(products, list):
            print('API error:', products)
            return
        print(f'Produse verificate: {len(products)}\n')

        empty = 0
        short = 0
        ok = 0

        for p_data in products:
            name = p_data.get('name', '?')[:50]
            desc_html = p_data.get('description', '')
            short_desc_html = p_data.get('short_description', '')

            desc_text = re.sub(r'<[^>]+>', ' ', desc_html).strip()
            desc_text = re.sub(r'\s+', ' ', desc_text)
            short_text = re.sub(r'<[^>]+>', ' ', short_desc_html).strip()
            short_text = re.sub(r'\s+', ' ', short_text)

            desc_words = len(desc_text.split()) if desc_text else 0
            short_words = len(short_text.split()) if short_text else 0

            if desc_words == 0 and short_words == 0:
                status = '❌ GOL'
                empty += 1
            elif desc_words < 50:
                status = '⚠️ SCURT'
                short += 1
            else:
                status = '✅ OK'
                ok += 1

            print(f'{status} [{desc_words}w desc / {short_words}w short] {name}')
            if desc_text and desc_words < 200:
                print(f'   DESC: {desc_text[:150]}')
            elif desc_text:
                print(f'   DESC: {desc_text[:150]}...')

        print(f'\n--- SUMAR ---')
        print(f'Goale: {empty} | Scurte (<50w): {short} | OK: {ok}')

        await browser.close()

asyncio.run(main())
