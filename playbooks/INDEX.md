# Playbooks Index — WooCommerce Optimisation Devrika

40 playbooks organizate pe categorie. Fiecare e autonom — codul e gata de copiat.

**Citeste `00-general-rules.md` inainte de orice implementare.**

---

## General

- [00-general-rules.md](00-general-rules.md) — Reguli generale: ordine implementare, WPCode, PHP hooks, CSS, Playwright, checklist final

---

## SEO Tehnic

- [01-security-headers.md](seo-tehnic/01-security-headers.md) — HSTS, X-Frame-Options, CSP, Referrer-Policy via WPCode PHP
- [02-noindex-url-params.md](seo-tehnic/02-noindex-url-params.md) — robots.txt filter + noindex pe parametri WooCommerce
- [03-google-fonts-local.md](seo-tehnic/03-google-fonts-local.md) — Download + serve Google Fonts local, elimina request extern
- [04-ai-crawlers-robots.md](seo-tehnic/04-ai-crawlers-robots.md) — Allow GPTBot/ClaudeBot/Google-Extended in robots.txt pentru GEO
- [05-llms-txt.md](seo-tehnic/05-llms-txt.md) — Serve /llms.txt pentru AI readiness via PHP snippet
- [06-og-image-rankmath.md](seo-tehnic/06-og-image-rankmath.md) — og:image setup in Rank Math pentru share social corect
- [07-sitemap-url-robots-fix.md](seo-tehnic/07-sitemap-url-robots-fix.md) — Fix URL sitemap declarat gresit in robots.txt

---

## Schema / Structured Data

- [01-product-schema-fix.md](schema/01-product-schema-fix.md) — Fix availability https + itemCondition + taxIncluded via rank_math/json_ld
- [02-itemlist-categories.md](schema/02-itemlist-categories.md) — ItemList schema pe pagini categorie cu transient cache
- [03-faq-schema-product.md](schema/03-faq-schema-product.md) — FAQ schema din post_meta injectata in wp_head pe pagini produs
- [04-breadcrumb-schema.md](schema/04-breadcrumb-schema.md) — BreadcrumbList via Rank Math, categoria primara, validare
- [05-aggregate-rating.md](schema/05-aggregate-rating.md) — AggregateRating in Product schema, stele in SERP
- [06-article-to-webpage-fix.md](schema/06-article-to-webpage-fix.md) — Fix @type Article → WebPage pe homepage

---

## UX / Design

- [01-images-contain.md](ux-design/01-images-contain.md) — object-fit contain pe grid produse fara a afecta logo
- [02-logo-size-fix.md](ux-design/02-logo-size-fix.md) — max-height explicit pe logo per tema (XStore, Astra, OceanWP etc.)
- [03-footer-dark.md](ux-design/03-footer-dark.md) — Footer dark CSS-type cu selectori Elementor
- [04-breadcrumb-redesign.md](ux-design/04-breadcrumb-redesign.md) — Rank Math breadcrumb styled + mutat deasupra H1
- [05-sort-dropdown-custom.md](ux-design/05-sort-dropdown-custom.md) — Sort dropdown WooCommerce custom styled, pastreaza functionalitate nativa
- [06-product-tabs-custom.md](ux-design/06-product-tabs-custom.md) — Tab-uri custom Date tehnice + FAQ pe pagina produs
- [07-smart-delivery-message.md](ux-design/07-smart-delivery-message.md) — Mesaj livrare dinamic (azi/maine/luni) bazat pe ora si zi
- [08-product-id-mpn-display.md](ux-design/08-product-id-mpn-display.md) — Afisare ID produs si MPN pe pagina produs
- [09-chaty-mobile-overlap.md](ux-design/09-chaty-mobile-overlap.md) — Fix Chaty widget care acopera produse pe mobile
- [10-category-description-editorial.md](ux-design/10-category-description-editorial.md) — Afisare + redactare descriere categorie 200+ cuvinte

---

## WooCommerce

- [01-related-products-taxonomy.md](woocommerce/01-related-products-taxonomy.md) — Filter related products pe taxonomie cu get_objects_in_term + wp_cache
- [02-body-class-taxonomy.md](woocommerce/02-body-class-taxonomy.md) — add_filter body_class pe categoria produsului curent
- [03-carousel-filter-taxonomy.md](woocommerce/03-carousel-filter-taxonomy.md) — JS filter carousel related products pe specie/categorie
- [04-enable-reviews.md](woocommerce/04-enable-reviews.md) — Activare recenzii WC global + open comment_status pe produse
- [05-category-archive-description.md](woocommerce/05-category-archive-description.md) — Afisare descriere categorie in shop loop via hook
- [06-gtin-identifier-feed.md](woocommerce/06-gtin-identifier-feed.md) — GTIN valid sau identifier_exists:no in feed GMC
- [07-google-product-category-feed.md](woocommerce/07-google-product-category-feed.md) — Mapare categorii WC → Google Product Category in feed
- [08-snippet-replacement-order.md](woocommerce/08-snippet-replacement-order.md) — Ordinea corecta la inlocuire snippet: creeaza→verifica→sterge

---

## Performance

- [01-wpcode-snippet-types.md](performance/01-wpcode-snippet-types.md) — CSS vs JS vs PHP: tabel de decizie, de ce conteaza
- [02-wc-hooks-caching.md](performance/02-wc-hooks-caching.md) — Guard obligatoriu + transient/wp_cache + get_objects_in_term pattern
- [03-schema-hook-vs-obstart.md](performance/03-schema-hook-vs-obstart.md) — Inlocuire ob_start cu hook direct Rank Math/Yoast/WC
- [04-wpcode-snippet-audit.md](performance/04-wpcode-snippet-audit.md) — Procedura audit complet: PHP query pentru lista reala, consolidare
- [05-wpcode-one-shot-lifecycle.md](performance/05-wpcode-one-shot-lifecycle.md) — Ciclu de viata snippet ONE-SHOT: creare, executie, stergere
- [06-css-conflict-audit.md](performance/06-css-conflict-audit.md) — Detectare conflicte CSS silentioase (cover vs contain etc.)
- [07-transient-cache-pattern.md](performance/07-transient-cache-pattern.md) — Pattern complet transient cache cu invalidare automata

---

## Setup

- [01-litespeed-cache-setup.md](setup/01-litespeed-cache-setup.md) — Instalare + configurare LiteSpeed Cache pentru WooCommerce
- [02-rank-math-sitemap-term-fix.md](setup/02-rank-math-sitemap-term-fix.md) — Fix termen cu URL broken in sitemap Rank Math
