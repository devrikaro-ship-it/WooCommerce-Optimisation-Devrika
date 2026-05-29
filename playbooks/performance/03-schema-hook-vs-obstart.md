# Schema JSON-LD: Hook Direct vs ob_start

## Ce face
Explica de ce `ob_start` cu regex pe output HTML este cel mai lent pattern pentru modificarea schemei JSON-LD si cum sa-l inlocuiesti cu hook-ul direct al pluginului de schema.

## Problema

```php
// GRESIT — ob_start bufferizeaza tot HTML-ul paginii
add_action('template_redirect', function() {
    if (!is_product()) return;
    ob_start(function($html) {
        return preg_replace_callback(
            '|<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>|s',
            function($m) {
                $data = json_decode($m[1], true);
                // modifica $data...
                return '<script type="application/ld+json">' . json_encode($data) . '</script>';
            },
            $html
        );
    });
});
```

**De ce e rau:**
- Bufferizeaza **intregul HTML** al paginii in memorie
- Ruleaza regex pe sute de KB de HTML
- `json_decode` + `json_encode` per request
- Ruleaza chiar si cu LiteSpeed cache activ (la primul request/cache miss)

## Solutia — hook direct per plugin

**Rank Math:**
```php
add_filter('rank_math/json_ld', function($data, $jsonld) {
    if (!is_product()) return $data;

    foreach ($data as &$item) {
        if (!is_array($item)) continue;

        // Handle flat Product
        if (($item['@type'] ?? '') === 'Product' && isset($item['offers'])) {
            // modifica $item['offers']...
        }

        // Handle @graph structure
        if (isset($item['@graph'])) {
            foreach ($item['@graph'] as &$g) {
                if (($g['@type'] ?? '') === 'Product' && isset($g['offers'])) {
                    // modifica $g['offers']...
                }
            }
        }
    }

    return $data;
}, 99, 2);
```

**Yoast SEO:**
```php
add_filter('wpseo_schema_graph', function($data) {
    if (!is_product()) return $data;
    foreach ($data as &$item) {
        if (($item['@type'] ?? '') !== 'Product') continue;
        // modifica $item...
    }
    return $data;
});
```

**WooCommerce structured data (fara plugin schema):**
```php
add_filter('woocommerce_structured_data_product', function($markup) {
    if (isset($markup['offers']['availability'])) {
        $markup['offers']['availability'] = str_replace('http://', 'https://', $markup['offers']['availability']);
    }
    return $markup;
});
```

## Cum sa identifici snippeturi ob_start existente

```
WPCode > cauta "ob_start" in snippeturi active
```

Fiecare rezultat = candidat pentru refactorizare cu hook direct.

## Cum se aplica corect (Best Practice)
- Priority `99` pe `rank_math/json_ld` = ruleaza dupa ce Rank Math a generat complet schema
- Handleaza ambele structuri (`flat` si `@graph`) — Rank Math schimba structura in versiuni diferite
- Guard `is_product()` obligatoriu — fara el filtrul ruleaza pe toate paginile
- Verifica in Rich Results Test dupa modificare

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Priority prea mica (< 10) | Filtrul ruleaza inainte de Rank Math, schema goala | Seteaza priority 99 |
| Nu handleaza `@graph` | Fix nu se aplica pe unele versiuni Rank Math | Adauga loop separat pentru `@graph` |
| `ob_start` lasat si hook adaugat | Dubla procesare | Sterge `ob_start` dupa ce hook-ul functioneaza |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/produs/
- Schema modificata corect (availability cu https, etc.)
- Query Monitor: fara overhead de buffering

## Timp estimat
30 minute per snippet ob_start inlocuit
