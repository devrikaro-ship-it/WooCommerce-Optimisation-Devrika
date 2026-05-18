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

        # Search for Despre noi page
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/pages?search=despre&per_page=5', {
                headers: {'X-WP-Nonce': nonce}
            });
            return await res.text();
        }""")
        pages = json.loads(result)
        print(f'Pages found: {len(pages)}')
        for pg in pages:
            desc_html = pg.get('content', {}).get('rendered', '')
            desc_text = re.sub(r'<[^>]+>', ' ', desc_html).strip()
            desc_text = re.sub(r'\s+', ' ', desc_text)
            meta = pg.get('excerpt', {}).get('rendered', '')
            meta_text = re.sub(r'<[^>]+>', '', meta).strip()
            print(f'\nID: {pg["id"]} | Slug: {pg["slug"]} | Link: {pg["link"]}')
            print(f'Content ({len(desc_text.split())}w): {desc_text[:300]}')
            print(f'Excerpt: {meta_text[:150]}')

        await browser.close()

asyncio.run(main())
