import asyncio
import json
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

DESPRE_NOI_ID = 235057

# Fix #16 — Despre Noi content (fara diacritice)
DESPRE_NOI_CONTENT = """<h2>Cine suntem</h2>
<p>Puria este un magazin online specializat in hrana premium si accesorii pentru animale de companie, operat de PETEXPRESS RETAIL SRL (CUI RO47725536, J23/1339/2023) din Pantelimon, Ilfov. Fondat in 2023, Puria s-a construit in jurul unui singur principiu: animalele de companie merita hrana adevarata, nu compromisuri.</p>

<h2>De ce am ales hrana premium</h2>
<p>Piata hranei pentru animale din Romania este dominata de marci de masa cu ingrediente de calitate medie. Am ales altceva: branduri care pun carnea pe primul loc — ingredient principal real, fara cereale sau aditivi artificiali inutili. Diferenta se vede in blana, energie si sanatatea pe termen lung a animalului.</p>
<p>Fiecare produs de pe Puria trece printr-un proces de selectie bazat pe lista de ingrediente, procentul de carne, metodele de preparare si feedback-ul real al proprietarilor de animale. Daca un produs nu trece acest filtru, nu ajunge pe site.</p>

<h2>Branduri selectate</h2>
<p>Lucram direct cu unele dintre cele mai apreciate marci din Europa:</p>
<ul>
<li><strong>MAC's</strong> (Germania) — retete monoproteice cu 60-99% carne, fara cereale, pentru caini si pisici</li>
<li><strong>Natural Greatness</strong> (Spania) — hrana grainfree pentru caini si pisici cu sensibilitati alimentare</li>
<li><strong>Terra Canis</strong> (Germania) — hrana umeda gourmet cu ingrediente proaspete, preparata la foc mic</li>
<li><strong>Petmex</strong> — recompense naturale 100% carne, fara aditivi sau conservanti</li>
<li><strong>Puffins</strong> — hrana uscata cu procent ridicat de carne pentru caini activi de talie mica</li>
<li><strong>Farm Nature</strong> — nutritie completa pentru catei si caini adulti in crestere</li>
<li><strong>Tundra</strong> — hrana bogata in proteine animale, inspirata din dieta naturala a lupului</li>
</ul>

<h2>Ce gasesti pe Puria</h2>
<p>Hrana uscata si umeda pentru <a href="/caini/">caini</a> de toate varstele si rasele, hrana pentru <a href="/pisici/">pisici</a> adulte, sterilizate si senioare, recompense naturale, suplimente, accesorii si produse de ingrijire pentru <a href="/pasari-rozatoare/">pasari si rozatoare</a>. Livram in toata Romania, cu comenzi peste 450 RON livrate gratuit.</p>

<h2>Contact</h2>
<p>Suntem disponibili la <strong>contact@puria.ro</strong> sau <strong>+40770757779</strong>. Echipa Puria raspunde in maxim 24 de ore pentru orice intrebare despre nutritia si ingrijirea animalului tau.</p>"""

DESPRE_NOI_META = "Puria — magazin online cu hrana premium pentru caini si pisici. Branduri selectate: MAC's, Natural Greatness, Terra Canis. Livrare gratuita peste 450 RON."

# Fix #14 — ItemList Schema pe pagini categorie
ITEMLIST_SNIPPET = r"""
// Fix #14 - ItemList Schema pe pagini categorie WooCommerce
add_action('wp_head', function() {
    if (!is_product_category()) return;

    $term = get_queried_object();
    if (!$term) return;

    $args = [
        'post_type'      => 'product',
        'posts_per_page' => 10,
        'post_status'    => 'publish',
        'tax_query'      => [[
            'taxonomy' => 'product_cat',
            'field'    => 'term_id',
            'terms'    => $term->term_id,
        ]],
        'orderby' => 'popularity',
    ];
    $products = get_posts($args);
    if (empty($products)) return;

    $items = [];
    foreach ($products as $i => $product) {
        $product_obj = wc_get_product($product->ID);
        if (!$product_obj) continue;
        $items[] = [
            '@type'    => 'ListItem',
            'position' => $i + 1,
            'url'      => get_permalink($product->ID),
            'name'     => $product_obj->get_name(),
        ];
    }

    $schema = [
        '@context' => 'https://schema.org',
        '@type'    => 'ItemList',
        'name'     => $term->name,
        'url'      => get_term_link($term),
        'numberOfItems' => count($items),
        'itemListElement' => $items,
    ];

    echo '<script type="application/ld+json">' . wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
}, 10);
"""

# Fix #19 — llms.txt
LLMS_SNIPPET = r"""
// Fix #19 - Genereaza llms.txt in radacina site-ului
add_action('admin_init', function() {
    $file = ABSPATH . 'llms.txt';
    if (file_exists($file)) return;

    $content = '# puria.ro

> Magazin online specializat in hrana premium si accesorii pentru animale de companie din Romania.
> Operator: PETEXPRESS RETAIL SRL (CUI RO47725536). Contact: contact@puria.ro

## Categorii principale

- [Caini](https://puria.ro/caini/) - Hrana uscata, hrana umeda, snackuri, accesorii caini
  - [Hrana uscata caini](https://puria.ro/caini/hrana-uscata-caini/)
  - [Hrana umeda caini](https://puria.ro/caini/hrana-umeda-caini/)
  - [Recompense caini](https://puria.ro/caini/recompense-si-snackuri-caini/)
- [Pisici](https://puria.ro/pisici/) - Hrana uscata, hrana umeda, litiera, accesorii pisici
  - [Hrana uscata pisici](https://puria.ro/pisici/hrana-uscata-pisici/)
  - [Hrana umeda pisici](https://puria.ro/pisici/hrana-umeda-pisici/)
  - [Litiera si accesorii](https://puria.ro/pisici/litiera-si-accesorii/)
- [Pasari si rozatoare](https://puria.ro/pasari-rozatoare/) - Hrana si accesorii

## Branduri reprezentate

MAC\'s (Germania), Natural Greatness (Spania), Terra Canis (Germania), Petmex, Puffins, Farm Nature, Tundra, Karnlea, Marova Pet Food, SuperBeno

## Informatii livrare

Livrare in toata Romania. Gratuita pentru comenzi peste 450 RON.
Curier rapid: 19.70 lei | Easybox Sameday: 14.70 lei | Termen: 2-3 zile lucratoare

## Sitemap

- https://puria.ro/sitemap_index.xml

## Licenta continut

Continutul editorial de pe puria.ro (descrieri produse, texte categorii) este protejat prin drepturi de autor.
Utilizarea pentru antrenament modele AI fara acord explicit scris este interzisa.

## Informatii tehnice

- Platform: WooCommerce / WordPress
- Moneda: RON (leu romanesc)
- Limba: romana
- Tara: Romania
';

    file_put_contents($file, $content);
});
"""

async def save_wpcode_snippet(page, title, code, snippet_type='php'):
    await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1', wait_until='networkidle')

    # Select PHP
    php_clicked = await page.evaluate("""() => {
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (h.textContent.includes('PHP')) { h.click(); return true; }
        }
        return false;
    }""")
    await page.wait_for_timeout(800)

    # Fill title
    title_sel = 'input[name="wpcode_snippet_title"]'
    await page.wait_for_selector(title_sel, timeout=5000)
    await page.fill(title_sel, title)

    # Fill code via CodeMirror
    filled = await page.evaluate("""(code) => {
        const cm = document.querySelector('.CodeMirror');
        if (cm?.CodeMirror) { cm.CodeMirror.setValue(code); return 'cm'; }
        const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
        if (ta) { ta.value = code; ta.dispatchEvent(new Event('input', {bubbles: true})); return 'ta'; }
        return 'nf';
    }""", code)

    # Activate
    await page.evaluate("""() => {
        const cb = document.querySelector('input[name="wpcode_active"]');
        if (cb && !cb.checked) cb.click();
    }""")

    # Save
    save_btn = await page.query_selector('#publish, input[name="button"][value="publish"]')
    if save_btn:
        await save_btn.click()
        await page.wait_for_load_state('networkidle')

    url = page.url
    snippet_id = None
    import re
    m = re.search(r'snippet_id=(\d+)', url)
    if m:
        snippet_id = m.group(1)

    print(f'  Saved "{title}" — ID: {snippet_id} | code filled: {filled}')
    return snippet_id


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
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        print('Logged in')

        # === FIX #16 — Update Despre Noi via REST API ===
        print('\n=== Fix #16 — Despre Noi ===')
        result = await page.evaluate(f"""async () => {{
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/pages/{DESPRE_NOI_ID}', {{
                method: 'POST',
                headers: {{'X-WP-Nonce': nonce, 'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    content: {json.dumps(DESPRE_NOI_CONTENT)},
                    meta: {{
                        rank_math_description: {json.dumps(DESPRE_NOI_META)}
                    }}
                }})
            }});
            return {{status: res.status, body: (await res.text()).substring(0, 200)}};
        }}""")
        print(f'  REST update: {result["status"]}')
        if result['status'] == 200:
            print('  Content updated ✅')
        else:
            print(f'  Error: {result["body"]}')

        # Try updating Rank Math meta via separate post meta endpoint
        meta_result = await page.evaluate(f"""async () => {{
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/pages/{DESPRE_NOI_ID}', {{
                method: 'POST',
                headers: {{'X-WP-Nonce': nonce, 'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    meta: {{
                        rank_math_description: {json.dumps(DESPRE_NOI_META)},
                        _yoast_wpseo_metadesc: {json.dumps(DESPRE_NOI_META)}
                    }}
                }})
            }});
            const data = await res.json();
            return {{status: res.status, meta: data.meta}};
        }}""")
        print(f'  Meta update: {meta_result["status"]} | meta keys: {list((meta_result.get("meta") or {}).keys())[:5]}')

        # === FIX #14 — ItemList Schema snippet ===
        print('\n=== Fix #14 — ItemList Schema ===')
        await save_wpcode_snippet(page, 'Fix #14 - ItemList Schema categorii', ITEMLIST_SNIPPET)

        # === FIX #19 — llms.txt snippet ===
        print('\n=== Fix #19 — llms.txt ===')
        llms_id = await save_wpcode_snippet(page, 'Fix #19 - llms.txt', LLMS_SNIPPET)

        # Trigger llms.txt creation by visiting admin
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')
        await page.wait_for_timeout(2000)

        # Verify llms.txt exists
        llms_check = await page.evaluate("""async () => {
            const res = await fetch('/llms.txt');
            return {status: res.status, body: (await res.text()).substring(0, 100)};
        }""")
        print(f'\nllms.txt: {llms_check["status"]} — {llms_check["body"][:80]}')

        # Verify Despre Noi
        despre_check = await page.evaluate("""async () => {
            const res = await fetch('/despre-noi/');
            const html = await res.text();
            return html.includes('MAC') && html.includes('Terra Canis') ? 'brands present ✅' : 'brands missing ❌';
        }""")
        print(f'Despre Noi brands: {despre_check}')

        # Verify ItemList on category page
        itemlist_check = await page.evaluate("""async () => {
            const res = await fetch('/caini/');
            const html = await res.text();
            return html.includes('ItemList') ? 'ItemList schema present ✅' : 'ItemList missing ❌';
        }""")
        print(f'ItemList schema /caini/: {itemlist_check}')

        await browser.close()

asyncio.run(main())
