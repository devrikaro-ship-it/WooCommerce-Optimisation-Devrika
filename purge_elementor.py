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

        # Elementor Tools page
        await page.goto('https://puria.ro/wp-admin/admin.php?page=elementor-tools', wait_until='networkidle')
        await page.wait_for_timeout(1000)

        # Click "Șterge fișierele și datele" button
        result = await page.evaluate("""async () => {
            for (const btn of document.querySelectorAll('button')) {
                if (btn.textContent.includes('terge fi') || btn.textContent.includes('terge fi')) {
                    btn.click();
                    return {clicked: btn.textContent.trim()};
                }
            }
            // Also try data-action attribute
            for (const btn of document.querySelectorAll('[data-elementor-action]')) {
                return {found_action: btn.getAttribute('data-elementor-action'), text: btn.textContent.trim()};
            }
            return {error: 'button not found'};
        }""")
        print(f'Elementor flush: {result}')
        await page.wait_for_timeout(3000)

        # Also try elementor AJAX flush directly
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        flush = await page.evaluate("""async () => {
            const nonce = window.elementorCommon?.config?.ajax?.nonce || '';
            const adminAjaxNonce = document.querySelector('#_wpnonce')?.value || '';

            // Try Elementor Ajax flush
            const fd = new FormData();
            fd.append('action', 'elementor_ajax');
            fd.append('actions', JSON.stringify({
                'flush_css': {nonce: nonce}
            }));
            const res = await fetch('/wp-admin/admin-ajax.php', {method: 'POST', body: fd});
            const text = await res.text();
            return {status: res.status, resp: text.substring(0, 300)};
        }""")
        print(f'AJAX flush CSS: {flush}')

        # SG Optimizer: find nonce via localized script data
        sg_purge = await page.evaluate("""async () => {
            // Look for SG nonce in window globals
            const sgData = window.SitegroundPageCacheData || window.sgCacheData || window.sg_optimizer || {};
            const nonce = sgData.nonce || sgData.purge_nonce || '';

            if (!nonce) {
                // Try to find it in scripts
                const scripts = document.scripts;
                for (let i = 0; i < scripts.length; i++) {
                    const src = scripts[i].src;
                    if (src && src.includes('sg')) return {found_sg_script: src};
                }
                return {error: 'no SG nonce', globals: Object.keys(window).filter(k => k.toLowerCase().includes('sg') || k.toLowerCase().includes('cache')).join(',')};
            }

            const fd = new FormData();
            fd.append('action', 'sg_cachepress_purge_cache');
            fd.append('nonce', nonce);
            const res = await fetch('/wp-admin/admin-ajax.php', {method: 'POST', body: fd});
            return {status: res.status, text: (await res.text()).substring(0, 100)};
        }""")
        print(f'SG purge: {sg_purge}')

        # Verify final state
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/', wait_until='domcontentloaded')
        footer_links = await page2.evaluate("""() => {
            const footer = document.querySelector('section.elementor-element-77d01b66');
            if (!footer) return [];
            return Array.from(footer.querySelectorAll('a[href]'))
                .map(a => a.getAttribute('href'))
                .filter(h => h.includes('pasari') || h.includes('promotii'));
        }""")
        print(f'Footer pasari/promotii links: {footer_links}')

        ok = all('/pasari-si-rozatoare/' not in l and '/promotii-si-oferte/' not in l for l in footer_links)
        print(f'All links correct: {ok}')

        await browser.close()

asyncio.run(main())
