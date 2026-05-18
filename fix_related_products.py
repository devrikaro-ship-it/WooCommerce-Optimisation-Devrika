import asyncio
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

# Species categories slugs — only match these as the "top" grouping
NEW_RELATED_CODE = """// Related products: same animal species category (caini/pisici/pasari-rozatoare)
add_filter('woocommerce_related_products', function($related_posts, $product_id, $args) {
    // Species L1 category slugs — the ones that matter for relevance
    $species_slugs = ['caini', 'pisici', 'pasari-rozatoare'];

    // Get all categories of current product
    $terms = get_the_terms($product_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) return $related_posts;

    // Find which species categories (and their children) the product belongs to
    $product_species_ids = [];
    foreach ($terms as $t) {
        // Check if this term or any ancestor is a species category
        $ancestors = array_merge([$t->term_id], get_ancestors($t->term_id, 'product_cat'));
        foreach ($ancestors as $anc_id) {
            $anc = get_term($anc_id, 'product_cat');
            if ($anc && !is_wp_error($anc) && in_array($anc->slug, $species_slugs)) {
                $product_species_ids[] = $anc->term_id;
            }
        }
    }
    $product_species_ids = array_unique($product_species_ids);

    // No species found — don't filter (generic product)
    if (empty($product_species_ids)) return $related_posts;

    // Collect all category IDs under the matched species
    $valid_cat_ids = $product_species_ids;
    foreach ($product_species_ids as $sid) {
        $children = get_terms(['taxonomy' => 'product_cat', 'child_of' => $sid, 'fields' => 'ids', 'hide_empty' => false]);
        if (!is_wp_error($children)) $valid_cat_ids = array_merge($valid_cat_ids, $children);
    }
    $valid_cat_ids = array_unique($valid_cat_ids);

    // Filter existing related posts
    $filtered = [];
    foreach ($related_posts as $rid) {
        $r_terms = wp_get_post_terms($rid, 'product_cat', ['fields' => 'ids']);
        if (!is_wp_error($r_terms) && array_intersect($valid_cat_ids, $r_terms))
            $filtered[] = $rid;
    }

    // Supplement if < 4
    if (count($filtered) < 4) {
        $extra = get_posts([
            'post_type'      => 'product',
            'posts_per_page' => 8,
            'post__not_in'   => array_merge([$product_id], $filtered),
            'post_status'    => 'publish',
            'tax_query'      => [['taxonomy' => 'product_cat', 'field' => 'term_id', 'terms' => $valid_cat_ids, 'operator' => 'IN']],
            'orderby'        => 'rand',
            'fields'         => 'ids',
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

        # Update snippet 248059 (the existing related products snippet)
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id=248059', wait_until='networkidle')
        await page.wait_for_timeout(500)

        await page.evaluate("""(c) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', {bubbles: true})); }
        }""", NEW_RELATED_CODE)

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
        }""", [NEW_RELATED_CODE, 'Puria — Related products by species category'])

        print(f'Updated snippet: {result}')

        # Verify: check related products on dog product page
        page2 = await context.new_page()
        await page2.goto('https://puria.ro/bautura-umeda-caini-macs-paw-power-vita-200g-79-6-suc-carne-15-carne-vita/', wait_until='domcontentloaded')
        await page2.wait_for_timeout(2000)

        related = await page2.evaluate("""() => {
            return Array.from(document.querySelectorAll('.woocommerce-loop-product__title'))
                .map(e => e.textContent.trim().substring(0, 60));
        }""")

        print(f'\nRelated products on dog page ({len(related)}):')
        has_cat = any('pisic' in t.lower() or 'Cat' in t or 'Ansamblu' in t for t in related)
        for t in related:
            flag = '❌ CAT' if ('pisic' in t.lower() or 'cat ' in t.lower() or 'Ansamblu' in t) else '✅'
            print(f'  {flag} {t}')

        print(f'\nCat products in related: {has_cat} (want: False)')

        await browser.close()

asyncio.run(main())
