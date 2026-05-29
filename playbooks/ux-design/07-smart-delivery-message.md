# Smart Delivery Message

## Ce face
Inlocuieste termenul de livrare static din XStore/WooCommerce cu un mesaj dinamic calculat in timp real: "Livrare maine", "Livrare luni", "Livrare in 2 zile" — in functie de ora curenta si ziua saptamanii. Creste urgenta si increderea.

## Cand se aplica
- Site-uri WooCommerce cu livrare rapida (24-48h)
- Cand WooCommerce sau tema afiseaza "Termen de livrare: 15-20 mai" (data fixa, depasita)
- Necesita cunoasterea orarului de expediere (ex: comenzi pana la 15:00 = livrare a doua zi)

## Inainte sa incepi
- Stabileste cu clientul: ora limita pentru expediere in aceeasi zi (ex: 15:00)
- Stabileste: se livreaza si weekend? (daca nu → logica pentru luni)
- Identifica daca XStore afiseaza un element custom de livrare care trebuie ascuns

## Implementare

### Pasul 1 — Creeaza snippet PHP in WPCode
- PHP type

### Pasul 2 — Adauga codul (ajusteaza ora limita si timezone)

### Pasul 3 — Daca tema afiseaza si elementul vechi: ascunde-l via CSS

### Pasul 4 — Activeaza si verifica la ore diferite

## Cod

```php
// Smart delivery message — inlocuieste disponibilitatea WC
add_filter('woocommerce_get_availability', function($availability, $product) {
    if (!$product->is_in_stock()) return $availability;

    $tz   = new DateTimeZone('Europe/Bucharest'); // ajusteaza timezone
    $now  = new DateTime('now', $tz);
    $hour = (int)$now->format('G');
    $dow  = (int)$now->format('N'); // 1=Luni, 7=Duminica

    $ora_limita = 15; // comanda pana la aceasta ora = livrare a doua zi

    if ($dow >= 6) {
        // Weekend → livrare luni
        $luni = new DateTime('next monday', $tz);
        $msg  = '&#9201; Livrare luni, ' . $luni->format('j M');
    } elseif ($hour < $ora_limita) {
        // Weekday inainte de ora limita → livrare maine
        $maine = new DateTime('tomorrow', $tz);
        $msg   = '&#9889; Livrare maine, ' . $maine->format('j M')
                . ' &mdash; comanda pana la ' . $ora_limita . ':00';
    } else {
        // Dupa ora limita → livrare in 2 zile lucratoare
        $zile = 2;
        $data = new DateTime('now', $tz);
        while ($zile > 0) {
            $data->modify('+1 day');
            if ((int)$data->format('N') <= 5) $zile--; // skip weekend
        }
        $msg = '&#128230; Livrare ' . $data->format('j M');
    }

    $availability['availability'] = $msg;
    return $availability;
}, 10, 2);
```

**CSS pentru a ascunde termenul de livrare vechi din XStore:**
```css
/* Ascunde elementul XStore de livrare — inlocuit de smart delivery */
.elementor-element-XXXXXXXX, /* ID element XStore livrare — identifica cu DevTools */
.woocommerce-product-details__delivery-date,
.et-delivery-time {
    display: none !important;
}
```

**Varianta cu format data in romana:**
```php
$luni_ro = ['', 'ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie',
             'iulie', 'august', 'septembrie', 'octombrie', 'noiembrie', 'decembrie'];
$msg = '&#9889; Livrare maine, ' . $maine->format('j') . ' ' . $luni_ro[(int)$maine->format('n')];
```

## Cum se aplica corect (Best Practice)
- Guard `$product->is_in_stock()` obligatoriu — nu afisa mesaj de livrare pe produse fara stoc
- Timezone **trebuie** specificat explicit — serverele pot rula pe UTC, rezultate gresite fara timezone
- Ascunde elementul vechi de livrare al temei **separat via CSS**, nu in acelasi snippet PHP
- Testeaza la 3 momente: inainte de ora limita (weekday), dupa ora limita (weekday), weekend
- Verifica ca filtrul nu se aplica si pe produse variable cu optiuni indisponibile

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Fara timezone explicit | Mesaj calculat pe UTC, gresit cu 2-3h | Adauga `new DateTimeZone('Europe/Bucharest')` |
| Nu ascunzi elementul vechi al temei | Doua mesaje de livrare pe pagina | Identifica si ascunde cu CSS selectorul temei |
| `woocommerce_get_availability` nu se declanseaza | Mesajul nu apare | Verifica daca tema suprascrie hook-ul |
| Emoji lipsa | Mesaj fara icon | Verifica ca PHP suporta UTF-8 (in mod normal da pe orice hosting modern) |

## Verificare
- Pagina produs, produs in stoc: mesajul smart de livrare vizibil
- Testeaza manual: schimba ora serverului sau logica `$hour` temporar
- Verifica ca mesajul vechi al temei nu mai apare
- Produs fara stoc: mesaj de livrare absent

## Timp estimat
30 minute
