# WPCode Snippet Audit — Procedura Completa

## Ce face
Defineste procedura corecta de audit al tuturor snippeturilor WPCode active, inclusiv cum sa obtii lista reala (UI-ul arata max 20), cum sa identifici problemele si cum sa consolidezi.

## Problema cu UI-ul WPCode

WPCode afiseaza implicit 20 snippeturi per pagina. Chiar daca adaugi `?per_page=100` in URL, WPCode ignora parametrul. **Poti avea 60 snippeturi active si sa crezi ca ai 20.**

## Procedura de audit

### Pasul 1 — Obtine lista reala via PHP snippet

Creeaza snippet PHP ONE-SHOT in WPCode:

```php
// ONE-SHOT: lista toate snippeturile active cu tip
add_action('wp_footer', function() {
    if (!current_user_can('manage_options') || !isset($_GET['audit_snippets'])) return;
    global $wpdb;
    $snippets = $wpdb->get_results("
        SELECT p.ID, p.post_title, p.post_status,
               (SELECT meta_value FROM {$wpdb->postmeta}
                WHERE post_id = p.ID AND meta_key = 'wpcode_snippet_type' LIMIT 1) as type
        FROM {$wpdb->posts} p
        WHERE p.post_type = 'wpcode'
        AND p.post_status = 'publish'
        ORDER BY p.ID ASC
    ");
    echo '<pre style="background:#000;color:#0f0;padding:20px;position:fixed;top:0;left:0;right:0;z-index:9999;overflow:auto;max-height:90vh;">';
    echo 'TOTAL ACTIVE: ' . count($snippets) . "\n\n";
    foreach ($snippets as $s) {
        echo $s->ID . ' | ' . ($s->type ?: 'php') . ' | ' . $s->post_title . "\n";
    }
    echo '</pre>';
});
// Acceseaza: https://domain.ro/?audit_snippets=1 (logat ca admin)
```

### Pasul 2 — Categorizeaza snippeturile

Din lista, grupeaza pe:
- **ONE-SHOT ramase active** — prefix `ONE-SHOT:` sau `DEBUG:` → sterge imediat
- **Duplicate** — acelasi titlu de mai multe ori → pastreaza cel mai recent, sterge restul
- **PHP care face echo style/script** → candidati pentru conversie CSS/JS-type
- **Hooks grele fara cache** → adauga transient
- **Filtre multiple pe acelasi hook** → consolideaza

### Pasul 3 — Target: sub 25 snippeturi active

```
> 40 active = problema garantata
25-40 active = acceptabil, da trebuie curatenie
< 25 active = optim
```

### Pasul 4 — Sterge definitiv (nu doar dezactiva)

```
WPCode list > Inactive view > selecteaza toate > Trash
WPCode list > Trash view > selecteaza toate > Delete Permanently
```

## Cum se aplica corect (Best Practice)
- **Audit la fiecare client nou** inainte de orice modificare — stii cu ce pornesti
- **Audit la finalul oricarei sesiuni de implementare** — verifica ca nu au ramas ONE-SHOT-uri
- Documenteaza numarul de snippeturi active in `DOCUMENTATION.md` per client
- Dupa stergere: flush cache complet si verifica site

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Te bazezi pe UI-ul WPCode pentru numar total | Crezi ca ai 20, ai 60 | Foloseste query PHP direct pe `wp_posts` |
| Dezactivezi fara sa stergi | Trash se umple, confuzie la audit viitor | Sterge definitiv snippeturile inutile |
| Audit sarit la client nou | Implementezi peste 50 snippeturi vechi neauditata | Audit obligatoriu la prima sesiune |

## Verificare
- PHP query returneaza numarul real de snippeturi active
- Dupa curatenie: site functioneaza normal (verifica paginile principale)

## Timp estimat
1-2h per client pentru audit complet + curatenie
