import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        # GET feed attributes config
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/attributes_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")

        print(f'GET attributes: {result["status"]}')

        try:
            data = json.loads(result['body'])
            print(f'Keys: {list(data.keys()) if isinstance(data, dict) else type(data)}')
            # Find GTIN-related fields
            raw = json.dumps(data)
            if 'gtin' in raw.lower() or 'ean' in raw.lower() or 'mpn' in raw.lower():
                print('Found GTIN/EAN/MPN in config')
            else:
                print('No GTIN/EAN/MPN found in attributes mapping')

            # Print full structure (condensed)
            if isinstance(data, dict):
                for k, v in list(data.items())[:5]:
                    print(f'  {k}: {str(v)[:100]}')
        except:
            print(f'Raw: {result["body"][:500]}')

        # Also get the full feed config
        print('\nGetting full feed config...')
        feed_result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/feed?id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")
        print(f'GET feed: {feed_result["status"]}')
        try:
            fd = json.loads(feed_result['body'])
            raw_fd = json.dumps(fd)
            if 'gtin' in raw_fd.lower():
                print('GTIN found in feed config')
                # Find gtin location
                import re
                matches = re.findall(r'["\']([^"\']*gtin[^"\']*)["\']\s*[:\s]', raw_fd, re.IGNORECASE)
                print(f'GTIN mentions: {matches[:5]}')
            print(f'Feed config keys: {list(fd.keys()) if isinstance(fd, dict) else type(fd)}')
            print(f'Sample: {str(fd)[:300]}')
        except:
            print(f'Raw: {feed_result["body"][:300]}')

        await browser.close()

asyncio.run(main())
