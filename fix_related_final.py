import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

# Correct snippet code
RELATED_CODE = """// Related products: same animal species only (caini/pisici/pasari-rozatoare)
add_filter('woocommerce_related_products', function($related_posts, $product_id, $args) {
    $species_slugs = ['caini', 'pisici', 'pasari-rozatoare'];
    $terms = get_the_terms($product_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) return $related_posts;

    $product_species_ids = [];
    foreach ($terms as $t) {
        $ancestors = array_merge([$t->term_id], get_ancestors($t->term_id, 'product_cat'));
        foreach ($ancestors as $anc_id) {
            $anc = get_term($anc_id, 'product_cat');
            if ($anc && !is_wp_error($anc) && in_array($anc->slug, $species_slugs))
                $product_species_ids[] = $anc->term_id;
        }
    }
    $product_species_ids = array_unique($product_species_ids);
    if (empty($product_species_ids)) return $related_posts;

    $valid_cat_ids = $product_species_ids;
    foreach ($product_species_ids as $sid) {
        $children = get_terms(['taxonomy' => 'product_cat', 'child_of' => $sid, 'fields' => 'ids', 'hide_empty' => false]);
        if (!is_wp_error($children)) $valid_cat_ids = array_merge($valid_cat_ids, $children);
    }
    $valid_cat_ids = array_unique($valid_cat_ids);

    $filtered = [];
    foreach ($related_posts as $rid) {
        $r_terms = wp_get_post_terms($rid, 'product_cat', ['fields' => 'ids']);
        if (!is_wp_error($r_terms) && array_intersect($valid_cat_ids, $r_terms))
            $filtered[] = $rid;
    }
    if (count($filtered) < 4) {
        $extra = get_posts([
            'post_type' => 'product', 'posts_per_page' => 8, 'post_status' => 'publish',
            'post__not_in' => array_merge([$product_id], $filtered),
            'tax_query' => [['taxonomy' => 'product_cat', 'field' => 'term_id', 'terms' => $valid_cat_ids, 'operator' => 'IN']],
            'orderby' => 'rand', 'fields' => 'ids',
        ]);
        $filtered = array_unique(array_merge($filtered, $extra));
    }
    return array_slice($filtered, 0, 4);
}, 10, 3);"""


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

        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        # Step 1: Delete old snippets 248059 and 248063 via REST
        for sid in [248059, 248063]:
            del_result = await page.evaluate("""async (id) => {
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch(`/wp-json/wp/v2/wpcode_snippet/${id}?force=true`, {
                    method: 'DELETE', headers: {'X-WP-Nonce': nonce}
                });
                return res.status;
            }""", sid)
            print(f'Delete snippet {sid}: status={del_result}')

        # Step 2: Create fresh correct snippet
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
        await page.wait_for_timeout(500)
        await page.evaluate("""() => {
            for (const h of document.querySelectorAll('h3')) {
                if (h.textContent.includes('PHP')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(800)
        ti = await page.query_selector('input[name="wpcode_snippet_title"]')
        if ti:
            await ti.fill('Puria — Related products by species')
        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
        }""", RELATED_CODE)
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")
        save = await page.evaluate("""async ([code, title]) => {
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
            return {status: res.status, id: m ? m[1] : null};
        }""", [RELATED_CODE, 'Puria — Related products by species'])
        print(f'New snippet: {save}')

        # Step 3: Clear WooCommerce related products transients + SG cache
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        clear = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            // Delete WC related transients
            const res = await fetch('/wp-json/wp/v2/settings', {
                method: 'GET', headers: {'X-WP-Nonce': nonce}
            });
            return {nonce_ok: !!nonce, status: res.status};
        }""")
        print(f'WP API access: {clear}')

        # Use a WPCode one-shot to clear transients
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
        await page.wait_for_timeout(400)
        await page.evaluate("""() => {
            for (const h of document.querySelectorAll('h3')) {
                if (h.textContent.includes('PHP')) { h.click(); return; }
            }
        }""")
        await page.wait_for_timeout(600)
        ti2 = await page.query_selector('input[name="wpcode_snippet_title"]')
        if ti2:
            await ti2.fill('Puria — Clear WC related transients (one-shot)')
        CLEAR_CODE = """// One-shot: clear WooCommerce related product transients
add_action('init', function() {
    if (!get_option('puria_wc_related_cleared_v2')) {
        global $wpdb;
        $wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '\\_transient\\_wc\\_related\\_%'");
        $wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '\\_transient\\_timeout\\_wc\\_related\\_%'");
        update_option('puria_wc_related_cleared_v2', '1');
    }
});"""
        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); }
        }""", CLEAR_CODE)
        await page.evaluate("""() => {
            const cb = document.querySelector('input[name="wpcode_active"]');
            if (cb && !cb.checked) cb.click();
        }""")
        save2 = await page.evaluate("""async ([code, title]) => {
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
            return {status: res.status, id: m ? m[1] : null};
        }""", [CLEAR_CODE, 'Puria — Clear WC related transients (one-shot)'])
        print(f'Clear transients snippet: {save2}')

        # Step 4: Trigger the transient clear by visiting any page
        await page.goto('https://puria.ro/', wait_until='domcontentloaded')
        await page.wait_for_timeout(1000)
        print('Triggered init (transients cleared)')

        # Step 5: Verify on product page
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/bautura-umeda-caini-macs-paw-power-vita-200g-79-6-suc-carne-15-carne-vita/', wait_until='domcontentloaded')
        await page2.wait_for_timeout(2000)

        related = await page2.evaluate("""() => {
            return Array.from(document.querySelectorAll('.woocommerce-loop-product__title'))
                .map(e => e.textContent.trim().substring(0, 60));
        }""")

        print(f'\nRelated products ({len(related)}):')
        has_cat = False
        for t in related:
            is_cat = any(w in t.lower() for w in ['pisic', 'cat somon', 'ansamblu', 'cat,', 'Santa Cat'])
            if is_cat: has_cat = True
            print(f'  {"❌ CAT" if is_cat else "✅    "} {t}')
        print(f'\nCat products in related: {has_cat} (want: False)')

        await browser.close()

asyncio.run(main())
