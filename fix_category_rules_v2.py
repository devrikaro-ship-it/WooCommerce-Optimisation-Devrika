import asyncio
import os
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
SESSION_DIR = '/tmp/puria-session'


async def ensure_logged_in(page):
    await page.goto('https://puria.ro/wp-admin/', wait_until='domcontentloaded')
    await page.wait_for_timeout(1000)
    if 'wp-admin' in page.url and 'login' not in page.url:
        print('Session OK — already logged in')
        return
    print('Logging in...')
    await page.goto(WP_LOGIN, wait_until='networkidle')
    await page.wait_for_timeout(800)
    await page.click('#user_login')
    await page.type('#user_login', WP_USER, delay=80)
    await page.wait_for_timeout(300)
    await page.click('#user_pass')
    await page.type('#user_pass', WP_PASS, delay=80)
    await page.wait_for_timeout(400)
    await page.click('#wp-submit')
    await page.wait_for_timeout(3000)
    try:
        await page.wait_for_url('**/wp-admin/**', timeout=25000)
    except Exception:
        if 'wp-admin' not in page.url:
            raise Exception(f'Login failed: {page.url}')
    print(f'Logged in: {page.url}')


async def save_css_snippet(page, title, code):
    await page.goto(
        'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
        wait_until='networkidle'
    )
    await page.wait_for_timeout(600)
    await page.evaluate("""() => {
        for (const h of document.querySelectorAll('h3')) {
            if (h.textContent.includes('CSS')) { h.click(); return; }
        }
    }""")
    await page.wait_for_timeout(800)
    ti = await page.query_selector('input[name="wpcode_snippet_title"]')
    if ti:
        await ti.fill(title)
    await page.evaluate("""(c) => {
        const cm = document.querySelector('.CodeMirror');
        if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
        const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
        if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles:true})); }
    }""", code)
    await page.evaluate("""() => {
        const cb = document.querySelector('input[name="wpcode_active"]');
        if (cb && !cb.checked) cb.click();
    }""")
    return await page.evaluate("""async ([code, title]) => {
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
        return {status: res.status, id: m ? m[1] : null};
    }""", [code, title])


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--start-maximized'],
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.pages[0] if context.pages else await context.new_page()

        await ensure_logged_in(page)

        # 1. Deactivate old conflicting image snippets (cover vs contain conflict)
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        for sid in [248076, 248077, 248078, 248075]:
            result = await page.evaluate("""async (id) => {
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch(`/wp-json/wp/v2/wpcode_snippet/${id}`, {
                    method: 'POST',
                    headers: {'X-WP-Nonce': nonce, 'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'inactive'})
                });
                return {id, status: res.status};
            }""", sid)
            print(f'Deactivate snippet {sid}: {result}')

        # 2. Nuclear CSS: contain wins with highest specificity
        CONTAIN_CSS = """/* Puria — images contain, nuclear specificity */
html body .etheme-product-grid-item .etheme-product-grid-image {
    aspect-ratio: 1/1 !important;
    height: auto !important;
    overflow: hidden !important;
    background: #fff !important;
    display: block !important;
}
html body .etheme-product-grid-item .etheme-product-grid-image > a {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
}
html body .etheme-product-grid-item .etheme-product-grid-image img,
html body .etheme-product-grid-item .etheme-product-grid-image a img {
    object-fit: contain !important;
    object-position: center center !important;
    width: 100% !important;
    height: 100% !important;
    padding: 6px !important;
    box-sizing: border-box !important;
    transition: transform .3s ease !important;
}
html body .etheme-product-grid-item:hover .etheme-product-grid-image img {
    transform: scale(1.04) !important;
}"""

        r = await save_css_snippet(page, 'Puria — Images contain (nuclear)', CONTAIN_CSS)
        print(f'Contain CSS snippet: {r}')

        # Clear SiteGround cache via admin-ajax with correct action
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        sg_flush = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const fd = new FormData();
            fd.append('action', 'siteground_optimizer_purge_cache');
            fd.append('security', nonce);
            const res = await fetch('/wp-admin/admin-ajax.php', {method: 'POST', body: fd});
            const text = await res.text();
            return {status: res.status, text: text.substring(0, 60)};
        }""")
        print(f'SG cache flush: {sg_flush}')

        # JS nuclear: force contain via inline style (beats ANY CSS including theme inline)
        JS_CONTAIN_TITLE = 'Puria — Force contain on all product images (JS)'
        JS_CONTAIN_CODE = """// Puria: force contain on product images + MutationObserver for slider reinit
(function() {
    var SELECTOR = [
        '.etheme-product-grid-image img',
        'li.product img.attachment-woocommerce_thumbnail',
        'li.product img.attachment-shop_catalog',
        '.product-image img',
        '.woocommerce-loop-product__link img'
    ].join(',');

    function fixImg(img) {
        if (img._puriaFixed) return;
        img.style.setProperty('object-fit', 'contain', 'important');
        img.style.setProperty('object-position', 'center center', 'important');
        img.style.setProperty('width', '100%', 'important');
        img.style.setProperty('height', '100%', 'important');
        img.style.setProperty('padding', '6px', 'important');
        img.style.setProperty('box-sizing', 'border-box', 'important');
        img.style.setProperty('max-width', '100%', 'important');
        img.style.setProperty('max-height', '100%', 'important');

        var wrap = img.closest('.etheme-product-grid-image, .product-image-wrap, [class*="product-image"]');
        if (wrap) {
            wrap.style.setProperty('background', '#ffffff', 'important');
            wrap.style.setProperty('overflow', 'hidden', 'important');
            wrap.style.setProperty('display', 'flex', 'important');
            wrap.style.setProperty('align-items', 'center', 'important');
            wrap.style.setProperty('justify-content', 'center', 'important');
        }
        img._puriaFixed = true;
    }

    function forceContain() {
        document.querySelectorAll(SELECTOR).forEach(fixImg);
    }

    // MutationObserver: catches Swiper/slider DOM changes
    var obs = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            m.addedNodes.forEach(function(node) {
                if (node.nodeType !== 1) return;
                if (node.matches && node.matches('img')) fixImg(node);
                node.querySelectorAll && node.querySelectorAll('img').forEach(fixImg);
            });
            // Also re-check attributeChange on img (style reset)
            if (m.type === 'attributes' && m.target.tagName === 'IMG') {
                m.target._puriaFixed = false;
                fixImg(m.target);
            }
        });
    });
    obs.observe(document.body, {childList: true, subtree: true, attributes: true, attributeFilter: ['style']});

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceContain);
    } else {
        forceContain();
    }
    setTimeout(forceContain, 500);
    setTimeout(forceContain, 1500);
    setTimeout(forceContain, 3000);
})();"""

        await page.goto(
            'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
            wait_until='networkidle'
        )
        await page.wait_for_timeout(600)
        await page.evaluate("""() => {
            for (const h of document.querySelectorAll('h3')) {
                if (h.textContent.includes('JavaScript') || h.textContent.includes('JS')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(800)
        ti2 = await page.query_selector('input[name="wpcode_snippet_title"]')
        if ti2:
            await ti2.fill(JS_CONTAIN_TITLE)
        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles:true})); }
        }""", JS_CONTAIN_CODE)
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")
        js_r = await page.evaluate("""async ([code, title]) => {
            const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
            const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
            const fd = new FormData();
            fd.append('wpcode_snippet_title', title);
            fd.append('wpcode_snippet_type', 'js');
            fd.append('wpcode_snippet_code', code);
            fd.append('wpcode_active', '1');
            fd.append('wpcode_auto_insert', '1');
            fd.append('wpcode_auto_insert_location', 'site_wide_footer');
            fd.append('wpcode-save-snippet-nonce', nonce);
            fd.append('_wp_http_referer', httpRef);
            fd.append('button', 'publish');
            const res = await fetch(window.location.href, {method: 'POST', body: fd});
            const m = res.url.match(/snippet_id=(\d+)/);
            return {status: res.status, id: m ? m[1] : null};
        }""", [JS_CONTAIN_CODE, JS_CONTAIN_TITLE])
        print(f'JS contain snippet: {js_r}')

        # Flush SiteGround cache via UI
        print('\nFlushing SiteGround cache via UI...')
        await page.goto('https://puria.ro/wp-admin/admin.php?page=sg-cachepress', wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        # Try clicking any purge/flush button
        flushed = await page.evaluate("""async () => {
            const btns = Array.from(document.querySelectorAll('button, a, input[type=button], input[type=submit]'));
            const purge = btns.find(b => /purge|flush|clear|cache/i.test(b.textContent || b.value || ''));
            if (purge) { purge.click(); return purge.textContent || purge.value; }
            return null;
        }""")
        print(f'Purge button clicked: {flushed}')
        await page.wait_for_timeout(3000)
        # Also try the SG Optimizer URL directly
        await page.goto('https://puria.ro/wp-admin/admin.php?page=sg-cachepress&tab=supercacher', wait_until='domcontentloaded')
        await page.wait_for_timeout(1500)
        flushed2 = await page.evaluate("""async () => {
            const btns = Array.from(document.querySelectorAll('button, a, input[type=button], input[type=submit]'));
            const purge = btns.find(b => /purge|flush|clear/i.test(b.textContent || b.value || ''));
            if (purge) { purge.click(); return purge.textContent || purge.value; }
            // Try all buttons text
            return btns.slice(0,8).map(b => b.textContent.trim().substring(0,30)).join(' | ');
        }""")
        print(f'Supercacher tab: {flushed2}')
        await page.wait_for_timeout(2000)

        # Verify images on /caini/
        print('\nVerifying /caini/ images...')
        await page.goto('https://puria.ro/caini/', wait_until='domcontentloaded')
        await page.wait_for_timeout(4000)
        check = await page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll(
                '.etheme-product-grid-item .etheme-product-grid-image img'
            )).slice(0, 5);
            return imgs.map(i => ({
                fit: getComputedStyle(i).objectFit,
                inlineFit: i.style.objectFit,
                dw: Math.round(i.getBoundingClientRect().width),
                dh: Math.round(i.getBoundingClientRect().height),
                puriaFixed: i._puriaFixed || false
            }));
        }""")
        print('\n--- Images on /caini/ ---')
        for idx, img in enumerate(check):
            status = 'OK' if img['fit'] == 'contain' else 'FAIL'
            print(f'  [{idx}] {status} fit={img["fit"]} inline={img["inlineFit"]} {img["dw"]}x{img["dh"]}px fixed={img["puriaFixed"]}')

        await context.close()


asyncio.run(main())
