import asyncio
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

        # Try the known CTX Feed URL slug
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wp-xml-feed', wait_until='networkidle')
        print('URL:', page.url)

        # Get all links and buttons
        elements = await page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('a, button, input[type=button], input[type=submit]').forEach(el => {
                const text = (el.innerText || el.value || '').trim().substring(0, 60);
                const href = el.href || '';
                if (text || href) results.push({tag: el.tagName, text, href: href.substring(0, 100)});
            });
            return results;
        }""")

        print('Elements found:')
        for el in elements:
            print(f'  <{el["tag"]}> "{el["text"]}" -> {el["href"]}')

        # Try AJAX to update feed
        print('\nTrying admin-ajax.php for feed update...')
        nonce_result = await page.evaluate("""async () => {
            // Try to get nonce from page or from wp-admin
            const nonce = window.wpApiSettings?.nonce || document.querySelector('#_wpnonce')?.value || '';
            return {nonce, wpApiSettings: window.wpApiSettings};
        }""")
        print('Nonce info:', nonce_result)

        # Try admin-ajax with AJAX handler for CTX Feed
        ajax_result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const formData = new FormData();
            formData.append('action', 'woo_feed_update');
            formData.append('feed_id', '2');
            formData.append('nonce', nonce);
            const res = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                body: formData
            });
            return {status: res.status, body: (await res.text()).substring(0, 200)};
        }""")
        print(f'AJAX update: {ajax_result["status"]} — {ajax_result["body"]}')

        # Try different AJAX actions
        ajax_result2 = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const formData = new FormData();
            formData.append('action', 'ctxfeed_update_feed');
            formData.append('id', '2');
            formData.append('nonce', nonce);
            const res = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                body: formData
            });
            return {status: res.status, body: (await res.text()).substring(0, 200)};
        }""")
        print(f'AJAX ctxfeed_update: {ajax_result2["status"]} — {ajax_result2["body"]}')

        await browser.close()

asyncio.run(main())
