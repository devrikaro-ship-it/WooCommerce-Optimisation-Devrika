# Best Practices — WooCommerce Automation Devrika

Metode corecte de lucru validate in productie pe clienti reali.
Citeste inainte de orice sesiune de implementare.

---

## #1 — Playwright: sesiune persistenta (nu newContext)

**Intotdeauna `launchPersistentContext`:**
```javascript
const context = await chromium.launchPersistentContext('/tmp/CLIENT-session', {
  headless: false,
  slowMo: 200
});
const page = await context.pages()[0] || await context.newPage();
```

**De evitat:**
- `browser.launch()` + `browser.newContext()` — sesiune fresh fara cookies, forteaza login la fiecare rulare
- `headless: true` — blocheaza logarea pe site-urile WordPress cu protectii anti-bot
- Timeout < 10000ms pe submit login

**Daca sesiunea anterioară a crashat:**
```bash
rm -f /tmp/CLIENT-session/Singleton*
```

---

## #2 — Playwright: un singur fisier per client

Toate operatiile pe acelasi client → acelasi `main()`, acelasi fisier.

**Nu crea fisiere noi pentru fiecare sub-task.**
Adauga pasi secventiali in `main()` existent.

```javascript
async function main() {
  // Pas 1: login
  // Pas 2: verifica snippeturi
  // Pas 3: dezactiveaza duplicate
  // Pas 4: creeaza snippet nou
  // Pas 5: verifica vizual
}
main().catch(console.error);
```

---

## #3 — WPCode: dezactivare corecta via AJAX

**Metoda recomandata (din contextul paginii wp-admin via Playwright):**
```javascript
const fd = new FormData();
fd.append('action', 'wpcode_activate_snippet');
fd.append('id', SNIPPET_ID);        // OBLIGATORIU — fara asta = snippet NOU
fd.append('activate', '0');         // 0 = dezactiv, 1 = activ
fd.append('nonce', window.wpcode_vars?.nonce || '');
const r = await fetch('/wp-admin/admin-ajax.php', { method: 'POST', body: fd });
const json = await r.json();
// Asteapta: { success: true }
```

**De evitat:**
- Form POST fara `snippet_id` → WPCode creeaza snippet NOU in loc sa editeze
- REST API `/wp-json/wp/v2/wpcode/{id}` → 404, WPCode nu expune endpoint REST
- Dezactivarea a 30+ snippeturi in aceeasi sesiune → sesiunea WP expira

---

## #4 — WPCode: regula unui singur snippet per functionalitate

Flux corect pentru update snippet:
1. Identifica ID-ul snippet-ului existent din lista WPCode
2. Dezactiveaza-l (metoda #3)
3. Creeaza versiunea noua si activeaz-o
4. Verifica vizual pe site (metoda #5)
5. Sterge vechiul snippet din lista

**Niciodata:** nu crea versiunea noua inainte sa dezactivezi vechea versiune.
**Niciodata:** nu lasa mai mult de 1 snippet activ per functionalitate.

---

## #5 — WPCode: navigare admin corecta

```javascript
// URL corect pentru snippeturi inactive:
'https://[client]/wp-admin/admin.php?page=wpcode-snippet-manager&view=inactive'
// NU: ?status=inactive — returneaza 0 rows

// Row actions sunt hidden CSS — forteaza vizibilitate:
document.querySelectorAll('.row-actions').forEach(el => el.style.visibility = 'visible');

// Selector pentru ID-uri snippeturi:
document.querySelectorAll('input[name="snippet_id[]"]')
// NU: tr[id^="snippet-"]
```

---

## #6 — WPCode: snippet-uri PHP

**Regula critica:** Nu adauga `<?php` in snippeturi PHP.
WPCode adauga automat tag-ul. Un al doilea tag = fatal parse error = site down.

**Preferinta:** CSS/JS in loc de PHP ori de cate ori posibil.
PHP = risc syntax error, CSS/JS = safe.

**Snippet PHP corect in WPCode:**
```php
// Scrie direct codul, fara <?php la inceput:
add_filter('woocommerce_structured_data_product', function($markup) {
    // codul tau
    return $markup;
});
```

---

## #7 — CSS: selectoare sigure pentru imagini produse

```css
/* CORECT — specific la grid produse */
li.product .woocommerce-loop-product__link img { object-fit: contain !important; }

/* GRESIT — prinde logo, slider, hero */
.product-image img { }
img { }
```

**Guard pentru a exclude logo si header:**
```javascript
if (img.closest('header, nav, .site-branding, .logo, #masthead, 
    .elementor-widget-theme-etheme_site-logo')) continue;
```

**Logo XStore — selector corect:**
```css
.elementor-widget-theme-etheme_site-logo img {
  max-height: 80px !important;
  width: auto !important;
  max-width: 220px !important;
}
```

---

## #8 — CSS vs JS pentru style override

**Regula:** CSS `!important` de specificitate inalta > JS pentru orice style fix.

```css
/* Preferat: */
li.product img { object-fit: contain !important; }

/* Ultima solutie (bate orice CSS inclusiv inline): */
element.style.setProperty('object-fit', 'contain', 'important');
```

**Nu folosi MutationObserver care:**
- Urmareste `style` si face `removeProperty()` → infinite loop
- Observa `document.body` cu `attributes` fara guard de self-loop

**MutationObserver corect (daca e absolut necesar):**
```javascript
observer.observe(container, { childList: true, subtree: true }); // NU attributes
```

---

## #9 — Snippet-uri ONE-SHOT si DEBUG

**Orice snippet temporar se dezactiveaza IMEDIAT dupa rulare.**

Flux:
1. Creeaza snippet cu prefix `ONE-SHOT:` sau `DEBUG:` in titlu
2. Activeaza → asteapta o cerere HTTP
3. Verifica log/rezultat
4. **Dezactiveaza imediat**
5. Sterge dupa o saptamana

---

## #10 — GitHub API: creare vs. actualizare fisier

**Creare fisier nou (fara SHA):**
```javascript
await octokit.rest.repos.createOrUpdateFileContents({
  owner, repo, path,
  message: 'commit msg',
  content: Buffer.from(content).toString('base64')
});
```

**Actualizare fisier existent (SHA obligatoriu):**
```javascript
const { data } = await octokit.rest.repos.getContent({ owner, repo, path });
await octokit.rest.repos.createOrUpdateFileContents({
  owner, repo, path,
  message: 'commit msg',
  content: Buffer.from(newContent).toString('base64'),
  sha: data.sha  // OBLIGATORIU — fara SHA la update = eroare 422
});
```

---

## #11 — Verificare vizuala dupa orice modificare CSS/JS

```javascript
// Adauga ?nocache=1 pentru a ocoli cache-ul
await page.goto('https://[client]/[categorie]/?nocache=1', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(3000);

// Verifica object-fit pe imaginile de produs
const objectFit = await page.evaluate(() => {
  const img = document.querySelector('li.product img');
  return img ? getComputedStyle(img).objectFit : 'NOT FOUND';
});
console.log('object-fit:', objectFit); // trebuie: 'contain'
await page.screenshot({ path: 'verify.png' });
```

**Verifica intotdeauna pe:** homepage, categorie principala, pagina produs, mobile viewport.

---

## #12 — Cache WooCommerce

| Hosting | Comportament | Bypass |
|---------|-------------|--------|
| SiteGround LiteSpeed | Server-side, utilizatori logati il ocolesc | `?nocache=1` |
| Kinsta | Endpoint REST propriu de flush | Doc Kinsta |
| WP Rocket | WP AJAX flush — poate returna 400 fara nonce | Dashboard WP Rocket |

Verificarile din wp-admin vad mereu versiunea live (utilizator logat = bypass cache automat).

---

## #13 — Audit snippeturi WPCode — metoda corecta

**REGULA CRITICA:** WPCode UI afisa maxim 20 snippeturi per pagina. `per_page=100` din URL e ignorat. Nu te baza pe UI pentru numarul real.

**Metoda corecta — PHP snippet one-shot:**
```php
global $wpdb;
$rows = $wpdb->get_results(
  "SELECT ID, post_title FROM {$wpdb->posts} 
   WHERE post_type='wpcode' AND post_status='publish' 
   ORDER BY ID ASC"
);
$out = array_map(fn($r) => ['id'=>$r->ID, 'name'=>$r->post_title], $rows);
file_put_contents(WP_CONTENT_DIR.'/wpcode-audit.json', json_encode($out));
```

**Audit lunar:**
1. Ruleaza query-ul de mai sus
2. Dezactiveaza orice cu `ONE-SHOT:` sau `DEBUG:` in titlu
3. Identifica duplicate (titluri identice sau cod identic)
4. Identifica conflicte (`cover` vs `contain` simultan)
5. Consolideaza grupuri per functionalitate (footer, sort, contain etc.)
6. Pastreaza maxim 15 active (ideal sub 10)
7. Documenteaza in `clients/[client]/DOCUMENTATION.md`

---

## #14 — Script Playwright: o singura sesiune lunga

**Regula:** Scrie TOTI pasii in `main()` INAINTE de prima rulare. Ruleaza o singura data. Nu modifica si nu restarta scriptul intre pasi — fiecare restart = browser nou.

```javascript
async function main() {
  const context = await chromium.launchPersistentContext(SESSION_DIR, { headless: false });
  const page = context.pages()[0] || await context.newPage();
  await ensureLoggedIn(page);

  // Pas 1
  // Pas 2
  // Pas 3
  // ... toti pasii aici, in secventa

  await context.close(); // DOAR la final absolut
}
```

**Gresit:** kill script → adauga pas → restart → browser nou → kill → adauga pas → restart...
**Corect:** planifica toti pasii → scrie tot → ruleaza o data → done.


---

## #15 — WPCode: tip corect per caz de utilizare

Nu folosi PHP-type pentru stiluri. Foloseste tipul nativ WPCode:

| Ce vrei sa faci | Tip snippet |
|-----------------|-------------|
| Culori, layout, fonturi, spacing | **CSS** |
| Dropdown, carousel, DOM interactions | **JS** |
| WC hooks/filters, body_class, schema conditionala | **PHP** |
| PHP care face doar `echo '<style>...</style>'` | ❌ Gresit — converteste la CSS |
| PHP care face doar `echo '<script>...</script>'` | ❌ Gresit — converteste la JS |

**Ordinea corecta la inlocuire snippet:**
1. Creezi noul snippet
2. Verifici ca merge
3. Abia apoi dezactivezi/stergi cel vechi

---

## #16 — PHP hooks WooCommerce: guard obligatoriu + cache

Orice hook PHP care face DB queries trebuie sa aiba:

**1. Guard de pagina** (nu rula pe tot site-ul):
```php
add_action('wp_head', function() {
    if (!is_product_category()) return; // fara asta ruleaza pe TOATE paginile
    // ...
});
```

**2. Cache pentru queries grele:**
```php
// Transient = persistent intre requests (pentru schema, related products)
$cache_key = 'prefix_' . $term->term_id;
$data = get_transient($cache_key);
if ($data === false) {
    $data = get_posts([...]); // query greu
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
}

// wp_cache = request-level doar (pentru deduplicare in acelasi request)
$cached = wp_cache_get($key, 'grup');
if ($cached === false) {
    $cached = /* calcul */;
    wp_cache_set($key, $cached, 'grup', 3600);
}
```

---

## #17 — Related products: 1 filter, get_objects_in_term

Nu pune multiple filtre pe `woocommerce_related_products`. Un singur filter, optimizat:

```php
// GRESIT: wp_get_post_terms() per produs = N queries
foreach ($related_posts as $rid) {
    $terms = wp_get_post_terms($rid, 'product_cat', ['fields' => 'ids']); // 1 query per produs!
}

// CORECT: get_objects_in_term = 1 query pentru toti
$all_in_cats = get_objects_in_term($valid_cat_ids, 'product_cat'); // 1 query
$filtered = array_intersect($related_posts, $all_in_cats);          // PHP, 0 queries
```

---

## #18 — Schema/JSON-LD: hook direct, nu ob_start

**Gresit (lent):**
```php
add_action('template_redirect', function() {
    ob_start(function($html) {
        return preg_replace_callback('|<script.*?ld\+json.*?>(.*?)</script>|s', function($m) {
            // modifica $m[1] ...
        }, $html);
    });
});
```
Bufferizeaza tot HTML-ul, ruleaza regex pe output complet.

**Corect (rapid):**
```php
// Rank Math
add_filter('rank_math/json_ld', function($data, $jsonld) {
    if (!is_product()) return $data;
    foreach ($data as &$item) {
        if (($item['@type'] ?? '') === 'Product') {
            // modifica direct $item['offers'] etc.
        }
    }
    return $data;
}, 99, 2);

// Yoast
add_filter('wpseo_schema_graph', function($data) { ... });

// WooCommerce
add_filter('woocommerce_structured_data_product', function($markup) { ... });
```
