import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

CSS_CODE = """/* ===== PURIA — DARK FOOTER ===== */

/* Background principal */
section.elementor-element-77d01b66 {
    background-color: #141928 !important;
    padding-top: 60px !important;
    padding-bottom: 0 !important;
}

/* Tot textul din footer */
.elementor-element-77d01b66 p,
.elementor-element-77d01b66 li,
.elementor-element-77d01b66 span:not(.et-icon):not(.screen-reader-text) {
    color: rgba(255,255,255,0.60) !important;
}

/* Headings coloane */
.elementor-element-77d01b66 .elementor-heading-title {
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding-bottom: 14px !important;
    margin-bottom: 20px !important;
    position: relative !important;
}
.elementor-element-77d01b66 .elementor-heading-title::after {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 28px !important;
    height: 2px !important;
    background: #5b8def !important;
    display: block !important;
}

/* Linkuri */
.elementor-element-77d01b66 a {
    color: rgba(255,255,255,0.60) !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}
.elementor-element-77d01b66 a:hover {
    color: #ffffff !important;
}

/* Icon list — adresa, telefon, email */
.elementor-element-77d01b66 .etheme-icon-list-item-text {
    color: rgba(255,255,255,0.60) !important;
    font-size: 13px !important;
}
.elementor-element-77d01b66 .et-icon {
    color: rgba(255,255,255,0.35) !important;
    font-size: 14px !important;
}

/* WhatsApp button — scoate din screen-reader */
.elementor-element-a90433d .follow-whatsapp {
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    color: rgba(255,255,255,0.60) !important;
    font-size: 13px !important;
    padding: 0 !important;
    background: none !important;
    border: none !important;
}
.elementor-element-a90433d .follow-whatsapp:hover {
    color: #ffffff !important;
}
.elementor-element-a90433d .follow-whatsapp .et-icon {
    font-size: 16px !important;
    color: rgba(255,255,255,0.35) !important;
}
.elementor-element-a90433d .screen-reader-text {
    position: static !important;
    width: auto !important;
    height: auto !important;
    clip: auto !important;
    overflow: visible !important;
    clip-path: none !important;
}

/* Bara de jos — separator */
section.elementor-element-17d34aa8 {
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    padding-top: 20px !important;
    padding-bottom: 20px !important;
    margin-top: 40px !important;
}

/* Copyright */
.elementor-element-6d45af6,
.elementor-element-6d45af6 p,
.elementor-element-6d45af6 a {
    color: rgba(255,255,255,0.30) !important;
    font-size: 12px !important;
}
.elementor-element-6d45af6 a:hover {
    color: rgba(255,255,255,0.60) !important;
}

/* Badges — Netopia cu bg alb rotunjit */
.elementor-element-9d0b20e img {
    background: #ffffff;
    border-radius: 6px;
    padding: 4px 8px;
    height: 36px !important;
    width: auto !important;
}

/* ANPC badges — micsorate uniform */
.elementor-element-bb3a42b img,
.elementor-element-15c135a img {
    height: 36px !important;
    width: auto !important;
    opacity: 0.85 !important;
}

/* Badges container — aliniere verticala centrat */
.elementor-element-af3f10e .elementor-widget-container,
.footerImages .elementor-widget-wrap {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 12px !important;
    flex-wrap: wrap !important;
}
.footerImages .elementor-widget {
    flex: 0 0 auto !important;
}

/* Logo deasupra primei coloane */
.elementor-element-2e938dde > .elementor-widget-wrap::before {
    content: '' !important;
    display: block !important;
    width: 120px !important;
    height: 42px !important;
    margin-bottom: 28px !important;
    background: url('https://puria.ro/wp-content/uploads/2025/04/puria.png') no-repeat left center / contain !important;
    filter: brightness(0) invert(1) !important;
}"""

SNIPPET_CODE = f"""// Fix Footer Dark — CSS dark footer puria.ro
add_action('wp_head', function() {{
    echo '<style id="puria-dark-footer">
{CSS_CODE}
    </style>';
}}, 99);"""

async def create_snippet(page, title, code):
    await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
    await page.wait_for_timeout(500)

    # Select CSS type
    await page.evaluate("""() => {
        for (const h of document.querySelectorAll('h3')) {
            if (h.textContent.includes('CSS')) { h.click(); return; }
        }
        // Fallback: try PHP
        for (const h of document.querySelectorAll('h3')) {
            if (h.textContent.includes('PHP')) { h.click(); return; }
        }
    }""")
    await page.wait_for_timeout(800)

    title_inp = await page.query_selector('input[name="wpcode_snippet_title"]')
    if title_inp:
        await title_inp.fill(title)

    await page.evaluate("""(c) => {
        const cm = document.querySelector('.CodeMirror');
        if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
        const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
        if (ta) { ta.value = c; ta.dispatchEvent(new Event('input',{bubbles:true})); }
    }""", code)

    await page.evaluate("""() => {
        const cb = document.querySelector('input[name="wpcode_active"]');
        if (cb && !cb.checked) cb.click();
    }""")

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

        snippet_id = await create_snippet(page, 'Puria — Dark Footer CSS', SNIPPET_CODE)
        print(f'Done. Snippet ID: {snippet_id}')

        # Verify CSS is live
        check = await page.evaluate("""async () => {
            const res = await fetch('/', {cache: 'no-store'});
            const html = await res.text();
            return html.includes('puria-dark-footer') ? 'CSS live ✅' : 'CSS NOT found ❌';
        }""")
        print(f'Verify: {check}')

        await browser.close()

asyncio.run(main())
