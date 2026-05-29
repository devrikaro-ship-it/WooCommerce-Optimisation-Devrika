# AggregateRating in Product Schema

## Ce face
Adauga rating-ul mediu si numarul de recenzii in schema Product, facand Google sa afiseze stelele galben in SERP sub rezultatul produsului. Impact vizual major — creste CTR cu 15-30% fata de rezultate fara stele.

## Cand se aplica
- Site-uri WooCommerce cu recenzii activate si produse care au minim 1 recenzie
- Cand Rich Results Test nu detecteaza AggregateRating pe paginile produs
- Nu se aplica pe produse fara recenzii — Google respinge schema cu ratingCount=0

## Inainte sa incepi
- Verifica ca recenziile WooCommerce sunt activate (Setari WC > Produse > Reviews)
- Verifica ca produsele au recenzii reale (nu fake) — Google penalizeaza rating-uri false
- Verifica daca Rank Math genereaza deja AggregateRating: Rank Math > Schema > Product

## Implementare

### Pasul 1 — Activeaza recenzii WooCommerce
WC > Setari > Produse > Reviews > bifa toate optiunile

### Pasul 2 — Activeaza AggregateRating in Rank Math
Rank Math > Schema > Product > AggregateRating > ON

### Pasul 3 — Daca Rank Math nu genereaza corect
Adauga snippet PHP care injecteaza AggregateRating in schema existenta.

## Cod

**Verifica daca Rank Math genereaza AggregateRating:**
```bash
curl -s "https://domain.ro/produs/" | grep -o '"aggregateRating":{[^}]*}'
```

**Adauga AggregateRating via filter Rank Math (daca nu e generat automat):**
```php
add_filter('rank_math/json_ld', function($data, $jsonld) {
    if (!is_product()) return $data;

    global $product;
    if (!$product) $product = wc_get_product(get_the_ID());
    if (!$product) return $data;

    $rating_count = $product->get_review_count();
    $rating_avg   = $product->get_average_rating();

    if ($rating_count < 1 || !$rating_avg) return $data; // nu adauga fara recenzii

    $aggregate = [
        '@type'       => 'AggregateRating',
        'ratingValue' => number_format((float)$rating_avg, 1),
        'reviewCount' => (int)$rating_count,
        'bestRating'  => '5',
        'worstRating' => '1',
    ];

    foreach ($data as &$item) {
        if (!is_array($item)) continue;
        if (($item['@type'] ?? '') === 'Product') {
            $item['aggregateRating'] = $aggregate;
        }
        if (isset($item['@graph'])) {
            foreach ($item['@graph'] as &$g) {
                if (($g['@type'] ?? '') === 'Product') {
                    $g['aggregateRating'] = $aggregate;
                }
            }
        }
    }

    return $data;
}, 99, 2);
```

## Cum se aplica corect (Best Practice)
- **Nu adauga AggregateRating pe produse fara recenzii** — Google afiseaza stelele doar la `reviewCount >= 1`; schema cu `reviewCount: 0` poate fi penalizata
- `ratingValue` trebuie sa fie intre 1-5, cu maxim 1 zecimala
- Verifica daca Rank Math deja genereaza AggregateRating inainte de a adauga snippet — duplicate = eroare schema
- Recenziile trebuie sa fie **reale si verificabile** — Google verifica cross-reference cu recenziile afisate pe pagina
- Dupa activare: asteapta 2-4 saptamani pana apar stelele in SERP

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| AggregateRating cu reviewCount=0 | Google ignora schema sau penalizeaza | Guard: `if ($rating_count < 1) return $data` |
| Duplicate AggregateRating (Rank Math + snippet) | Eroare schema in Rich Results Test | Verifica mai intai ce genereaza Rank Math |
| ratingValue ca string (`"4.5"`) nu number | Unii parseri Google o interpreteaza gresit | `number_format((float)$rating_avg, 1)` |
| Stele afisate pe pagina dar nu in schema | Google nu afiseaza stele in SERP | Asigura-te ca schema reflecta exact ce e pe pagina |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/produs-cu-recenzii/
- Cauta `aggregateRating` cu `ratingValue` si `reviewCount`
- Dupa 2-4 saptamani: cauta produsul in Google si verifica stelele galbene sub titlu

## Timp estimat
20 minute
