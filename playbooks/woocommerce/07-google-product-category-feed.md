# Google Product Category in Feed GMC

## Ce face
Mapeaza categoriile WooCommerce la taxonomia Google Product Category (camp obligatoriu pentru aprobarea produselor in Google Shopping). Absenta sa = produse respinse sau cu performanta slaba in Shopping.

## Cand se aplica
- La orice site nou conectat la Google Merchant Center
- Eroare GMC: "google_product_category missing" sau "Disapproved: missing required attribute"
- Obligatoriu pentru toate produsele in feed

## Inainte sa incepi
- Identifica pluginul de feed: CTX Feed, WooFeed, Google Listings & Ads, WooCommerce Google Listings
- Download taxonomia Google: https://www.google.com/basepages/producttype/taxonomy-with-ids.ro-RO.txt
- Mapeaza categoriile WooCommerce la categoria Google corespunzatoare

## Implementare

### Pasul 1 — Identifica toate categoriile WooCommerce
```bash
wp term list product_cat --fields=term_id,name,slug --format=csv
```

### Pasul 2 — Mapeaza la taxonomia Google
Exemple comune:
| Categoria WC | Google Product Category |
|-------------|------------------------|
| Caini > Hrana Uscata | `Animals & Pet Supplies > Pet Food > Dog Food > Dry Dog Food` |
| Pisici > Hrana Umeda | `Animals & Pet Supplies > Pet Food > Cat Food > Wet Cat Food` |
| Caini > Accesorii | `Animals & Pet Supplies > Pet Supplies > Dog Supplies` |
| Electronice > Telefoane | `Electronics > Communications > Telephony > Mobile Phones` |

### Pasul 3 — Seteaza in pluginul de feed
CTX Feed: Manage Feeds > editeaza feed > Mappings > Category Mapping

### Pasul 4 — Re-genereaza feed-ul si valideaza in GMC

## Cod

**Stocheaza Google Product Category per categorie WC (via term meta):**
```php
// Adauga camp GPC in editarea categoriei WC
add_action('product_cat_edit_form_fields', function($term) {
    $gpc = get_term_meta($term->term_id, '_google_product_category', true);
    ?>
    <tr class="form-field">
        <th><label>Google Product Category</label></th>
        <td>
            <input type="text" name="google_product_category" value="<?= esc_attr($gpc) ?>" />
            <p class="description">Ex: Animals & Pet Supplies > Pet Food > Dog Food</p>
        </td>
    </tr>
    <?php
});

add_action('edited_product_cat', function($term_id) {
    if (isset($_POST['google_product_category'])) {
        update_term_meta($term_id, '_google_product_category', sanitize_text_field($_POST['google_product_category']));
    }
});
```

**Afiseaza GPC in feed via filtru CTX Feed:**
```php
// Filtru CTX Feed pentru a injecta GPC din term meta
add_filter('ctx_feed_product_data', function($data, $product, $config) {
    if (!isset($data['google_product_category'])) {
        $terms = get_the_terms($product->get_id(), 'product_cat');
        if ($terms && !is_wp_error($terms)) {
            foreach ($terms as $term) {
                $gpc = get_term_meta($term->term_id, '_google_product_category', true);
                if ($gpc) {
                    $data['google_product_category'] = $gpc;
                    break;
                }
            }
        }
    }
    return $data;
}, 10, 3);
```

## Cum se aplica corect (Best Practice)
- Mapeaza **toate** categoriile — o singura categorie nemapata = toate produsele din ea respinse
- Verifica taxonomia Google actualizata periodic — Google o actualizeaza anual
- Categorii mai specifice = mai bune (ex: "Dry Dog Food" > "Dog Food" > "Pet Food")
- Dupa configurare: regenereaza feed-ul si verifica in GMC Feed Diagnostics

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Categorii WC mapate la GPC gresit | Produse in categorie gresita in Shopping | Reverifica taxonomia Google |
| Categorie lipsa din mapping | Produse respinse in GMC | Adauga mapping pentru toate categoriile |
| GPC in format ID (ex: 3) nu text | Unele pluginuri nu accepta ID | Foloseste textul complet al categoriei |

## Verificare
- Feed URL: camp `google_product_category` prezent si populat pentru fiecare produs
- GMC > Feed Diagnostics: erori "missing google_product_category" disparute
- GMC > Produse: statusul schimbat din "Disapproved" in "Approved" dupa 24-72h

## Timp estimat
2-4h (mapare categorii + configurare + verificare)
