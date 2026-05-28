# Greseli Inregistrate — WooCommerce Automation Devrika

Fiecare greseala documentata cu context, efect negativ si lectie. 
Citeste inainte de orice implementare noua.

> Lectiile din aceste greseli sunt integrate si in `CHECKLIST-TEMPLATE.md` si `BEST-PRACTICES.md`.

---

## GRESEALA #1 — Snippeturi one-shot lasate active dupa executie

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Snippeturi PHP de tip one-shot (debug, flush cache, modificare optiuni) au ramas active in WPCode dupa ce si-au facut treaba.

**Efect negativ:**
- Flush sitemap rula la FIECARE request → cache-ul sters continuu
- Script dump debug scria fisiere pe server la fiecare vizita
- Overhead DB inutil pe fiecare request

**Regula:** Orice snippet cu prefix `ONE-SHOT:` sau `DEBUG:` se dezactiveaza IMEDIAT dupa prima rulare confirmata.

---

## GRESEALA #2 — Duplicate snippeturi CSS/JS acumulate

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** La fiecare iteratie de fix, versiunea noua a fost salvata ca snippet nou fara dezactivarea versiunii vechi. Rezultat: 5 CSS identice + 4 JS identice, toate active simultan.

**Efect negativ:**
- CSS incarcata de 5x per pagina
- MutationObserver JS rula de 4x in paralel → conflict intre versiuni
- Logo distorsionat din conflictul versiunilor
- Performanta degradata

**Regula:** Inainte sa creezi un snippet care inlocuieste altul, dezactiveaza/sterge-l pe cel vechi. 1 snippet activ per functionalitate.

---

## GRESEALA #3 — Dezactivare WPCode fara `snippet_id`

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Incercare de dezactivare a 13 snippeturi prin form POST fara campul `snippet_id` in body. WPCode a interpretat ca cerere de CREARE snippet nou.

**Efect negativ:** Repo snippeturi: 94 → 107. Cleanup suplimentar 2h.

**Cod gresit:**
```javascript
const fd = new FormData();
fd.append('wpcode_snippet_title', title);
fd.append('wpcode_snippet_code', code);
// LIPSESTE: fd.append('snippet_id', id)
fd.append('button', 'publish');
await fetch(window.location.href, { method: 'POST', body: fd });
```

**Regula:** Dezactivare corecta = AJAX pe `/wp-admin/admin-ajax.php` cu `snippet_id` explicit. Vezi BEST-PRACTICES.md #3.

---

## GRESEALA #4 — Playwright headless blocheaza login WP

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Scripturi cu `headless: true` au esuat la login, ramanand blocate pe pagina de login → timeout.

**Efect negativ:** Scripturi care par sa ruleze dar nu fac nimic.

**Regula:** Intotdeauna `headless: false` + `slowMo: 200` pentru login WordPress.

---

## GRESEALA #5 — `waitForURL` cu functie lambda fara `.toString()`

**Proiect:** puria.ro | **Data:** Mai 2026

**Eroare:** `TypeError: url.includes is not a function`

**Cod gresit:**
```javascript
await page.waitForURL(url => !url.includes('/login'));
```

**Cod corect:**
```javascript
await page.waitForURL(url => !url.toString().includes('/login'));
// sau glob:
await page.waitForURL('**/wp-admin/**');
```

---

## GRESEALA #6 — `<?php` dublu in snippeturi WPCode

**Proiect:** orice client | **Risc:** CRITIC

**Ce se intampla:** WPCode adauga automat `<?php` la inceputul snippeturilor PHP. Daca adaugi si tu manual `<?php`, rezulta tag dublu = fatal parse error = **site down**.

**Efect negativ:** Site inaccesibil pana la dezactivare manuala din DB sau FTP.

**Regula:** Nu adauga niciodata `<?php` in snippeturi PHP WPCode. Scrie codul direct fara tag de deschidere.

---

## GRESEALA #7 — MutationObserver pe `style` cu `removeProperty`

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** MutationObserver care urmarea schimbarile de `style` si apela `removeProperty()` pe elemente a creat un infinite loop cu alte MO active pe pagina.

**Efect negativ:** UI thread blocat → site **unclickable**. Utilizatorii nu puteau apasa niciun element.

**Regula:**
- Nu folosi MO care observa `attributes` pe style si face modificari → se re-declanseaza la propriile modificari
- Structura corecta MO: `observe(el, { childList: true, subtree: true })`
- Preferat: CSS `!important` de specificitate inalta, nu JS

---

## GRESEALA #8 — Selector broad CSS prinde logo si header

**Proiect:** puria.ro | **Data:** Mai 2026

**Ce s-a intamplat:** Selector `.product-image img` sau `img` aplicat pentru `object-fit: contain` a prins si logo-ul din header.

**Efect negativ:** Logo distorsionat (`contain` pe un logo care are alte proportii decat gridul de produse).

**Regula:**
- Mereu `li.product` sau `.woocommerce-loop-product__link` ca parent
- Adauga guard de excludere: `img.closest('header, nav, .site-branding, #masthead')`
- Logo: selector separat, intentionat, cu `max-height` explicit

---

## GRESEALA #9 — Fara sesiune persistenta Playwright

**Proiect:** orice client | **Data:** Mai 2026

**Ce s-a intamplat:** Scripturi cu `browser.launch()` + `browser.newContext()` forteaza login la fiecare rulare. In sesiuni lungi, sesiunea WP expira → actiunile urmatoare esueaza silentios.

**Regula:** Intotdeauna `chromium.launchPersistentContext('/tmp/CLIENT-session', ...)`. Login o singura data, sesiune reutilizata.

---

## GRESEALA #10 — GitHub API update fara SHA

**Proiect:** puria.ro | **Data:** Mai 2026

**Eroare:** `422 Unprocessable Entity`

**Ce s-a intamplat:** Actualizarea unui fisier existent in GitHub via API fara a include SHA-ul curent al fisierului.

**Regula:** La update fisier existent, fetui intai `GET /contents/path` pentru SHA, includ-o in body la PUT. Vezi BEST-PRACTICES.md #10.

---

## Template — adauga greseala noua

```
## GRESEALA #N — [Titlu scurt descriptiv]

**Proiect:** [client.ro] | **Data:** [Luna Anul]

**Ce s-a intamplat:** [Context — ce actiune a declansat greseala]

**Efect negativ:** [Ce s-a stricat, cat a costat in timp/impact]

**Regula:** [Lectia — ce faci diferit data viitoare]
```
