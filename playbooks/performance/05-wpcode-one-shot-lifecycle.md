# WPCode ONE-SHOT Snippet Lifecycle

## Ce face
Defineste ciclul complet de viata al unui snippet temporar (one-shot): creare cu prefix corect, executie, verificare, stergere imediata. Snippeturile one-shot lasate active = risc critic.

## De ce e critic

Un snippet one-shot lasat activ poate:
- Flush sitemap la fiecare request (query + I/O per pageview)
- Scrie fisiere de debug pe server la fiecare vizita
- Face `update_option` per request (write DB)
- Re-executa migrari deja executate

## Lifecycle corect

```
1. Creeaza cu prefix "ONE-SHOT:" in titlu
2. Activeaza
3. Executa (acceseaza URL-ul cu parametrul de trigger)
4. Verifica rezultatul
5. Dezactiveaza IMEDIAT
6. Sterge definitiv din WPCode
```

## Template snippet ONE-SHOT corect

```php
// ONE-SHOT: [descriere actiune] — sterge dupa executie
// Acceseaza: https://domain.ro/?run_ACTIUNE=1 (o singura data, logat ca admin)

add_action('init', function() {
    // Guard 1: doar admin logat
    if (!current_user_can('manage_options')) return;

    // Guard 2: parametru URL explicit
    if (!isset($_GET['run_ACTIUNE'])) return;

    // Guard 3: executie o singura data (optional dar recomandat)
    if (get_option('client_ACTIUNE_done_v1')) {
        wp_die('Already done');
    }

    // --- Actiunea ta one-shot ---
    // ex: update_option, $wpdb->update, file_put_contents, etc.
    // ---

    update_option('client_ACTIUNE_done_v1', '1'); // mark as done
    wp_die('Done: ACTIUNE executata cu succes');
});
```

## Exemple de actiuni one-shot comune

**Flush sitemap Rank Math:**
```php
add_action('init', function() {
    if (!current_user_can('manage_options') || !isset($_GET['flush_sitemap'])) return;
    delete_transient('rank_math_sitemap_index');
    do_action('rank_math/sitemap/invalidate_sitemap');
    wp_die('Sitemap flushed');
});
```

**Deschide comment_status pe produse:**
```php
add_action('init', function() {
    if (!current_user_can('manage_options') || !isset($_GET['open_reviews'])) return;
    if (get_option('reviews_opened_v1')) { wp_die('Already done'); }
    global $wpdb;
    $wpdb->update($wpdb->posts, ['comment_status' => 'open'], ['post_type' => 'product', 'post_status' => 'publish']);
    update_option('reviews_opened_v1', '1');
    wp_die('Reviews opened');
});
```

## Cum se aplica corect (Best Practice)
- Prefixul `ONE-SHOT:` in titlu = identificare rapida la audit
- Guard cu `get_option` previne re-executia accidentala daca snippetul e lasat activ
- `wp_die()` cu mesaj clar = confirmare imediata ca actiunea s-a executat
- **Nu pune actiunea one-shot in `wp_head`** — se executa la fiecare request de pagina; foloseste `init` cu parametru URL
- Dupa executie: dezactiveaza imediat, sterge a doua zi dupa confirmare

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Snippet one-shot in `wp_head` fara trigger URL | Ruleaza la fiecare pageview | Muta in `init` cu guard `isset($_GET['...'])` |
| Fara guard `current_user_can` | Oricine poate executa actiunea | Adauga guard admin |
| Lasat activ dupa executie | Executa la fiecare request sau la fiecare vizita admin | Dezactiveaza imediat dupa verificare |
| Nu adaugi guard `get_option` | Executie accidentala multipla | Adauga flag in DB dupa prima executie |

## Verificare
- Dupa executie: `wp_die()` arata mesajul de confirmare
- WPCode > snippet dezactivat + in trash
- Site functioneaza normal dupa stergere

## Timp estimat
5 minute per snippet one-shot (creare + executie + stergere)
