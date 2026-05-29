# FAQ Schema pe Pagini Produs

## Ce face
Injecteaza schema `FAQPage` in `<head>` pe paginile de produs individual, citind datele din post meta (`_faq_schema`). Permite Google sa afiseze intrebarile si raspunsurile direct in SERP sub rezultatul produsului — creste CTR cu 20-40%.

## Cand se aplica
- Site-uri WooCommerce unde produsele au intrebari frecvente (ingrediente, utilizare, livrare)
- Cand SEO Tool-ul sau un proces extern populeaza `_faq_schema` post meta cu JSON-LD valid
- Nu se aplica daca produsele nu au FAQ-uri redactate

## Inainte sa incepi
- Verifica daca exista deja post meta `_faq_schema` pe produse:
  ```sql
  SELECT post_id, meta_value FROM wp_postmeta WHERE meta_key = '_faq_schema' LIMIT 5;
  ```
- Confirma formatul: trebuie sa fie JSON-LD valid `{"@type":"FAQPage","mainEntity":[...]}`
- Rank Math poate genera FAQPage din blocul FAQ — verifica daca nu e deja prezent

## Implementare

### Pasul 1 — Verifica existenta post meta pe un produs
WP-Admin > Produse > editeaza produs > Custom Fields > cauta `_faq_schema`

### Pasul 2 — Creeaza snippet PHP in WPCode
- PHP type, Run Everywhere

### Pasul 3 — Adauga codul

### Pasul 4 — Activeaza + Salveaza

### Pasul 5 — Verifica pe un produs cu FAQ

## Cod

```php
// Injecteaza FAQPage schema din post meta _faq_schema pe pagini produs
add_action('wp_head', function() {
    if (!is_product()) return;

    $schema = get_post_meta(get_the_ID(), '_faq_schema', true);
    if (empty($schema)) return;

    // Valideaza ca e JSON valid inainte de output
    $decoded = json_decode($schema, true);
    if (!$decoded) return;

    echo '<script type="application/ld+json">'
        . wp_json_encode($decoded, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)
        . '</script>' . "\n";
}, 10);
```

**Format corect pentru `_faq_schema` post meta:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Ce ingrediente contine produsul?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Produsul contine pui, orez si legume naturale, fara aditivi artificiali."
      }
    },
    {
      "@type": "Question",
      "name": "Este potrivit pentru caini cu alergii?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Da, formula este hipoalergenica si nu contine grau, soia sau porumb."
      }
    }
  ]
}
```

**Populeaza `_faq_schema` via WP-CLI (bulk):**
```bash
wp post meta update PRODUCT_ID _faq_schema '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Intrebare?","acceptedAnswer":{"@type":"Answer","text":"Raspuns."}}]}'
```

## Cum se aplica corect (Best Practice)
- **Nu folosi JS** pentru a citi si injecta post meta — JS ruleaza in browser, nu are acces la WP DB; foloseste obligatoriu PHP
- Valideaza JSON inainte de output (`json_decode` + verificare) — un JSON corupt crapa intreaga schema
- Minim 2-3 intrebari per produs pentru a fi eligibil rich result
- Intrebarile trebuie sa fie **unice per produs** — nu acelasi FAQ pe toate produsele
- Rank Math FAQ Block genereaza si el FAQPage schema — nu activa ambele simultan pe acelasi produs

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Snippet JS care citeste post meta | Nu functioneaza — JS nu are acces la WP DB | Inlocuieste cu PHP obligatoriu |
| JSON invalid in post meta | Schema nu se injecteaza sau e corupta | Valideaza cu `json_decode` inainte de output |
| Duplicate cu Rank Math FAQ Block | Google primeste 2 FAQPage pe aceeasi pagina | Dezactiveaza una dintre surse |
| FAQ identic pe toate produsele | Google poate penaliza duplicate content in schema | Intrebari unice sau specifice per produs |

## Verificare
- https://search.google.com/test/rich-results?url=https://domain.ro/produs/
- Cauta tipul `FAQPage` cu `mainEntity` populat
- `curl -s https://domain.ro/produs/ | grep -o '"@type":"FAQPage"'`
- Dupa 2-4 saptamani: cauta produsul in Google si verifica daca apar intrebarile sub rezultat

## Timp estimat
20 minute (implementare snippet) + timp pentru redactare FAQ per produs
