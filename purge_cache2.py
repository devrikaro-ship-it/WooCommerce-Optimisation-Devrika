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

        # Try SiteGround SG Optimizer cache purge page
        await page.goto('https://puria.ro/wp-admin/admin.php?page=sg-cachepress', wait_until='networkidle')
        await page.wait_for_timeout(1000)
        page_content = await page.content()
        print(f'SG Optimizer page: {len(page_content)} chars')

        # Find and click purge all button
        purge = await page.evaluate("""() => {
            const btns = document.querySelectorAll('button, input[type=submit], a');
            const found = [];
            for (const b of btns) {
                const t = (b.textContent || b.value || b.href || '').toLowerCase();
                if (t.includes('purge') || t.includes('clear') || t.includes('flush')) {
                    found.push({tag: b.tagName, text: (b.textContent||b.value||'').substring(0,60), href: b.href||''});
                }
            }
            return found;
        }""")
        print(f'Purge buttons found: {purge}')

        # Also try Elementor Tools page
        await page.goto('https://puria.ro/wp-admin/admin.php?page=elementor-tools', wait_until='networkidle')
        await page.wait_for_timeout(1000)
        el_tools = await page.evaluate("""() => {
            const btns = document.querySelectorAll('button, input[type=submit]');
            return Array.from(btns).map(b => ({tag: b.tagName, text: (b.textContent||b.value||'').substring(0,80)}));
        }""")
        print(f'Elementor Tools buttons: {el_tools[:10]}')

        # Click "Regenerate Files & Data"
        clicked = await page.evaluate("""() => {
            for (const btn of document.querySelectorAll('button')) {
                if (btn.textContent.includes('Regenerate') || btn.textContent.includes('Clear Cache')) {
                    btn.click();
                    return btn.textContent.substring(0,60);
                }
            }
            return null;
        }""")
        print(f'Clicked: {clicked}')
        await page.wait_for_timeout(3000)

        # Purge SG cache via WP Cron / direct endpoint
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        # Get proper nonce from admin bar
        purge_result = await page.evaluate("""async () => {
            // Try SG purge via admin ajax with proper nonce discovery
            const adminBar = document.querySelector('#wp-admin-bar-sg-cachepress-purge-cache a, #wp-admin-bar-sgo_cache_purge a');
            if (adminBar) {
                const href = adminBar.href;
                const res = await fetch(href);
                return {method: 'admin_bar', status: res.status, url: href};
            }

            // Try wp_create_nonce style
            const allLinks = document.querySelectorAll('a[href]');
            for (const a of allLinks) {
                if (a.href.includes('sg-cachepress') || a.href.includes('purge')) {
                    return {found_link: a.href};
                }
            }
            return {error: 'no purge link found'};
        }""")
        print(f'Purge via admin bar: {purge_result}')

        # Check if there's a nonce in the page for SG
        nonces = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            for (const s of scripts) {
                if (s.textContent.includes('nonce') && s.textContent.includes('sg')) {
                    return s.textContent.substring(0, 500);
                }
            }
            return null;
        }""")
        if nonces:
            print(f'SG nonce script: {nonces[:300]}')

        await browser.close()

asyncio.run(main())
