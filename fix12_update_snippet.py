import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
SNIPPET_ID = 248046

SNIPPET_CODE = r'''
// Fix #12 - Local Google Fonts

// Step 1: Download fonts on first admin load
add_action('admin_init', function() {
    if (get_option('puria_local_fonts_v1')) return;

    $dir = WP_CONTENT_DIR . '/uploads/fonts/';
    if (!wp_mkdir_p($dir)) return;

    $ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
    $base_url = content_url('/uploads/fonts/');
    $all_css = '';

    $font_urls = [
        'https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wdth,wght@0,62.5..100,100..900;1,62.5..100,100..900&display=swap',
        'https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap',
        'https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@100;200;300;400;500;600;700;800;900&display=swap',
        'https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap',
        'https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200;0,300;0,400;0,600;0,700;0,800;0,900;1,200;1,300;1,400;1,600;1,700;1,800;1,900&display=swap',
    ];

    foreach ($font_urls as $api_url) {
        $resp = wp_remote_get($api_url, ['timeout' => 30, 'user-agent' => $ua, 'sslverify' => false]);
        if (is_wp_error($resp)) continue;
        $css = wp_remote_retrieve_body($resp);
        if (empty($css)) continue;

        preg_match_all('/url\((https:\/\/fonts\.gstatic\.com\/[^)]+\.woff2)\)/', $css, $matches);
        foreach ($matches[1] as $font_url) {
            $filename = md5($font_url) . '.woff2';
            $local_path = $dir . $filename;
            if (!file_exists($local_path)) {
                $fr = wp_remote_get($font_url, ['timeout' => 30, 'sslverify' => false]);
                if (!is_wp_error($fr)) {
                    file_put_contents($local_path, wp_remote_retrieve_body($fr));
                }
            }
            $css = str_replace($font_url, $base_url . $filename, $css);
        }
        $all_css .= $css . "\n";
    }

    if (!empty($all_css)) {
        file_put_contents($dir . 'local-fonts.css', $all_css);
        update_option('puria_local_fonts_v1', time());
    }
});

// Step 2: Remove Google Fonts via output buffer (catches all sources incl. Elementor/theme)
add_action('template_redirect', function() {
    if (!get_option('puria_local_fonts_v1')) return;
    ob_start(function($html) {
        // Remove all <link> tags pointing to fonts.googleapis.com
        $html = preg_replace('/<link[^>]+href=["\'][^"\']*fonts\.googleapis\.com[^"\']*["\'][^>]*\/?>/i', '', $html);
        // Remove dns-prefetch for google fonts
        $html = preg_replace('/<link[^>]+dns-prefetch[^>]+fonts\.google[^>]*>/i', '', $html);
        return $html;
    });
});

// Step 3: Enqueue local CSS
add_action('wp_enqueue_scripts', function() {
    if (!get_option('puria_local_fonts_v1')) return;
    wp_enqueue_style('puria-local-fonts', content_url('/uploads/fonts/local-fonts.css'), [], null);
}, 999);
'''

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

        # Edit existing snippet
        await page.goto(f'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id={SNIPPET_ID}', wait_until='networkidle')
        print('Editing snippet', SNIPPET_ID)

        # Set code via CodeMirror
        filled = await page.evaluate("""(code) => {
            const cmEl = document.querySelector('.CodeMirror');
            if (cmEl && cmEl.CodeMirror) { cmEl.CodeMirror.setValue(code); return 'codemirror'; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = code; ta.dispatchEvent(new Event('input', {bubbles: true})); return 'textarea'; }
            return 'not found';
        }""", SNIPPET_CODE)
        print('Code set via:', filled)

        # Ensure active
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")

        # Save
        saved = await page.evaluate("""async () => {
            const form = document.querySelector('form#wpcode-snippet-form, form');
            if (!form) return 'no form';
            const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
            const id = document.querySelector('input[name="id"]')?.value || '';
            const fd = new FormData(form);
            fd.set('button', 'publish');
            const res = await fetch(form.action || window.location.href, {method: 'POST', body: fd});
            return res.url;
        }""")
        print('Save result:', saved)

        await page.wait_for_timeout(2000)
        await page.reload(wait_until='networkidle')

        # Verify snippet content saved
        code_check = await page.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            return cm?.CodeMirror?.getValue()?.substring(0, 80) || 'not found';
        }""")
        print('Code in editor:', code_check)

        await browser.close()

asyncio.run(main())
