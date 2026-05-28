# Audit SEO Complet — puria.ro
**Data:** 13 mai 2026 | **Auditor:** Claude SEO Suite | **Scor Global: 43/100**

---

## Scor per Categorie

| Categorie | Greutate | Scor | Contribuție |
|---|---|---|---|
| Technical SEO | 22% | 61/100 | 13.4 |
| Content Quality | 23% | 29/100 | 6.7 |
| On-Page SEO | 20% | 35/100 | 7.0 |
| Schema / Structured Data | 10% | 40/100 | 4.0 |
| Performance (CWV) | 10% | 52/100 | 5.2 |
| AI Search Readiness (GEO) | 10% | 34/100 | 3.4 |
| Images | 5% | 35/100 | 1.75 |
| **TOTAL** | **100%** | **43/100** | |

---

## Executive Summary

**Site:** puria.ro — magazin WooCommerce hrana animale companie (câini, pisici, rozătoare)
**Stack:** WordPress 6.9.4 / XStore theme / Elementor / Rank Math / WP Rocket / SiteGround
**Catalog:** ~900 produse, ~55 categorii, 5 pagini statice

**Top 5 probleme critice:**
1. `google_product_category` **complet absent** din feed-ul Google Shopping (toate 429 produse) — blochează aprobarea în GMC
2. **Conținut editorial zero** pe paginile de categorie (H1 = "Caini", H1 = "Pisici", fără descrieri)
3. **Schema Product invalida** — `availability` folosește `http://` (trebuie `https://`), `itemCondition` format greșit, GTIN invalid
4. **`og:image` lipseste complet** — niciun share social nu afișează imagine
5. **Lipsesc headere de securitate critice** — HSTS, X-Frame-Options, CSP, Referrer-Policy absente

**Top 5 quick wins:**
1. Setează `google_product_category` în CTX Feed/WooFeed → deblocat GMC în 24-72h
2. Adaugă `og:image` (1200x630px) în Rank Math → share social fix imediat
3. Adaugă descrieri categorii (200+ cuvinte) pe /caini/ și /pisici/ → conținut indexabil
4. Corectează `availability` Schema la `https://schema.org/InStock` → validare GMC/Google
5. Aplică `noindex` pe URL-urile `?filter_*` → elimini mii de pagini subțiri din index

---

## 1. Technical SEO — 61/100

### Crawlability & Robots.txt ✅
- robots.txt structurat corect, blochează `/wp-admin/`, permite uploads
- **Problemă medie:** declară `Sitemap: https://puria.ro/sitemap_index.xml` dar URL-ul fizic e `/sitemap.xml`
- **Fix:** corectează URL-ul în robots.txt sau în setările Rank Math

### Sitemaps ✅
- 7 sub-sitemaps Rank Math: ~1.014 URL-uri total (201+200+200+200+153 produse + 55 categorii + 5 pagini)
- `lastmod` actualizat recent (2026-05-12/13) ✅
- **Lipsă:** image sitemap (recomandat pentru e-commerce cu 900+ produse)

### Canonicals ✅
- Homepage, categorii, paginare — canonical self-referential corect
- rel="next" pe paginare prezent ✅

### HTTPS & Securitate ⚠️ CRITICAL
- HTTP→HTTPS 301 activ, HTTP/2+HTTP/3 activate ✅
- **LIPSESC headere esențiale:**
  - `Strict-Transport-Security` (HSTS)
  - `X-Frame-Options` (risc clickjacking)
  - `Content-Security-Policy`
  - `Referrer-Policy`
  - `Permissions-Policy`

```apache
# Adaugă în .htaccess sau SiteGround > Security Headers:
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

### Core Web Vitals (lab) ⚠️
- LCP: 1.36-1.76s — **PASS** (sub 2.5s)
- CLS: 0.000-0.017 — **PASS** (sub 0.1)
- TTFB: 472-633ms — **FAIL** (recomandat <200ms pe pagini cached)
- TBT: 5-30ms (lab, nu reflectă interacțiunea reală)

### Redirect Chains ✅
- Fără lanțuri multiple. http→https = 1 salt ✅

### Parametri URL ⚠️
- `?filter_brand=`, `?orderby=` generează pagini duplicate indexabile
- Fix: adaugă în robots.txt sau Rank Math `noindex` pe aceste URL-uri

---

## 2. Content Quality — 29/100

### Homepage (puria.ro/)
- **H1:** "Magazin online hrana, accesorii animale companie" — slab, generic
- **Meta title:** "Magazin online animale – Hrană câini, pisici, rozătoare | Puria"
- **Meta description:** prezentă, 155 chars ✅
- **Conținut editorial:** ~500 cuvinte reale (restul = titluri produse și prețuri)
- **E-E-A-T: 2/5** — zero autor, zero an înființare, zero certificări
- **Thin content: DA** — sub 500 cuvinte editorial real

### Categorii (/caini/, /pisici/)
- **H1:** "Caini" / "Pisici" (un singur cuvânt)
- **Descriere categorie: ABSENTĂ** pe ambele pagini critice
- **E-E-A-T: 1/5** — zero text editorial, conținut = filtre + titluri produse
- **Risc duplicate:** structura identică între /caini/ și /pisici/
- **Thin content: CRITIC**

### Pagina Despre Noi
- Date juridice prezente (CUI, Nr. Reg. Com.) ✅
- **Lipsesc:** fondatori/echipă nominalizată, ani experiență, testimoniale, politică retur
- Meta description = 6 cuvinte generice ❌
- **E-E-A-T: 2.5/5**

### Pagini Produs
- Descrieri prezente, ~1.500 cuvinte ✅
- Text formulaic, AI-generic — fraze ca "alegere superioară", "stare de sănătate excelentă"
- Titluri cu SKU-uri: "Hrana caini Natural Greatness ASK79LR15, 15kg..." (105 chars) ❌
- **Risc duplicate: POSIBIL** — dacă toate produsele din aceeași categorie au același șablon

### Blog / News
- **ABSENT** — zero conținut editorial proaspăt, zero semnale de freshness pentru AI

---

## 3. On-Page SEO — 35/100

| Pagina | H1 | Meta desc | Keyword targeting |
|---|---|---|---|
| Homepage | ⚠️ generic | ✅ prezentă | "magazin animale" — prea larg |
| /caini/ | ❌ 1 cuvânt | ✅ prezentă | "hrana caini" — slabă fără text |
| /pisici/ | ❌ 1 cuvânt | ✅ prezentă | "hrana pisici" — slabă fără text |
| /branduri/macs/ | ⚠️ "MAC's" | ❌ lipsă | brand page neoptimizată |
| Produs | ✅ descriptiv | ✅ SEO-optimizat | OK dar titlu prea lung |

**Probleme breadcrumb:** lipsesc vizual pe paginile de categorie și produs (schema BreadcrumbList e prezentă, dar nu se afișează în UI).

**Internal linking:** produsele nu sunt linkuite din text editorial (nu există text editorial). Zero contextual linking.

---

## 4. Schema / Structured Data — 40/100

### Ce există
- Homepage: Organization, Place, WebSite, WebPage, Article (tip greșit), SearchAction ✅
- Categorii: BreadcrumbList, CollectionPage ✅
- Produse: Product, Offer, BreadcrumbList ✅

### Erori critice

**CRITICAL — blochează validarea GMC:**
```json
// GREȘIT:
"availability": "http://schema.org/InStock"
"itemCondition": "NewCondition"

// CORECT:
"availability": "https://schema.org/InStock"
"itemCondition": "https://schema.org/NewCondition"
```

**CRITICAL — Offer.price inconsistent:**
- `price: "263"` vs `priceSpecification.price: "262.82"` (același produs)
- `valueAddedTaxIncluded: "true"` (string) → trebuie `true` (boolean)

**HIGH — Lipsă AggregateRating:**
- Produsele au stele în HTML (`.star-rating`) dar Schema nu le include
- Fără aceasta: ZERO stele în SERP, indiferent câte recenzii există

**MEDIUM:**
- BreadcrumbList pe produs pornește din `/branduri/`, nu din `/caini/` — asociere greșită în SERP
- Homepage: `@type: Article` în loc de `WebPage` sau `CollectionPage`
- Lipsă `brand` în Product schema — redus Shopping Graph

### Oportunități lipsă

| Prioritate | Schema | Beneficiu |
|---|---|---|
| 🔴 Critic | AggregateRating | Stele în SERP — cel mai mare CTR boost |
| 🔴 Critic | ItemList pe categorii | Carusel produse în Google |
| 🟡 Mediu | Brand în Product | Shopping Graph, filtrare Google Shopping |
| 🟡 Mediu | LocalBusiness | Rich result local (hartă, ore) |

---

## 5. Performance / Core Web Vitals — 52/100

| Metric | Valoare | Status |
|---|---|---|
| LCP Desktop | 1.76s | ✅ PASS |
| LCP Mobile | 1.36s | ✅ PASS |
| CLS Desktop | 0.000 | ✅ PASS |
| CLS Mobile | 0.017 | ✅ PASS |
| TTFB (categorii) | 633ms | ❌ FAIL |
| JavaScript total | 3.9 MB | ❌ critic |

### Top 3 bottlenecks

**1. TTFB 633ms pe /caini/** — WP Rocket cu cache activ ar trebui <100ms. Posibil: paginile cu sesiune WooCommerce nu sunt cached, sau SiteGround Dynamic Cache intră în conflict.

**2. 3.9 MB JavaScript** — Elementor (~800KB), WooCommerce (~600KB), XStore, jQuery+migrate sincron în head, fbevents.js, 3 instanțe gtag duplicate.

**3. 50+ stylesheet-uri render-blocking** — Elementor generează CSS per-post individual, XStore încarcă ~40 fișiere CSS separate.

### Fix-uri prioritizate
1. Activează Delay JS în WP Rocket pentru fbevents.js, Chaty, scripts non-critice
2. Descarcă fonturile Google local (Poppins, Roboto, Nunito, Noto Sans) — elimini 4 round-trips externe
3. Activează Elementor Optimized Asset Loading — CSS per-widget, nu per-pagină
4. Diagnostichează TTFB: verifică dacă paginile de categorie sunt în cache WP Rocket

---

## 6. E-commerce SEO — 38/100

### Google Shopping Feed — CRITIC

**`google_product_category`: COMPLET ABSENT**
- Toate 429 produse au câmpul gol
- Aceasta este cauza primară a oricăror respingeri GMC
- Fix: în CTX Feed > Editare feed > Mapeaza câmpurile:

| Categorie WooCommerce | Google Product Category |
|---|---|
| Caini > Hrana Uscata | Animals & Pet Supplies > Pet Food > Dog Food > Dry Dog Food |
| Caini > Hrana Umeda | Animals & Pet Supplies > Pet Food > Dog Food > Wet Dog Food |
| Pisici > Hrana Uscata | Animals & Pet Supplies > Pet Food > Cat Food > Dry Cat Food |

**`product_type` contaminat cross-categorie (38% produse):**
- Produse câini apar sub pisici și invers din cauza taxonomiei WooCommerce prost configurate
- Fix: setează o categorie primară per produs, configurează feed-ul să folosească doar categoria primară

**GTIN invalid:**
- Schema: `"gtin": "82828282828"` (11 cifre, EAN-13 necesită 13)
- Feed: zero produse au GTIN
- Fix: ori GTIN real (EAN de pe ambalaj) ori `identifier_exists=no`

### Titluri Produse — HIGH
- Titluri 80-105 caractere cu SKU-uri incluse
- Google truncheaza la ~60 caractere în SERP
- Pattern recomandat: `[Brand] [Produs] [Gramaj] — [Beneficiu cheie]`
- Ex: "MAC's Hrana Uscata Curcan Senior 3kg" în loc de "Hrana caini MACs Dog Mono Soft Fresh Lamb 90237, 50% carne miel proaspata, 300g, toate rasele"

### Filtre Indexabile — MEDIUM
- `?filter_brand=`, `?orderby=` → indexabile, generează mii de pagini subțiri
- Fix: Rank Math > Titluri și Meta > noindex pe parametrii WooCommerce

### Feed incomplet
- 429 produse din ~900 declarate (50% lipsesc din feed)

---

## 7. AI Search Readiness (GEO) — 34/100

### Accces AI Crawlers
- Toți crawlerii AI acceptați implicit (nicio regulă explicită per-bot) ✅
- `llms.txt`: **ABSENT** ❌

### Citability Score: 3/10
- H1 homepage = etichetă navigare, nu declarație factual citabilă
- Zero FAQ, zero articole de nutriție, zero statistici proprii
- Brandurile listate fără descrieri asociate
- Nu există blog sau conținut editorial proaspăt

### Semnale de brand ✅
- NAP complet (PETEXPRESS RETAIL SRL, CUI, Nr. Reg. Com., telefon, email)
- Structura de categorii clară

### Acțiuni GEO (prioritizate)
1. Creează `/llms.txt` — efort 1 oră, impact imediat pe toți crawlerii AI
2. Adaugă secțiune FAQ pe homepage (8-10 întrebări despre produse/livrare/branduri)
3. Creează 4-6 articole blog despre nutriție animale cu pasaje self-contained (134-167 cuvinte)

---

## 8. Visual / Mobile — 35/100

### Probleme Critice

**`og:image` — COMPLET ABSENT** ❌
- Share Facebook/WhatsApp/LinkedIn = fără imagine
- Fix: adaugă în Rank Math > Social > og:image implicit (1200x630px)

**Imagini produs = placeholder WooCommerce**
- Pe paginile de categorie, imaginile de produs se încarcă cu `woocommerce-placeholder.webp`
- Posibil: lazy loading JS nu rulează, sau configurație slider greșită

**LCP element (`puria.png`) neoptimizat**
- Logo-ul are `fetchpriority="high"` dar nu și hero slider-ul
- Hero (LCP element real) nu are `loading="eager"`
- Format: PNG (trebuie WebP/AVIF)

**Chaty widget suprapus pe mobile (390px)**
- "Scrie-ne!" acoperă primul produs card în colțul stânga-jos

```css
/* Fix Chaty overlap mobile: */
@media (max-width: 480px) {
  .chaty-bar { bottom: 70px !important; }
}
```

### Cookie Banner
- Ocupă 60-75% din viewport la prima încărcare (desktop și mobile)
- CTA-ul principal nu e vizibil above-the-fold din cauza bannerului

### Zero WebP pe imagini produs
- Toate imaginile de produs: JPEG/PNG
- WP Rocket sau ShortPixel neconfigurate pentru conversie WebP

---

## 9. SXO — Search Experience — 48/100

### Intent Match per Pagina

| Query | Pagina | Match | Problemă |
|---|---|---|---|
| "hrana uscata caini" | /caini/hrana-uscata-caini/ | 8/10 ✅ | Lipsă filtru greutate (1kg/3kg/10kg) |
| "hrana pisici MAC's" | /branduri/macs/ | 5/10 ⚠️ | Brand page fără editorial, meta desc lipsă |
| "recompense caini naturale" | — | 2/10 ❌ | MISMATCH CRITIC: URL duce la produs individual, nu PLP |
| "puria.ro" | homepage | 9/10 ✅ | OK |

### Gap-uri UX critice
- **Lipsă filtru greutate** pe hrana uscată — cel mai căutat filtru după brand
- **Prag livrare gratuită 450 lei** vs. 149 lei (maxi-pet) — dezavantaj competitiv vizibil
- **Subcategorii text în sidebar** vs. grid vizual cu imagini (standard competitori)
- **Fără autocomplete** în search bar (zooplus, petmart au — crește conversiile ~30%)

---

## Notă privind fix-urile deja aplicate în această sesiune

Înainte de audit, au fost rezolvate:
- ✅ Widget subcategorii (JS via REST API) — /caini/, /pisici/ afișează subcategorii corecte
- ✅ Footer copyright © 2025 → © 2026
- ✅ Hero links 404 (/caini-2/, /pisici-2/) — corectate via REST API
- ✅ JS error `window._googlesitekit undefined` — snippet JS în head
- ✅ 26 produse necategorizate — recategorizate/șterse
