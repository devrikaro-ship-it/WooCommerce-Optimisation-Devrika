# Breadcrumb Redesign + Above H1

## Ce face
Restilizeaza breadcrumb-ul Rank Math (culori, separatori, marime text) si il muta deasupra H1-ului pe paginile de arhiva, respectand ierarhia vizuala corecta (breadcrumb → H1 → produse).

## Cand se aplica
- Site-uri cu Rank Math Breadcrumbs active
- Cand breadcrumb-ul apare dupa H1 sau e invizibil/nestiilizat
- Necesita identificarea claselor Elementor pentru breadcrumb si H1 widgets

## Inainte sa incepi
- Rank Math > General > Breadcrumbs > ON
- Identifica ID-urile Elementor pentru widget breadcrumb si widget H1:
  ```javascript
  // DevTools Console pe pagina categorie:
  document.querySelector('.rank-math-breadcrumb')?.closest('[class*="elementor-element"]')?.className
  document.querySelector('h1')?.closest('[class*="elementor-element"]')?.className
  ```
- Ambele widget-uri trebuie sa fie in acelasi `.elementor-widget-wrap` container

## Implementare

### Pasul 1 — Identifica structura DOM
Gaseste ID-ul Elementor al widget-ului breadcrumb si al widget-ului H1. Verifica ca sunt in acelasi flex container.

### Pasul 2 — Creeaza snippet CSS-type in WPCode
Titlu: `Client — Breadcrumb Redesign`

### Pasul 3 — Adauga CSS

### Pasul 4 — Verifica pe pagina categorie

## Cod

**CSS complet breadcrumb redesign + above H1:**
```css
/* === Breadcrumb Redesign === */

/* Container breadcrumb */
.rank-math-breadcrumb p {
    display: flex !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    gap: 0 !important;
    font-size: 12px !important;
    margin: 0 !important;
    padding: 2px 0 !important;
}

/* Linkuri */
.rank-math-breadcrumb a {
    color: #9ca3af !important;
    text-decoration: none !important;
    font-weight: 400 !important;
    transition: color 0.15s !important;
    white-space: nowrap !important;
}
.rank-math-breadcrumb a:hover {
    color: #374151 !important;
}

/* Separator: inlocuieste " - " cu › */
.rank-math-breadcrumb .separator {
    font-size: 0 !important;
    padding: 0 2px !important;
}
.rank-math-breadcrumb .separator::after {
    content: "›" !important;
    font-size: 12px !important;
    color: #d1d5db !important;
    padding: 0 6px !important;
    font-weight: 400 !important;
}

/* Pagina curenta (ultimul item) */
.rank-math-breadcrumb .last {
    color: #374151 !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 320px !important;
    display: inline-block !important;
    vertical-align: middle !important;
    font-size: 12px !important;
}

/* === Breadcrumb DEASUPRA H1 === */
/* Inlocuieste cu ID-ul Elementor al widget-ului breadcrumb */
.elementor-element-BREADCRUMB_ID {
    order: -1 !important;
}
```

**Gaseste ID-urile automat:**
```javascript
// DevTools Console pe pagina categorie:
const bc = document.querySelector('.rank-math-breadcrumb');
const h1 = document.querySelector('h1');
if (bc && h1) {
    const bcWidget = bc.closest('[class*="elementor-element-"]');
    const h1Widget = h1.closest('[class*="elementor-element-"]');
    console.log('Breadcrumb widget:', bcWidget?.className?.match(/elementor-element-([a-z0-9]+)/)?.[1]);
    console.log('H1 widget:', h1Widget?.className?.match(/elementor-element-([a-z0-9]+)/)?.[1]);
    console.log('Same parent:', bcWidget?.parentElement === h1Widget?.parentElement);
}
```

## Cum se aplica corect (Best Practice)
- `order: -1` functioneaza doar daca breadcrumb-ul si H1-ul sunt in acelasi **flex container** (`.elementor-widget-wrap`)
- Verifica ca parintele comun are `display: flex` — Elementor il seteaza automat
- Daca sunt in containere diferite: restructureaza in Elementor UI sau foloseste `position: absolute` (mai complex)
- ID-ul Elementor al breadcrumb-ului se schimba daca template-ul e modificat — re-verifica dupa orice editare Elementor

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `order: -1` pe widget din alt container decat H1 | Nu se muta, CSS nu are efect | Verifica ca sunt in acelasi `.elementor-widget-wrap` |
| ID Elementor gresit | CSS nu se aplica | Identifica din nou cu DevTools |
| Breadcrumb ascuns de tema | Nu apare deloc dupa CSS | Verifica ca Rank Math breadcrumb widget e in template |
| Separator " - " nu dispare complet | `font-size: 0` nu functioneaza pe toate browserele | Adauga `display: none` si injecteaza separator cu `::after` |

## Verificare
- Pagina categorie: breadcrumb vizibil DEASUPRA H1
- Separatorul e `›` nu ` - `
- Ultimul item (pagina curenta) e in culoare mai inchisa
- DevTools > computed pe `.elementor-element-BREADCRUMB_ID` > `order: -1`

## Timp estimat
30 minute
