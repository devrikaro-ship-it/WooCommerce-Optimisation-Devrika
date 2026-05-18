import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

SNIPPET_CODE = r'''
// Fix #12 - Local Google Fonts
// Download on first admin load, serve local on frontend

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
        $resp = wp_remote_get($api_url, [
            'timeout'    => 30,
            'user-agent' => $ua,
            'sslverify'  => false,
        ]);
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

add_action('wp_enqueue_scripts', function() {
    if (!get_option('puria_local_fonts_v1')) return;

    global $wp_styles;
    foreach ((array) $wp_styles->queue as $handle) {
        $src = $wp_styles->registered[$handle]->src ?? '';
        if (strpos((string)$src, 'fonts.googleapis.com') !== false) {
            wp_dequeue_style($handle);
        }
    }
    wp_enqueue_style('puria-local-fonts', content_url('/uploads/fonts/local-fonts.css'), [], null);
}, 999);

add_filter('style_loader_tag', function($tag, $handle) {
    if ($handle === 'puria-local-fonts') {
        return str_replace("rel='stylesheet'", "rel='preload' as='style' onload=\"this.onload=null;this.rel='stylesheet'\"", $tag)
             . '<noscript>' . $tag . '</noscript>';
    }
    return $tag;
}, 10, 2);
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
        print('Logged in:', page.url)

        # Navigate to WPCode Add New
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
        await page.screenshot(path='/tmp/wpcode_new.png')

        # Select PHP snippet type
        php_option = await page.evaluate("""() => {
            const h3s = document.querySelectorAll('h3');
            for (const h of h3s) {
                if (h.textContent.includes('PHP')) {
                    h.click();
                    return 'clicked: ' + h.textContent.trim();
                }
            }
            return 'not found';
        }""")
        print('PHP select:', php_option)
        await page.wait_for_timeout(1000)

        # Fill title
        title_sel = 'input[name="wpcode_snippet_title"], #wpcode-snippet-title, input[placeholder*="title"], input[placeholder*="titlu"]'
        await page.wait_for_selector(title_sel, timeout=5000)
        await page.fill(title_sel, 'Fix #12 - Local Google Fonts')

        # Fill code via CodeMirror or textarea
        filled = await page.evaluate("""(code) => {
            // Try CodeMirror first
            const cmEl = document.querySelector('.CodeMirror');
            if (cmEl && cmEl.CodeMirror) {
                cmEl.CodeMirror.setValue(code);
                return 'codemirror';
            }
            // Fallback: direct textarea
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) {
                ta.value = code;
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                return 'textarea';
            }
            return 'not found';
        }""", SNIPPET_CODE)
        print('Code filled via:', filled)

        # Set auto-insert to run everywhere
        await page.evaluate("""() => {
            const sel = document.querySelector('select[name="wpcode_auto_insert_location"], #wpcode-auto-insert-location');
            if (sel) sel.value = 'everywhere';
        }""")

        # Activate snippet
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")

        # Save
        save_btn = await page.query_selector('button[name="button"][value="publish"], input[value*="Save"], #publish, button.wpcode-button-primary')
        if save_btn:
            await save_btn.click()
            await page.wait_for_load_state('networkidle')
            print('Saved. URL:', page.url)
        else:
            # Try submitting the form
            await page.evaluate("document.querySelector('form').submit()")
            await page.wait_for_load_state('networkidle')
            print('Form submitted. URL:', page.url)

        await page.screenshot(path='/tmp/wpcode_saved.png')

        # Now trigger the download by visiting any admin page
        print('\nTriggering font download via admin page load...')
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        await page.wait_for_timeout(3000)

        # Check if fonts were downloaded
        check = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/settings', {
                headers: {'X-WP-Nonce': nonce}
            });
            return res.status;
        }""")
        print('Admin page loaded, status:', check)

        # Wait a bit for download to complete
        print('Waiting 15s for font downloads...')
        await page.wait_for_timeout(15000)

        # Verify: check if local-fonts.css exists
        verify = await page.evaluate("""async () => {
            const res = await fetch('/wp-content/uploads/fonts/local-fonts.css');
            return {status: res.status, size: parseInt(res.headers.get('content-length') || '0')};
        }""")
        print(f'\nlocal-fonts.css: status={verify["status"]}, size={verify["size"]}b')

        await browser.close()

asyncio.run(main())
