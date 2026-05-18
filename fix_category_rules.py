import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

SNIPPET_TITLE = 'Puria — Category page rules v3'

SNIPPET_CODE = r"""// Puria — Category page rules v3 (images/sort/breadcrumb order)
add_action('wp_head', function() {
    if (!is_archive() && !is_tax('product_cat')) return;
    echo '<style id="puria-cat-v3">
/* 1. Images: same apparent size via contain (all products fully visible) */
body .etheme-product-grid-item .etheme-product-grid-image {
    aspect-ratio: 1/1 !important;
    height: auto !important;
    background: #fff !important;
    overflow: hidden !important;
    display: block !important;
}
body .etheme-product-grid-item .etheme-product-grid-image > a {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
}
body .etheme-product-grid-item .etheme-product-grid-image img {
    object-fit: contain !important;
    object-position: center center !important;
    width: 100% !important;
    height: 100% !important;
    padding: 8px !important;
    box-sizing: border-box !important;
    transition: transform .3s ease !important;
}
body .etheme-product-grid-item:hover .etheme-product-grid-image img {
    transform: scale(1.05) !important;
}

/* 2. Sort dropdown clearly visible */
body.archive .woocommerce-ordering,
body.tax-product_cat .woocommerce-ordering {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
body.archive .woocommerce-ordering select,
body.tax-product_cat .woocommerce-ordering select {
    display: inline-block !important;
    visibility: visible !important;
    min-width: 190px !important;
    padding: 8px 32px 8px 12px !important;
    border: 2px solid #16a34a !important;
    border-radius: 8px !important;
    background: #fff url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' viewBox=\'0 0 12 12\'%3E%3Cpath fill=\'%23374151\' d=\'M6 8L1 3h10z\'/%3E%3C/svg%3E") no-repeat right 10px center !important;
    color: #111827 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    -webkit-appearance: none !important;
    appearance: none !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.08) !important;
}
body.archive .woocommerce-ordering select:focus,
body.tax-product_cat .woocommerce-ordering select:focus {
    outline: none !important;
    border-color: #15803d !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,.15) !important;
}
</style>';
}, 25);

add_action('wp_footer', function() {
    if (!is_archive() && !is_tax('product_cat')) return;
    ?>
<script id="puria-cat-v3-js">
(function() {
    function reorderBreadcrumb() {
        var bc = document.querySelector('.woocommerce-breadcrumb');
        var h1 = document.querySelector('h1.elementor-heading-title, h1.page-title, h1');
        if (!bc || !h1) return;
        var bcEl = bc.closest('.elementor-element') || bc.parentElement;
        var h1El = h1.closest('.elementor-element') || h1.parentElement;
        if (!bcEl || !h1El || bcEl === h1El) return;
        if (bcEl.parentElement !== h1El.parentElement) return;
        // If h1 appears before breadcrumb in DOM, move bc before h1
        if (h1El.compareDocumentPosition(bcEl) & Node.DOCUMENT_POSITION_FOLLOWING) {
            h1El.parentElement.insertBefore(bcEl, h1El);
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', reorderBreadcrumb);
    } else {
        reorderBreadcrumb();
    }
})();
</script>
    <?php
}, 25);"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--start-maximized']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
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
        print('Logged in OK')

        # Open new snippet form
        await page.goto(
            'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
            wait_until='networkidle'
        )
        await page.wait_for_timeout(600)

        # Select PHP type
        await page.evaluate("""() => {
            for (const h of document.querySelectorAll('h3, button, .wpcode-type-card')) {
                if (h.textContent && h.textContent.includes('PHP')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(800)

        # Fill title
        ti = await page.query_selector('input[name="wpcode_snippet_title"]')
        if ti:
            await ti.fill(SNIPPET_TITLE)
            print(f'Title set: {SNIPPET_TITLE}')
        else:
            print('WARNING: title input not found')

        # Set code via CodeMirror
        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return 'cm'; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles: true})); return 'ta'; }
            return 'none';
        }""", SNIPPET_CODE)
        print('Code set')

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
            return {status: res.status, id: m ? m[1] : null, url: res.url};
        }""", [SNIPPET_CODE, SNIPPET_TITLE])

        print(f'Snippet saved: {result}')

        # Verify on category page
        await page.wait_for_timeout(1500)
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/pisici/hrana-uscata/', wait_until='domcontentloaded')
        await page2.wait_for_timeout(2500)

        checks = await page2.evaluate("""() => {
            // Breadcrumb / H1 order
            const bc = document.querySelector('.woocommerce-breadcrumb');
            const h1 = document.querySelector('h1');
            const bcY = bc ? bc.getBoundingClientRect().top : -1;
            const h1Y = h1 ? h1.getBoundingClientRect().top : -1;
            const bcAboveH1 = bcY < h1Y;

            // Image sizes
            const imgs = Array.from(document.querySelectorAll('.etheme-product-grid-item .etheme-product-grid-image img'));
            const imgSizes = imgs.slice(0, 6).map(img => ({
                w: img.naturalWidth,
                h: img.naturalHeight,
                dw: img.getBoundingClientRect().width,
                dh: img.getBoundingClientRect().height,
                fit: getComputedStyle(img).objectFit
            }));

            // Sort
            const sort = document.querySelector('.woocommerce-ordering select');
            const sortVis = sort ? {
                display: getComputedStyle(sort).display,
                border: getComputedStyle(sort).border,
                width: getComputedStyle(sort).width
            } : null;

            // Style tag
            const styleTag = !!document.querySelector('#puria-cat-v3');

            return { bcY, h1Y, bcAboveH1, imgSizes, sortVis, styleTag };
        }""")

        print(f'\nStyle tag #puria-cat-v3: {checks["styleTag"]}')
        print(f'Breadcrumb Y={checks["bcY"]:.0f}, H1 Y={checks["h1Y"]:.0f}')
        print(f'Breadcrumb above H1: {checks["bcAboveH1"]} (want: True)')
        print(f'Sort select: {checks["sortVis"]}')
        print(f'\nImage display sizes:')
        for i, img in enumerate(checks['imgSizes']):
            print(f'  [{i}] displayed {img["dw"]:.0f}x{img["dh"]:.0f}px | natural {img["w"]}x{img["h"]} | fit={img["fit"]}')

        await browser.close()


asyncio.run(main())
