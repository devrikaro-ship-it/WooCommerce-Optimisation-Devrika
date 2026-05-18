import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

CODE = """// Fix #16 - Meta description Despre Noi
add_filter('rank_math/frontend/description', function($desc) {
    if (!is_page('despre-noi')) return $desc;
    return 'Puria — magazin online cu hrana premium pentru caini si pisici. Branduri selectate: MAC\\'s, Natural Greatness, Terra Canis. Livrare gratuita peste 450 RON.';
});"""

async def create_snippet(page, title, code):
    await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
    await page.wait_for_timeout(500)
    await page.evaluate("""() => { for (const h of document.querySelectorAll('h3')) { if (h.textContent.includes('PHP')) { h.click(); return; } } }""")
    await page.wait_for_timeout(800)
    ti = await page.query_selector('input[name="wpcode_snippet_title"]')
    if ti: await ti.fill(title)
    await page.evaluate("""(c) => { const cm = document.querySelector('.CodeMirror'); if (cm?.CodeMirror) cm.CodeMirror.setValue(c); }""", code)
    await page.evaluate("""() => { const cb = document.querySelector('input[name="wpcode_active"]'); if (cb && !cb.checked) cb.click(); }""")
    result = await page.evaluate("""async ([code, title]) => {
        const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
        const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
        const fd = new FormData();
        fd.append('wpcode_snippet_title', title);
        fd.append('wpcode_snippet_type', 'php');
        fd.append('wpcode_snippet_code', code);
        fd.append('wpcode_active', '1');
        fd.append('wpcode_auto_insert', '1');
        fd.append('wpcode_auto_insert_location', 'everywhere');
        fd.append('wpcode-save-snippet-nonce', nonce);
        fd.append('_wp_http_referer', httpRef);
        fd.append('button', 'publish');
        const res = await fetch(window.location.href, {method: 'POST', body: fd});
        const m = res.url.match(/snippet_id=(\d+)/);
        return {url: res.url, id: m ? m[1] : null};
    }""", [code, title])
    print(f'Snippet "{title}": ID={result["id"]}')
    return result["id"]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)

        await create_snippet(page, 'Fix #16 - Meta description Despre Noi', CODE)

        # Verify
        import re
        check = await page.evaluate("""async () => {
            const res = await fetch('/despre-noi/', {cache: 'no-store'});
            const html = await res.text();
            const m = html.match(/name="description"[^>]+content="([^"]+)"/);
            return m ? m[1] : 'not found';
        }""")
        print(f'Meta desc live: {check[:160]}')
        await browser.close()

asyncio.run(main())
