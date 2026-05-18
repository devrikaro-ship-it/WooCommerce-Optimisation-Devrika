import asyncio
import json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

ITEMLIST_CODE = r"""// Fix #14 - ItemList Schema pe pagini categorie WooCommerce
add_action('wp_head', function() {
    if (!function_exists('is_product_category') || !is_product_category()) return;
    $term = get_queried_object();
    if (!$term || !isset($term->term_id)) return;
    $products = get_posts([
        'post_type'      => 'product',
        'posts_per_page' => 10,
        'post_status'    => 'publish',
        'orderby'        => 'popularity',
        'tax_query'      => [[
            'taxonomy' => 'product_cat',
            'field'    => 'term_id',
            'terms'    => $term->term_id,
        ]],
    ]);
    if (empty($products)) return;
    $items = [];
    foreach ($products as $i => $p) {
        $obj = wc_get_product($p->ID);
        if (!$obj) continue;
        $items[] = ['@type'=>'ListItem','position'=>$i+1,'url'=>get_permalink($p->ID),'name'=>$obj->get_name()];
    }
    $schema = ['@context'=>'https://schema.org','@type'=>'ItemList','name'=>$term->name,'url'=>get_term_link($term),'numberOfItems'=>count($items),'itemListElement'=>$items];
    echo '<script type="application/ld+json">'.wp_json_encode($schema,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).'</script>'."\n";
}, 10);"""

LLMS_CODE = """// Fix #19 - Serve llms.txt
add_action('init', function() {
    if ($_SERVER['REQUEST_URI'] !== '/llms.txt') return;
    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: public, max-age=86400');
    echo '# puria.ro

> Magazin online specializat in hrana premium si accesorii pentru animale de companie din Romania.
> Operator: PETEXPRESS RETAIL SRL (CUI RO47725536). Contact: contact@puria.ro

## Categorii principale

- [Caini](https://puria.ro/caini/) - Hrana uscata, hrana umeda, snackuri, accesorii caini
- [Pisici](https://puria.ro/pisici/) - Hrana uscata, hrana umeda, litiera, accesorii pisici
- [Pasari si rozatoare](https://puria.ro/pasari-rozatoare/) - Hrana si accesorii

## Branduri reprezentate

MAC\\'s, Natural Greatness, Terra Canis, Petmex, Puffins, Farm Nature, Tundra, Karnlea

## Livrare

Livrare in toata Romania. Gratuita pentru comenzi peste 450 RON.

## Sitemap

https://puria.ro/sitemap_index.xml

## Licenta continut

Continutul editorial este protejat. Utilizarea pentru antrenament AI fara acord scris este interzisa.
';
    exit;
});"""

async def create_snippet(page, title, code):
    """Create WPCode snippet using known-working form POST method."""
    # Navigate to new snippet page
    await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')
    await page.wait_for_timeout(500)

    # Click PHP
    await page.evaluate("""() => {
        for (const h of document.querySelectorAll('h3')) {
            if (h.textContent.includes('PHP')) { h.click(); return; }
        }
    }""")
    await page.wait_for_timeout(800)

    # Fill title
    title_inp = await page.query_selector('input[name="wpcode_snippet_title"]')
    if title_inp:
        await title_inp.fill(title)

    # Set code via CodeMirror
    await page.evaluate("""(c) => {
        const cm = document.querySelector('.CodeMirror');
        if (cm?.CodeMirror) cm.CodeMirror.setValue(c);
        else {
            const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
            if (ta) { ta.value = c; ta.dispatchEvent(new Event('input',{bubbles:true})); }
        }
    }""", code)

    # Activate
    await page.evaluate("""() => {
        const cb = document.querySelector('input[name="wpcode_active"]');
        if (cb && !cb.checked) cb.click();
    }""")

    # Get nonce and submit via fetch (most reliable)
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
        const url = res.url;
        const m = url.match(/snippet_id=(\d+)/);
        return {url, snippet_id: m ? m[1] : null};
    }""", [code, title])

    print(f'  Snippet "{title}": ID={result.get("snippet_id")} url={result.get("url", "")[:80]}')
    return result.get('snippet_id')


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        print('Logged in')

        print('\n=== Fix #14 — ItemList Schema ===')
        id14 = await create_snippet(page, 'Fix #14 - ItemList Schema categorii', ITEMLIST_CODE)

        print('\n=== Fix #19 — llms.txt ===')
        id19 = await create_snippet(page, 'Fix #19 - llms.txt', LLMS_CODE)

        # Verify
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        await page.wait_for_timeout(1000)

        checks = await page.evaluate("""async () => {
            const caini = await fetch('/caini/', {cache: 'no-store'});
            const cainiHtml = await caini.text();
            const llms = await fetch('/llms.txt', {cache: 'no-store'});
            const llmsText = await llms.text();
            return {
                itemlist: cainiHtml.includes('ItemList') ? 'OK' : 'MISSING',
                schemas: (cainiHtml.match(/application\/ld\+json/g)||[]).length,
                llms_status: llms.status,
                llms_preview: llmsText.substring(0, 60)
            };
        }""")
        print(f'\nVerificare:')
        print(f'  ItemList /caini/: {checks["itemlist"]} ({checks["schemas"]} schema blocks)')
        print(f'  llms.txt: HTTP {checks["llms_status"]} — {checks["llms_preview"]}')

        await browser.close()

asyncio.run(main())
