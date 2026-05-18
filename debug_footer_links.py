import asyncio, json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
POST_ID = 40380

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
        print('Logged in')

        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        raw_data = await page.evaluate("""async (postId) => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch(`/wp-json/wp/v2/elementor_library/${postId}?context=edit`, {
                headers: {'X-WP-Nonce': nonce}
            });
            const data = await res.json();
            return data.meta?._elementor_data || '';
        }""", POST_ID)

        # Search for pasari or promotii
        for term in ['pasari', 'promotii', 'rozatoare', 'oferte', 'puria.ro\\/']:
            indices = [m.start() for m in re.finditer(term, raw_data, re.IGNORECASE)]
            if indices:
                print(f'\nTerm "{term}" found at positions: {indices}')
                for idx in indices[:3]:
                    snippet = raw_data[max(0,idx-50):idx+100]
                    print(f'  ...{snippet}...')
            else:
                print(f'Term "{term}": NOT found')

        # Save full data for offline inspection
        with open('/tmp/elementor_footer_data.json', 'w') as f:
            f.write(raw_data)
        print(f'\nFull data saved to /tmp/elementor_footer_data.json ({len(raw_data)} chars)')

        await browser.close()

asyncio.run(main())
