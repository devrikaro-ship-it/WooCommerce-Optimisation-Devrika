# Rank Math Sitemap — Fix Termen cu URL Broken

## Ce face
Rezolva situatia in care o categorie WordPress/WooCommerce genereaza URL broken in sitemap-ul Rank Math (ex: `/fara-` in loc de `/fara-categorie/`). Cauza: Rank Math trunchiaza slug-ul sau termenul are configuratie incorecta.

## Cand se aplica
- `curl -s https://domain.ro/sitemap_index.xml | grep "404"` sau URL-uri trunchiate
- GSC arata erori 404 in sitemap
- Categoria "Fara categorie" (Uncategorized) sau alte categorii cu slug special

## Inainte sa incepi
- Identifica termenul problematic: `curl -s https://domain.ro/product_cat-sitemap.xml | grep "fara-\|broken"`
- Gaseste term_id: WP-Admin > WC > Categorii > editeaza categoria > nota ID din URL
- Sau: `wp term list product_cat --fields=term_id,slug | grep fara`

## Implementare

### Optiunea 1 — Noindex pe termen (recomandat)
Exclude termenul din sitemap via noindex.

### Optiunea 2 — Skip termen via filter Rank Math
Exclude direct via `rank_math/sitemap/skip_terms`.

### Optiunea 3 — Sterge/merge categoria
Daca categoria e goala sau inutila, sterge-o din WC.

## Cod

**Optiunea 1 — noindex pe termen (ONE-SHOT sau permanent):**
```php
// ONE-SHOT: seteaza noindex pe termenul problematic
add_action('init', function() {
    if (!current_user_can('manage_options') || !isset($_GET['fix_term_sitemap'])) return;

    $term_id = 15; // inlocuieste cu ID-ul corect
    update_term_meta($term_id, 'rank_math_robots', ['noindex']);

    // Invalideaza cache sitemap Rank Math
    delete_transient('rank_math_sitemap_index');
    global $wpdb;
    $wpdb->delete($wpdb->options, ['option_name' => 'rank_math_sitemap_cache_product_cat']);

    wp_die('Done: term ' . $term_id . ' set to noindex, sitemap cache cleared');
});
// Acceseaza: https://domain.ro/?fix_term_sitemap=1
```

**Optiunea 2 — filter permanent:**
```php
// Exclude termeni specifici din sitemap Rank Math
add_filter('rank_math/sitemap/skip_terms', function($skip) {
    $skip[] = 15; // ID-ul termenului de exclus — ajusteaza
    return $skip;
});
```

**Verifica eficienta:**
```bash
# Dupa fix: termenul nu mai apare in sitemap
curl -s https://domain.ro/product_cat-sitemap.xml | grep "fara-"
# Trebuie sa returneze gol
```

## Cum se aplica corect (Best Practice)
- `rank_math/sitemap/skip_terms` nu functioneaza in toate versiunile Rank Math — verifica; daca nu, foloseste `update_term_meta` cu noindex
- Dupa fix: trimite sitemap-ul din nou in GSC: GSC > Sitemaps > adauga URL > Submit
- Categoria "Fara categorie" WordPress (term_id default = 1 sau altul) apare frecvent — exclud-o implicit pe orice site nou
- Cache-ul sitemap Rank Math se regenereaza automat la urmatoarea vizita dupa invalidare

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `skip_terms` filter fara efect | Termenul continua sa apara in sitemap | Foloseste `update_term_meta` + cache clear |
| Nu invalidezi cache sitemap | Sitemap-ul vechi servit timp de ore | `delete_transient('rank_math_sitemap_index')` |
| Fix pe term_id gresit | Alt termen ascuns, problema persista | Verifica ID-ul exact cu `wp term list` |

## Verificare
- `curl -s https://domain.ro/product_cat-sitemap.xml | grep "fara-"` → gol
- GSC > Sitemaps > re-submit → stare "Succes" fara erori 404
- https://domain.ro/sitemap_index.xml → sitemap valabil

## Timp estimat
20 minute
