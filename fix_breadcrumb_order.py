import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

SNIPPET_TITLE = 'Puria — Breadcrumb above H1 (category pages)'

# The breadcrumb widget has Elementor ID elementor-element-9b27421
# It's in the same .elementor-widget-wrap flex container as H1 (elementor-element-96ea11e)
# Setting order: -1 moves it before H1
SNIPPET_CODE = """/* Puria — Breadcrumb above H1 on archive/category pages */
/* elementor-element-9b27421 = Rank Math breadcrumb widget */
/* elementor-element-96ea11e = H1 heading widget */
/* Both share same .elementor-widget-wrap flex container */

body.archive .elementor-element-9b27421,
body.tax-product_cat .elementor-element-9b27421 {
    order: -1 !important;
}"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # Login
        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.wait_for_timeout(800)
        await page.click('#user_login')
        await page.type('#user_login', WP_USER, delay=80)
        await page.wait_for_timeout(300)
        await page.click('#user_pass')
        await page.type('#user_pass', WP_PASS, delay=80)
        await page.wait_for_timeout(400)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=20000)
        print('Logged in')

        await page.goto(
            'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
            wait_until='networkidle'
        )
        await page.wait_for_timeout(600)

        # Select CSS
        await page.evaluate("""() => {
            const h3s = document.querySelectorAll('h3');
            for (const h of h3s) {
                if (h.textContent.includes('CSS')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(800)

        ti = await page.query_selector('input[name="wpcode_snippet_title"]')
        if ti:
            await ti.fill(SNIPPET_TITLE)

        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles:true})); }
        }""", SNIPPET_CODE)

        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")

        result = await page.evaluate("""async ([code, title]) => {
            const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
            const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
            const fd = new FormData();
            fd.append('wpcode_snippet_title', title);
            fd.append('wpcode_snippet_type', 'css');
            fd.append('wpcode_snippet_code', code);
            fd.append('wpcode_active', '1');
            fd.append('wpcode_auto_insert', '1');
            fd.append('wpcode_auto_insert_location', 'site_wide_footer');
            fd.append('wpcode-save-snippet-nonce', nonce);
            fd.append('_wp_http_referer', httpRef);
            fd.append('button', 'publish');
            const res = await fetch(window.location.href, {method: 'POST', body: fd});
            const m = res.url.match(/snippet_id=(\d+)/);
            return {status: res.status, id: m ? m[1] : null, url: res.url};
        }""", [SNIPPET_CODE, SNIPPET_TITLE])
        print(f'CSS snippet: {result}')

        # Verify
        await page.wait_for_timeout(2000)
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/caini/', wait_until='domcontentloaded')
        await page2.wait_for_timeout(3000)

        check = await page2.evaluate("""() => {
            const bc = document.querySelector('.rank-math-breadcrumb');
            const h1 = document.querySelector('h1');
            const bcY = bc ? Math.round(bc.getBoundingClientRect().top) : -1;
            const h1Y = h1 ? Math.round(h1.getBoundingClientRect().top) : -1;

            const bcWidget = bc ? bc.closest('.elementor-element') : null;
            const bcOrder = bcWidget ? getComputedStyle(bcWidget).order : 'n/a';

            const sortSelect = document.querySelector('select.orderby, select[name="orderby"]');
            const sortBorder = sortSelect ? getComputedStyle(sortSelect).border.substring(0, 50) : 'not found';

            const imgs = Array.from(document.querySelectorAll(
                '.etheme-product-grid-item .etheme-product-grid-image img'
            )).slice(0, 3);

            return {
                bcY, h1Y,
                bcAboveH1: bcY < h1Y && bcY >= 0,
                bcOrder,
                sortBorder,
                imgs: imgs.map(i => ({
                    fit: getComputedStyle(i).objectFit,
                    dw: Math.round(i.getBoundingClientRect().width),
                    dh: Math.round(i.getBoundingClientRect().height)
                }))
            };
        }""")

        print(f'\n--- /caini/ verification ---')
        print(f'Breadcrumb Y={check["bcY"]}, H1 Y={check["h1Y"]}')
        print(f'Breadcrumb above H1: {check["bcAboveH1"]} (want: True)')
        print(f'Breadcrumb widget order: {check["bcOrder"]}')
        print(f'Sort border: {check["sortBorder"]}')
        print(f'Images:')
        for i, img in enumerate(check['imgs']):
            print(f'  [{i}] {img["dw"]}x{img["dh"]}px fit={img["fit"]}')

        await browser.close()


asyncio.run(main())
