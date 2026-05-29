# Noindex URL Parametri WooCommerce

## Ce face
Aplica noindex/disallow pe URL-urile cu parametri WooCommerce (?orderby=, ?filter_*, ?add-to-cart=) care genereaza mii de pagini duplicate indexabile, consuma crawl budget si dilueaza autoritatea domeniului.

## Cand se aplica
- Orice site WooCommerce cu filtre de produse active (brand, pret, atribute)
- Cand GSC arata erori "Pagini duplicate fara canonical" sau crawl budget irosit
- Nu se aplica pe URL-uri care contin continut unic (nu parametri de filtrare)

## Inainte sa incepi
- Verifica in GSC > Index > Pagini ce URL-uri cu parametri sunt indexate
- Identifica ce parametri genereaza duplicate: `?orderby=`, `?filter_brand=`, `?add-to-cart=`, `?per_page=`
- Verifica daca Rank Math are deja setare de noindex pe arhive parametrizate

## Implementare

### Pasul 1 — Verifica parametrii activi pe site
```bash
curl -s "https://domain.ro/sitemap.xml" | grep "filter_\|orderby\|add-to-cart"
```

### Pasul 2 — Optiunea 1: robots.txt filter (recomandat)
Creeaza snippet PHP in WPCode — **PHP type**:

### Pasul 3 — Optiunea 2: Rank Math noindex
Rank Math > Titluri si Meta > WooCommerce > seteaza noindex pe arhive cu parametri

### Pasul 4 — Verifica robots.txt
`https://domain.ro/robots.txt` — confirma ca regulile apar

## Cod

**Optiunea 1 — robots.txt via PHP filter:**
```php
// Adauga disallow pe parametri WC in robots.txt
add_filter('robots_txt', function($output) {
    $output .= "\nDisallow: /?orderby=";
    $output .= "\nDisallow: /?filter_";
    $output .= "\nDisallow: /?add-to-cart=";
    $output .= "\nDisallow: /?per_page=";
    $output .= "\nDisallow: /?s=";
    return $output;
}, 10, 1);
```

**Optiunea 2 — noindex via Rank Math filter:**
```php
// Noindex pe pagini cu parametri URL WooCommerce
add_action('wp', function() {
    if (!is_shop() && !is_product_category() && !is_product_tag()) return;
    $params = ['orderby', 'filter_brand', 'filter_color', 'add-to-cart', 'per_page'];
    foreach ($params as $param) {
        if (isset($_GET[$param])) {
            add_filter('rank_math/frontend/robots', function($robots) {
                $robots['index'] = 'noindex';
                return $robots;
            });
            break;
        }
    }
});
```

## Cum se aplica corect (Best Practice)
- Preferabil robots.txt Disallow pentru parametri care nu ar trebui niciodata indexati
- Noindex PHP pentru parametri care uneori pot fi utili (ex: pagini de cautare cu rezultate)
- Nu aplica noindex pe `/caini/?min_price=10` daca acele pagini au trafic organic real — verifica GSC mai intai
- Adauga noii parametri in lista ori de cate ori adaugi un nou plugin de filtrare
- Parametrii specifici pluginului de filtrare (WooCommerce Price Slider, YITH Filters etc.) difera — identifica-i cu DevTools

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Disallow prea larg (`Disallow: /?`) | Blocheaza tot site-ul inclusiv pagini valide | Fii specific pe fiecare parametru |
| Noindex fara Disallow in robots.txt | Googlebot crawleaza in continuare, consuma budget | Combina ambele |
| Uiti parametri nou adaugati de plugin-uri | Continua indexarea paginilor duplicate | Audit periodic GSC |

## Verificare
- `https://domain.ro/robots.txt` — parametrii apar in sectiunea Disallow
- GSC > Acoperire > Excluse > "Exclus de tag robots (noindex)" dupa 2-4 saptamani
- `site:domain.ro orderby=` in Google — dupa 1-2 luni ar trebui sa dispara

## Timp estimat
30 minute
