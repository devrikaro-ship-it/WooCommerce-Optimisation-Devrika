# Fix @type Article → WebPage pe Homepage

## Ce face
Corecteaza schema gresita de pe homepage care are `@type: Article` in loc de `WebPage` sau `CollectionPage`. Rank Math seteaza implicit `Article` pe unele pagini statice — pe homepage e incorect semantic si poate cauza erori in GSC.

## Cand se aplica
- Cand Rich Results Test pe homepage arata `@type: Article` (nu e o pagina de articol)
- Cand GSC > Imbunatatiri > Articole arata erori pe homepage
- Dupa instalare Rank Math cu setari default

## Inainte sa incepi
```bash
curl -s https://domain.ro/ | python3 -c "
import sys, json, re
html = sys.stdin.read()
scripts = re.findall(r'application/ld\+json.*?>(.*?)</script>', html, re.DOTALL)
for s in scripts:
    try:
        d = json.loads(s.strip())
        graphs = d.get('@graph', [d])
        for item in graphs:
            if 'type' in str(item.get('@type','')).lower() or 'Article' in str(item.get('@type','')):
                print(item.get('@type'), item.get('url',''))
    except: pass
"
```

## Implementare

### Optiunea 1 — Rank Math UI (recomandat)
Editeaza Homepage > Rank Math > Schema > schimba tipul de la Article la WebPage

### Optiunea 2 — PHP filter
```php
add_filter('rank_math/json_ld', function($data, $jsonld) {
    if (!is_front_page()) return $data;

    foreach ($data as &$item) {
        if (!is_array($item)) continue;
        if (in_array($item['@type'] ?? '', ['Article', 'BlogPosting', 'NewsArticle'])) {
            $item['@type'] = 'WebPage';
            // sterge campuri specifice Article care nu se aplica
            unset($item['author'], $item['datePublished'], $item['dateModified'], $item['articleBody']);
        }
        if (isset($item['@graph'])) {
            foreach ($item['@graph'] as &$g) {
                if (in_array($g['@type'] ?? '', ['Article', 'BlogPosting', 'NewsArticle'])) {
                    $g['@type'] = 'WebPage';
                    unset($g['author'], $g['datePublished'], $g['articleBody']);
                }
            }
        }
    }
    return $data;
}, 99, 2);
```

## Cum se aplica corect (Best Practice)
- Preferabil fix din UI Rank Math — mai robust decat PHP filter
- `WebPage` = homepage generica, `CollectionPage` = homepage cu lista de produse/categorii, `ItemPage` = pagina de produs
- Dupa schimbare: sterge cache si re-verifica cu Rich Results Test
- Nu schimba tipul pe paginile de blog/articole — acolo `Article` e corect

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Schimbi tipul si pe pagini de blog | Blog posts cu @type WebPage = incorect | Guard `is_front_page()` strict |
| Campuri Article raman dupa schimbare tip | Schema invalida (author pe WebPage) | Sterge campurile specifice Article |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/
- Nu trebuie sa mai apara `Article` sau `BlogPosting` pe homepage
- GSC > Imbunatatiri > Articole — homepage disparuta din lista de erori

## Timp estimat
15 minute
