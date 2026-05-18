import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

GENERAL_CATEGORY = 'Animals & Pet Supplies > Pet Food'
BRAND_CAT_IDS = list(range(10862, 10889))  # 10862-10888

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

        # GET current mapping
        get_res = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")

        data = json.loads(get_res['body'])
        feed_data = data.get('data', {})
        current_map = feed_data.get('wf_cmapping-2', {}).get('cmapping', {})
        print(f'Current mapping: {len(current_map)} categories')

        # Update brand categories to general category
        updated_map = dict(current_map)
        for cat_id in BRAND_CAT_IDS:
            updated_map[str(cat_id)] = GENERAL_CATEGORY

        print(f'Setting {len(BRAND_CAT_IDS)} brand categories -> "{GENERAL_CATEGORY}"')

        # PUT updated mapping
        put_res = await page.evaluate("""async (mapping) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping', {
                method: 'PUT',
                headers: {'X-WP-Nonce': nonce, 'Content-Type': 'application/json'},
                body: JSON.stringify({feed_id: 2, mapping: mapping})
            });
            return {status: res.status, body: await res.text()};
        }""", updated_map)

        print(f'PUT status: {put_res["status"]}')

        # Verify
        verify_res = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")

        verify_data = json.loads(verify_res['body'])
        verify_map = verify_data.get('data', {}).get('wf_cmapping-2', {}).get('cmapping', {})

        print('\n=== Verificare brand categories ===')
        for cat_id in BRAND_CAT_IDS:
            val = verify_map.get(str(cat_id), '(not set)')
            status = '✅' if val == GENERAL_CATEGORY else '❌'
            print(f'  {status} [{cat_id}]: {val}')

        print('\n=== Type-based categories (trebuie neschimbate) ===')
        type_cats = {'10836': 'Hrana Uscata Caini', '10837': 'Hrana Umeda Caini',
                     '10845': 'Hrana Uscata Pisici', '10846': 'Hrana Umeda Pisici',
                     '10840': 'Recompense Caini', '10849': 'Recompense Pisici'}
        for cat_id, name in type_cats.items():
            val = verify_map.get(cat_id, '(not set)')
            print(f'  [{cat_id}] {name}: {val}')

        await browser.close()

asyncio.run(main())
