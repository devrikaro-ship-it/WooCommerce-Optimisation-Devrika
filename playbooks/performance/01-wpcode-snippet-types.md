# WPCode Snippet Types — Reguli de Selectie

## Ce face
Defineste ce tip de snippet WPCode sa folosesti pentru fiecare caz de utilizare. Tipul gresit = overhead inutil, debugging dificil, site lent.

## Regula principala

```
Daca poti face cu CSS → CSS-type
Daca poti face cu JS → JS-type
PHP numai cand ai nevoie de functii WordPress/WooCommerce server-side
```

## Tabel de decizie

| Ce vrei sa faci | Tip corect | Tip GRESIT |
|-----------------|-----------|------------|
| Stiluri vizuale (culori, layout, fonturi, spacing) | **CSS** | PHP cu echo style |
| Override CSS tema cu specificitate mare | **CSS** | PHP cu echo style |
| Animatii, hover effects | **CSS** | JS sau PHP |
| DOM manipulation, dropdown custom, carousel filter | **JS** | PHP cu echo script |
| WC hooks/filters (`woocommerce_*`) | **PHP** | — |
| WordPress filters (`body_class`, `robots_txt`) | **PHP** | — |
| Schema JSON-LD conditionata (is_product) | **PHP** | JS (nu are acces la WP DB) |
| Citire post meta / term meta | **PHP** | JS |
| Continut HTML static (banner, disclaimer) | **HTML** | PHP |
| Script third-party (pixel, analytics) | **HTML** | PHP sau JS |

## De ce conteaza

**PHP cu echo style — de evitat:**
```php
// GRESIT
add_action('wp_head', function() {
    echo '<style>.selector { color: red; }</style>';
});
```
- Executa PHP per request
- Adauga un `<style>` tag inline in plus
- Greu de auditat (apare ca PHP in WPCode, nu ca CSS)
- Nu beneficiaza de optimizarile WPCode pentru CSS

**CSS-type — corect:**
```css
/* CORECT — acelasi efect, zero overhead PHP */
.selector { color: red; }
```
- WPCode injecteaza CSS optimizat
- Vizibil ca CSS in audit
- Fara executie PHP

## Cum se aplica corect (Best Practice)
- La audit: orice snippet PHP care contine DOAR `echo '<style>'` → candidat pentru conversie la CSS-type
- Conversie PHP→CSS: extrage CSS din echo, creaza CSS-type snippet, dezactiveaza PHP (vezi playbook 08-snippet-replacement-order)
- PHP cu conditii (`is_product()`, `is_product_category()`) care outputeaza CSS: converteste la CSS-type + foloseste WPCode Location feature pentru a limita la paginile relevante
- JS-type pentru scripturi care ruleaza in browser — nu PHP care face echo `<script>`

## Audit rapid

```
WPCode > cauta "echo '<style>" in snippeturi PHP active
→ fiecare rezultat = candidat pentru conversie la CSS-type
```

## Timp estimat pentru conversie per snippet
10-15 minute
