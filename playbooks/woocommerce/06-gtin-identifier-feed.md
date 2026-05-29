# GTIN / identifier_exists in Feed GMC

## Ce face
Rezolva erorile Google Merchant Center legate de GTIN invalid sau lipsa: fie furnizezi GTIN-uri EAN-13 valide, fie setezi `identifier_exists: no` in feed pentru produsele fara cod de bare standardizat.

## Cand se aplica
- Eroare GMC: "Invalid GTIN" sau "GTIN format incorect"
- Produse cu GTIN de 11 cifre (trebuie sa fie 13 pentru EAN sau 12 pentru UPC)
- Produse manufacturate intern fara EAN standard

## Inainte sa incepi
- Identifica pluginul de feed: CTX Feed, WooFeed, Google Listings & Ads
- Verifica ce meta key stocheaza GTIN: `_gtin`, `_ean`, `_barcode`
- Verifica lungimea GTIN-urilor existente: EAN-13 = 13 cifre, UPC = 12 cifre

## Implementare

### Optiunea 1 — identifier_exists: no (cel mai rapid)
In pluginul de feed: adauga camp `identifier_exists` cu valoare `no` pentru toate produsele sau filtreza pe categorii fara EAN.

### Optiunea 2 — Fix GTIN existent
Standardizeaza GTIN-urile la 13 cifre sau inlocuieste cu `identifier_exists: no`.

## Cod

**Filtru WooCommerce pentru a adauga identifier_exists via hook:**
```php
// Adauga identifier_exists in product meta daca GTIN lipseste sau e invalid
add_action('woocommerce_product_options_general_product_data', function() {
    global $post;
    $gtin = get_post_meta($post->ID, '_gtin', true);
    $is_valid = $gtin && preg_match('/^\d{12,14}$/', $gtin);
    if (!$is_valid) {
        update_post_meta($post->ID, '_identifier_exists', 'no');
    }
});
```

**Script WP-CLI pentru bulk update:**
```bash
# Seteaza identifier_exists=no pe toate produsele fara GTIN valid
wp db query "
INSERT INTO wp_postmeta (post_id, meta_key, meta_value)
SELECT p.ID, '_identifier_exists', 'no'
FROM wp_posts p
LEFT JOIN wp_postmeta m ON p.ID = m.post_id AND m.meta_key = '_gtin'
WHERE p.post_type = 'product'
AND p.post_status = 'publish'
AND (m.meta_value IS NULL OR m.meta_value = '' OR LENGTH(m.meta_value) != 13)
ON DUPLICATE KEY UPDATE meta_value = 'no'
"
```

## Cum se aplica corect (Best Practice)
- `identifier_exists: no` = valid pentru produse unice, handmade, fara EAN — Google accepta
- Nu inventa GTIN-uri — GMC verifica baza de date GS1 si penalizeaza GTIN-uri false
- Dupa fix: resincronizeaza feed-ul si asteapta 24-72h pentru revalidare GMC

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| GTIN de 11 cifre in loc de 13 | Eroare GMC "invalid GTIN" | Seteaza `identifier_exists: no` sau obtine EAN-13 real |
| GTIN inventat | Suspendare cont GMC | Foloseste `identifier_exists: no` in loc de GTIN fals |

## Verificare
- GMC > Produse > Probleme: erori GTIN reduse/eliminate dupa 24-72h
- Feed URL: camp `identifier_exists` prezent cu valoare `no` pe produsele relevante

## Timp estimat
30 minute (configurare feed) + 24-72h asteptare GMC
