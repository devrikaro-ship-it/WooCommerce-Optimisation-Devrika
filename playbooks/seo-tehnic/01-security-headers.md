# Security Headers

## Ce face
Adauga headere HTTP de securitate (HSTS, X-Frame-Options, CSP, Referrer-Policy) care protejeaza site-ul si sunt semnal de incredere pentru Google. Absenta lor = risc clickjacking + scor securitate slab.

## Cand se aplica
- Pe orice site WordPress in productie
- Obligatoriu inainte de orice campanie GMC sau audit securitate
- Nu necesita plugin suplimentar — se face via WPCode PHP snippet

## Inainte sa incepi
- Verifica daca headerele exista deja: `curl -I https://domain.ro | grep -i "strict\|x-frame\|referrer\|content-security"`
- Daca exista in `.htaccess` sau la nivel de hosting, nu duplica via snippet

## Implementare

### Pasul 1 — Verifica headerele curente
```bash
curl -I https://domain.ro
```
Cauta: `Strict-Transport-Security`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`

### Pasul 2 — Creeaza snippet PHP in WPCode
- WPCode > Add New > **PHP type**
- Titlu: `Client — Security Headers`
- Location: `Run Everywhere`

### Pasul 3 — Adauga codul
### Pasul 4 — Activeaza + Salveaza
### Pasul 5 — Verifica cu curl sau securityheaders.com

## Cod

```php
add_action('send_headers', function() {
    if (is_admin()) return;
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    header('Permissions-Policy: geolocation=(), microphone=(), camera=()');
});
```

**Nota:** Nu adauga `Content-Security-Policy` strict fara audit prealabil — poate bloca scripturi Elementor/WooCommerce.

## Cum se aplica corect (Best Practice)
- Foloseste `send_headers` hook, nu `wp_head` — ruleaza mai devreme, inainte de orice output
- Guard `is_admin()` obligatoriu — altfel blocheaza admin panel
- Nu adauga CSP fara sa testezi mai intai in `Content-Security-Policy-Report-Only`
- HSTS cu `max=31536000` = 1 an — odata setat, browserul nu mai accepta HTTP; asigura-te ca HTTPS functioneaza corect
- Verifica ca LiteSpeed/SiteGround nu suprascrie headerele (unele hosting-uri au propriile headere)

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| CSP strict fara audit | Blocheaza Elementor, WC, Google Analytics | Foloseste `Report-Only` mai intai |
| Lipsa `is_admin()` | Admin panel broken | Adauga guard |
| HSTS fara HTTPS functional | Site inaccesibil dupa 1 an | Verifica HTTPS 100% inainte |
| Duplicate cu `.htaccess` | Browser primeste headere duble | Verifica cu curl inainte |

## Verificare
- `curl -I https://domain.ro` — cauta headerele in raspuns
- `https://securityheaders.com/?q=domain.ro` — scor A sau A+
- DevTools > Network > click request > Response Headers

## Timp estimat
20-30 minute
