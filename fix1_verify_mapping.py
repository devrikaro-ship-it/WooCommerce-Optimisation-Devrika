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

        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")

        data = json.loads(result['body'])

        # Find the actual cmapping for feed 2
        # Structure: {status, data: {wf_cmapping_2: {cmapping: {...}}, ...}, extra}
        feed_data = data.get('data', {})

        # Try wf_cmapping-2 first (hyphen), then wf_cmapping_2 (underscore)
        mapping_key = None
        for key in ['wf_cmapping-2', 'wf_cmapping_2']:
            if key in feed_data:
                mapping_key = key
                break

        print(f'Mapping key found: {mapping_key}')
        print(f'All keys in data: {list(feed_data.keys())}')

        if mapping_key:
            cmapping = feed_data[mapping_key].get('cmapping', {})
            print(f'\nTotal categories mapped: {len(cmapping)}')
            print('\n=== Key category mappings (type-based) ===')
            key_cats = {
                '10836': 'Hrana Uscata Caini',
                '10837': 'Hrana Umeda Caini',
                '10838': 'Snackuri Caini (subcategorie)',
                '10840': 'Recompense Caini',
                '10841': 'Suplimente Caini',
                '10842': 'Cosmetica Caini',
                '10845': 'Hrana Uscata Pisici',
                '10846': 'Hrana Umeda Pisici',
                '10849': 'Recompense Pisici',
                '10852': 'Litiera Pisici',
            }
            for cat_id, name in key_cats.items():
                val = cmapping.get(cat_id, '(not set)')
                print(f'  [{cat_id}] {name}: {val}')

            print('\n=== Brand category mappings (IDs 10862-10888) ===')
            brand_cats = {k: v for k, v in cmapping.items() if int(k) >= 10862 and int(k) <= 10888}
            for cat_id, val in sorted(brand_cats.items(), key=lambda x: int(x[0])):
                print(f'  [{cat_id}]: {val}')

        await browser.close()

asyncio.run(main())
