# Body Class per Taxonomie

## Ce face
Adauga o clasa CSS pe `<body>` in functie de categoria/taxonomia produsului curent (ex: `body.puria-species-caini`, `body.puria-species-pisici`). Permite targetarea CSS specifica per categorie fara JS suplimentar.

## Cand se aplica
- Cand diferite categorii necesita stilizare CSS diferita (culori, layout, imagini)
- Cand vrei sa filtrezi elemente DOM pe baza categoriei fara JS complex
- Ruleza doar pe `is_product()` — zero impact pe alte pagini

## Inainte sa incepi
- Identifica slugurile categoriilor care necesita body class distincta
- Decide prefix-ul clasei (ex: `puria-species-`, `client-cat-`)

## Implementare

### Pasul 1 — Creeaza snippet PHP in WPCode
- PHP type

### Pasul 2 — Adauga codul (ajusteaza slugurile si prefix-ul)

### Pasul 3 — Verifica clasa in DevTools pe o pagina produs

## Cod

```php
// Adauga body class per specie/categorie pe paginile produs
add_filter('body_class', function($classes) {
    if (!is_product()) return $classes; // guard obligatoriu

    $product = wc_get_product(get_the_ID());
    if (!$product) return $classes;

    // Slugurile categoriilor L1 care definesc "grupa"
    $group_slugs = ['caini', 'pisici', 'pasari-rozatoare']; // AJUSTEAZA

    $terms = get_the_terms($product->get_id(), 'product_cat');
    if (!$terms || is_wp_error($terms)) return $classes;

    foreach ($terms as $t) {
        // Verifica termenul si toti stramosii
        $ancestors = array_merge([$t->term_id], get_ancestors($t->term_id, 'product_cat'));
        foreach ($ancestors as $anc_id) {
            $anc = get_term($anc_id, 'product_cat');
            if ($anc && !is_wp_error($anc) && in_array($anc->slug, $group_slugs)) {
                $classes[] = 'puria-species-' . $anc->slug; // ajusteaza prefix
                break 2;
            }
        }
    }

    return array_unique($classes);
});
```

**Utilizare in CSS dupa body class:**
```css
/* Stilizare specifica pentru pagina produs caini */
body.puria-species-caini .related-products-title::before {
    content: "🐕 ";
}

body.puria-species-pisici .related-products-title::before {
    content: "🐈 ";
}
```

**Utilizare in JS:**
```javascript
if (document.body.classList.contains('puria-species-caini')) {
    // logica specifica caini
}
```

## Cum se aplica corect (Best Practice)
- Guard `is_product()` obligatoriu — fara el ruleaza `get_the_terms()` pe TOATE paginile
- `array_unique` la final — previne clase duplicate daca produsul e in mai multe subcategorii ale aceluiasi grup
- Prefix unic (`puria-`, `client-`) — previne conflicte cu clasele WordPress/WooCommerce existente
- `break 2` = opreste cautarea dupa primul grup gasit — un produs nu poate fi simultan in doua grupe principale

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Fara guard `is_product()` | `get_the_terms` ruleaza pe toate paginile | Adauga guard la inceputul callback-ului |
| Prefix fara `-` (ex: `puriaspp`) | Clase CSS greu de citit si de targetat | Foloseste prefix cu `-`: `puria-species-` |
| Sluguri cu diacritice | Nu se potrivesc | Verifica slug exact din WC > Categorii (slugul e mereu fara diacritice in WP) |

## Verificare
- DevTools > `document.body.className` pe pagina produs → trebuie sa contina clasa adaugata
- Pagina produs din "Caini": `body.puria-species-caini` prezent
- Pagina homepage sau categorie: clasa absenta (guard functional)

## Timp estimat
15 minute
