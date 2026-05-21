# Best Practices â€” puria.ro Automation

Metodele corecte de lucru validate in sesiunile de automatizare.

---

## #1 â€” Login Playwright pe puria.ro

**Intotdeauna:**
```javascript
const browser = await chromium.launch({ headless: false, slowMo: 200 });
const page = await browser.newPage();
await page.goto('https://puria.ro/wp-login.php?sgs-token=logare', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1500);
await page.type('#user_login', WP_USER, { delay: 60 });
await page.type('#user_pass', WP_PASS, { delay: 60 });
await page.click('#wp-submit');
await page.waitForTimeout(5000);
if (page.url().includes('wp-login')) throw new Error('Login esuat');
```

**De evitat:**
- `headless: true` â€” blocheaza logarea pe puria.ro
- `waitForURL` cu functie lambda fara `.toString()`
- Timeout < 10000ms pe submit login

---

## #2 â€” Regula snippet-urilor one-shot

**Orice snippet ONE-SHOT sau DEBUG se dezactiveaza IMEDIAT dupa rulare.**

Flux corect:
1. Creeaza snippet cu prefix `ONE-SHOT:` in titlu
2. Activeaza â†’ asteapta o cerere HTTP sa il ruleze
3. Verifica log/fisier debug ca a functionat
4. **Dezactiveaza imediat**
5. Optional: sterge complet dupa o saptamana

---

## #3 â€” Dezactivare corecta snippet WPCode via AJAX

**Metoda recomandata:**
```javascript
// Din contextul paginii wp-admin (via Playwright page.evaluate):
const fd = new FormData();
fd.append('action', 'wpcode_activate_snippet');
fd.append('id', SNIPPET_ID);
fd.append('activate', '0');  // 0 = dezactiv, 1 = activ
fd.append('nonce', window.wpcode_vars?.nonce || '');
const r = await fetch('/wp-admin/admin-ajax.php', { method: 'POST', body: fd });
const json = await r.json();
console.log(json); // { success: true }
```

**De evitat:** Form POST pe pagina de editare fara campul `snippet_id` â†’ creeaza snippet NOU.

---

## #4 â€” Actualizare snippet existent (nu crea unul nou)

Flux corect pentru update:
1. Identifica ID-ul snippet-ului existent din lista WPCode
2. Dezactiveaza-l intai (metoda #3)
3. Creeaza versiunea noua si activeaz-o
4. Verifica vizual pe site (metoda #5)
5. Sterge vechiul snippet din lista

**Niciodata:** nu crea versiunea noua inainte sa dezactivezi vechea versiune.

---

## #5 â€” Verificare vizuala dupa orice modificare CSS/JS

```javascript
await page.goto('https://puria.ro/caini/?nocache=1', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(3000);
const objectFit = await page.evaluate(() => {
  const img = document.querySelector('.etheme-product-grid-image img');
  return img ? getComputedStyle(img).objectFit : 'NOT FOUND';
});
console.log('object-fit:', objectFit); // trebuie: 'contain'
await page.screenshot({ path: 'verify.png' });
```

Verifica intotdeauna pe: /caini/, /pisici/, homepage (logo si hero).

---

## #6 â€” GitHub API: creare vs. actualizare fisier

**Creare fisier nou (PUT fara SHA):**
```powershell
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($content))
$body = @{ message = "commit msg"; content = $encoded } | ConvertTo-Json
Invoke-RestMethod -Uri "$base/FISIER.md" -Method PUT -Headers $headers -Body $body
```

**Actualizare fisier existent (PUT cu SHA obligatoriu):**
```powershell
$existing = Invoke-RestMethod -Uri "$base/FISIER.md" -Headers $headers
$sha = $existing.sha
$body = @{ message = "commit msg"; content = $encoded; sha = $sha } | ConvertTo-Json
Invoke-RestMethod -Uri "$base/FISIER.md" -Method PUT -Headers $headers -Body $body
```

Fara SHA la update â†’ eroare 422 Unprocessable Entity.

---

## #7 â€” Audit lunar snippet-uri WPCode

Ruleaza o data pe luna:
1. Lista toate snippet-urile active
2. Dezactiveaza orice snippet cu ONE-SHOT sau DEBUG in titlu
3. Identifica duplicate (titluri similare sau cod identic)
4. Mentine maxim 10 snippet-uri active simultan
5. Documenteaza orice schimbare in DOCUMENTATION.md