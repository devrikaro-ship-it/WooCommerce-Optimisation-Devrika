# Category Archive Description in Shop Loop

## Ce face
Afiseaza descrierea categoriei WooCommerce vizibil in pagina de arhiva, deasupra grilei de produse. WooCommerce nu afiseaza automat descrierea — necesita hook sau setare tema.

## Cand se aplica
- Cand ai adaugat descrieri in WC > Categorii dar nu apar in pagina
- Distinct de playbook-ul 10-category-description-editorial care acopera si redactarea textului

## Inainte sa incepi
- Verifica daca tema afiseaza automat (unele teme o afiseaza, altele nu)
- Verifica ca exista descrieri adaugate: WC > Produse > Categorii > editeaza

## Cod

```php
add_action('woocommerce_before_shop_loop', function() {
    if (!is_product_category()) return;
    $term = get_queried_object();
    if (!$term || empty($term->description)) return;
    echo '<div class="category-editorial-description" style="margin-bottom:24px;font-size:15px;line-height:1.7;color:#475569;">'
        . wp_kses_post($term->description)
        . '</div>';
}, 5);
```

## Verificare
- Pagina categorie cu descriere adaugata: textul vizibil deasupra produselor
- Pagina categorie fara descriere: niciun element afisat

## Timp estimat
10 minute
