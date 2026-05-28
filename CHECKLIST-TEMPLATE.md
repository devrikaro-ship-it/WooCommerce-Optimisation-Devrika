# WooCommerce Optimisation Checklist — [CLIENT.RO]

**Data start:** ___________
**Implementat de:** ___________
**URL site:** ___________

> Copiaza acest fisier in `clients/[client]/CHECKLIST.md` inainte de a bifa.
> Nu modifica template-ul master.

---

## FAZA 0 — Setup client

### Date acces
- [ ] URL WP Admin: `https://[client]/wp-admin`
- [ ] User/parola WP: salvat in password manager
- [ ] Acces GSC (Google Search Console): confirmat
- [ ] Acces GA4: confirmat
- [ ] Hosting: SiteGround / Kinsta / altul: ___________
- [ ] Token GitHub (daca folosim GitHub API): configurat

### Stack identificat
- [ ] Versiune WordPress: ___________
- [ ] Versiune WooCommerce: ___________
- [ ] Tema activa: XStore / Astra / Divi / alta: ___________
- [ ] Builder: Elementor / Gutenberg / altul: ___________
- [ ] SEO plugin: Rank Math / Yoast / altul: ___________
- [ ] Cache plugin: LiteSpeed / WP Rocket / altul: ___________
- [ ] Nr. snippeturi WPCode active la start: ___________

### Playwright — sesiune persistenta
```javascript
// Inlocuieste CLIENT cu numele clientului
const context = await chromium.launchPersistentContext('/tmp/CLIENT-session', {
  headless: false,
  slowMo: 200
});
```
- [ ] Sesiune Playwright creata si testata
- [ ] Login WP confirmat functional (non-headless)

---

## FAZA 1 — Audit SEO initial

**Tool:** `/seo-audit [URL]` in Claude Code
**Output asteptat:** `FULL-AUDIT-REPORT.md` + `ACTION-PLAN.md`

- [ ] Crawl complet site (robots.txt, sitemap, pagini indexate)
- [ ] Screenshot desktop: homepage + categorie + produs
- [ ] Screenshot mobile: homepage + categorie + produs
- [ ] Core Web Vitals — CrUX field data (nu lab data)
- [ ] Indexare GSC: cate pagini indexate total
- [ ] Indexare GSC: cate pagini categorii indexate
- [ ] Lista toate plugin-urile active + versiuni
- [ ] Security headers check
- [ ] Baseline snapshot: title/H1/meta pe primele 20 pagini
- [ ] Sitemap.xml: exista, trimis in GSC, nr. URL-uri
- [ ] robots.txt: nu blocheaza CSS/JS/imagini

**Salveaza raportul:** `clients/[client]/FULL-AUDIT-REPORT.md`
**Salveaza planul:** `clients/[client]/ACTION-PLAN.md`

---

## FAZA 2 — UX Review

**Tool:** `/ui-ux-pro-max` in Claude Code pe baza screenshot-urilor din Faza 1

- [ ] Design system identificat (stil, culori, tipografie)
- [ ] Imagini produse: `object-fit` corect (contain vs cover)
- [ ] Logo header: dimensiune corecta (nu supradimensionat)
- [ ] Grid produse: uniform, fara distorsiuni
- [ ] Mobile: touch targets min 44x44px
- [ ] Mobile: fara horizontal scroll
- [ ] Accesibilitate: contrast text suficient
- [ ] Accesibilitate: alt text pe imagini principale
- [ ] Footer: vizibil, trust signals prezente
- [ ] CTA principal: vizibil above-fold pe mobile

**Salveaza recomandarile:** `clients/[client]/UX-REVIEW.md`

---

## FAZA 3 — SEO Tehnic

**Tool:** WPCode Lite (PHP snippet) + Rank Math + hosting panel

### Security headers
- [ ] `X-Frame-Options: SAMEORIGIN`
- [ ] `Strict-Transport-Security` (HSTS)
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`

> **Tool:** WPCode PHP snippet (nu adauga `<?php` — WPCode il pune automat)
> **Verifica:** securityheaders.com

### Crawlabilitate
- [ ] Noindex pe parametri URL WooCommerce (`?orderby`, `?add-to-cart`, `?per_page`, `?s`)
- [ ] Canonical URLs corecte (cu/fara trailing slash uniform)
- [ ] Redirect 301 uniform: www→non-www sau invers
- [ ] HTTPS fortat pe tot site-ul

### Sitemap
- [ ] sitemap.xml generat si activ
- [ ] Trimis in GSC
- [ ] Nu contine pagini noindex sau redirectate
- [ ] Image sitemap activat

### Robots.txt
- [ ] Nu blocheaza CSS/JS/imagini
- [ ] AI crawlers configurati (GPTBot, ClaudeBot, Google-Extended)

### Google Fonts
- [ ] Fonturi gazduite local (nu CDN Google) — GDPR + performanta
- [ ] Verificat: zero request extern la fonts.googleapis.com

---

## FAZA 4 — Schema / Structured Data

**Tool:** WPCode PHP snippet + Rank Math

> **ATENTIE:** Snippet-urile PHP in WPCode — NU adauga `<?php`. WPCode il adauga automat.
> Un al doilea tag = fatal parse error = site down.

### Product schema
- [ ] `availability`: HTTPS (nu HTTP)
- [ ] `itemCondition`: `https://schema.org/NewCondition`
- [ ] `price` cu `taxIncluded: true`
- [ ] `brand` prezent

### Alte scheme
- [ ] **ItemList** pe paginile categorie (primele 10 produse)
- [ ] **BreadcrumbList** (verificat in Google Rich Results Test)
- [ ] **FAQ schema** pe paginile produs (din tabs existente)
- [ ] **Organization** pe homepage (logo, contactPoint, sameAs social)

### Validare
- [ ] search.google.com/test/rich-results pe 3 URL-uri diferite
- [ ] Zero erori blocking in Google Search Console > Rich Results

---

## FAZA 5 — On-Page SEO

**Tool:** Rank Math + WPCode CSS + editare manuala

### Meta
- [ ] Meta titles unice: `Keyword principal | Brand` (max 60 chars)
- [ ] Meta descriptions unice (max 155 chars, include CTA)
- [ ] og:image setat (1200x630px) pentru share social

### Continut pagini
- [ ] H1 unic per pagina, corespunde titlului
- [ ] Texte SEO unice pe fiecare categorie principala (min 150 cuvinte)
- [ ] Texte SEO pe subcategorii prioritare
- [ ] Breadcrumb vizual deasupra H1 pe categorii

### Imagini
- [ ] Alt text pe TOATE imaginile produse (bulk sau individual)
- [ ] Alt text pe imaginile de categorii

### Linking
- [ ] Internal linking: categorii → produse, homepage → categorii principale
- [ ] llms.txt creat si accesibil la `/llms.txt`

---

## FAZA 6 — UX / Design

**Tool:** WPCode CSS/JS

> **Selectoare sigure pentru imagini produse:**
> - Corect: `li.product .woocommerce-loop-product__link img`
> - GRESIT: `.product-image img` (prinde logo si alte imagini)
>
> **Pentru logo XStore:** `.elementor-widget-theme-etheme_site-logo img`
> Fix universal: `max-height: 80px !important; width: auto !important;`
>
> **NU MutationObserver pe `style` cu `removeProperty`** — infinite loop.
> Foloseste CSS `!important` de specificitate inalta.

### Imagini produse (grid)
- [ ] `object-fit: contain` pe grid produse — desktop
- [ ] `object-fit: contain` pe grid produse — mobile
- [ ] Aspect ratio fix pe container (ex: 1/1)
- [ ] Verifica: logo NOT afectat de selector

### Logo si header
- [ ] Logo: dimensiune corecta cu `max-height` explicit
- [ ] Logo: verifica pe desktop si mobile

### Footer
- [ ] Background inchis (dark)
- [ ] Trust badges vizibile
- [ ] Date firma: CUI, adresa, telefon, program

### Pagina produs
- [ ] Smart delivery message (prag transport gratuit, dinamic)
- [ ] Reviews activate si afisate
- [ ] Tab-uri: Specificatii tehnice + FAQ
- [ ] Related products filtrate pe categorie (nu random)
- [ ] Breadcrumb redesign (vizibil, styled)

### Mobile UX
- [ ] Touch targets min 44x44px pe butoane
- [ ] Font size min 16px body (evita iOS auto-zoom)
- [ ] Cart + checkout flow verificat pe mobile pana la plata
- [ ] Widget chat (Chaty etc.) nu acopera CTA pe mobile

### Card produse
- [ ] Hover effects: imagine scale + buton vizibil
- [ ] Sort dropdown styled (nu nativ `<select>`)

---

## FAZA 7 — Performance

**Tool:** Plugin ShortPixel/Imagify + LiteSpeed Cache + DevTools

- [ ] Imagini: WebP/AVIF conversia activata
- [ ] Imagini: `srcset` si `sizes` corecte
- [ ] Imagini: lazy load pe non-hero
- [ ] `width` si `height` declarate pe imagini (previne CLS)
- [ ] `font-display: swap` pe declaratiile @font-face
- [ ] Plugin-uri inactive dezactivate si sterse
- [ ] Nr. requesturi per pagina categorie (DevTools Network): ___________
- [ ] Core Web Vitals masurate (CrUX): LCP ___ / INP ___ / CLS ___

---

## FAZA 8 — Curatenie finala

**Tool:** WPCode admin + DevTools Console

> **Dezactivare WPCode corecta:** AJAX cu `snippet_id` explicit.
> Form POST fara `snippet_id` = creeaza snippet NOU in loc sa dezactiveze.

- [ ] 1 snippet WPCode per functionalitate (nu duplicate)
- [ ] Toate snippeturi ONE-SHOT/DEBUG dezactivate
- [ ] Snippeturi dezactivate de 30+ zile: sterse definitiv
- [ ] Maxim 15 snippeturi active simultan (ideal sub 10)
- [ ] Audit plugin-uri: dezactivate + sterse cele neutilizate
- [ ] Zero JS console errors pe: homepage, categorie, produs, cart
- [ ] Cache cleared si verificat pe incognito

---

## Scor final

| Categorie | Scor initial | Scor final | Delta |
|-----------|-------------|-----------|-------|
| SEO tehnic | /100 | /100 | + |
| On-page content | /100 | /100 | + |
| Schema | /100 | /100 | + |
| Performance | /100 | /100 | + |
| UX desktop | /100 | /100 | + |
| UX mobile | /100 | /100 | + |
| AI readiness | /100 | /100 | + |

---

## Snippeturi active la final

| Snippet ID | Functionalitate | Tip | Status |
|------------|-----------------|-----|--------|
| | | CSS/JS/PHP | activ |

---

## Ce ramane (dupa sprint)

- [ ] ___________
- [ ] ___________
