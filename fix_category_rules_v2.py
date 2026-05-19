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


async def deactivate_snippet(page, snippet_id):
    url = f'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id={snippet_id}'
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(600)
        result = await page.evaluate("""async () => {
            const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value;
            if (!nonce) return {error: 'no nonce - session expired?', url: window.location.href};
            const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
            const title = document.querySelector('input[name="wpcode_snippet_title"]')?.value || '';
            const cm = document.querySelector('.CodeMirror');
            const code = cm?.CodeMirror ? cm.CodeMirror.getValue() :
                (document.querySelector('textarea[name="wpcode_snippet_code"]')?.value || '');
            let snipType = 'css';
            for (const inp of document.querySelectorAll('input[name="wpcode_snippet_type"]')) {
                if (inp.checked) { snipType = inp.value; break; }
            }
            const fd = new FormData();
            fd.append('wpcode_snippet_title', title);
            fd.append('wpcode_snippet_type', snipType);
            fd.append('wpcode_snippet_code', code);
            fd.append('wpcode_auto_insert', '0');
            fd.append('wpcode_auto_insert_location', 'site_wide_footer');
            fd.append('wpcode-save-snippet-nonce', nonce);
            fd.append('_wp_http_referer', httpRef);
            fd.append('button', 'publish');
            const res = await fetch(window.location.href, {method: 'POST', body: fd});
            return {status: res.status, url: res.url.substring(0, 80)};
        }""")
        print(f'[{snippet_id}] deactivated: {result}')
        return result
    except Exception as e:
        print(f'[{snippet_id}] ERROR: {e}')
        return None


async def activate_snippet(page, snippet_id):
    url = f'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id={snippet_id}'
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=25000)
        await page.wait_for_timeout(600)
        result = await page.evaluate("""async () => {
            const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value;
            if (!nonce) return {error: 'no nonce', url: window.location.href};
            const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
            const title = document.querySelector('input[name="wpcode_snippet_title"]')?.value || '';
            const cm = document.querySelector('.CodeMirror');
            const code = cm?.CodeMirror ? cm.CodeMirror.getValue() :
                (document.querySelector('textarea[name="wpcode_snippet_code"]')?.value || '');
            let snipType = 'css';
            for (const inp of document.querySelectorAll('input[name="wpcode_snippet_type"]')) {
                if (inp.checked) { snipType = inp.value; break; }
            }
            const fd = new FormData();
            fd.append('wpcode_snippet_title', title);
            fd.append('wpcode_snippet_type', snipType);
            fd.append('wpcode_snippet_code', code);
            fd.append('wpcode_active', '1');
            fd.append('wpcode_auto_insert', '1');
            fd.append('wpcode_auto_insert_location', 'site_wide_footer');
            fd.append('wpcode-save-snippet-nonce', nonce);
            fd.append('_wp_http_referer', httpRef);
            fd.append('button', 'publish');
            const res = await fetch(window.location.href, {method: 'POST', body: fd});
            return {status: res.status, url: res.url.substring(0, 80)};
        }""")
        print(f'[{snippet_id}] activated: {result}')
        return result
    except Exception as e:
        print(f'[{snippet_id}] ERROR: {e}')
        return None


async def main():
    import glob as _glob, os as _os
    for f in _glob.glob(f'{SESSION_DIR}/Singleton*'):
        try: _os.remove(f)
        except: pass

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.pages[0] if context.pages else await context.new_page()

        await ensure_logged_in(page)

        # SiteGround cache flush
        print('Flushing SiteGround cache...')

        # Extract SG-specific nonce from admin page scripts
        await page.goto('https://puria.ro/wp-admin/', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(1000)
        sg_data = await page.evaluate("""() => {
            // SG Optimizer injects window variable with nonce
            if (window.SiteGroundOptimizer) return JSON.stringify(window.SiteGroundOptimizer);
            if (window.sg_optimizer) return JSON.stringify(window.sg_optimizer);
            if (window.sgCachePress) return JSON.stringify(window.sgCachePress);
            // Scan inline scripts for nonce
            for (const s of document.querySelectorAll('script:not([src])')) {
                const t = s.textContent;
                if (t.includes('SiteGroundOptimizer') || t.includes('sg_cachepress') || t.includes('sg_optimizer')) {
                    return t.substring(0, 500);
                }
            }
            return 'not found';
        }""")
        print(f'SG vars: {sg_data[:300]}')

        # Try with SG nonce extracted, or use admin bar link
        flush_result = await page.evaluate("""async () => {
            // Method: click WP toolbar cache flush link
            const toolbarLinks = Array.from(document.querySelectorAll('#wpadminbar a, #wpadminbar button'));
            const cacheLink = toolbarLinks.find(el => /cache|purge|flush/i.test(el.textContent + (el.href||'')));
            if (cacheLink) {
                if (cacheLink.href && cacheLink.href.includes('flush')) {
                    const r = await fetch(cacheLink.href);
                    return {method: 'toolbar_link', status: r.status, url: cacheLink.href.substring(0,80)};
                }
                cacheLink.click();
                return {method: 'toolbar_click', text: cacheLink.textContent.trim()};
            }
            // Dump toolbar links for debugging
            return {method: 'none', toolbar: toolbarLinks.slice(0,15).map(l => l.textContent.trim().substring(0,20) + '|' + (l.href||'').substring(30,60))};
        }""")
        import json
        print(f'Flush attempt: {json.dumps(flush_result)}')

        await context.close()


asyncio.run(main())
