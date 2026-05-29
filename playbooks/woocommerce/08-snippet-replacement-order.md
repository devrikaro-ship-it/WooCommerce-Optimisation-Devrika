# Ordinea Corecta la Inlocuire Snippet

## Ce face
Defineste fluxul obligatoriu pentru a inlocui un snippet existent fara a lasa site-ul broken intre etape. Greseala inversa (dezactivezi inainte sa creezi replacement) = site fara CSS/JS = client afectat.

## Cand se aplica
- La orice inlocuire de snippet (PHP→CSS, refactorizare, consolidare)
- La orice dezactivare de snippet care furnizeaza CSS sau functionalitate activa

## Fluxul corect

```
GRESIT:  dezactivezi cel vechi → (site broken) → creezi cel nou → activezi
CORECT:  creezi cel nou → activezi → verifici → dezactivezi cel vechi
```

## Implementare

### Pasul 1 — Creeaza snippet-ul nou
Titlu diferit: `Client — Functionalitate v2`

### Pasul 2 — Activeaza snippet-ul nou
Ambele snippeturi (vechi + nou) sunt acum active simultan.

### Pasul 3 — Verifica ca noul snippet functioneaza
Incognito + cache bypass: `https://domain.ro/?nocache=1`

### Pasul 4 — Dezactiveaza si sterge cel vechi
Abia acum, dupa confirmare vizuala.

### Pasul 5 — Verifica din nou dupa dezactivare
Confirma ca functionalitatea persista fara snippetul vechi.

## Situatii speciale

**Conflict intre versiunea veche si noua:**
Daca ambele snippeturi active simultan cauzeaza conflict (CSS contradictoriu):
- Dezactiveaza rapid versiunea veche
- Verifica ca noua functioneaza
- Total timp de "downtime": sub 30 secunde

**Inlocuire PHP→CSS (cel mai frecvent caz):**
```
1. Creeaza snippet CSS-type nou cu tot CSS-ul extras din PHP
2. Activeaza CSS-type snippet
3. Verifica stilizarea pe site (incognito)
4. Dezactiveaza PHP snippet
5. Verifica din nou
6. Sterge PHP snippet din WPCode (sau muta in trash)
```

## Cum se aplica corect (Best Practice)
- Nu dezactiva niciodata un snippet care furnizeaza CSS pentru footer, header, imagini, logo fara replacement gata
- Testeaza intotdeauna in **incognito** + cache bypass — utilizatorul logat vede mereu versiunea live, nu cached
- Dupa dezactivare: flush cache (LiteSpeed/WP Rocket/SiteGround) pentru a curata versiunea cached cu snippetul vechi
- Documenteaza in titlul snippet-ului: `v1`, `v2`, `(consolidat)`, `(CSS-type)` — usor de identificat la audit

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Dezactivezi PHP footer fara CSS replacement | Footer fara CSS, layout broken | Creeaza CSS-type inainte, verifica, abia dezactiveaza |
| Nu verifici in incognito | Crezi ca functioneaza dar e cached versiunea veche | Testeaza in incognito + `?nocache=1` |
| Nu flushuiesti cache-ul dupa | Utilizatorii vad versiunea broken cached | Flush LiteSpeed/WP Rocket dupa orice schimbare de snippeturi |

## Timp estimat
+10 minute fata de inlocuire directa — merita intotdeauna
