import asyncio
import json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

CAT_IDS = {'Caini': 10831, 'Pisici': 10832, 'Pasari-rozatoare': 10833}

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

        for name, cat_id in CAT_IDS.items():
            result = await page.evaluate(f"""async () => {{
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch('/wp-json/wc/v3/products/categories/{cat_id}', {{
                    headers: {{'X-WP-Nonce': nonce}}
                }});
                return await res.text();
            }}""")
            data = json.loads(result)
            desc_html = data.get('description', '')
            text = re.sub(r'<[^>]+>', ' ', desc_html).strip()
            text = re.sub(r'\s+', ' ', text)
            word_count = len(text.split())
            print(f'\n{"="*60}')
            print(f'{name} (ID {cat_id}) — {word_count} cuvinte')
            print(f'{"="*60}')
            print(text)

        await browser.close()

asyncio.run(main())
