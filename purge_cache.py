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
        print('Logged in')

        # 1. Purge SiteGround SG Optimizer cache via AJAX
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        sg_result = await page.evaluate("""async () => {
            const fd = new FormData();
            fd.append('action', 'sg_cachepress_purge_cache');
            fd.append('nonce', window.SitegroundPageCacheData?.nonce ||
                               window.sitegroundCache?.nonce || '');
            const res = await fetch('/wp-admin/admin-ajax.php', {method: 'POST', body: fd});
            return {status: res.status, text: (await res.text()).substring(0, 200)};
        }""")
        print(f'SG cache purge: {sg_result}')

        # 2. Purge Elementor cache via admin-ajax
        el_result = await page.evaluate("""async () => {
            const fd = new FormData();
            fd.append('action', 'elementor_ajax');
            fd.append('actions', JSON.stringify({'regenerate_assets': {}}));
            const nonce = document.cookie.match(/wp-settings-time/);
            const res = await fetch('/wp-admin/admin-ajax.php', {method: 'POST', body: fd});
            return {status: res.status, text: (await res.text()).substring(0, 200)};
        }""")
        print(f'Elementor cache: {el_result}')

        # 3. Use SG admin bar purge link
        await page.goto('https://puria.ro/wp-admin/admin.php?page=sg-cachepress', wait_until='networkidle')
        purge_btn = await page.query_selector('a[href*="purge"], button[id*="purge"], input[value*="Purge"]')
        if purge_btn:
            await purge_btn.click()
            await page.wait_for_timeout(2000)
            print('Clicked SG purge button')
        else:
            # Try direct URL purge
            await page.goto('https://puria.ro/wp-admin/admin.php?page=sg-cachepress&action=purge-all', wait_until='networkidle')
            print(f'Purge URL: {page.url}')

        # 4. Navigate to homepage with cache-busting header
        await page.goto('https://puria.ro/wp-admin/post.php?post=40380&action=elementor', wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        print(f'Elementor editor URL: {page.url}')

        # 5. Verify after cache purge
        await page.goto('https://puria.ro/?nocache=1', wait_until='domcontentloaded')
        links = await page.evaluate("""() => {
            const all = document.querySelectorAll('a[href]');
            return Array.from(all)
                .map(a => a.getAttribute('href'))
                .filter(h => h.includes('pasari') || h.includes('promotii'));
        }""")
        print(f'Pasari/Promotii links on homepage: {links}')

        await browser.close()

asyncio.run(main())
