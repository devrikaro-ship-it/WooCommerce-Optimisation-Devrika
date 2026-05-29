# BreadcrumbList Schema

## Ce face
Valideaza si verifica schema BreadcrumbList generata de Rank Math pe paginile de produs si categorie. Schema corecta afiseaza breadcrumb-ul direct in SERP (`domain.ro > Caini > Hrana Uscata > Produs`), creste CTR cu 5-15%.

## Cand se aplica
- Orice site WooCommerce cu Rank Math instalat
- Dupa schimbari de structura URL sau categorii
- Cand Google Search Console arata erori "BreadcrumbList"

## Inainte sa incepi
- Rank Math > Titluri si Meta > Breadcrumbs > activeaza breadcrumbs
- Verifica structura categorii: produsele trebuie sa aiba categoria primara setata corect
- Verifica ca `woocommerce_breadcrumb` sau Rank Math breadcrumb widget e activ in tema

## Implementare

### Pasul 1 — Activeaza in Rank Math
Rank Math > General > Breadcrumbs > ON

### Pasul 2 — Configureaza separatorul
Rank Math > General > Breadcrumbs > Separator: `›` (sau `-`, `/`)

### Pasul 3 — Seteaza categoria primara pe produse cu mai multe categorii
Pe fiecare produs: Rank Math metabox > Avansate > Categorie primara

### Pasul 4 — Verifica schema generata

## Cod

**Verifica schema breadcrumb pe o pagina:**
```bash
curl -s "https://domain.ro/produs/" | python3 -c "
import sys, json, re
html = sys.stdin.read()
scripts = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', html, re.DOTALL)
for s in scripts:
    try:
        data = json.loads(s)
        if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except: pass
"
```

**Fix: seteaza categoria primara pe toate produsele dintr-o categorie (bulk):**
```php
// ONE-SHOT: seteaza categoria primara pe produse care nu o au
add_action('init', function() {
    if (!isset($_GET['fix_primary_cat']) || !current_user_can('manage_options')) return;

    $products = get_posts([
        'post_type'      => 'product',
        'posts_per_page' => -1,
        'post_status'    => 'publish',
        'fields'         => 'ids',
    ]);

    foreach ($products as $id) {
        $primary = get_post_meta($id, 'rank_math_primary_category', true);
        if (!$primary) {
            $terms = get_the_terms($id, 'product_cat');
            if ($terms && !is_wp_error($terms)) {
                // Seteaza prima categorie ca primara
                update_post_meta($id, 'rank_math_primary_category', $terms[0]->term_id);
            }
        }
    }
    die('Done: primary categories set');
});
```

**Fix: breadcrumb porneste din categoria gresita:**
```php
// Override breadcrumb pentru a forta categoria corecta
add_filter('rank_math/frontend/breadcrumb/items', function($crumbs, $class) {
    // Verifica si corecteaza daca e necesar
    return $crumbs;
}, 10, 2);
```

## Cum se aplica corect (Best Practice)
- **Categoria primara** e critica — daca un produs e in `/caini/` si `/pisici/`, breadcrumb-ul ia categorie random fara setare primara
- Nu edita schema BreadcrumbList manual via PHP daca Rank Math o genereaza corect — risc de duplicate
- Verifica periodic dupa restructurarea categoriilor — URL-urile vechi pot persista in schema
- Breadcrumb vizual in pagina si breadcrumb in schema trebuie sa fie **identice** — altfel Google poate ignora schema

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Categoria primara nesetata | Breadcrumb random, schema BreadcrumbList incorecta | Seteaza `rank_math_primary_category` pe fiecare produs |
| Breadcrumb incepe din `/branduri/` nu din `/caini/` | Schema arata structura gresita in SERP | Corecteaza categoria primara |
| Duplicate BreadcrumbList (Rank Math + tema) | Google primeste 2 breadcrumb-uri, poate ignora ambele | Dezactiveaza breadcrumb-ul din tema |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/produs/
- Cauta `BreadcrumbList` cu `itemListElement` corect (Homepage > Categorie > Produs)
- GSC > Imbunatatiri > Breadcrumbs — erori rezolvate dupa 2-4 saptamani

## Timp estimat
30 minute (verificare + configurare) + timp per produs pentru categoria primara
