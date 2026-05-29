# Images Contain — Grid Produse WooCommerce

## Ce face
Forteaza `object-fit: contain` pe imaginile din gridul de produse WooCommerce, eliminand taierile (cropping) si asigurand ca intregul produs e vizibil indiferent de proportia imaginii. Esential pe site-uri cu imagini de produse in formate mixte.

## Cand se aplica
- Site-uri WooCommerce unde imaginile din grid sunt taiate sau distorsionate
- Cand produsele au imagini cu proportii diferite (patrate, portret, landscape)
- Nu se aplica daca clientul vrea deliberat `cover` (imagini full-bleed uniform)

## Inainte sa incepi
- **CRITIC: verifica daca exista snippeturi active cu `object-fit: cover`** — conflict silentios
  ```
  WPCode > cauta "cover" in lista snippeturi active
  ```
- Dezactiveaza orice snippet cu `cover` pe imagini produs INAINTE de a adauga `contain`
- Verifica selectorul corect pentru tema: DevTools > inspect imagine produs > copie selector

## Implementare

### Pasul 1 — Gaseste selectorul corect pentru tema
| Tema | Selector imagine produs |
|------|------------------------|
| XStore (etheme) | `li.product .woocommerce-product-gallery__image img, li.product .etheme-product-grid-item img` |
| Astra | `li.product .woocommerce-loop-product__link img` |
| OceanWP | `li.product .woocommerce-LoopProduct-link img` |
| Flatsome | `li.product .box-image img` |
| Generic WC | `li.product img:not(.logo):not(.attachment-logo)` |

### Pasul 2 — Dezactiveaza snippeturi conflictuale
Orice snippet cu `cover` pe imagini produs → dezactiveaza INAINTE

### Pasul 3 — Creeaza snippet CSS-type in WPCode

### Pasul 4 — Verifica vizual pe pagina categorie

## Cod

```css
/* === Contain imagini produs — grid WooCommerce === */

/* Container cu aspect ratio fix */
li.product .woocommerce-product-gallery__image,
li.product .product-images-holder,
li.product .image-container,
li.product a.woocommerce-loop-product__link > img {
    aspect-ratio: 1 / 1;
    overflow: hidden;
    display: block;
}

/* Imaginea — contain, centrata */
li.product img:not(.logo):not([class*="logo"]):not([class*="site-logo"]) {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    object-position: center center !important;
    background-color: #ffffff !important;
}

/* Protectie logo header — nu prinde imaginile din nav/header */
header img,
nav img,
.site-header img,
.elementor-widget-theme-etheme_site-logo img,
.custom-logo-link img {
    object-fit: unset !important;
    width: auto !important;
    height: auto !important;
}
```

**Varianta XStore cu nuclear specificity (cand CSS-ul temei bate snippet-ul):**
```css
html body li.product .etheme-product-grid-item .product-image-container img,
html body li.product .woocommerce-LoopProduct-link img {
    object-fit: contain !important;
    object-position: center !important;
    background: #fff !important;
    width: 100% !important;
    height: 100% !important;
}
```

## Cum se aplica corect (Best Practice)
- **Nu folosi selector broad** (`.product-image img`, `img`) — prinde logo-ul din header
- Adauga intotdeauna **protectie logo** in CSS (exclude `.site-logo`, `header img`, `.custom-logo`)
- Verifica pe desktop SI mobile dupa implementare
- `background-color: #ffffff` pe imagine = spatiul alb uniform pe continut transparent (PNG)
- Daca theme CSS bate snippet-ul: creste specificitatea cu `html body` prefix sau adauga `!important` pe toate proprietatile

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Selector broad prinde logo | Logo distorsionat in header | Adauga protectie `header img { object-fit: unset }` |
| `cover` si `contain` active simultan | Comportament impredictibil pe unele imagini | Dezactiveaza snippetul cu `cover` inainte |
| Aspect ratio lipsa pe container | Containere colapsate sau inaltime 0 | Adauga `aspect-ratio: 1/1` sau `height` fix |
| MutationObserver JS in loc de CSS | Loop infinit cu alte MO active, site unclickable | Foloseste exclusiv CSS, fara JS |

## Verificare
- DevTools > inspect imagine produs > Computed > `object-fit: contain`
- Verifica 4 produse cu proportii diferite — toate trebuie sa apara intregi, netatiate
- Verifica logo header — trebuie sa ramana neschimbat
- Verifica pe mobile (390px)

## Timp estimat
30 minute
