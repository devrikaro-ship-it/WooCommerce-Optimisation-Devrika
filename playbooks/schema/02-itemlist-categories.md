# ItemList Schema pe Pagini Categorie

## Ce face
Injecteaza schema `ItemList` in `<head>` pe paginile de categorie WooCommerce, listând primele 10 produse cu pozitie, URL si nume. Permite Google sa afiseze un carousel de produse in SERP direct din pagina de categorie.

## Cand se aplica
- Site-uri WooCommerce cu categorii de produse bine populate (minim 5-10 produse per categorie)
- Cand Google Rich Results Test nu detecteaza schema ItemList pe paginile categorie
- Nu se aplica pe pagini de produs individual (au schema Product proprie)

## Inainte sa incepi
- Verifica daca Rank Math genereaza deja ItemList: https://search.google.com/test/rich-results?url=https://domain.ro/categorie/
- Identifica categoriile principale (slug-urile)
- Verifica ca produsele din categorii au imagini si titluri complete

## Implementare

### Pasul 1 — Creeaza snippet PHP in WPCode
- PHP type, Run Everywhere

### Pasul 2 — Adauga codul cu transient cache (OBLIGATORIU)

### Pasul 3 — Activeaza + Salveaza

### Pasul 4 — Verifica pe Google Rich Results Test

## Cod

```php
// ItemList Schema pe pagini categorie WooCommerce — cu transient cache 1h
add_action('wp_head', function() {
    if (!function_exists('is_product_category') || !is_product_category()) return;

    $term = get_queried_object();
    if (!$term || !isset($term->term_id)) return;

    // Cache: evita 11 DB queries per request
    $cache_key = 'itemlist_schema_' . $term->term_id;
    $schema_html = get_transient($cache_key);

    if ($schema_html === false) {
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
            $items[] = [
                '@type'    => 'ListItem',
                'position' => $i + 1,
                'url'      => get_permalink($p->ID),
                'name'     => $obj->get_name(),
            ];
        }

        if (empty($items)) return;

        $schema = [
            '@context'        => 'https://schema.org',
            '@type'           => 'ItemList',
            'name'            => $term->name,
            'url'             => get_term_link($term),
            'numberOfItems'   => count($items),
            'itemListElement' => $items,
        ];

        $schema_html = '<script type="application/ld+json">'
            . wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
            . '</script>';

        set_transient($cache_key, $schema_html, HOUR_IN_SECONDS);
    }

    echo $schema_html . "\n";
}, 10);
```

**Invalidare cache cand se actualizeaza produsele dintr-o categorie:**
```php
// Sterge transient cand un produs e salvat
add_action('save_post_product', function($post_id) {
    $terms = get_the_terms($post_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) return;
    foreach ($terms as $term) {
        delete_transient('itemlist_schema_' . $term->term_id);
    }
});
```

## Cum se aplica corect (Best Practice)
- **Transient cache este OBLIGATORIU** — fara el, fiecare request pe o pagina categorie face 11 DB queries (`get_posts` + 10x `wc_get_product`)
- `HOUR_IN_SECONDS` e suficient — produsele nu se schimba mai des de atat
- Adauga si invalidarea cache la `save_post_product` daca site-ul are produse actualizate frecvent
- Verifica ca `$items` nu e gol inainte de a genera schema — categorii fara produse ar genera schema invalida
- Nu adauga mai mult de 10 produse — Google nu indexeaza mai mult in carousel

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Fara transient cache | 11 DB queries per request pe fiecare categorie | Wraps in get_transient/set_transient |
| `wc_get_product` in loop fara cache | N queries suplimentare | Alternativ: `get_post_meta` direct pentru datele necesare |
| Schema generata si de Rank Math simultan | Duplicate schema ItemList | Dezactiveaza ItemList din Rank Math daca il genereaza |
| `get_term_link` intoarce WP_Error | Schema cu URL invalid | Adauga `if (!is_wp_error(get_term_link($term)))` |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/categorie/
- Cauta tipul `ItemList` cu `itemListElement` populat
- `curl -s https://domain.ro/categorie/ | grep -o '"@type":"ItemList"'`
- Dupa 2-4 saptamani: cauta `domain.ro + categorie` in Google si verifica daca apare carousel

## Timp estimat
30 minute
