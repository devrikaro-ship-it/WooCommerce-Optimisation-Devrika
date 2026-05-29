# Enable Product Reviews WooCommerce

## Ce face
Activeaza recenziile WooCommerce global si deschide `comment_status` pe toate produsele publicate. Necesar pentru AggregateRating schema si pentru a permite clientilor sa lase recenzii.

## Cand se aplica
- Site-uri unde recenziile sunt dezactivate (setare WC sau produse importate cu `comment_status = closed`)
- Dupa import bulk de produse (importul nu seteaza `comment_status = open` implicit)
- Inainte de implementarea AggregateRating schema

## Inainte sa incepi
- Verifica starea curenta: WC > Setari > Produse > Reviews — bifeaza?
- Verifica un produs: WP-Admin > Produse > editeaza > Discussion tab (daca e vizibil)
- Verifica optiunea DB: `SELECT option_value FROM wp_options WHERE option_name = 'woocommerce_enable_reviews'`

## Implementare

### Optiunea 1 — UI (recomandat pentru setarile globale)
WC > Setari > Produse > Reviews > bifa toate optiunile > Salveaza

### Optiunea 2 — PHP snippet (pentru a deschide `comment_status` pe produse existente)
Creeaza snippet PHP ONE-SHOT.

## Cod

**ONE-SHOT PHP — activeaza recenzii + deschide comment_status pe toate produsele:**
```php
// ONE-SHOT: ruleaza o data, apoi dezactiveaza/sterge snippet-ul
add_action('init', function() {
    if (!current_user_can('manage_options')) return;
    if (!isset($_GET['enable_reviews_now'])) return;

    // Activeaza optiunile WC
    update_option('woocommerce_enable_reviews', 'yes');
    update_option('woocommerce_review_rating_verification_required', 'no');
    update_option('woocommerce_review_rating_required', 'no');
    update_option('woocommerce_enable_review_rating', 'yes');

    // Deschide comment_status pe toate produsele publicate (1 query SQL)
    if (!get_option('client_reviews_opened_v1')) {
        global $wpdb;
        $updated = $wpdb->update(
            $wpdb->posts,
            ['comment_status' => 'open'],
            ['post_type' => 'product', 'post_status' => 'publish']
        );
        update_option('client_reviews_opened_v1', '1');
        wp_send_json_success(['message' => 'Reviews enabled', 'products_updated' => $updated]);
    }

    wp_send_json_success(['message' => 'Already done']);
});
// Acceseaza o data: https://domain.ro/?enable_reviews_now=1
// Sterge snippet dupa executie!
```

**Verifica starea recenziilor:**
```bash
# Via MySQL/WP-CLI:
wp option get woocommerce_enable_reviews
wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type='product' AND post_status='publish' AND comment_status='open'"
```

## Cum se aplica corect (Best Practice)
- **Sterge snippet-ul imediat dupa executie** — e ONE-SHOT, nu trebuie sa ruleze la fiecare request
- Adauga `get_option('client_reviews_opened_v1')` guard ca sa nu re-actualizeze la fiecare rulare accidentala
- UPDATE bulk via `$wpdb->update()` = 1 query SQL pe toate produsele — nu foloseste `foreach` + `update_post_meta`
- Dupa activare: verifica ca tab-ul Reviews apare pe un produs

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Snippet ONE-SHOT lasat activ | Ruleaza la fiecare request, overhead DB | Sterge sau dezactiveaza imediat dupa verificare |
| `foreach` + `wp_update_post` per produs | Sute de queries pe site cu multe produse | Foloseste `$wpdb->update()` bulk |
| Optiunile WC setate dar `comment_status` ramas `closed` | Recenziile nu apar pe produse | Adauga si UPDATE pe `wp_posts` |

## Verificare
- WC > Setari > Produse > Reviews: toate bifate
- Pagina produs: tab "Reviews" vizibil
- Pagina produs: formular "Add a review" vizibil
- `wp option get woocommerce_enable_reviews` → `yes`

## Timp estimat
15 minute
