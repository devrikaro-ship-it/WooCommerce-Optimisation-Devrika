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

        # Try REST API to regenerate feed 2
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';

            // Try regenerate endpoint
            const endpoints = [
                '/wp-json/ctxfeed/v1/feeds?id=2&regenerate=1',
                '/wp-json/ctxfeed/v1/regenerate?id=2',
                '/wp-json/ctxfeed/v1/feed/2/regenerate',
            ];

            const results = [];
            for (const ep of endpoints) {
                const res = await fetch(ep, {
                    method: 'GET',
                    headers: {'X-WP-Nonce': nonce}
                });
                results.push({ep, status: res.status, body: (await res.text()).substring(0, 100)});
            }
            return results;
        }""")

        print('GET regenerate attempts:')
        for r in result:
            print(f'  {r["ep"]}: {r["status"]} — {r["body"][:80]}')

        # Try POST to feeds endpoint
        post_result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/feeds', {
                method: 'POST',
                headers: {'X-WP-Nonce': nonce, 'Content-Type': 'application/json'},
                body: JSON.stringify({id: 2, regenerate: true})
            });
            return {status: res.status, body: (await res.text()).substring(0, 200)};
        }""")
        print(f'\nPOST /feeds: {post_result["status"]} — {post_result["body"]}')

        # Navigate to CTX Feed page and click Update Feed button
        print('\nNavigating to CTX Feed edit page...')
        await page.goto('https://puria.ro/wp-admin/admin.php?page=woo-feed&action=edit&id=2', wait_until='networkidle')
        print('Page URL:', page.url)

        # Check for update/generate button
        update_btn = await page.query_selector('input[name="update_feed"], button[name="update_feed"], #update-feed, .update-feed, input[value*="Update"], input[value*="Generate"]')
        if update_btn:
            btn_text = await update_btn.get_attribute('value') or await update_btn.inner_text()
            print(f'Found button: {btn_text}')
            await update_btn.click()
            await page.wait_for_load_state('networkidle')
            print('Clicked update, URL:', page.url)
        else:
            # Try finding any submit button
            buttons = await page.query_selector_all('input[type="submit"], button[type="submit"]')
            print(f'Found {len(buttons)} submit buttons')
            for btn in buttons:
                txt = await btn.get_attribute('value') or await btn.inner_text()
                print(f'  Button: {txt}')

        await browser.close()

asyncio.run(main())
