# LiteSpeed Cache Setup pentru WooCommerce

## Ce face
Configureaza LiteSpeed Cache pe un server LiteSpeed/OpenLiteSpeed pentru a cache-ui paginile WooCommerce, reducand TTFB de la 600ms+ la sub 100ms pe paginile cached.

## Cand se aplica
- Site-uri pe hosting cu server LiteSpeed (Hostgate, SiteGround, Namecheap, multe shared hosting)
- Cand WP Rocket nu e activ sau nu are licenta
- Verifica server: `curl -I https://domain.ro | grep -i server` → `LiteSpeed`

## Inainte sa incepi
- Verifica serverul: `curl -I https://domain.ro | grep -i "server\|x-litespeed"`
- Dezactiveaza orice alt plugin de cache (WP Rocket, W3 Total Cache) inainte de activare
- LiteSpeed Cache functioneaza **doar pe servere LiteSpeed** — pe Apache/Nginx nu face nimic util

## Implementare

### Pasul 1 — Instaleaza pluginul
Plugins > Adauga Nou > cauta "LiteSpeed Cache" > Instaleaza + Activeaza

### Pasul 2 — Configurare de baza
LiteSpeed Cache > Cache:
- Enable Cache: **ON**
- Cache Logged-in Users: **OFF** (important pentru WC)
- Cache Commenters: **OFF**

### Pasul 3 — WooCommerce exclusions (automate)
LiteSpeed Cache detecteaza WooCommerce automat si exclude:
- `/cart/`
- `/checkout/`
- `/my-account/`
- Pagini cu cookie `woocommerce_items_in_cart`

Verifica: LiteSpeed Cache > Cache > Excludes — aceste pagini trebuie sa fie excluse.

### Pasul 4 — TTL
LiteSpeed Cache > Cache > TTL:
- Default Public Cache TTL: `604800` (7 zile) — recomandat pentru e-commerce cu produse stabile
- Sau `86400` (1 zi) daca preturile/stocurile se schimba frecvent

### Pasul 5 — Verifica headers
```bash
curl -I https://domain.ro/caini/
# Trebuie sa apara:
# x-litespeed-cache-control: public,max-age=604800
# x-litespeed-cache: hit
```

## Cod

**Flush cache programatic (via PHP):**
```php
// Flush cache LiteSpeed programatic
if (class_exists('LiteSpeed_Cache_API')) {
    LiteSpeed_Cache_API::purge_all();
}
// sau
do_action('litespeed_purge_all');
```

**Exclude URL-uri custom din cache:**
```php
// Adauga excluderi custom pentru LiteSpeed Cache
add_filter('litespeed_cache_force_miss', function($force_miss) {
    // Exclude paginile cu parametru user-specific
    if (isset($_GET['user_token'])) return true;
    return $force_miss;
});
```

## Cum se aplica corect (Best Practice)
- Dezactiveaza WP Rocket inainte de LiteSpeed Cache — doua plugin-uri de cache = conflict garantat
- **Nu activa "Cache Logged-in Users"** pe site-uri WooCommerce — utilizatorii logati vad cosul altor useri
- Verifica `x-litespeed-cache: hit` in headers dupa prima vizita — daca nu apare, cache-ul nu functioneaza
- Flush cache dupa orice modificare de CSS/JS/PHP snippeturi
- LiteSpeed nu sterge transient-urile WordPress la flush — acestea se gestioneaza separat

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Activ pe server non-LiteSpeed | Pluginul nu face nimic, dar consuma resurse | Verifica serverul inainte de instalare |
| WP Rocket + LiteSpeed Cache simultan | Conflict, cache inconsistent | Dezactiveaza WP Rocket |
| Cache Logged-in Users ON | Utilizatorii logati vad datele altora | OFF obligatoriu pe site-uri WC |
| Nu verifica cu curl | Crezi ca functioneaza dar cache-ul nu e activ | `curl -I` + verifica `x-litespeed-cache: hit` |

## Verificare
```bash
# Prima vizita (cache miss):
curl -I https://domain.ro/caini/ | grep "x-litespeed"
# → x-litespeed-cache: miss

# A doua vizita (cache hit):
curl -I https://domain.ro/caini/ | grep "x-litespeed"
# → x-litespeed-cache: hit
# → x-litespeed-cache-control: public,max-age=604800
```

## Timp estimat
30 minute (instalare + configurare + verificare)
