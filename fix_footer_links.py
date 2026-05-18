import asyncio, json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
POST_ID = 40380

REPLACEMENTS = {
    'https:\\/\\/puria.ro\\/pasari-si-rozatoare\\/': 'https:\\/\\/puria.ro\\/pasari-rozatoare\\/',
    'https:\\/\\/puria.ro\\/promotii-si-oferte\\/': 'https:\\/\\/puria.ro\\/promotii\\/',
}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # Login
        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        print('Logged in')

        # Navigate to wp-admin to get nonce
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        # Fetch current _elementor_data via REST API
        result = await page.evaluate("""async (postId) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch(`/wp-json/wp/v2/elementor_library/${postId}?context=edit`, {
                headers: {'X-WP-Nonce': nonce}
            });
            if (!res.ok) return {error: res.status, text: await res.text()};
            const data = await res.json();
            return {
                status: res.status,
                meta_keys: Object.keys(data.meta || {}),
                has_elementor_data: !!(data.meta && data.meta._elementor_data),
                elementor_data_length: data.meta?._elementor_data?.length || 0,
                content_length: data.content?.rendered?.length || 0
            };
        }""", POST_ID)
        print(f'REST fetch result: {result}')

        if result.get('error'):
            print(f'REST API error: {result}')
            await browser.close()
            return

        # Get raw elementor_data
        raw_data = await page.evaluate("""async (postId) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch(`/wp-json/wp/v2/elementor_library/${postId}?context=edit`, {
                headers: {'X-WP-Nonce': nonce}
            });
            const data = await res.json();
            return data.meta?._elementor_data || '';
        }""", POST_ID)

        if not raw_data:
            print('No _elementor_data found via REST. Trying direct DB approach via WPCode...')
            # Fallback: use wp-admin AJAX to get post meta
            result2 = await page.evaluate("""async (postId) => {
                const nonce = window.wpApiSettings?.nonce || '';
                // Try getting post content which may contain elementor data
                const res = await fetch(`/wp-json/wp/v2/elementor_library/${postId}?context=edit&_fields=meta,content,title`, {
                    headers: {'X-WP-Nonce': nonce}
                });
                const data = await res.json();
                return JSON.stringify(data).substring(0, 500);
            }""", POST_ID)
            print(f'Debug: {result2}')
            await browser.close()
            return

        print(f'Got elementor_data: {len(raw_data)} chars')

        # Find broken URLs
        found_replacements = {}
        for old_url, new_url in REPLACEMENTS.items():
            if old_url in raw_data:
                found_replacements[old_url] = new_url
                print(f'Found: {old_url[:60]}')
            else:
                print(f'NOT found: {old_url[:60]}')

        if not found_replacements:
            # Check what URLs exist for diagnosis
            import re
            urls_in_data = re.findall(r'puria\\.ro\\\\/[a-z0-9\\-]+\\\\/', raw_data)
            print(f'Sample paths in elementor_data: {urls_in_data[:10]}')
            await browser.close()
            return

        # Apply replacements
        new_data = raw_data
        for old_url, new_url in found_replacements.items():
            new_data = new_data.replace(old_url, new_url)
            count = raw_data.count(old_url)
            print(f'Replaced {count}x: {old_url} -> {new_url}')

        # Save back via REST API
        save_result = await page.evaluate("""async ([postId, elementorData]) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch(`/wp-json/wp/v2/elementor_library/${postId}`, {
                method: 'POST',
                headers: {
                    'X-WP-Nonce': nonce,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    meta: {_elementor_data: elementorData}
                })
            });
            const data = await res.json();
            return {status: res.status, ok: res.ok, id: data.id || null, error: data.message || null};
        }""", [POST_ID, new_data])

        print(f'Save result: {save_result}')

        if save_result.get('ok'):
            print('Saved OK. Verifying on live site...')
            page2 = await context.new_page()
            await page2.goto('https://puria.ro/', wait_until='domcontentloaded')
            html = await page2.content()

            for old_url, new_url in found_replacements.items():
                has_old = old_url in html
                has_new = new_url in html
                print(f'  Old {old_url}: {"STILL PRESENT ❌" if has_old else "gone ✅"}')
                print(f'  New {new_url}: {"present ✅" if has_new else "NOT found ❌"}')
            await page2.close()
        else:
            print(f'Save FAILED: {save_result}')

        await browser.close()

asyncio.run(main())
