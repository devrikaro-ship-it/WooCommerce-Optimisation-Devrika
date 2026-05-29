# Chaty Widget — Fix Overlap Mobile

## Ce face
Corecteaza pozitionarea widget-ului Chaty (chat flotant) pe mobile, prevenind acoperirea primului card de produs sau a butonului "Adauga in cos". Chaty implicit se pozitioneaza `bottom: 15px` ceea ce pe ecrane mici acopera continut interactiv.

## Cand se aplica
- Site-uri cu plugin Chaty instalat si activ
- Cand pe mobile (< 480px) widget-ul Chaty acopera produse, butoane sau alt continut
- Verifica: pe 390px viewport, primul produs din grid e acoperit de butonul Chaty?

## Inainte sa incepi
- Identifica selectorul Chaty: DevTools > inspect widget > clasa container (ex: `#chaty-widget`, `.chaty-pos-left`, `.chaty-pos-right`)
- Verifica pozitia curenta in DevTools: Computed > `bottom`, `right`/`left`

## Implementare

### Pasul 1 — Identifica selectorul si pozitia curenta
```javascript
// DevTools Console:
const chaty = document.querySelector('[id*="chaty"], [class*="chaty"]');
console.log(chaty?.id, chaty?.className);
console.log(getComputedStyle(chaty).bottom, getComputedStyle(chaty).right);
```

### Pasul 2 — Creeaza snippet CSS-type in WPCode

### Pasul 3 — Adauga CSS cu media query

## Cod

```css
/* Chaty widget — muta mai sus pe mobile ca sa nu acopere produsele */
@media (max-width: 480px) {
    #chaty-widget,
    .chaty-pos-right,
    .chaty-pos-left,
    [class*="chaty-channel-list"] {
        bottom: 70px !important; /* ajusteaza valoarea */
    }
}

@media (max-width: 768px) {
    #chaty-widget,
    .chaty-pos-right,
    .chaty-pos-left {
        bottom: 60px !important;
    }
}
```

**Daca widget-ul Chaty are si un buton de deschidere separat:**
```css
@media (max-width: 480px) {
    .chaty-open-btn,
    .chaty-close-btn,
    [class*="chaty-widget-"] {
        bottom: 70px !important;
    }
}
```

## Cum se aplica corect (Best Practice)
- Testeaza pe viewport real de 390px (iPhone 14) nu doar resize browser
- Valoarea `bottom: 70px` e un punct de start — ajusteaza vizual per site
- Verifica si cu sticky footer (ex: "Adauga in cos" sticky pe mobile) — poate trebui `bottom: 90px`
- Verifica dupa update plugin Chaty — uneori update-ul schimba selectorul

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Selector gresit dupa update Chaty | CSS nu se aplica | Re-identifica selectorul cu DevTools |
| `bottom` insuficient | Widget inca acopera continut | Creste valoarea la 80-90px |
| Fix pe desktop din greseala | Widget prea sus pe desktop | Wraps strict in `@media (max-width: 480px)` |

## Verificare
- DevTools > toggle mobile view (390px)
- Scroll la primul produs din grid: butonul "Adauga in cos" trebuie sa fie clickabil
- Widget Chaty vizibil dar nu acoperitor

## Timp estimat
15 minute
