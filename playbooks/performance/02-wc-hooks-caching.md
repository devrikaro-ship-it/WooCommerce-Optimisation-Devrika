# WC Hooks — Guard + Cache + Query Optimizare

## Ce face
Defineste pattern-ul corect pentru orice hook WooCommerce cu DB queries: guard de pagina obligatoriu, cache cu transient sau wp_cache, si `get_objects_in_term` in loc de queries in bucla.

## Reguli

### 1. Guard de pagina — OBLIGATORIU

```php
// Fara guard → ruleaza pe TOATE paginile → overhead pe fiecare request
add_action('wp_head', function() {
    // GRESIT: fara guard
    $products = get_posts([...]); // ruleaza pe homepage, blog, contact, etc.
});

// CORECT
add_action('wp_head', function() {
    if (!is_product()) return;          // doar pe pagini produs
    if (!is_product_category()) return; // doar pe categorii
    if (!is_shop()) return;             // doar pe shop page
});
```

### 2. Cache — OBLIGATORIU pentru queries grele

```php
// Request-level cache (wp_cache) — se pierde la sfarsitul request-ului
$cache_key = 'my_data_' . $product_id;
$data = wp_cache_get($cache_key, 'my_group');
if ($data === false) {
    $data = /* query greu */;
    wp_cache_set($cache_key, $data, 'my_group', 3600);
}

// Persistent cache (transient) — supravietuieste intre requests
$cache_key = 'my_schema_' . $term_id;
$data = get_transient($cache_key);
if ($data === false) {
    $data = /* query greu */;
    set_transient($cache_key, $data, HOUR_IN_SECONDS);
}
```

**Cand folosesti ce:**
| Tip cache | Cand |
|-----------|------|
| `wp_cache` | Deduplicare in acelasi request (hook apelat de mai multe ori) |
| `transient` | DB queries grele in wp_head (schema, related products) |
| Niciunul | Queries triviale (1-2 query-uri, fara bucla) |

### 3. get_objects_in_term — 1 query in loc de N

```php
// GRESIT: 1 query per produs related = N queries
foreach ($related_posts as $rid) {
    $terms = wp_get_post_terms($rid, 'product_cat', ['fields' => 'ids']); // query!
    if (array_intersect($valid_cats, $terms)) $filtered[] = $rid;
}

// CORECT: 1 query total
$all_in_cats = get_objects_in_term($valid_cats, 'product_cat'); // 1 query SQL
$filtered = array_intersect($related_posts, $all_in_cats);       // PHP, 0 queries
```

### 4. Max 1 filter per hook WooCommerce

```php
// GRESIT: 3 filtre pe acelasi hook = queries triple
add_filter('woocommerce_related_products', 'filter_by_l1', 10, 3);
add_filter('woocommerce_related_products', 'filter_by_species', 10, 3);
add_filter('woocommerce_related_products', 'filter_by_subcategory', 10, 3);

// CORECT: 1 filter care face tot
add_filter('woocommerce_related_products', 'filter_consolidated', 10, 3);
```

## Pattern complet recomandat

```php
add_filter('woocommerce_related_products', function($related_posts, $product_id, $args) {

    // 1. Cache request-level
    $cache_key = 'related_' . $product_id;
    $cached = wp_cache_get($cache_key, 'wc_related');
    if ($cached !== false) return $cached;

    // 2. Guard: produsul trebuie sa aiba categorii
    $terms = get_the_terms($product_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) {
        wp_cache_set($cache_key, $related_posts, 'wc_related');
        return $related_posts;
    }

    // 3. Logica de filtrare (fara queries in bucla)
    $valid_cats = [/* ... */]; // calculeaza categoriile valide
    $all_in_cats = get_objects_in_term($valid_cats, 'product_cat'); // 1 query
    $filtered = array_intersect($related_posts, $all_in_cats);       // PHP

    // 4. Fallback daca rezultat gol
    if (empty($filtered)) {
        wp_cache_set($cache_key, $related_posts, 'wc_related');
        return $related_posts;
    }

    // 5. Cache si return
    $result = array_slice(array_values($filtered), 0, 4);
    wp_cache_set($cache_key, $result, 'wc_related');
    return $result;

}, 10, 3);
```

## Verificare
- Query Monitor plugin: verifica numarul de queries pe paginile afectate
- Inainte/dupa optimizare: compara numarul de queries
- Target: sub 30 queries per pagina (WC default e ~25 fara snippeturi suplimentare)

## Timp estimat
30-60 minute per snippet optimizat
