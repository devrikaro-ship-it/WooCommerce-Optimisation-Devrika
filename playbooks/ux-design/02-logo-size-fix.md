# Logo Size Fix

## Ce face
Seteaza dimensiunea maxima a logo-ului in header via CSS, prevenind afisarea la dimensiunea naturala a fisierului (care poate fi 300-600px). Fara `max-height` explicit, builder-ele (Elementor, Divi) afiseaza logo-ul la dimensiunea originala a imaginii.

## Cand se aplica
- Orice site unde logo-ul apare supradimensionat in header
- Dupa schimbarea imaginii logo cu una mai mare
- Pe teme care nu au setare de logo size in Customizer

## Inainte sa incepi
- Verifica dimensiunea curenta in DevTools: inspect logo > Computed > width/height
- Identifica selectorul corect pentru tema (tabel mai jos)
- **Nu folosi MutationObserver pentru logo** — cauzeaza infinite loop cu alte MO active; CSS simplu e suficient si mai robust

## Implementare

### Pasul 1 — Identifica selectorul logo pentru tema
| Tema | Selector logo |
|------|--------------|
| XStore (etheme) | `.elementor-widget-theme-etheme_site-logo img` |
| Elementor generic | `.elementor-widget-image img` (in header — atentie la alte imagini) |
| Astra | `.ast-site-logo img, .custom-logo` |
| OceanWP | `#site-logo img, .custom-logo-link img` |
| Divi | `#logo img, .et_pb_image_wrap img` (in header section) |
| GeneratePress | `.site-logo img, .custom-logo` |
| WP generic | `.custom-logo-link img, .site-branding img` |

### Pasul 2 — Creeaza snippet CSS-type in WPCode
Titlu: `Client — Logo Size Fix`

### Pasul 3 — Adauga CSS

### Pasul 4 — Verifica dimensiunea in DevTools

## Cod

**Universal (ajusteaza selectorul per tema):**
```css
/* Logo size fix — inlocuieste selectorul cu cel corect pentru tema */
.elementor-widget-theme-etheme_site-logo img,
.custom-logo-link img,
.site-branding img {
    max-height: 80px !important;
    width: auto !important;
    max-width: 220px !important;
    height: auto !important;
    object-fit: contain !important;
}
```

**XStore specific:**
```css
.elementor-widget-theme-etheme_site-logo img {
    max-height: 100px !important;
    width: auto !important;
    max-width: 220px !important;
}
```

**Mobile — logo mai mic pe ecrane mici:**
```css
@media (max-width: 768px) {
    .elementor-widget-theme-etheme_site-logo img,
    .custom-logo-link img {
        max-height: 60px !important;
        max-width: 160px !important;
    }
}
```

## Cum se aplica corect (Best Practice)
- Foloseste `max-height` nu `height` fix — permite logo-uri cu proportii diferite
- `width: auto` obligatoriu impreuna cu `max-height` — altfel logo-ul se distorsioneaza
- Nu folosi MutationObserver — un CSS simplu e mai fiabil si nu cauzeaza loop-uri
- Daca logo-ul apare corect dar se "reseteaza" dupa un timp: alta MO sau JS din tema il modifica → creste specificitatea CSS sau adauga `!important` pe `width`
- Verifica atat desktop cat si mobile

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| MutationObserver care reseteaza dimensiunea logo | Infinite loop cu alte MO → site unclickable | Sterge MO, foloseste CSS |
| Selector prea broad (`.header img`) | Prinde alte imagini din header (bannere, icoane) | Foloseste selectorul specific al widget-ului logo |
| `height` fix in loc de `max-height` | Logo distorsionat pe ecrane cu alta densitate | Foloseste `max-height` + `width: auto` |
| Logo pixelat dupa CSS | Imaginea originala e prea mica | Inlocuieste imaginea cu una @2x sau SVG |

## Verificare
- DevTools > inspect logo > Computed > verifica `width` si `height` rezultate
- Verifica pe 3 breakpoints: desktop (1440px), tablet (768px), mobile (390px)
- Verifica ca alte imagini din header nu sunt afectate

## Timp estimat
15 minute
