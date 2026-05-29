# Category Description Editorial

## Ce face
Adauga si afiseaza descrierea editoriala a categoriei (200+ cuvinte) pe paginile de arhiva WooCommerce, vizibil sub H1 si deasupra produselor. Continut indexabil, semnal E-E-A-T, ranking pentru keyword-uri de categorie.

## Cand se aplica
- Categorii principale fara continut editorial (H1 = un cuvant, zero text)
- Prioritar: categorii cu volum de cautare (ex: "hrana caini", "hrana pisici")
- Minim 200 cuvinte per categorie pentru impact SEO

## Inainte sa incepi
- Verifica daca tema afiseaza deja descrierea categoriei (unele teme o afiseaza automat)
- WooCommerce > Produse > Categorii > editeaza categoria > camp "Descriere" (accept HTML)
- Verifica ca WPCode snippet nu duplica afisarea cu ce face tema

## Implementare

### Pasul 1 — Scrie descrierile categoriilor
In WC Admin > Categorii > editeaza fiecare categorie > adauga descriere in campul text.

### Pasul 2 — Verifica daca tema afiseaza automat descrierea
Daca nu: adauga snippet PHP.

### Pasul 3 — Creeaza snippet PHP in WPCode
- PHP type

### Pasul 4 — Adauga codul + CSS

## Cod

**PHP — afiseaza descriere categorie sub H1, deasupra produselor:**
```php
add_action('woocommerce_before_shop_loop', function() {
    if (!is_product_category()) return;

    $term = get_queried_object();
    if (!$term || empty($term->description)) return;

    echo '<div class="category-description-editorial">'
        . wp_kses_post($term->description)
        . '</div>';
}, 5); // priority 5 = inainte de produse (default WC e 10)
```

**CSS (CSS-type snippet):**
```css
.category-description-editorial {
    margin-bottom: 32px;
    font-size: 15px;
    line-height: 1.7;
    color: #475569;
    max-width: 800px;
}

.category-description-editorial h2 {
    font-size: 18px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 8px;
}

.category-description-editorial ul {
    padding-left: 20px;
    margin-bottom: 16px;
}

.category-description-editorial a {
    color: #2563eb;
    text-decoration: underline;
}
```

**Template descriere recomandata (pentru redactare):**
```
[Categorie] — [Descriere generala 2-3 propozitii cu keyword principal]

## De ce sa alegi [produse din categorie] de la [Brand]?

[3-4 puncte cu beneficii specifice, include keyword-uri secundare]

## Ce gasesti in aceasta sectiune

[Subcategorii linkuite, tipuri de produse, branduri reprezentative]

## Sfaturi de alegere

[2-3 sfaturi practice relevante pentru clientul tinta]
```

## Cum se aplica corect (Best Practice)
- **Nu copia aceeasi descriere pe categorii diferite** — duplicate content penalizat de Google
- Minim 200 cuvinte, recomandat 300-400 pentru categorii mari
- Include keyword-ul principal al categoriei natural in primele 2 propozitii
- Adauga linkuri interne catre subcategorii si produse reprezentative
- Verifica ca descrierea nu duplica ce afiseaza deja tema (hook-ul se poate adauga de doua ori)
- Pe mobile: verifica ca textul nu e prea lung si nu impinge produsele prea jos

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Descriere identica pe mai multe categorii | Penalizare duplicate content | Descrieri unice per categorie |
| Tema afiseaza si ea descrierea | Continut duplicat pe pagina | Dezactiveaza afisarea din tema sau nu adauga snippet |
| HTML invalid in descriere WC | Layout broken | Testeaza cu `wp_kses_post()` sau editeaza in modul Text din editor |
| Descriere prea lunga impinge produsele | UX degradat | Foloseste "Citeste mai mult" expand sau max 400 cuvinte vizibile |

## Verificare
- Pagina categorie: textul descrierii vizibil sub H1, deasupra grilei de produse
- `curl -s https://domain.ro/categorie/ | grep -c "category-description-editorial"` → 1
- Lungime text: minim 200 cuvinte per categorie
- Mobile: textul nu impinge produsele excesiv de jos

## Timp estimat
20 minute (implementare snippet) + 30-60 minute per categorie (redactare)
