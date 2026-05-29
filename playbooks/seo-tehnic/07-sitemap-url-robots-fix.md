# Fix URL Sitemap in robots.txt

## Ce face
Corecteaza discrepanta dintre URL-ul sitemap declarat in robots.txt si URL-ul real al sitemap-ului. O declaratie gresita face ca Googlebot sa nu gaseasca sitemap-ul automat, reducand viteza de indexare.

## Cand se aplica
- Cand robots.txt declara `Sitemap: https://domain.ro/sitemap_index.xml` dar URL-ul real e `/sitemap.xml` (sau invers)
- Dupa migrari de la Yoast la Rank Math sau invers (genereaza URL-uri diferite)
- Cand GSC arata eroare "Nu s-a putut prelua sitemap-ul"

## Inainte sa incepi
```bash
# Verifica ce declara robots.txt
curl https://domain.ro/robots.txt | grep -i sitemap

# Verifica ce URL-uri de sitemap exista efectiv
curl -I https://domain.ro/sitemap.xml
curl -I https://domain.ro/sitemap_index.xml
# 200 = exista, 301/404 = nu exista
```

## Implementare

### Pasul 1 — Identifica URL-ul corect al sitemap-ului
Rank Math genereaza: `/sitemap_index.xml`
Yoast genereaza: `/sitemap_index.xml`
Sitemap static: `/sitemap.xml`

### Pasul 2 — Corecteaza in Rank Math
Rank Math > Sitemap > verifica URL-ul generat > copiaza URL-ul exact

### Pasul 3 — Corecteaza in robots.txt
Rank Math > General > Edit robots.txt > actualizeaza linia Sitemap:

### Pasul 4 — Daca fisierul fizic robots.txt are prioritate
Editeaza direct `/robots.txt` de pe server sau via PHP ONE-SHOT.

## Cod

**PHP filter pentru a corecta URL sitemap in robots.txt dinamic:**
```php
add_filter('robots_txt', function($output) {
    // Inlocuieste URL-ul gresit cu cel corect
    $output = str_replace(
        'Sitemap: https://domain.ro/sitemap_index.xml',
        'Sitemap: https://domain.ro/sitemap.xml',
        $output
    );
    // Daca nu exista deloc, adauga
    if (strpos($output, 'Sitemap:') === false) {
        $output .= "\nSitemap: https://domain.ro/sitemap_index.xml\n";
    }
    return $output;
});
```

**Fix categorie cu URL broken in sitemap Rank Math (ex: "Fara categorie"):**
```php
// ONE-SHOT: exclude categoria din sitemap via noindex pe termen
add_action('init', function() {
    if (!current_user_can('manage_options')) return;
    // term_id = ID-ul categoriei cu URL broken
    $term_id = 15; // inlocuieste cu ID-ul corect
    update_term_meta($term_id, 'rank_math_robots', ['noindex']);
    // Invalideaza cache Rank Math sitemap
    delete_transient('rank_math_sitemap_index');
    wp_clear_scheduled_hook('rank_math/sitemap/cron_ping');
    die('Done: term ' . $term_id . ' set to noindex in sitemap');
});
// Acceseaza o data: https://domain.ro/?run_sitemap_fix=1
// Adauga si conditia: if (!isset($_GET['run_sitemap_fix'])) return;
```

**Filter Rank Math pentru a exclude termeni din sitemap:**
```php
add_filter('rank_math/sitemap/skip_terms', function($skip) {
    $skip[] = 15; // ID termen de exclus
    return $skip;
});
```

## Cum se aplica corect (Best Practice)
- Trimite sitemap-ul manual in GSC dupa fix: GSC > Sitemaps > Adauga sitemap nou
- Dupa modificare robots.txt: asteapta 24-48h sau forteaza recrawl din GSC
- Verifica ca sitemap-ul nu contine URL-uri cu 404 sau redirecturi inainte de a-l trimite
- "Fara categorie" (Uncategorized) WC/WP apare frecvent in sitemap cu URL broken — exclud-o implicit

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `rank_math/sitemap/skip_terms` nu functioneaza in unele versiuni | Termenul continua sa apara | Foloseste `update_term_meta` cu noindex |
| Fisier fizic robots.txt suprascrie filtrul PHP | Fix-ul nu se aplica | Editeaza fisierul fizic direct |
| Cache Rank Math sitemap nu e invalidat dupa fix | Sitemap vechi servit | `delete_transient('rank_math_sitemap_index')` |

## Verificare
- `curl https://domain.ro/robots.txt | grep Sitemap` — URL corect
- `curl -I https://[URL_SITEMAP]` — raspuns 200 OK
- GSC > Sitemaps > Re-submit > stare "Succes"
- `curl -s https://domain.ro/sitemap_index.xml | grep "fara-"` — URL broken dispare

## Timp estimat
20-30 minute
