# Reguli Generale — WooCommerce Optimisation Devrika

Manual de start. Citeste inainte de orice implementare pe orice client.

---

## Ordinea de implementare pe orice client

```
1. Audit initial (snapshots, CWV, snippeturi active, plugins)
2. SEO Tehnic (headers, noindex, fonts, robots)
3. Schema / Structured Data
4. UX / Design
5. WooCommerce (hooks, related products, reviews)
6. Performance (cache, query optimizare)
7. Cleanup final (snippeturi inutile, verificare site)
```

Nu sari etape. Nu implementa UX inainte de tehnic.

---

## Reguli WPCode

| Regula | De ce |
|--------|-------|
| Max 20-25 snippeturi active | Fiecare ruleaza pe fiecare request |
| 1 snippet activ per functionalitate | Duplicate = comportament impredictibil |
| CSS-type pentru stiluri, JS-type pentru interactii, PHP doar pentru hooks | PHP cu echo style = overhead inutil |
| ONE-SHOT snippeturi se sterg imediat dupa executie | Altfel ruleaza la fiecare request |
| Creezi nou → verifici → abia apoi stergi pe cel vechi | Invers = site broken fara CSS |
| Prefix obligatoriu in titlu: `Client — Functionalitate` | Audit rapid, evita confuzia |
| Audit via PHP query, nu via UI | UI-ul arata max 20 snippeturi per pagina |

---

## Reguli PHP hooks

```php
// OBLIGATORIU: guard de pagina pe orice hook
add_action('wp_head', function() {
    if (!is_product()) return;        // fara asta ruleaza pe TOATE paginile
    if (!is_product_category()) return;
    // ...
});

// OBLIGATORIU: cache pe orice DB query in wp_head
$data = get_transient('prefix_' . $id);
if ($data === false) {
    $data = get_posts([...]); // query greu
    set_transient('prefix_' . $id, $data, HOUR_IN_SECONDS);
}

// MAX 1 filter per hook WooCommerce
// Gresit: 3 filtre pe woocommerce_related_products
// Corect: 1 filter care face tot
```

---

## Reguli CSS

- **Nu selectoare broad** (`.product img`, `img`) — prind logo, header, slider
- Foloseste parent de produs: `li.product .woocommerce-product-gallery img`
- Cauta toate snippeturile cu aceeasi proprietate CSS inainte sa adaugi unul nou
- Nu `object-fit: cover` si `object-fit: contain` active simultan
- Nu MutationObserver pe `style` cu `removeProperty` — infinite loop
- `!important` pe CSS-type snippet bate orice inline style

---

## Reguli Playwright / Admin

- Intotdeauna `launchPersistentContext('/tmp/CLIENT-session')` — nu `browser.launch()`
- Login o singura data, toti pasii in acelasi `main()`
- `context.close()` doar la finalul absolut
- Daca sesiunea a crashat: `rm -f /tmp/CLIENT-session/Singleton*`
- Dezactivare snippet: toggle OFF + Save — nu stergere directa fara verificare

---

## Reguli snippet replacement

```
GRESIT:  dezactivezi → (site broken) → creezi nou
CORECT:  creezi nou → verifici ca merge → dezactivezi pe cel vechi
```

---

## Checklist final inainte de a inchide task-ul

- [ ] Site se incarca fara erori JS in console
- [ ] Footer vizibil si corect stilizat
- [ ] Imagini produse arata correct (contain, fara taieri)
- [ ] Sort dropdown functional
- [ ] Mobile: niciun element acoperit, nicio defilare orizontala
- [ ] Snippeturi ONE-SHOT sterse
- [ ] Cache flushed (LiteSpeed / WP Rocket / SiteGround)
- [ ] Verificat pe URL incognito (bypass cache utilizator logat)
- [ ] Numar snippeturi active documentat
