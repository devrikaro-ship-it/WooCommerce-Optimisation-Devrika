# CSS Conflict Audit — Proprietati in Conflict

## Ce face
Procedura de detectare si rezolvare a conflictelor CSS silentioase intre snippeturi active care seteaza aceeasi proprietate CSS pe aceleasi elemente. Conflictele CSS silentioase cauzeaza comportament impredictibil.

## Conflicte frecvente

| Proprietate | Valori conflictuale | Efect |
|-------------|---------------------|-------|
| `object-fit` | `cover` vs `contain` | Imagini taiate pe unele produse, intregi pe altele |
| `display` | `flex` vs `block` vs `grid` | Layout inconsistent |
| `height` | valori fixe diferite | Elemete de inaltimi diferite |
| `background-color` | culori diferite | Footer/header culoare aleatorie |
| `max-height` | valori diferite | Imagini cu inaltimi diferite per produs |

## Procedura de audit

### Pasul 1 — Identifica toate snippeturile cu proprietatea problematica
```
WPCode > Active view > cauta in titluri sau coduri:
- "object-fit"
- "cover"
- "contain"
- proprietatea la care ai probleme
```

Sau via PHP:
```php
// ONE-SHOT: cauta proprietatea in toate snippeturile active
add_action('wp_footer', function() {
    if (!current_user_can('manage_options') || !isset($_GET['css_audit'])) return;
    global $wpdb;
    $snippets = $wpdb->get_results("
        SELECT p.ID, p.post_title, pm.meta_value as code
        FROM {$wpdb->posts} p
        JOIN {$wpdb->postmeta} pm ON p.ID = pm.post_id AND pm.meta_key = 'wpcode_snippet_code'
        WHERE p.post_type = 'wpcode' AND p.post_status = 'publish'
        AND pm.meta_value LIKE '%object-fit%'  /* schimba proprietatea */
    ");
    echo '<pre>';
    foreach ($snippets as $s) echo $s->ID . ' | ' . $s->post_title . "\n";
    echo '</pre>';
});
```

### Pasul 2 — Compara valorile pentru aceleasi selectoare
Daca doua snippeturi seteaza `object-fit: cover` si `object-fit: contain` pe `.product img` → conflict.

### Pasul 3 — Decide care e valoarea corecta
O singura sursa de adevar per proprietate.

### Pasul 4 — Dezactiveaza snippetul cu valoarea gresita
Pastreaza doar snippetul cu valoarea corecta.

### Pasul 5 — Daca amandoua snippeturile au si alte reguli utile
Consolideaza intr-un singur snippet CSS care are TOATE regulile corecte.

## Cum se aplica corect (Best Practice)
- **Inainte de a adauga orice snippet CSS**: cauta daca proprietatea pe care o setezi exista deja intr-un snippet activ
- `!important` nu rezolva conflictele — ambele snippeturi cu `!important` = cascada bazata pe ordinea din DOM
- Ordinea de incarcare a CSS-type snippets in WPCode = ordinea ID-urilor (ID mai mic = incarca primul)
- Dupa rezolvare: flush cache si verifica pe pagini reale

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Adaugi `!important` la ambele | Cascada impredictibila | Pastreaza un singur snippet, sterge celalalt |
| Nu cauti conflicte inainte de implementare | Descoperi conflictul dupa ce clientul raporteaza problema | Audit CSS rapid inainte de fiecare snippet nou |
| Dezactivezi snippetul gresit fara sa verifici celelalte reguli din el | Pierzi alte stiluri utile | Extrage regulile utile inainte de dezactivare |

## Verificare
- DevTools > Elements > Styles: proprietatea conflictuala apare de N ori (strickethrough = suprascris)
- Dupa rezolvare: proprietatea apare o singura data, aplicata uniform
- Verifica pe 5-6 produse cu imagini diferite

## Timp estimat
20-30 minute per conflict identificat si rezolvat
