# Greseli Inregistrate â€” puria.ro Automation

Fiecare greseala este documentata cu context, efect negativ si lectie invatata.

---

## GRESEALA #1 â€” Snippet-uri one-shot lasate active dupa executie

**Data:** Mai 2026
**Context:** Snippet-urile PHP de tip one-shot (debug, flush cache, modificare optiuni)
au fost create si activate in WPCode dar nu au fost dezactivate dupa ce si-au facut treaba.

**Snippet-uri afectate:** 248205, 248206, 248207, 248208, 248215, 248219

**Efect negativ:**
- Flush sitemap rula la FIECARE request â€” cache-ul era sters continuu
- Script dump debug scria fisiere pe server la fiecare vizita a oricarui utilizator
- Script Rank Math modifica optiunile la fiecare request (overhead DB inutil)

**Lectie:** Orice snippet cu prefix ONE-SHOT sau DEBUG trebuie dezactivat IMEDIAT
dupa prima rulare confirmata cu succes.

---

## GRESEALA #2 â€” Duplicate de snippet-uri CSS/JS acumulate in timp

**Data:** Mai 2026
**Context:** La fiecare iteratie de fix pentru imaginile produselor, versiunea noua
a fost salvata ca snippet nou fara a dezactiva/sterge versiunea veche.
Rezultat: 5 copii CSS identice + 4 copii JS identice, toate active simultan.

**Snippet-uri afectate:**
- CSS duplicate: 248118, 248125, 248131, 248146 (versiunea corecta: 248197)
- JS duplicate:  248119, 248126, 248132 (versiunea corecta: 248147)

**Efect negativ:**
- CSS-ul pentru imagini se incarca de 5x pe fiecare pagina
- MutationObserver JS rula de 4x in paralel â€” conflict intre versiuni
- Logo distorsionat din cauza conflictului intre versiunile vechi si noi
- Performanta degradata inutil

**Lectie:** Inainte de a crea un snippet nou care inlocuieste unul vechi,
dezactiveaza/sterge-l pe cel vechi. Pastreaza mereu un singur snippet activ per functionalitate.

---

## GRESEALA #3 â€” Dezactivare WPCode via form POST fara snippet_id

**Data:** Mai 2026
**Context:** Incercare de dezactivare a 13 snippet-uri prin trimiterea formularului
de editare WPCode via fetch(), fara a include campul snippet_id in POST body.

**Ce s-a intamplat:** WPCode a interpretat POST-ul fara ID ca cerere de CREARE snippet
nou, nu de editare. Au fost create 13 snippet-uri noi (dezactivate), iar originalele
au ramas neschimbate (inca active).

**Efect negativ:** Repo snippet-uri: 94 -> 107. Cleanup suplimentar necesar.

**Metoda GRESITA:**
```javascript
const fd = new FormData();
fd.append('wpcode_snippet_title', title);
fd.append('wpcode_snippet_code', code);
// LIPSESTE: fd.append('snippet_id', id);  <-- fara asta = snippet NOU
fd.append('button', 'publish');
await fetch(window.location.href, { method: 'POST', body: fd });
```

**Metoda CORECTA:** Vezi BEST-PRACTICES.md #3

---

## GRESEALA #4 â€” Login Playwright headless esueaza pe puria.ro

**Data:** Mai 2026
**Context:** Mai multe scripturi cu `headless: true` au esuat la login,
ramanand blocate pe pagina de login si causand timeout.

**Efect negativ:** Scripturi care par sa ruleze dar nu fac nimic.

**Lectie:** puria.ro necesita `headless: false` + `slowMo: 200-300` pentru login fiabil.

---

## GRESEALA #5 â€” waitForURL cu functie lambda

**Data:** Mai 2026
**Eroare:** `TypeError: url.includes is not a function`

**Cod gresit:**
```javascript
await page.waitForURL(url => !url.includes('/login'));
```

**Cod corect:**
```javascript
await page.waitForURL(url => !url.toString().includes('/login'));
// sau foloseste glob:
await page.waitForURL('**/wp-admin/**');
```