import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
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

        # Get product permalink via WP REST with nonce
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        urls = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            // Search for MAC's products
            const res = await fetch('/wp-json/wp/v2/product?per_page=5&search=paw+power&context=edit', {
                headers: {'X-WP-Nonce': nonce}
            });
            if (!res.ok) return {error: res.status};
            const data = await res.json();
            return data.map(p => ({id: p.id, link: p.link, slug: p.slug, title: (p.title?.rendered || '').substring(0,50)}));
        }""")
        print(f'WP REST products: {urls}')

        # Also try searching for any product with hrana-umeda in URL
        if not isinstance(urls, list) or not urls:
            urls2 = await page.evaluate("""async () => {
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch('/wp-json/wp/v2/product?per_page=3&context=edit', {
                    headers: {'X-WP-Nonce': nonce}
                });
                if (!res.ok) return {error: res.status};
                const data = await res.json();
                return data.map(p => ({id: p.id, link: p.link, slug: p.slug}));
            }""")
            print(f'First 3 products: {urls2}')

        await browser.close()

asyncio.run(main())
