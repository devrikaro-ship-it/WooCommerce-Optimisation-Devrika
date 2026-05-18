import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

# CSS fara ghilimele in url() ca sa nu rupa PHP single-quoted string
CSS_CODE = r"""section.elementor-element-77d01b66{background-color:#141928!important;padding-top:60px!important;padding-bottom:0!important}.elementor-element-77d01b66 p,.elementor-element-77d01b66 li,.elementor-element-77d01b66 span:not(.et-icon):not(.screen-reader-text){color:rgba(255,255,255,.60)!important}.elementor-element-77d01b66 .elementor-heading-title{color:#fff!important;font-size:11px!important;font-weight:700!important;letter-spacing:2px!important;text-transform:uppercase!important;padding-bottom:14px!important;margin-bottom:20px!important;position:relative!important}.elementor-element-77d01b66 .elementor-heading-title::after{content:""!important;position:absolute!important;bottom:0!important;left:0!important;width:28px!important;height:2px!important;background:#5b8def!important;display:block!important}.elementor-element-77d01b66 a{color:rgba(255,255,255,.60)!important;text-decoration:none!important}.elementor-element-77d01b66 a:hover{color:#fff!important}.elementor-element-77d01b66 .etheme-icon-list-item-text{color:rgba(255,255,255,.60)!important;font-size:13px!important}.elementor-element-77d01b66 .et-icon{color:rgba(255,255,255,.35)!important;font-size:14px!important}.elementor-element-a90433d .follow-whatsapp{display:inline-flex!important;align-items:center!important;gap:8px!important;color:rgba(255,255,255,.60)!important;font-size:13px!important;padding:0!important;background:none!important;border:none!important}.elementor-element-a90433d .follow-whatsapp:hover{color:#fff!important}.elementor-element-a90433d .screen-reader-text{position:static!important;width:auto!important;height:auto!important;clip:auto!important;overflow:visible!important;clip-path:none!important}section.elementor-element-17d34aa8{border-top:1px solid rgba(255,255,255,.08)!important;padding-top:20px!important;padding-bottom:20px!important;margin-top:40px!important}.elementor-element-6d45af6,.elementor-element-6d45af6 p,.elementor-element-6d45af6 a{color:rgba(255,255,255,.30)!important;font-size:12px!important}.elementor-element-9d0b20e img{background:#fff;border-radius:6px;padding:4px 8px;height:36px!important;width:auto!important}.elementor-element-bb3a42b img,.elementor-element-15c135a img{height:36px!important;width:auto!important;opacity:.85!important}.footerImages .elementor-widget-wrap{display:flex!important;align-items:center!important;justify-content:flex-end!important;gap:12px!important;flex-wrap:wrap!important}.footerImages .elementor-widget{flex:0 0 auto!important}.elementor-element-2e938dde>.elementor-widget-wrap::before{content:""!important;display:block!important;width:120px!important;height:42px!important;margin-bottom:28px!important;background:url(https://puria.ro/wp-content/uploads/2025/04/puria.png) no-repeat left center/contain!important;filter:brightness(0) invert(1)!important}"""

# PHP snippet folosind heredoc — nu are probleme cu ghilimele
SNIPPET_CODE = """// Puria Dark Footer CSS
add_action('wp_head', function() {
    echo '<style id="puria-dark-footer">""" + CSS_CODE + """</style>';
}, 99);"""


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

        # First disable/delete the broken snippet 248051 if it exists
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        del_result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/wpcode_snippet/248051?force=true', {
                method: 'DELETE',
                headers: {'X-WP-Nonce': nonce}
            });
            return res.status;
        }""")
        print(f'Delete 248051: {del_result}')

        # Create new snippet
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
        await page.wait_for_timeout(500)

        # Select PHP type
        await page.evaluate("""() => {
            for (const h of document.querySelectorAll('h3')) {
                if (h.textContent.includes('PHP')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(800)

        title = 'Puria — Dark Footer CSS'
        title_inp = await page.query_selector('input[name="wpcode_snippet_title"]')
        if title_inp:
            await title_inp.fill(title)

        # Set code
        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input',{bubbles:true})); }
        }""", SNIPPET_CODE)

        # Activate
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")

        # Save via FormData POST
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
        }""", [SNIPPET_CODE, title])

        print(f'Snippet saved: ID={result["id"]}')

        # Verify on frontend
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/', wait_until='domcontentloaded')
        html = await page2.content()

        has_style = 'puria-dark-footer' in html
        has_color = '#141928' in html or '141928' in html
        print(f'Style tag on homepage: {has_style}')
        print(f'Dark color present: {has_color}')

        await browser.close()

asyncio.run(main())
