# Transient Cache Pattern pentru DB Queries

## Ce face
Defineste pattern-ul corect pentru a cache-ui rezultatele query-urilor grele in `wp_head` sau hook-uri WordPress, folosind WordPress Transients API. Reduce drastic numarul de DB queries pe site-uri cu trafic.

## Cand folosesti transient vs wp_cache

| Situatie | Tip cache |
|----------|-----------|
| Schema JSON-LD generata din produse | **transient** (persistent) |
| Related products filtrate | **wp_cache** (request) sau **transient** |
| Date de categorie in wp_head | **transient** (persistent) |
| Deduplicare in acelasi request | **wp_cache** (request) |
| Date care se schimba rar (ore/zile) | **transient** |
| Date care se schimba des | **fara cache** sau TTL scurt |

## Pattern complet cu transient

```php
add_action('wp_head', function() {
    if (!is_product_category()) return; // guard obligatoriu

    $term = get_queried_object();
    if (!$term || !isset($term->term_id)) return;

    // 1. Cheie unica per entitate
    $cache_key = 'my_prefix_' . $term->term_id;

    // 2. Verifica cache
    $cached = get_transient($cache_key);

    if ($cached === false) {
        // 3. Query greu — ruleaza doar la cache miss
        $products = get_posts([
            'post_type'      => 'product',
            'posts_per_page' => 10,
            'post_status'    => 'publish',
            'tax_query'      => [[
                'taxonomy' => 'product_cat',
                'field'    => 'term_id',
                'terms'    => $term->term_id,
            ]],
        ]);

        if (empty($products)) return;

        // 4. Pregateste datele
        $output = '<div class="cached-result">';
        foreach ($products as $p) {
            $output .= '<span>' . esc_html($p->post_title) . '</span>';
        }
        $output .= '</div>';

        // 5. Salveaza in transient
        set_transient($cache_key, $output, HOUR_IN_SECONDS); // 1h
        $cached = $output;
    }

    echo $cached;
}, 10);
```

## Invalidarea cache-ului

```php
// Invalideaza transient cand termenul e actualizat
add_action('edited_term', function($term_id, $tt_id, $taxonomy) {
    if ($taxonomy !== 'product_cat') return;
    delete_transient('my_prefix_' . $term_id);
}, 10, 3);

// Invalideaza cand un produs din categoria respectiva e salvat
add_action('save_post_product', function($post_id) {
    $terms = get_the_terms($post_id, 'product_cat');
    if (!$terms || is_wp_error($terms)) return;
    foreach ($terms as $term) {
        delete_transient('my_prefix_' . $term->term_id);
    }
});
```

## TTL recomandate

| Tip date | TTL |
|----------|-----|
| Schema produse categorie | `HOUR_IN_SECONDS` (1h) |
| Related products | `HOUR_IN_SECONDS` (1h) |
| Date statistici | `DAY_IN_SECONDS` (24h) |
| Date care nu se schimba | `WEEK_IN_SECONDS` (7 zile) |

## Cum se aplica corect (Best Practice)
- **Prefix unic** pe cheie: `client_schema_`, `client_related_` — previne coliziuni cu alte pluginuri
- **Nu cache-ui HTML cu user-specific data** (cos, comenzi, mesaje utilizator) — diferit per user
- **Adauga invalidare** cand datele sursa se schimba — altfel cache-ul serveste date vechi
- **Verifica ca transient-ul exista** dupa prima scriere: `get_transient('key') !== false`
- LiteSpeed Cache si WP Rocket nu sterg transient-urile la flush — gestioneaza manual sau cu `delete_transient`

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Cheie fara prefix unic | Coliziuni cu alte pluginuri | Prefix `client_feature_` |
| Nu adaugi invalidare | Date vechi servite dupa update produs/categorie | Adauga `save_post_product` + `edited_term` hooks |
| Cache-uiesti HTML cu session data | Utilizator A vede datele lui B | Nu cache-ui date user-specific |
| TTL prea scurt (< 5 min) | Cache inefficient, query rulat des | Minim HOUR_IN_SECONDS pentru date statice |

## Verificare
- Prima vizita: query ruleaza, transient creat
- A doua vizita: `get_transient` returneaza valoarea, niciun query
- Dupa update produs: transient invalidat, query reruleaza la urmatoarea vizita
- Query Monitor: numar queries redus pe vizitele cu cache

## Timp estimat
20-30 minute pentru implementare pattern + invalidare
