import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # visible to debug
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1400, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)

        # Go to CTX Feed list
        await page.goto('https://puria.ro/wp-admin/admin.php?page=woo-feed', wait_until='networkidle')
        print('CTX Feed list page loaded')

        # Dump all links and buttons on the page
        elements = await page.evaluate("""() => {
            const results = [];
            // All links
            document.querySelectorAll('a').forEach(el => {
                const text = el.innerText.trim();
                const href = el.href;
                if (text || href.includes('feed')) {
                    results.push({type: 'a', text: text.substring(0, 50), href: href.substring(0, 100)});
                }
            });
            return results.slice(0, 50);
        }""")
        print('Links:')
        for el in elements:
            print(f'  {el["text"]} -> {el["href"]}')

        await page.screenshot(path='/tmp/ctx_feed_list.png')
        print('Screenshot saved to /tmp/ctx_feed_list.png')

        await browser.close()

asyncio.run(main())
