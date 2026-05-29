# Product Tabs Custom — Date tehnice + FAQ

## Ce face
Adauga sau restructureaza tab-urile de pe pagina de produs WooCommerce: redenumeste tab-ul Description, adauga tab custom "Date tehnice" (din post meta) si tab "FAQ" (din post meta sau camp custom). Creste informatia disponibila si sansele de rich result FAQ.

## Cand se aplica
- Site-uri WooCommerce cu produse care au specificatii tehnice
- Cand tab-ul Description e gol sau contine HTML redundant
- Necesita fie post meta custom, fie ACF fields pentru continut tabs

## Inainte sa incepi
- Identifica ce meta keys stocheaza datele tehnice si FAQ ale produselor
- Verifica ce tab-uri exista deja: `woocommerce_product_tabs` filter
- Decide daca renumesti Description sau adaugi tab-uri noi

## Implementare

### Pasul 1 — Creeaza snippet PHP in WPCode
- PHP type

### Pasul 2 — Adauga codul

### Pasul 3 — Activeaza

### Pasul 4 — Testeaza pe un produs cu date tehnice

## Cod

```php
// Restructureaza tab-urile produsului WooCommerce
add_filter('woocommerce_product_tabs', function($tabs) {

    // Redenumeste Description → Descriere
    if (isset($tabs['description'])) {
        $tabs['descriere'] = $tabs['description'];
        $tabs['descriere']['title'] = 'Descriere';
        $tabs['descriere']['priority'] = 10;
        $tabs['descriere']['callback'] = '_puria_tab_descriere';
        unset($tabs['description']);
    }

    // Tab Date tehnice (din post meta _date_tehnice sau ACF)
    $tabs['date_tehnice'] = [
        'title'    => 'Date tehnice',
        'priority' => 20,
        'callback' => function() {
            global $product;
            $data = get_post_meta($product->get_id(), '_date_tehnice', true);
            if (empty($data)) {
                echo '<p>Nu sunt disponibile date tehnice pentru acest produs.</p>';
                return;
            }
            // Daca e array cheie-valoare
            if (is_array($data)) {
                echo '<table class="shop_attributes">';
                foreach ($data as $key => $val) {
                    echo '<tr><th>' . esc_html($key) . '</th><td>' . esc_html($val) . '</td></tr>';
                }
                echo '</table>';
            } else {
                echo wp_kses_post($data);
            }
        },
    ];

    // Tab FAQ (din post meta _faq_items)
    $tabs['faq'] = [
        'title'    => 'Intrebari frecvente',
        'priority' => 30,
        'callback' => function() {
            global $product;
            $faqs = get_post_meta($product->get_id(), '_faq_items', true);
            if (empty($faqs) || !is_array($faqs)) {
                echo '<p>Nu sunt disponibile intrebari frecvente.</p>';
                return;
            }
            echo '<dl class="faq-list">';
            foreach ($faqs as $faq) {
                echo '<dt>' . esc_html($faq['question'] ?? '') . '</dt>';
                echo '<dd>' . wp_kses_post($faq['answer'] ?? '') . '</dd>';
            }
            echo '</dl>';
        },
    ];

    return $tabs;
}, 98);

// Callback pentru tab Descriere
function _puria_tab_descriere() {
    global $product;
    $desc = $product->get_description();
    if ($desc) {
        echo '<div class="woocommerce-product-details__short-description">' . wp_kses_post($desc) . '</div>';
    } else {
        echo '<p>Descriere indisponibila pentru acest produs.</p>';
    }
}
```

## Cum se aplica corect (Best Practice)
- Ajusteaza `meta_key`-urile (`_date_tehnice`, `_faq_items`) la cele folosite efectiv de site
- Priority 10/20/30 = ordinea tab-urilor — Reviews tab are priority 50 by default in WC
- Tab-ul FAQ trebuie sa aiba continut unic per produs pentru FAQ schema — nu acelasi text pe toate
- Nu sterge `reviews` tab daca site-ul are recenzii active — afecteaza schema AggregateRating

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `unset($tabs['description'])` fara adaugare callback | Tab Descriere dispare complet | Adauga callback inainte de unset sau redenumeste in loc sa stergi |
| Meta key gresit | Tab gol pe toate produsele | Verifica meta key real: `get_post_meta($id, '', true)` returneaza toate |
| Callback definit ca function anonima nested | Erori PHP pe versiuni vechi | Defineste functia separat sau ca closure |

## Verificare
- Pagina produs: tab-urile noi vizibile (Date tehnice, FAQ)
- Tab cu date: tabelul se afiseaza corect
- Tab gol: mesaj "Nu sunt disponibile" (nu eroare PHP)
- DevTools console: fara erori JS

## Timp estimat
45 minute (implementare) + timp pentru populare date per produs
