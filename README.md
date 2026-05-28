# WooCommerce Optimisation — Devrika

Framework intern Devrika pentru optimizarea completa a oricarui site WooCommerce.
Bazat pe experienta reala din proiecte: puria.ro, diente.ro, brisa.ro.

---

## Ce contine acest repo

| Fisier | Rol |
|--------|-----|
| `CHECKLIST-TEMPLATE.md` | Template universal per client — copiaza si completeaza |
| `BEST-PRACTICES.md` | Metode corecte de lucru validate in productie |
| `MISTAKES.md` | Greseli documentate — citeste inainte de orice implementare |
| `scripts/` | Scripturi Playwright reutilizabile per client |
| `clients/[client]/` | Dosare per client cu audit, plan de actiuni, documentatie |

---

## Cum se foloseste pentru un client nou

### Pas 1 — Setup initial
```
cp CHECKLIST-TEMPLATE.md clients/[client.ro]/CHECKLIST.md
```
Completeaza FAZA 0 din checklist (date client, acces, stack).

### Pas 2 — Audit SEO
Ruleaza `/seo-audit [URL]` in Claude Code.
Output: `FULL-AUDIT-REPORT.md` + `ACTION-PLAN.md` → salveaza in `clients/[client]/`.

### Pas 3 — UX Review
Ruleaza `/ui-ux-pro-max review [URL]` in Claude Code pe baza screenshot-urilor din audit.
Documenteaza recomandarile in `clients/[client]/UX-REVIEW.md`.

### Pas 4 — Implementare (Faze 3-8 din checklist)
Bifeaza fazele in ordine. Nu sari peste faze. Nu implementa fara audit.

### Pas 5 — Documentatie post-implementare
Actualizeaza `clients/[client]/DOCUMENTATION.md` cu ce s-a implementat, ID-uri snippet-uri active, starea finala.

---

## Structura repo

```
WooCommerce-Optimisation-Devrika/
├── README.md
├── CHECKLIST-TEMPLATE.md
├── BEST-PRACTICES.md
├── MISTAKES.md
├── scripts/
│   ├── fix_category_rules_v2.js
│   └── fix1_category_mapping.js
└── clients/
    └── puria.ro/
        ├── CHECKLIST.md
        ├── DOCUMENTATION.md
        ├── FULL-AUDIT-REPORT.md
        └── ACTION-PLAN.md
```

---

## Reguli critice — citeste inainte de orice

1. **Nu adauga `<?php` in snippeturi WPCode** — WPCode il adauga automat. Tag dublu = fatal parse error, site down.
2. **Nu MutationObserver pe `style` cu `removeProperty`** — infinite loop, site unclickable.
3. **Nu selectoare broad** (`.product-image img`) — prinde logo. Mereu `li.product` sau `li.product img`.
4. **Nu headless Playwright** — foloseste `headless: false` + `slowMo: 200` pentru login WP.
5. **Nu dezactiva WPCode via form POST fara `snippet_id`** — creeaza snippet nou in loc sa dezactiveze.
6. **Nu lasa snippeturi ONE-SHOT active** — dezactiveaza imediat dupa prima rulare confirmata.
7. **Nu crea snippet nou inainte sa dezactivezi pe cel vechi** — duplicatele CSS/JS ruleaza in paralel.
8. **Nu git push fara aprobare explicita** — commit local OK, push doar la cerere.

---

## Stack WooCommerce Devrika

Toti clientii Devrika folosesc:
- **Tema:** XStore (etheme) + Elementor Pro
- **Automatizare:** WPCode Lite pentru CSS/JS/PHP snippeturi
- **Hosting:** SiteGround (LiteSpeed Cache) sau Kinsta
- **SEO plugin:** Rank Math

**Implicatii critice:**
- WC PHP hooks NU se apeleaza in Elementor widgets — foloseste Elementor UI sau JS footer
- Selector logo XStore: `.elementor-widget-theme-etheme_site-logo img`
- LiteSpeed Cache server-side — bypass manual: `?nocache=1` in URL

---

## Adaugare client nou

1. `mkdir -p clients/[client.ro]`
2. `cp CHECKLIST-TEMPLATE.md clients/[client.ro]/CHECKLIST.md`
3. Completeaza FAZA 0 in noul fisier
4. Ruleaza auditul SEO + UX
5. Implementeaza in ordine fazele 3-8
6. Documteaza snippeturi active in `clients/[client.ro]/DOCUMENTATION.md`
