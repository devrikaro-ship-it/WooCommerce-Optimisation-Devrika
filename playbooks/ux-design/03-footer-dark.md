# Footer Dark — CSS-type Snippet

## Ce face
Stilizeaza footer-ul site-ului cu fundal inchis (dark), text alb semitransparent, headinguri cu underline colorat, si badge-uri de plata/siguranta orizontale. Creste credibilitatea si aspectul profesional al site-ului.

## Cand se aplica
- Site-uri cu footer Elementor (sectiune cu ID specific)
- Cand footer-ul are aspect generic/alb fara diferentiere vizuala
- Necesita identificarea ID-ului Elementor al sectiunii footer

## Inainte sa incepi
- Identifica ID-ul sectiunii Elementor footer: DevTools > inspect sectiunea footer > clasa `elementor-element-XXXXXXXX`
- Noteaza ID-urile coloanelor/elementelor importante (titluri meniu, sectiunea de copyright, badge-uri)
- **Creeaza snippet CSS-type** — nu PHP cu echo style

## Implementare

### Pasul 1 — Gaseste ID-ul sectiunii footer
```javascript
// In DevTools Console pe pagina cu footer vizibil:
Array.from(document.querySelectorAll('section[class*="elementor-element"]'))
    .slice(-5)
    .map(s => s.className.match(/elementor-element-([a-z0-9]+)/)?.[1])
```

### Pasul 2 — Creeaza snippet CSS-type in WPCode
Titlu: `Client — Footer CSS`

### Pasul 3 — Adauga CSS (inlocuieste ID-urile cu cele ale clientului)

### Pasul 4 — Activeaza si verifica vizual

## Cod

```css
/* === Footer Dark — inlocuieste elementor-element-XXXXXXXX cu ID-ul real === */

/* Fundal si padding sectiune principala footer */
section.elementor-element-XXXXXXXX {
    background-color: #141928 !important;
    padding-top: 48px !important;
    padding-bottom: 0 !important;
}

/* Text general footer */
.elementor-element-XXXXXXXX p,
.elementor-element-XXXXXXXX li,
.elementor-element-XXXXXXXX span:not(.et-icon):not(.screen-reader-text) {
    color: rgba(255,255,255,0.60) !important;
}

/* Headinguri coloane */
.elementor-element-XXXXXXXX .elementor-heading-title {
    color: #fff !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding-bottom: 10px !important;
    margin-bottom: 10px !important;
    position: relative !important;
}

/* Linie decorativa sub headinguri */
.elementor-element-XXXXXXXX .elementor-heading-title::after {
    content: "" !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 28px !important;
    height: 2px !important;
    background: #5b8def !important; /* culoarea brand */
    display: block !important;
}

/* Linkuri */
.elementor-element-XXXXXXXX a {
    color: rgba(255,255,255,0.60) !important;
    text-decoration: none !important;
}
.elementor-element-XXXXXXXX a:hover {
    color: #fff !important;
}

/* Linie despartitoare + sectiune copyright */
section.elementor-element-YYYYYYYY { /* ID sectiune copyright */
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    padding-top: 20px !important;
    padding-bottom: 20px !important;
    margin-top: 40px !important;
}

/* Text copyright */
.elementor-element-ZZZZZZZZ,
.elementor-element-ZZZZZZZZ p,
.elementor-element-ZZZZZZZZ a {
    color: rgba(255,255,255,0.30) !important;
    font-size: 12px !important;
}

/* Badge-uri plata orizontale */
.footerImages .elementor-widget-wrap {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 10px !important;
    flex-wrap: nowrap !important;
}
.footerImages .elementor-widget {
    flex: 0 0 auto !important;
    margin: 0 !important;
}

/* Inaltimea badge-urilor */
.footerImages img {
    height: 30px !important;
    width: auto !important;
    opacity: 0.85 !important;
}
```

## Cum se aplica corect (Best Practice)
- Snippet **CSS-type**, nu PHP cu `add_action('wp_head', function() { echo '<style>'; })` — PHP echo style e mai lent si mai greu de intretinut
- ID-urile Elementor (`elementor-element-XXXXXXXX`) sunt unice per site — identifica-le cu DevTools pe site-ul clientului curent
- Daca dezactivezi snippet-ul PHP vechi: **creeaza mai intai CSS-type replacement**, verifica, abia apoi dezactiveaza PHP-ul
- Schimba culoarea accentului (`#5b8def`) cu culoarea brand a clientului
- Adauga clasa CSS `footerImages` manual in Elementor pe containerul de badge-uri daca nu exista

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Snippet PHP cu `echo '<style>'` dezactivat fara replacement | Footer fara CSS, layout broken | Creeaza CSS-type snippet inainte de dezactivare |
| ID Elementor gresit (copiat de pe alt site) | CSS nu se aplica | Identifica ID-ul cu DevTools pe site-ul curent |
| Multiple snippeturi PHP footer active simultan | Stil inconsistent, CSS duplicat | Consolideaza intr-un singur snippet CSS-type |
| Lipseste `background-color` pe sectiunea footer | Footer ramane alb | Asigura-te ca selectorul prinde sectiunea corecta |

## Verificare
- Navigheaza la homepage si scroll la footer
- Verifica: fundal inchis, text alb, headinguri cu linie decorativa
- DevTools > computed pe sectiunea footer > `background-color: rgb(20, 25, 40)`
- Verifica si pe mobile

## Timp estimat
45-60 minute (identificare ID-uri + implementare)
