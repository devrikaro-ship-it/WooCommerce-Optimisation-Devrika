# Plan de Acțiuni SEO — puria.ro
**Data:** 13 mai 2026 | **Scor curent: 43/100** | **Scor țintă: 72/100**

---

## 🔴 CRITIC — Fix imediat (blochează indexarea/GMC)

### 1. `google_product_category` în feed Google Shopping
**Impact:** Deblocat aprobarea produselor în GMC → Google Shopping trafic
**Efort:** 2-4h
**Unde:** CTX Feed > Editare feed > Mapping câmpuri
**Cum:** Mapează fiecare categorie WooCommerce la taxonomia Google:
- Caini > Hrana Uscata → `Animals & Pet Supplies > Pet Food > Dog Food > Dry Dog Food`
- Pisici > Hrana Uscata → `Animals & Pet Supplies > Pet Food > Cat Food > Dry Cat Food`
- etc.

### 2. Schema Product — corectare erori blocking
**Impact:** Validare Google Merchant Center, eligibilitate rich results
**Efort:** 1h (snippet PHP în WPCode sau plugin)
**Fix specific:**
```php
// Adaugă în functions.php sau WPCode:
add_filter('woocommerce_structured_data_product', function($markup) {
    if (isset($markup['offers'])) {
        $markup['offers']['availability'] = str_replace('http://', 'https://', $markup['offers']['availability']);
        $markup['offers']['itemCondition'] = 'https://schema.org/NewCondition';
        if (isset($markup['offers']['priceSpecification']['valueAddedTaxIncluded'])) {
            $markup['offers']['priceSpecification']['valueAddedTaxIncluded'] = true; // boolean
        }
    }
    return $markup;
});
```

### 3. Headere de securitate HSTS + X-Frame-Options
**Impact:** Securitate site, semnal de încredere Google
**Efort:** 30 min
**Unde:** SiteGround > Security > Headers sau `.htaccess`
```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

---

## 🟠 HIGH — Fix în 1 săptămână

### 4. og:image — adaugă imagine pentru share social
**Impact:** Share Facebook/WhatsApp/LinkedIn funcțional, CTR social
**Efort:** 1h
**Unde:** Rank Math > Titluri și Meta > Global Meta > Social > og:image
**Specificații:** 1200x630px, JPG/PNG, fără text important la margini

### 5. Descrieri categorii principale
**Impact:** Conținut indexabil, E-E-A-T, ranking pentru "hrana caini/pisici"
**Efort:** 3-4h (redactare + implementare)
**Unde:** WooCommerce > Produse > Categorii > Editează categoria > Descriere (câmp text)
**Minim:** 200-250 cuvinte per categorie (/caini/, /pisici/, /pasari-rozatoare/)
**Include:** keyword-ul principal natural, subcategorii linkuite, beneficii produse

### 6. Rescrie H1 homepage
**Impact:** Targeting keyword mai specific, diferențiere față de competitori
**Efort:** 30 min (Elementor editor)
**Actual:** "Magazin online hrana, accesorii animale companie"
**Propunere:** "Hrana Premium pentru Câini și Pisici — Branduri Selectate | Puria"

### 7. noindex pe URL-uri cu parametri WooCommerce
**Impact:** Elimini mii de pagini subțiri din index, îmbunătățești crawl budget
**Efort:** 1h
**Unde:** Rank Math > Titluri și Meta > WooCommerce > Arhive produs > parametrii URL
**Alternativ robots.txt:**
```
Disallow: /?orderby=
Disallow: /?filter_*
```

### 8. GTIN fix în feed
**Impact:** Elimini erori GMC "identifier invalid"
**Efort:** 2h
**Fix:** pentru produse fără EAN real: setează `identifier_exists=no` în feed
**Unde:** CTX Feed > Câmpuri avansate > identifier_exists → mapează la "no" dacă nu ai GTIN

### 9. AggregateRating în Schema Product
**Impact:** Stele în SERP — cel mai vizibil CTR boost
**Efort:** 2-3h
**Unde:** Rank Math > Schema > Product > activează AggregateRating
**Sau:** plugin separat (WP Review Pro, Product Reviews for WooCommerce)
**Condiție:** produsele trebuie să aibă recenzii existente în WooCommerce

### 10. `product_type` cross-categorie — fix feed
**Impact:** 38% produse cu categorie greșită în Shopping
**Efort:** 3h
**Fix:** în CTX Feed, setează `product_type` să folosească **doar categoria primară** a produsului, nu toate categoriile concatenate

---

## 🟡 MEDIU — Fix în 1 lună

### 11. Titluri produse — scurtare și reformatare
**Impact:** CTR mai bun în SERP (trunchere la ~60 chars)
**Efort:** 4-8h (bulk edit via WP All Import)
**Pattern:** `[Brand] [tip produs] [gramaj]` (max 60 chars)
**Exemple:**
- ❌ "Hrana caini MACs Dog Mono Soft Fresh Lamb 90237, 50% carne miel, 300g"
- ✅ "MAC's Hrana Uscata Miel 300g"

### 12. Optimizare performanță JS/CSS
**Impact:** TTFB, INP, Core Web Vitals reale
**Efort:** 4-6h
**Acțiuni:**
- WP Rocket > Delay JS: activează pentru fbevents.js, Chaty
- Descarcă fonturile Google local (Poppins, Roboto, Nunito, Noto Sans)
- Elementor > Experiments > Optimized Asset Loading: activează
- Elimină cele 3 instanțe duplicate gtag.js din GTM

### 13. Conversie imagini la WebP
**Impact:** Dimensiune imagini -30-50%, LCP mai rapid
**Efort:** 1h configurare + timp procesare background
**Unde:** WP Rocket > Media > conversie WebP automată SAU ShortPixel

### 14. ItemList Schema pe pagini categorie
**Impact:** Carusel produse în Google SERP
**Efort:** 3h
**Implementare:** WPCode snippet PHP care generează JSON-LD ItemList cu primele 10 produse din categorie

### 15. BreadcrumbList fix — pornit din categoria corectă
**Impact:** Google asociază produsul cu categoria relevantă, nu cu /branduri/
**Efort:** 1h
**Unde:** Rank Math > Schema > Breadcrumb settings — verifică că primarul categorie e cel principal

### 16. Pagina Despre Noi — îmbunătățire E-E-A-T
**Impact:** Trust signals, Knowledge Panel potential
**Efort:** 2-3h
**Adaugă:** nume fondator/echipă, motivația selecției brandurilor, ani experiență, certificări parteneri (MAC's, Terra Canis etc.)
**Meta description:** rescrie de la 6 cuvinte la 155 chars cu CTA

### 17. Chaty widget — fix overlap mobile
**Impact:** UX mobile, click pe produse neobstrucționat
**Efort:** 30 min
**Fix CSS în WPCode:**
```css
@media (max-width: 480px) {
  .chaty-bar { bottom: 70px !important; }
}
```

### 18. Organization Schema — adaugă sameAs
**Impact:** Entity matching, Knowledge Panel
**Efort:** 30 min
**Unde:** Rank Math > Schema > Organization > sameAs
**Linkuri:** Facebook page URL, Google Business Profile URL

---

## 🟢 LOW — Backlog

### 19. Creează llms.txt
**Impact:** Vizibilitate în ChatGPT, Perplexity, Claude
**Efort:** 1h
**Conținut:** descriere site, categorii principale, URL-uri canonice, licență conținut

### 20. Blog cu articole de nutriție (4-6 articole)
**Impact:** GEO readiness, E-E-A-T, long-tail keywords
**Efort:** 8-16h
**Topicuri sugerate:**
- "Hrana uscată vs. umedă pentru câini — ghid complet"
- "Cum alegi hrana pentru câine senior"
- "Branduri premium de hrană pisici disponibile în România"
- "Dieta hipoalergenică pentru pisici — ce să cauți pe etichetă"

### 21. Filtru greutate pe hrana uscată
**Impact:** SXO — filtrul cel mai căutat după brand pe PLP-uri
**Efort:** 4-6h (atribut WooCommerce + widget filtru)

### 22. Image sitemap
**Impact:** Indexare imagini produs în Google Images
**Efort:** 30 min
**Unde:** Rank Math > Sitemap > activează Image Sitemap

### 23. Subcategorii vizuale (grid cu imagini) pe /caini/, /pisici/
**Impact:** UX, reducere clicuri necesare, dwell time
**Efort:** 4-6h (Elementor widget sau XStore category grid)

### 24. Secțiune FAQ pe homepage
**Impact:** GEO, AI citations, featured snippets
**Efort:** 2-3h
**Format:** 8-10 întrebări scurte cu răspunsuri 50-70 cuvinte, marcate cu FAQPage Schema

### 25. Autocomplete în search bar
**Impact:** Conversie internă +~30% (benchmark industrie)
**Efort:** 4-8h sau plugin dedicat

---

## Roadmap recomandat

| Săptămâna | Acțiuni | Impact estimat scor |
|---|---|---|
| S1 | #1, #2, #3, #4, #7, #8 | +8 puncte → 51/100 |
| S2 | #5, #6, #9, #10 | +6 puncte → 57/100 |
| S3-S4 | #11, #12, #13, #14, #17 | +6 puncte → 63/100 |
| Luna 2 | #15, #16, #18, #19, #20 | +5 puncte → 68/100 |
| Luna 3 | #21-#25 | +4 puncte → 72/100 |
