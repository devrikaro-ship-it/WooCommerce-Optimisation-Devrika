# Product Schema Fix — availability, itemCondition, taxIncluded

## Ce face
Corecteaza erorile frecvente in schema Product generata de Rank Math/WooCommerce: `availability` cu `http://` in loc de `https://`, `itemCondition` format gresit, `valueAddedTaxIncluded` ca string in loc de boolean. Fara fix = erori in Google Merchant Center si pierdere eligibilitate rich results.

## Cand se aplica
- Orice site WooCommerce cu Rank Math care arata erori schema in GMC sau Google Rich Results Test
- Cand schema Product contine `http://schema.org/` in loc de `https://schema.org/`
- Cand `valueAddedTaxIncluded` apare ca `"true"` (string) in loc de `true` (boolean)

## Inainte sa incepi
- Verifica schema curenta: https://search.google.com/test/rich-results?url=https://domain.ro/produs/
- Sau: `curl -s https://domain.ro/produs-slug/ | grep -o '"availability":"[^"]*"'`
- Identifica exact ce erori apar (availability / itemCondition / taxIncluded)

## Implementare

### Pasul 1 — Verifica schema curenta
```bash
curl -s "https://domain.ro/SLUG-PRODUS/" | python3 -m json.tool 2>/dev/null | grep -A5 "availability\|itemCondition\|taxIncluded"
```

### Pasul 2 — Creeaza snippet PHP in WPCode
- PHP type, Run Everywhere

### Pasul 3 — Adauga codul (vezi sectiunea Cod)

### Pasul 4 — Activeaza + Salveaza

### Pasul 5 — Verifica pe Google Rich Results Test

## Cod

```php
// Fix Product schema: availability https + itemCondition + taxIncluded boolean
// Inlocuieste ob_start cu rank_math/json_ld filter — fara overhead de buffering
add_filter('rank_math/json_ld', function($data, $jsonld) {
    if (!is_product()) return $data;

    $fix_offers = function(&$offers) {
        if (!is_array($offers)) return;

        // Fix: http://schema.org/ → https://schema.org/
        if (isset($offers['availability'])) {
            $offers['availability'] = str_replace(
                'http://schema.org/',
                'https://schema.org/',
                $offers['availability']
            );
        }

        // Fix: itemCondition format → https://schema.org/NewCondition
        if (isset($offers['itemCondition'])) {
            $c = $offers['itemCondition'];
            $offers['itemCondition'] = strpos($c, 'http') === false
                ? 'https://schema.org/' . $c
                : str_replace('http://schema.org/', 'https://schema.org/', $c);
        }

        // Fix: valueAddedTaxIncluded "true" → true (boolean)
        if (isset($offers['priceSpecification']['valueAddedTaxIncluded'])) {
            $v = $offers['priceSpecification']['valueAddedTaxIncluded'];
            $offers['priceSpecification']['valueAddedTaxIncluded'] =
                ($v === true || $v === 'true' || $v === 1);
        }
    };

    foreach ($data as &$item) {
        if (!is_array($item)) continue;
        // Handle direct Product type
        if (($item['@type'] ?? '') === 'Product' && isset($item['offers'])) {
            $fix_offers($item['offers']);
        }
        // Handle @graph structure
        if (isset($item['@graph']) && is_array($item['@graph'])) {
            foreach ($item['@graph'] as &$graph_item) {
                if (($graph_item['@type'] ?? '') === 'Product' && isset($graph_item['offers'])) {
                    $fix_offers($graph_item['offers']);
                }
            }
        }
    }

    return $data;
}, 99, 2);
```

**Varianta pentru Yoast SEO:**
```php
add_filter('wpseo_schema_graph', function($data) {
    foreach ($data as &$item) {
        if (($item['@type'] ?? '') !== 'Product') continue;
        if (!isset($item['offers'])) continue;
        if (isset($item['offers']['availability'])) {
            $item['offers']['availability'] = str_replace('http://', 'https://', $item['offers']['availability']);
        }
    }
    return $data;
});
```

## Cum se aplica corect (Best Practice)
- Foloseste `rank_math/json_ld` filter, **NU `ob_start`** — ob_start bufferizeaza tot HTML-ul paginii si ruleaza regex pe output complet, e cel mai lent snippet posibil
- Priority `99` asigura ca ruleaza dupa ce Rank Math a generat schema
- Guard `is_product()` obligatoriu — fara el ruleaza pe toate paginile
- Handleaza ambele structuri (`@graph` si flat) — Rank Math schimba structura in functie de versiune
- Dupa implementare: verifica in Google Rich Results Test si asteapta 2-4 saptamani pentru revalidare GMC

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `ob_start` cu regex pe HTML complet | Bufferizeaza tot HTML-ul, cel mai lent snippet | Foloseste `rank_math/json_ld` filter |
| Lipsa guard `is_product()` | Ruleaza pe toate paginile, overhead inutil | Adauga guard la inceputul callback-ului |
| Priority prea mica (< 10) | Ruleaza inainte de Rank Math, nu gaseste schema | Seteaza priority 99 |
| Nu handleaza structura `@graph` | Fix nu se aplica pe unele versiuni Rank Math | Adauga loop prin `$item['@graph']` |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/produs/
- Cauta: `"availability": "https://schema.org/InStock"` (cu https)
- Cauta: `"itemCondition": "https://schema.org/NewCondition"`
- Cauta: `"valueAddedTaxIncluded": true` (boolean, fara ghilimele)
- GMC > Produse > Probleme > erorile de schema ar trebui sa dispara in 7-14 zile

## Timp estimat
30 minute
