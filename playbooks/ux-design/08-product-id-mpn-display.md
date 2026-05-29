# Afisare ID Produs si MPN

## Ce face
Afiseaza ID-ul WooCommerce si MPN (Model Part Number) vizibil pe pagina de produs, sub meta-datele produsului. Util pentru clientii care comanda dupa cod, pentru B2B si pentru imbunatatirea schema (MPN in Product schema).

## Cand se aplica
- Site-uri cu produse tehnice, alimentare sau de nisa unde clientii cauta dupa cod
- Cand produsele au MPN stocat in post meta (ex: `_wpfoof_mpn`, `_mpn`, `_sku`)
- Nu se aplica pe site-uri de fashion sau lifestyle unde codul nu e relevant

## Inainte sa incepi
- Identifica meta key-ul unde e stocat MPN: DevTools > WP-Admin > produs > Custom Fields
- Daca MPN lipseste: foloseste SKU ca fallback (`$product->get_sku()`)
- Identifica hook-ul corect pentru pozitionare: `woocommerce_product_meta_end`, `woocommerce_single_product_summary`

## Implementare

### Pasul 1 — Identifica meta key MPN
```php
// Temporar in WPCode pentru debug:
add_action('woocommerce_product_meta_end', function() {
    global $product;
    $all_meta = get_post_meta($product->get_id());
    var_dump(array_filter($all_meta, fn($k) => str_contains(strtolower($k), 'mpn'), ARRAY_FILTER_USE_KEY));
});
```

### Pasul 2 — Creeaza snippet PHP in WPCode
### Pasul 3 — Adauga codul cu meta key-ul corect
### Pasul 4 — Adauga CSS pentru stilizare

## Cod

**PHP snippet:**
```php
add_action('woocommerce_product_meta_end', function() {
    global $product;
    if (!$product) return;

    $id  = get_the_ID();
    $mpn = get_post_meta($id, '_mpn', true); // ajusteaza meta key

    // Fallback: incearca meta key-uri alternative
    if (!$mpn) $mpn = get_post_meta($id, '_wpfoof_mpn', true);
    if (!$mpn) {
        $wpfoof = get_post_meta($id, 'wpfoof-box-media', true);
        $mpn = is_array($wpfoof) ? ($wpfoof['wpfoof-mpn-name'] ?? '') : '';
    }
    // Fallback la SKU
    if (!$mpn) $mpn = $product->get_sku();

    echo '<span class="product-ids-display" style="display:block;font-size:13px;color:#666;margin-top:6px;">';
    echo 'Cod produs: <strong>' . esc_html($id) . '</strong>';
    if ($mpn) {
        echo ' &nbsp; MPN: <strong>' . esc_html($mpn) . '</strong>';
    }
    echo '</span>';
});
```

**CSS (optional, pentru stilizare mai buna):**
```css
.product-ids-display {
    display: block;
    font-size: 12px;
    color: #9ca3af;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #f3f4f6;
}
.product-ids-display strong {
    color: #6b7280;
    font-weight: 600;
}
```

## Cum se aplica corect (Best Practice)
- `esc_html()` obligatoriu pe orice output de post meta — previne XSS
- Fallback la SKU daca MPN lipseste — altfel campul e gol pe produse fara MPN
- Hook-ul `woocommerce_product_meta_end` = dupa SKU, categorie, taguri — pozitie naturala
- Daca vrei si in schema Product: adauga MPN in filtrul `rank_math/json_ld` separat

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Meta key gresit | Campul gol pe toate produsele | Verifica exact cu `get_post_meta($id, '', true)` |
| Lipsa `esc_html()` | XSS vulnerability | Adauga obligatoriu pe orice echo din post meta |
| Apar duplicate (meta key si SKU sunt acelasi) | `MPN: COD COD` | Adauga conditie: daca MPN == SKU, nu afisa separat |

## Verificare
- Pagina produs: sectiunea cu ID si MPN vizibila sub categorie/taguri
- Produs fara MPN: apare doar ID-ul sau SKU-ul
- DevTools > Sources > verifica ca nu exista XSS potential in output

## Timp estimat
20 minute
