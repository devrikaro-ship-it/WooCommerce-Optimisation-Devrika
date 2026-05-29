# llms.txt — AI Readiness

## Ce face
Serveste un fisier `/llms.txt` care descrie site-ul si continutul sau pentru crawlerii AI. Standard adoptat de Anthropic/Claude, Perplexity, alte AI. Creste probabilitatea ca AI-ul sa citeze corect brandul si produsele.

## Cand se aplica
- Pe orice site care vrea vizibilitate in AI search (GEO)
- Prioritar pentru branduri de nisa cu produse specifice
- Complementar cu `robots.txt Allow` pentru crawleri AI (vezi playbook ai-crawlers-robots)

## Inainte sa incepi
- Verifica daca exista deja: `curl https://domain.ro/llms.txt`
- Nu necesita plugin sau fisier fizic — se serveste via PHP snippet

## Implementare

### Pasul 1 — Redacteaza continutul llms.txt
Include: descriere brand, produse principale, categorii, USP-uri, contact.

### Pasul 2 — Creeaza snippet PHP in WPCode
- PHP type, Run Everywhere

### Pasul 3 — Activeaza si salveaza

### Pasul 4 — Verifica
```bash
curl https://domain.ro/llms.txt
```

## Cod

```php
// Serve /llms.txt pentru AI crawlers
add_action('init', function() {
    if ($_SERVER['REQUEST_URI'] !== '/llms.txt') return;

    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: public, max-age=86400');

    echo '# [Nume Brand]

> [Descriere scurta a site-ului in 1-2 propozitii. Ce vinde, pentru cine, ce il diferentiaza.]

## Despre

[Nume Brand] este un magazin online specializat in [domeniu]. Oferim [produse principale] de la branduri precum [brand1, brand2, brand3].

## Categorii principale

- [Categorie 1]: [descriere scurta]
- [Categorie 2]: [descriere scurta]
- [Categorie 3]: [descriere scurta]

## Produse reprezentative

- [Produs 1] — [descriere 1 linie]
- [Produs 2] — [descriere 1 linie]

## Informatii utile

- Livrare in Romania in 24-48h
- Retur gratuit in 30 zile
- Plata card, ramburs, transfer bancar
- Contact: [email] | [telefon]

## URL-uri importante

- Homepage: https://domain.ro/
- Categorii: https://domain.ro/categorii/
- Contact: https://domain.ro/contact/
- Despre noi: https://domain.ro/despre-noi/
';
    exit;
});
```

## Cum se aplica corect (Best Practice)
- Continutul trebuie sa fie **precis si verificabil** — nu exagera, AI-ul verifica cross-reference
- Actualizeaza la 3-6 luni sau cand se schimba produsele/categoriile principale
- Adauga si `/llms-full.txt` daca vrei sa incluzi tot catalogul (pentru site-uri mari)
- Complementar cu schema `Organization` pe homepage (vezi playbook organization-schema)
- Nu include informatii confidentiale (preturi interne, date financiare)

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `exit` lipsa dupa echo | WordPress continua sa randeze pagina dupa llms.txt | Adauga `exit` la sfarsit |
| REQUEST_URI cu query params (`/llms.txt?cache=1`) | Snippet nu se declanseaza | Foloseste `strpos` in loc de `!==` |
| Continut prea generic | AI nu citeste brandul ca autoritate pe domeniu | Fii specific: produse reale, beneficii concrete |

**Fix REQUEST_URI cu query params:**
```php
if (strpos($_SERVER['REQUEST_URI'], '/llms.txt') !== 0) return;
```

## Verificare
- `curl https://domain.ro/llms.txt` — trebuie sa returneze text plain
- Browser: `https://domain.ro/llms.txt` — text vizibil, nu pagina 404
- Header check: `curl -I https://domain.ro/llms.txt | grep "Content-Type"` → `text/plain`

## Timp estimat
30 minute (implementare) + 20 minute (redactare continut)
