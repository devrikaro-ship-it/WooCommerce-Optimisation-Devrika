import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'
SNIPPET_ID = 248046

SNIPPET_CODE = r'''// Fix #12 - Local Google Fonts

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
                if (!is_wp_error($fr)) file_put_contents($local_path, wp_remote_retrieve_body($fr));
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

add_action('template_redirect', function() {
    if (!get_option('puria_local_fonts_v1')) return;
    ob_start(function($html) {
        $html = preg_replace('/<link[^>]+href=["\'][^"\']*fonts\.googleapis\.com[^"\']*["\'][^>]*\/?>/i', '', $html);
        $html = preg_replace('/<link[^>]+dns-prefetch[^>]+fonts\.google[^>]*>/i', '', $html);
        return $html;
    });
});

add_action('wp_enqueue_scripts', function() {
    if (!get_option('puria_local_fonts_v1')) return;
    wp_enqueue_style('puria-local-fonts', content_url('/uploads/fonts/local-fonts.css'), [], null);
}, 999);'''

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

        await page.goto(f'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id={SNIPPET_ID}', wait_until='networkidle')

        # Get form fields
        form_data = await page.evaluate("""() => {
            return {
                nonce: document.querySelector('#wpcode-save-snippet-nonce')?.value,
                id: document.querySelector('input[name="id"]')?.value,
                http_referer: document.querySelector('input[name="_wp_http_referer"]')?.value,
                active: document.querySelector('input[name="wpcode_active"]')?.checked,
                location: document.querySelector('select[name="wpcode_auto_insert_location"]')?.value,
            };
        }""")
        print('Form fields:', form_data)

        # Set code
        await page.evaluate("""(code) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) cm.CodeMirror.setValue(code);
        }""", SNIPPET_CODE)

        # Click Update button directly
        update_btn = await page.query_selector('#publish, input[name="button"][value="publish"], button[name="button"]')
        if update_btn:
            btn_val = await update_btn.get_attribute('value') or await update_btn.inner_text()
            print(f'Clicking: {btn_val}')
            await update_btn.click()
            await page.wait_for_load_state('networkidle')
            print('After click URL:', page.url)
        else:
            # Try all submit buttons
            btns = await page.query_selector_all('input[type="submit"], button[type="submit"]')
            print(f'Found {len(btns)} submit buttons')
            for btn in btns:
                txt = await btn.get_attribute('value') or await btn.inner_text()
                print(f'  {txt}')

        # Verify via reload
        await page.wait_for_timeout(1000)
        check = await page.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            const val = cm?.CodeMirror?.getValue() || '';
            return val.includes('template_redirect') ? 'OK - has template_redirect' : 'OLD - missing template_redirect: ' + val.substring(0, 60);
        }""")
        print('Verification:', check)

        await browser.close()

asyncio.run(main())
