---
name: woocommerce-optimize
description: "Optimizare completa WooCommerce: audit SEO + UX review + implementare prioritizata. Urmeaza 8 faze bazate pe experienta reala Devrika. Ruleaza /woocommerce-optimize [URL] pentru client nou sau /woocommerce-optimize [URL] --faza N pentru a continua de unde s-a oprit."
user-invokable: true
argument-hint: "[url] [--faza N]"
---

# WooCommerce Optimize — Devrika

Skill pentru optimizarea completa a oricarui site WooCommerce. Orchestreaza audit SEO, UX review si implementare prioritizata. Bazat pe experienta reala din proiecte Devrika.

**Repo documentatie:** `WooCommerce-Optimisation-Devrika`
**Repo local:** `/Users/VladMoloso/WooCommerce-Optimisation-Devrika`

---

## Invocare

```
/woocommerce-optimize https://client.ro          ← client nou, porneste din FAZA 0
/woocommerce-optimize https://client.ro --faza 3  ← continua din faza specificata
```

---

## Continuitate intre sesiuni

La fiecare start, inainte de orice actiune:

1. Verifica daca exista `clients/[client]/CHECKLIST.md` — daca da, citeste bifele
2. Verifica fisierele existente in `clients/[client]/`:
   - `FULL-AUDIT-REPORT.md` exista → FAZA 1 done
   - `UX-REVIEW.md` exista → FAZA 2 done
3. Daca bife si fisiere se contrazic → intreaba utilizatorul
4. Continua de unde s-a oprit, nu reface fazele deja completate

---

## FAZA 0 — Setup client

**Executie:** interactiva

### Detectare automata (fetch homepage)
- Tema: XStore / Astra / Divi / GeneratePress / alta
- Builder: Elementor / Gutenberg / Divi Builder / altul
- Hosting: SiteGround / Kinsta / altul (din response headers)
- WooCommerce: confirmat activ (da/nu)

Prezinta detectia → utilizatorul confirma sau corecteaza.

### Date colectate
```
OBLIGATORII:
- URL site + URL WP Admin
- User + parola WP Admin
- Hosting confirmat

PENTRU AUDIT SEO:
- GSC (Google Search Console): acces da/nu
- GA4 Property ID
- CrUX API key (pentru Core Web Vitals field data reale)

OPTIONALE:
- GMC Merchant ID + URL feed (Google Merchant Center)
- Google Ads Customer ID
```

### Output
- Creeaza `clients/[client]/CHECKLIST.md` din `CHECKLIST-TEMPLATE.md`
- Completeaza sectiunea FAZA 0 cu datele colectate
- ✅ Confirmare utilizator → trece la FAZA 1

---

## FAZA 1 — Audit SEO

**Executie:** automat via subagent `/seo-audit`

### Subagenti activi
- `seo-technical` — robots.txt, sitemaps, canonicals, security headers
- `seo-content` — E-E-A-T, thin content, readability
- `seo-schema` — detectie, validare, recomandari
- `seo-sitemap` — structura, quality gates
- `seo-performance` — LCP, INP, CLS
- `seo-visual` — screenshots desktop + mobile
- `seo-geo` — AI crawler access, llms.txt, citability
- `seo-sxo` — page-type mismatch, intent analysis
- `seo-google` — CrUX field data, GSC indexare, GA4 trafic organic (daca credentiale disponibile)
- `seo-ecommerce` — Product schema, WooCommerce-specific (detectat automat)

### Output salvat
```
clients/[client]/FULL-AUDIT-REPORT.md
clients/[client]/ACTION-PLAN.md
clients/[client]/screenshots/desktop-homepage.png
clients/[client]/screenshots/desktop-category.png
clients/[client]/screenshots/desktop-product.png
clients/[client]/screenshots/mobile-homepage.png
clients/[client]/screenshots/mobile-category.png
clients/[client]/screenshots/mobile-product.png
```

### Dupa audit
Prezinta **top 10 probleme prioritizate** (Critical → High → Medium) din `ACTION-PLAN.md`.
✅ Confirmare utilizator → trece la FAZA 2.

---

## FAZA 2 — UX Review

**Executie:** automat via subagent `/ui-ux-pro-max`

**Input:** screenshot-urile din `clients/[client]/screenshots/` (generate in FAZA 1)

### Analizeaza
- Imagini produse: `object-fit` contain vs cover
- Logo header: dimensiune corecta, nu supradimensionat
- Grid produse: uniform, fara distorsiuni
- Mobile UX: touch targets, scroll, font size
- Accesibilitate: contrast text, alt text principal
- Footer: trust signals, vizibilitate
- CTA principal: vizibil above-fold pe mobile

### Output salvat
```
clients/[client]/UX-REVIEW.md
```

### Dupa review
Prezinta **top 5 probleme UX cu prioritate**.
✅ Confirmare utilizator → trece la implementare.

---

## FAZE 3-8 — Implementare

**Executie:** hibrid — Claude genereaza, utilizatorul confirma, Playwright executa

### Ordinea fix-urilor
Din `ACTION-PLAN.md` (prioritate din audit: Critical → High → Medium → Low).
**Nu** ordinea rigida a fazelor 3-8 — auditul determina ce e urgent.

### Ierarhia de implementare per fix

```
1. Plugin UI — Rank Math, WooCommerce, XStore, Elementor settings
   → daca setarea exista in interfata pluginului, se face acolo

2. WordPress nativ — Customizer, Settings, Menus, Widgets
   → daca WP core poate face asta, se face acolo

3. Elementor UI — widget settings, global styles, section options
   → daca e un element Elementor, se editeaza in builder

4. WPCode CSS — style overrides care nu pot fi facute altfel
   → selector specific (li.product parent), nu broad

5. WPCode JS — comportament dinamic imposibil altfel
   → fara MutationObserver pe style/attributes

6. WPCode PHP — ULTIMA SOLUTIE
   → NU adauga <?php (WPCode pune automat — tag dublu = site down)
```

### Flow per fix

```
1. Identifica metoda (ierarhia de mai sus)
2. Genereaza codul sau instructiunile
3. Prezinta:
   - CE face
   - UNDE se implementeaza (plugin/pagina/sectiune specifica)
   - ANTI-PATTERN de evitat (din MISTAKES.md)
4. ✅ Asteapta confirmare utilizator
5. Executa via Playwright (WP Admin, Elementor, sau WPCode)
6. Verifica imediat (pasul urmator)
```

### Verificare dupa fiecare fix

```
CSS/design (imagini, logo, grid):
→ Playwright: screenshot desktop + mobile
→ Playwright: verifica computed style (object-fit, max-height, etc.)

Plugin settings (Rank Math, WooCommerce):
→ Playwright: screenshot pagina afectata
→ Playwright: verifica HTML generat (ex: JSON-LD in <head>)

WPCode snippet:
→ Playwright: confirma snippet activ in lista WPCode
→ Playwright: screenshot pagina + verifica efectul vizual

Security headers:
→ Playwright: fetch response headers, verifica prezenta
```

**Toate verificarile = pe site-ul real, vizual, Playwright. Fara redirectionare catre tool-uri externe.**

### Bifeaza in CHECKLIST.md
Dupa fiecare fix confirmat + verificat → bifeaza itemul corespunzator din `clients/[client]/CHECKLIST.md`.

---

## FINAL — Documentatie si commit

**Executie:** automat dupa ultimul fix confirmat

### 1. Completeaza CHECKLIST.md
- Bife finale pe toti itemii implementati
- Tabel "Snippeturi active la final" (ID + functionalitate + tip)
- Tabel "Scor final" (scor initial → scor final → delta per categorie)

### 2. Genereaza DOCUMENTATION.md
```
clients/[client]/DOCUMENTATION.md
```
Continut:
- Data sesiunii
- Ce s-a implementat (lista: fix + metoda folosita)
- Snippeturi WPCode active (ID + functionalitate + tip CSS/JS/PHP)
- Ce ramane (items nebifate din CHECKLIST)

### 3. Commit local
```bash
git add clients/[client]/
git commit -m "Optimizare [client] — sprint [data]"
```

### 4. Push
Intreaba: "Fac push pe GitHub?"
**NU face push fara confirmare explicita.**

---

## Reguli critice

Verifica aceste reguli inainte de orice implementare. Sursa: `MISTAKES.md`.

| Regula | Risc daca incalcata |
|--------|---------------------|
| Nu adauga `<?php` in WPCode | Fatal parse error — site down |
| Nu MutationObserver pe `style` + `removeProperty` | Infinite loop — site unclickable |
| Nu selectoare broad (`img`, `.product-image img`) | Prinde logo — distorsionat |
| `headless: false` + `slowMo: 200` Playwright | Login blocat |
| AJAX cu `snippet_id` explicit la dezactivare WPCode | Fara ID = creeaza snippet NOU |
| Dezactiveaza ONE-SHOT imediat dupa rulare | Sitemap regenerat la fiecare request |
| Dezactiveaza snippetul vechi inainte de a crea versiunea noua | Duplicate ruleaza in paralel |
| `launchPersistentContext` nu `newContext` | Login la fiecare rulare |
| **Audit WPCode via PHP query, nu UI** | UI arata 20/pagina — poti rata 30+ snippeturi active |
| **Verifica `cover` vs `contain` inainte de fix imagini** | Conflict silentios — comportament impredictibil |
| **Scrie TOTI pasii in main() inainte de rulare** | Fiecare restart script = browser nou = sesiune noua |

---

## Stack Devrika (toti clientii)

- **Tema:** XStore (etheme) + Elementor Pro
- **Snippeturi:** WPCode Lite
- **Hosting:** SiteGround (LiteSpeed Cache) sau Kinsta
- **SEO plugin:** Rank Math

**Implicatii:**
- WC PHP hooks NU se apeleaza in Elementor widgets — foloseste Elementor UI sau JS footer
- Selector logo XStore: `.elementor-widget-theme-etheme_site-logo img`
- Cache bypass manual: `?nocache=1` in URL
- Playwright sesiune: `/tmp/[CLIENT]-session`

---

## Fisiere referinta

| Fisier | Rol |
|--------|-----|
| `CHECKLIST-TEMPLATE.md` | Template copiat per client in FAZA 0 |
| `BEST-PRACTICES.md` | Metode corecte validate in productie |
| `MISTAKES.md` | Greseli documentate — citit inainte de implementare |
| `scripts/fix_category_rules_v2.js` | Script Playwright reutilizabil |
| `clients/[client]/` | Tot ce tine de un client specific |
