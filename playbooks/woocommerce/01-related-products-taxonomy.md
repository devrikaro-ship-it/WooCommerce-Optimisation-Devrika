# Related Products Filter pe Taxonomie

## Ce face
Filtreaza produsele recomandate ("Related products") pe pagina de produs astfel incat sa apara doar produse din aceeasi taxonomie/categorie (ex: aceeasi specie animala, aceeasi categorie principala). Previne recomandarile irelevante cross-categoria.

## Cand se aplica
- Site-uri WooCommerce cu categorii distincte (ex: caini/pisici, copii/adulti, sport/casual)
- Cand related products afiseaza produse din categorii complet diferite
- **Max 1 filter activ pe `woocommerce_related_products`** — nu adauga mai multe filtre pe acelasi hook

## Inainte sa incepi
- Identifica slugurile categoriilor L1 (nivel 1, fara parinte) care definesc "speciile" sau grupele
- Verifica ca nu exista deja alte filtre pe `woocommerce_related_products` active:
  ```
  WPCode > cauta "woocommerce_related_products" in snippeturi active
  ```
- **Dezactiveaza orice filtru existent inainte de a adauga acesta**

## Implementare

### Pasul 1 — Dezactiveaza filtre existente pe hook
Cauta si dezactiveaza TOATE snippeturile cu `woocommerce_related_products`.

### Pasul 2 — Identifica slugurile categoriilor L1
```php
// Temporar in WPCode pentru debug:
add_action('wp_footer', function() {
    if (!is_product()) return;
    $terms = get_the_terms(get_the_ID(), 'product_cat');
    if ($terms) foreach ($terms as $t) {
        echo $t->slug . ' (parent: ' . $t->parent . ')<br>';
    }
});
```

### Pasul 3 — Creeaza snippet PHP in WPCode

### Pasul 4 — Activeaza si verifica pe o pagina produs

## Cod

```php
// Related products filtrate pe taxonomie — consolida, cached
// Inlocuieste $species_slugs cu slugurile categoriilor L1 ale clientului
add_filter('woocommerce_related_products', function($related_posts, $product_id, $args) {

    // Cache per produs (request-level)
    $cache_key = 'related_filtered_' . $product_id;
    $cached = wp_cache_get($cache_key, 'wc_related');
    if ($cached !== false) return $cached;

    // Slugurile categoriilor L1 care definesc "grupele" de produse
    // Ajusteaza la structura categoriilor clientului
    $group_slugs = ['caini', 'pisici', 'pasari-rozatoare']; // AJUSTEAZA

    $terms = get_the_terms($product_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) {
        wp_cache_set($cache_key, $related_posts, 'wc_related', 3600);
        return $related_posts;
    }

    // Gaseste categoria L1 (grup) a produsului curent
    $group_ids = [];
    foreach ($terms as $t) {
        $ancestors = array_merge([$t->term_id], get_ancestors($t->term_id, 'product_cat'));
        foreach ($ancestors as $anc_id) {
            $anc = get_term($anc_id, 'product_cat');
            if ($anc && !is_wp_error($anc) && in_array($anc->slug, $group_slugs)) {
                $group_ids[] = $anc->term_id;
            }
        }
    }
    $group_ids = array_unique($group_ids);

    // Daca produsul nu e in niciun grup definit: returneaza related normal
    if (empty($group_ids)) {
        wp_cache_set($cache_key, $related_posts, 'wc_related', 3600);
        return $related_posts;
    }

    // Colecteaza toate cat IDs din grupurile gasite (L1 + subcategorii)
    $valid_cats = $group_ids;
    foreach ($group_ids as $gid) {
        $children = get_terms([
            'taxonomy'   => 'product_cat',
            'child_of'   => $gid,
            'fields'     => 'ids',
            'hide_empty' => false,
        ]);
        if (!is_wp_error($children)) {
            $valid_cats = array_merge($valid_cats, $children);
        }
    }
    $valid_cats = array_unique($valid_cats);

    // 1 query: toti post ID-urile din categoriile valide
    $all_in_group = get_objects_in_term($valid_cats, 'product_cat');
    if (is_wp_error($all_in_group)) {
        wp_cache_set($cache_key, $related_posts, 'wc_related', 3600);
        return $related_posts;
    }

    // Intersectie: related posts care sunt si in grup
    $filtered = array_values(array_filter(
        array_intersect($related_posts, $all_in_group),
        fn($id) => (int)$id !== (int)$product_id
    ));

    // Completeaza daca < 4 produse
    if (count($filtered) < 4) {
        $extra = get_posts([
            'post_type'      => 'product',
            'posts_per_page' => 8,
            'post__not_in'   => array_merge([$product_id], $filtered),
            'post_status'    => 'publish',
            'tax_query'      => [[
                'taxonomy' => 'product_cat',
                'field'    => 'term_id',
                'terms'    => $valid_cats,
                'operator' => 'IN',
            ]],
            'orderby' => 'rand',
            'fields'  => 'ids',
        ]);
        $filtered = array_unique(array_merge($filtered, $extra));
    }

    $result = array_slice(array_values($filtered), 0, 4);
    wp_cache_set($cache_key, $result, 'wc_related', 3600);
    return $result;

}, 10, 3);
```

## Cum se aplica corect (Best Practice)
- **Max 1 filter pe `woocommerce_related_products`** — filtrele se executa secvential, al doilea filtreaza output-ul primului, rezultat nepredictibil
- `get_objects_in_term()` = 1 query SQL pentru toti post ID-urile din N categorii; **nu** `wp_get_post_terms()` in bucla (N queries)
- `wp_cache_get/set` = request-level — suficient pentru a nu repeta calculul daca hook-ul e apelat de mai multe ori per request
- Daca `$group_slugs` e gol sau produsul nu are categorie din lista: returneaza related normal (nu gol)
- Ajusteaza `posts_per_page: 8` si limita finala `array_slice(..., 0, 4)` per preferinta clientului

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Filtre multiple pe acelasi hook | Queries triple, rezultate gresita | Dezactiveaza toate, lasa doar acesta |
| `wp_get_post_terms` in bucla pentru fiecare related | N queries = lent | Inlocuieste cu `get_objects_in_term` + `array_intersect` |
| `$group_slugs` gresit (slug cu diacritice) | Nu gaseste niciun grup, returneaza related goale | Verifica slug-ul exact din WC > Categorii |
| Related goale pe toate produsele | UX broken | Adauga fallback: daca `$filtered` gol, returneaza `$related_posts` original |

## Verificare
- Pagina produs "caini": related products = doar produse din categoria caini
- Pagina produs "pisici": related products = doar produse din categoria pisici
- Produs in categorie necunoscuta: related products normale (fallback)
- DevTools Network: nu exista query-uri lente de taxonomy

## Timp estimat
30 minute
