import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
WP_ADMIN_PAGE = 'https://puria.ro/wp-admin/admin.php?page=wp-xml-feed'

CATEGORY_MAPPINGS = {
    '10836': 'Animals & Pet Supplies > Pet Food > Dog Food > Dry Dog Food',
    '10837': 'Animals & Pet Supplies > Pet Food > Dog Food > Wet Dog Food',
    '10840': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Treats',
    '10841': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Health Supplies',
    '10842': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Grooming Supplies',
    '10845': 'Animals & Pet Supplies > Pet Food > Cat Food > Dry Cat Food',
    '10846': 'Animals & Pet Supplies > Pet Food > Cat Food > Wet Cat Food',
    '10849': 'Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Treats',
}

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

        print('Logging in...')
        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        print('Logged in:', page.url)

        # Navigate to dashboard to get wpApiSettings nonce
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        nonce_check = await page.evaluate("window.wpApiSettings")
        print(f'wpApiSettings on dashboard: {nonce_check}')

        # Get current mapping
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            console.log('Using nonce:', nonce);
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")
        print(f'GET mapping status: {result["status"]}')

        existing = {}
        try:
            existing = json.loads(result['body'])
            print(f'Existing mappings: {len(existing)} entries')
            # Show first few
            for k, v in list(existing.items())[:3]:
                print(f'  {k}: {v}')
        except:
            print(f'Raw: {result["body"][:300]}')

        # Merge
        merged = {**existing, **CATEGORY_MAPPINGS}
        print(f'\nApplying {len(CATEGORY_MAPPINGS)} specific mappings...')
        for cat_id, gcat in CATEGORY_MAPPINGS.items():
            print(f'  {cat_id} -> {gcat}')

        # Try PUT
        put_result = await page.evaluate("""async (mappings) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping', {
                method: 'PUT',
                headers: {'X-WP-Nonce': nonce, 'Content-Type': 'application/json'},
                body: JSON.stringify({feed_id: 2, mapping: mappings})
            });
            return {status: res.status, body: await res.text()};
        }""", merged)
        print(f'\nPUT status: {put_result["status"]}')
        print(f'PUT body: {put_result["body"][:300]}')

        if put_result['status'] not in (200, 201):
            # Try POST
            post_result = await page.evaluate("""async (mappings) => {
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch('/wp-json/ctxfeed/v1/category_mapping', {
                    method: 'POST',
                    headers: {'X-WP-Nonce': nonce, 'Content-Type': 'application/json'},
                    body: JSON.stringify({feed_id: 2, mapping: mappings})
                });
                return {status: res.status, body: await res.text()};
            }""", merged)
            print(f'\nPOST status: {post_result["status"]}')
            print(f'POST body: {post_result["body"][:300]}')

        # Verify
        verify = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")
        print('\nVerification:')
        try:
            parsed = json.loads(verify['body'])
            for cat_id in ['10836', '10837', '10845', '10846', '10840', '10849']:
                print(f'  {cat_id}: {parsed.get(cat_id, "(not set)")}')
        except:
            print(verify['body'][:300])

        await browser.close()

asyncio.run(main())
