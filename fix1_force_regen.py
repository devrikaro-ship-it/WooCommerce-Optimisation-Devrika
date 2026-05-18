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

        # Get nonce from dashboard
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        nonce = await page.evaluate("window.wpApiSettings?.nonce || ''")
        print(f'Nonce: {nonce}')

        # Try CTX Feed generate endpoints
        endpoints = [
            ('GET', '/wp-json/ctxfeed/v1/generate?id=2'),
            ('GET', '/wp-json/ctxfeed/v1/feeds/2'),
            ('GET', '/wp-json/ctxfeed/v1/feeds'),
            ('POST', '/wp-json/ctxfeed/v1/generate'),
        ]

        for method, ep in endpoints:
            result = await page.evaluate(f"""async () => {{
                const nonce = '{nonce}';
                const res = await fetch('{ep}', {{
                    method: '{method}',
                    headers: {{'X-WP-Nonce': nonce, 'Content-Type': 'application/json'}},
                    {'''body: JSON.stringify({id: 2})''' if method == 'POST' else ''}
                }});
                return {{status: res.status, body: (await res.text()).substring(0, 150)}};
            }}""")
            print(f'{method} {ep}: {result["status"]} — {result["body"][:100]}')

        # Try frontend regeneration URL
        print('\nTrying frontend feed URL with force param...')
        feed_urls = [
            'https://puria.ro/?wf_feed=1&feedName=googleandmetafeed',
            'https://puria.ro/?ctx_feed=1&id=2',
        ]
        for url in feed_urls:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            content_len = len(await page.content())
            print(f'{url}: {content_len} chars, URL: {page.url}')

        await browser.close()

asyncio.run(main())
