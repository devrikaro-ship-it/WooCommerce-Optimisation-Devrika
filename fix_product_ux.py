import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

SNIPPETS = [

# ── 1. Related products: same L1 category ──────────────────────────────────
('Puria — Related products by L1 category', """// Related products only from same top-level category
add_filter('woocommerce_related_products', function($related_posts, $product_id, $args) {
    if (empty($related_posts)) return $related_posts;

    $terms = get_the_terms($product_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) return $related_posts;

    // Find L1 category IDs
    $top_cats = [];
    foreach ($terms as $t) {
        if ($t->parent == 0) $top_cats[] = $t->term_id;
    }
    if (empty($top_cats)) {
        foreach ($terms as $t) {
            if ($t->parent != 0) {
                $parent = get_term($t->parent, 'product_cat');
                if ($parent && !is_wp_error($parent) && $parent->parent == 0)
                    $top_cats[] = $parent->term_id;
            }
        }
    }
    if (empty($top_cats)) return $related_posts;

    // Collect all sub-category IDs under L1
    $all_cat_ids = $top_cats;
    foreach ($top_cats as $pid) {
        $children = get_terms(['taxonomy' => 'product_cat', 'parent' => $pid, 'fields' => 'ids', 'hide_empty' => false]);
        if (!is_wp_error($children)) $all_cat_ids = array_merge($all_cat_ids, $children);
    }
    $all_cat_ids = array_unique($all_cat_ids);

    // Filter existing related to same L1
    $filtered = [];
    foreach ($related_posts as $rid) {
        $r_terms = wp_get_post_terms($rid, 'product_cat', ['fields' => 'ids']);
        if (!is_wp_error($r_terms) && array_intersect($all_cat_ids, $r_terms))
            $filtered[] = $rid;
    }

    // Supplement if < 4
    if (count($filtered) < 4) {
        $extra = get_posts([
            'post_type'      => 'product',
            'posts_per_page' => 8,
            'post__not_in'   => array_merge([$product_id], $filtered),
            'post_status'    => 'publish',
            'tax_query'      => [['taxonomy' => 'product_cat', 'field' => 'term_id', 'terms' => $all_cat_ids, 'operator' => 'IN']],
            'orderby'        => 'rand',
            'fields'         => 'ids',
        ]);
        $filtered = array_unique(array_merge($filtered, $extra));
    }

    return array_slice($filtered, 0, 4);
}, 10, 3);"""),

# ── 2. Enable reviews globally + open comment_status on all products ────────
('Puria — Enable product reviews', """// Enable WooCommerce reviews globally
add_action('init', function() {
    if (get_option('woocommerce_enable_reviews') !== 'yes') {
        update_option('woocommerce_enable_reviews', 'yes');
        update_option('woocommerce_review_rating_verification_required', 'no');
        update_option('woocommerce_review_rating_required', 'no');
        update_option('woocommerce_enable_review_rating', 'yes');
    }
    // Open comment_status on all published products (runs once)
    if (!get_option('puria_reviews_opened')) {
        global $wpdb;
        $wpdb->update($wpdb->posts,
            ['comment_status' => 'open'],
            ['post_type' => 'product', 'post_status' => 'publish']
        );
        update_option('puria_reviews_opened', '1');
    }
});"""),

# ── 3. CSS: SKU hidden, CTA full-width, breadcrumb separator, price unit ───
('Puria — Product page CSS fixes', r"""// Product page UX CSS
add_action('wp_head', function() {
    if (!is_product()) return;
    echo '<style id="puria-product-ux">
/* Hide SKU (Cod produs) — not useful above fold */
.sku_wrapper{display:none!important}

/* CTA button full-width */
form.cart .single_add_to_cart_button,
.et-single-product-content .single_add_to_cart_button{
    width:100%!important;
    min-width:200px!important;
    justify-content:center!important;
}

/* Breadcrumb: dash -> › */
.woocommerce-breadcrumb{font-size:13px!important;color:#888!important}
.woocommerce-breadcrumb .delimiter,
.woocommerce-breadcrumb>span:not(.breadcrumb-item):not(:last-child)::after{
    content:" › "!important;
}

/* Review stars placeholder text */
#reviews .woocommerce-Reviews-title{font-size:16px!important;font-weight:600!important}

/* Trust box icon size */
.et-product-usps .et-usp-item svg,
.et-product-usps .et-usp-item .et-icon{font-size:20px!important}

/* Favorite link -> subtle button */
.yith-wcwl-add-to-wishlist .add_to_wishlist,
a.add_to_wishlist{
    display:inline-flex!important;
    align-items:center!important;
    gap:6px!important;
    font-size:13px!important;
    color:#666!important;
    text-decoration:none!important;
    padding:6px 0!important;
}
.yith-wcwl-add-to-wishlist .add_to_wishlist:hover,
a.add_to_wishlist:hover{color:#333!important}

/* Product tabs: bolder active tab */
.woocommerce-tabs .tabs li.active a{
    font-weight:700!important;
    border-bottom:2px solid #C09578!important;
}

/* Description headings with left accent */
.woocommerce-Tabs-panel h2,
.woocommerce-Tabs-panel h3{
    font-size:15px!important;
    font-weight:700!important;
    padding-left:12px!important;
    border-left:3px solid #C09578!important;
    margin-bottom:8px!important;
}
</style>';
}, 99);"""),

# ── 4. Smart delivery message ───────────────────────────────────────────────
('Puria — Smart delivery message', """// Replace delivery date with smart "Livrare maine" message
add_filter('woocommerce_get_availability', function($availability, $product) {
    if (!$product->is_in_stock()) return $availability;

    // Romania timezone
    $tz = new DateTimeZone('Europe/Bucharest');
    $now = new DateTime('now', $tz);
    $hour = (int)$now->format('G');
    $dow  = (int)$now->format('N'); // 1=Mon, 7=Sun

    if ($dow >= 6) {
        // Weekend: livrare luni
        $msg = '⏱ Livrare luni, ' . (new DateTime('next monday', $tz))->format('j M');
    } elseif ($hour < 15) {
        // Before 15:00 weekday: livrare maine
        $tomorrow = new DateTime('tomorrow', $tz);
        $msg = '⚡ Livrare maine, ' . $tomorrow->format('j M') . ' — comanda pana la 15:00';
    } else {
        // After 15:00: livrare in 2 zile
        $d = new DateTime('+2 weekdays', $tz);
        $msg = '📦 Livrare ' . $d->format('j M');
    }

    $availability['availability'] = $msg;
    return $availability;
}, 10, 2);"""),

]


async def create_snippet(page, title, code):
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
        await ti.fill(title)

    await page.evaluate("""(c) => {
        const cm = document.querySelector('.CodeMirror');
        if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
        const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
        if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles: true})); }
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
        return {status: res.status, id: m ? m[1] : null};
    }""", [code, title])

    print(f'  Snippet "{title[:50]}": ID={result["id"]} status={result["status"]}')
    return result['id']


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

        ids = []
        for title, code in SNIPPETS:
            sid = await create_snippet(page, title, code)
            ids.append(sid)

        print(f'\nAll snippets deployed: {ids}')

        # Verify on product page
        TEST_URL = 'https://puria.ro/caini/hrana-umeda/bautura-umeda-caini-macs-paw-power-vita-200g-796-suc-carne-15-carne-vita-90695/'
        page2 = await context.new_page()
        await page2.goto(TEST_URL, wait_until='domcontentloaded')

        checks = await page2.evaluate("""() => {
            const has_sku = !!document.querySelector('.sku_wrapper');
            const btn = document.querySelector('.single_add_to_cart_button');
            const btn_width = btn ? getComputedStyle(btn).width : 'n/a';
            const related = Array.from(document.querySelectorAll('.related.products .product .woocommerce-loop-product__title'))
                .map(el => el.textContent.trim().substring(0, 40));
            const avail = document.querySelector('.availability .availability')?.textContent?.trim() || 'n/a';
            return {has_sku, btn_width, related, avail};
        }""")

        print(f'\n=== Verify on product page ===')
        print(f'SKU wrapper visible: {checks["has_sku"]} (should be False)')
        print(f'CTA button width: {checks["btn_width"]}')
        print(f'Related products: {checks["related"]}')
        print(f'Availability msg: {checks["avail"]}')

        await browser.close()

asyncio.run(main())
