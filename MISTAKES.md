# Greseli Inregistrate — WooCommerce Automation Devrika

Fiecare greseala documentata cu context, efect negativ si lectie. 
Citeste inainte de orice implementare noua.

> Lectiile din aceste greseli sunt integrate si in `CHECKLIST-TEMPLATE.md` si `BEST-PRACTICES.md`.

---

## GRESEALA #1 — Snippeturi one-shot lasate active dupa executie

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Snippeturi PHP de tip one-shot (debug, flush cache, modificare optiuni) au ramas active in WPCode dupa ce si-au facut treaba.

**Efect negativ:**
- Flush sitemap rula la FIECARE request → cache-ul sters continuu
- Script dump debug scria fisiere pe server la fiecare vizita
- Overhead DB inutil pe fiecare request

**Regula:** Orice snippet cu prefix `ONE-SHOT:` sau `DEBUG:` se dezactiveaza IMEDIAT dupa prima rulare confirmata.

---

## GRESEALA #2 — Duplicate snippeturi CSS/JS acumulate

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** La fiecare iteratie de fix, versiunea noua a fost salvata ca snippet nou fara dezactivarea versiunii vechi. Rezultat: 5 CSS identice + 4 JS identice, toate active simultan.

**Efect negativ:**
- CSS incarcata de 5x per pagina
- MutationObserver JS rula de 4x in paralel → conflict intre versiuni
- Logo distorsionat din conflictul versiunilor
- Performanta degradata

**Regula:** Inainte sa creezi un snippet care inlocuieste altul, dezactiveaza/sterge-l pe cel vechi. 1 snippet activ per functionalitate.

---

## GRESEALA #3 — Dezactivare WPCode fara `snippet_id`

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Incercare de dezactivare a 13 snippeturi prin form POST fara campul `snippet_id` in body. WPCode a interpretat ca cerere de CREARE snippet nou.

**Efect negativ:** Repo snippeturi: 94 → 107. Cleanup suplimentar 2h.

**Cod gresit:**
```javascript
const fd = new FormData();
fd.append('wpcode_snippet_title', title);
fd.append('wpcode_snippet_code', code);
// LIPSESTE: fd.append('snippet_id', id)
fd.append('button', 'publish');
await fetch(window.location.href, { method: 'POST', body: fd });
```

**Regula:** Dezactivare corecta = AJAX pe `/wp-admin/admin-ajax.php` cu `snippet_id` explicit. Vezi BEST-PRACTICES.md #3.

---

## GRESEALA #4 — Playwright headless blocheaza login WP

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Scripturi cu `headless: true` au esuat la login, ramanand blocate pe pagina de login → timeout.

**Efect negativ:** Scripturi care par sa ruleze dar nu fac nimic.

**Regula:** Intotdeauna `headless: false` + `slowMo: 200` pentru login WordPress.

---

## GRESEALA #5 — `waitForURL` cu functie lambda fara `.toString()`

**Proiect:** puria.ro | **Data:** Mai 2026

**Eroare:** `TypeError: url.includes is not a function`

**Cod gresit:**
```javascript
await page.waitForURL(url => !url.includes('/login'));
```

**Cod corect:**
```javascript
await page.waitForURL(url => !url.toString().includes('/login'));
// sau glob:
await page.waitForURL('**/wp-admin/**');
```

---

## GRESEALA #6 — `<?php` dublu in snippeturi WPCode

**Proiect:** orice client | **Risc:** CRITIC

**Ce se intampla:** WPCode adauga automat `<?php` la inceputul snippeturilor PHP. Daca adaugi si tu manual `<?php`, rezulta tag dublu = fatal parse error = **site down**.

**Efect negativ:** Site inaccesibil pana la dezactivare manuala din DB sau FTP.

**Regula:** Nu adauga niciodata `<?php` in snippeturi PHP WPCode. Scrie codul direct fara tag de deschidere.

---

## GRESEALA #7 — MutationObserver pe `style` cu `removeProperty`

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** MutationObserver care urmarea schimbarile de `style` si apela `removeProperty()` pe elemente a creat un infinite loop cu alte MO active pe pagina.

**Efect negativ:** UI thread blocat → site **unclickable**. Utilizatorii nu puteau apasa niciun element.

**Regula:**
- Nu folosi MO care observa `attributes` pe style si face modificari → se re-declanseaza la propriile modificari
- Structura corecta MO: `observe(el, { childList: true, subtree: true })`
- Preferat: CSS `!important` de specificitate inalta, nu JS

---

## GRESEALA #8 — Selector broad CSS prinde logo si header

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Selector `.product-image img` sau `img` aplicat pentru `object-fit: contain` a prins si logo-ul din header.

**Efect negativ:** Logo distorsionat (`contain` pe un logo care are alte proportii decat gridul de produse).

**Regula:**
- Mereu `li.product` sau `.woocommerce-loop-product__link` ca parent
- Adauga guard de excludere: `img.closest('header, nav, .site-branding, #masthead')`
- Logo: selector separat, intentionat, cu `max-height` explicit

---

## GRESEALA #9 — Fara sesiune persistenta Playwright

**Proiect:** orice client | **Data:** Mai 2026

**Ce s-a intamplat:** Scripturi cu `browser.launch()` + `browser.newContext()` forteaza login la fiecare rulare. In sesiuni lungi, sesiunea WP expira → actiunile urmatoare esueaza silentios.

**Regula:** Intotdeauna `chromium.launchPersistentContext('/tmp/CLIENT-session', ...)`. Login o singura data, sesiune reutilizata.

---

## GRESEALA #10 — GitHub API update fara SHA

**Proiect:** puria.ro | **Data:** Mai 2026

**Eroare:** `422 Unprocessable Entity`

**Ce s-a intamplat:** Actualizarea unui fisier existent in GitHub via API fara a include SHA-ul curent al fisierului.

**Regula:** La update fisier existent, fetui intai `GET /contents/path` pentru SHA, includ-o in body la PUT. Vezi BEST-PRACTICES.md #10.

---

## Template — adauga greseala noua

## GRESEALA #11 — WPCode UI arata doar 20 snippeturi, nu toate active

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** WPCode afisa 20 snippeturi per pagina in admin. Am presupus ca sunt toate. In realitate erau 56 active. Parametrul `per_page=100` din URL e ignorat de WPCode.

**Efect negativ:** Audit incomplet — 36 snippeturi invizibile, inclusiv ONE-SHOT-uri periculoase active.

**Regula:** Auditul WPCode se face via PHP snippet cu query direct pe `wp_posts`:
```php
$rows = $wpdb->get_results("SELECT ID, post_title FROM {$wpdb->posts} WHERE post_type='wpcode' AND post_status='publish' ORDER BY ID ASC");
```
Niciodata nu te baza pe UI pentru a cunoaste numarul real de snippeturi active.

---

## GRESEALA #12 — Script Playwright restartat pentru fiecare pas = browser nou la fiecare rulare

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** La fiecare pas nou (verifica, fix, verifica din nou), am modificat scriptul si l-am restartat. Fiecare restart = browser nou, chiar daca `launchPersistentContext` refoloseste profilul.

**Efect negativ:** 10+ ferestre Chrome deschise succesiv, utilizatorul frustrat, context pierdut intre pasi.

**Regula:** Scrie TOTI pasii in `main()` INAINTE de prima rulare. Ruleaza o singura data. `context.close()` doar la finalul absolut. Nu modifica si nu restarta scriptul intre pasi.

---

## GRESEALA #13 — CSS cover activ simultan cu CSS contain = conflict silentios

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Snippeturi CSS vechi cu `object-fit: cover !important` (248076, 248078) au ramas active dupa adaugarea snippeturilor cu `contain`. Ambele rulau simultan.

**Efect negativ:** Comportament impredictibil — unele imagini cover, altele contain, depindea de ordinea de incarcare CSS.

**Regula:** La orice modificare `object-fit`, cauta si dezactiveaza TOATE snippeturile cu `cover` sau `contain` pe imagini inainte de a adauga unul nou. Un singur snippet activ per proprietate CSS.

---

## GRESEALA #14 — PHP snippet cu `echo '<style>'` in loc de CSS-type

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Snippeturi de footer (248053–248058, apoi 248265/267/268) au fost create ca PHP-type cu `add_action('wp_head', function() { echo '<style>...</style>'; })`. Dezactivate pentru ca faceau site-ul lent.

**Efect negativ:** Dezactivarea a lasat footrul fara niciun CSS activ. Site broken. Debugging 2h ca sa gasim cauza.

**Regula:** Orice snippet care face DOAR styling → tip **CSS** nativ in WPCode, nu PHP cu echo.

| Caz | Tip corect |
|-----|-----------|
| Culori, layout, fonturi | **CSS** |
| Interactiuni DOM | **JS** |
| WC hooks, filters, body_class | **PHP** |
| PHP care face doar `echo '<style>'` | **Gresit → converteste la CSS** |

---

## GRESEALA #15 — Acelasi WC hook filtrat de 3 snippeturi diferite simultan

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** `woocommerce_related_products` filter inregistrat de 3 snippeturi (248059, 248063, 248064). Fiecare lua output-ul precedentului si il filtra din nou.

**Efect negativ:** Pe fiecare pagina produs: get_terms + get_ancestors + get_term (nested) + get_terms + wp_get_post_terms × N + get_posts × 3 runde = 20-30 DB queries doar pentru related products.

**Regula:** Max 1 filter activ per hook WooCommerce. Consolida logica in acelasi filter. Verifica ce filtre exista pe hook inainte sa adaugi unul nou.

---

## GRESEALA #16 — `ob_start` + regex pe tot HTML-ul paginii

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Schema Product fix (248032) folosea `ob_start()` cu callback pe `template_redirect` → bufferiza intregul HTML generat, rula `preg_replace_callback` + `json_decode` + `json_encode` pe output complet.

**Efect negativ:** Cel mai lent snippet din tot site-ul. Rula pe fiecare request de pagina produs, chiar si cu cache activ (la prima incarcate/cache miss).

**Regula:** Nu folosi `ob_start` pentru a modifica schema/JSON-LD. Foloseste hook-ul direct:
- Rank Math: `add_filter('rank_math/json_ld', function($data) {...}, 99, 2)`
- Yoast: `add_filter('wpseo_schema_graph', ...)`
- WooCommerce: `add_filter('woocommerce_structured_data_product', ...)`

---

## GRESEALA #17 — `wp_get_post_terms()` in bucla per produs

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Filtrul related products facea `wp_get_post_terms($rid, 'product_cat')` pentru FIECARE produs related ca sa verifice daca e din aceeasi specie. Cu 4 produse related = 4 query-uri suplimentare.

**Efect negativ:** O(n) queries unde n = numarul de produse related. Scala prost.

**Regula:** Inlocuieste cu `get_objects_in_term($cat_ids, 'product_cat')` care returneaza TOTI post ID din N categorii intr-un singur query SQL, apoi `array_intersect()` in PHP:

```php
$all_in_species = get_objects_in_term($valid_cats, 'product_cat'); // 1 query
$filtered = array_intersect($related_posts, $all_in_species);      // PHP, 0 queries
```

---

## GRESEALA #18 — DB queries in wp_head fara cache

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** ItemList Schema (248048) facea `get_posts()` + 10× `wc_get_product()` in `wp_head` pe fiecare pagina categorie. Total: 11 DB queries per request.

**Efect negativ:** Fiecare cache miss pe o pagina categorie = 11 queries suplimentare. Cu 20 categorii si trafic moderat = sute de queries evitabile.

**Regula:** Orice `get_posts()` / `wc_get_product()` / `get_terms()` in wp_head pe pagini publice → wraps obligatoriu in transient:

```php
$cache_key = 'puria_itemlist_' . $term->term_id;
$schema = get_transient($cache_key);
if ($schema === false) {
    // ... queries grele ...
    set_transient($cache_key, $schema, HOUR_IN_SECONDS);
}
echo $schema;
```

`wp_cache_get/set` = request-level (se pierde). `get_transient/set_transient` = persistent intre requests.

---

## GRESEALA #19 — Dezactivat snippet PHP fara replacement CSS gata

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Snippeturi PHP footer dezactivate pentru performanta (248265/267/268) fara a crea mai intai CSS-type replacement. Vechile snippeturi PHP (248053-248058) erau deja in trash.

**Efect negativ:** Footer fara niciun CSS activ. Culori disparute, layout broken, trust badges disparute. Client afectat.

**Regula:** Ordinea corecta la inlocuire snippet:
1. Creezi noul snippet (CSS-type sau versiunea imbunatatita)
2. Verifici ca functioneaza pe staging/preview sau cu cache bypass
3. **Abia apoi** dezactivezi/stergi cel vechi

Niciodata dezactivezi mai intai, creezi dupa.

---

```
## GRESEALA #N — [Titlu scurt descriptiv]

**Proiect:** [client.ro] | **Data:** [Luna Anul]

**Ce s-a intamplat:** [Context — ce actiune a declansat greseala]

**Efect negativ:** [Ce s-a stricat, cat a costat in timp/impact]

**Regula:** [Lectia — ce faci diferit data viitoare]
```
