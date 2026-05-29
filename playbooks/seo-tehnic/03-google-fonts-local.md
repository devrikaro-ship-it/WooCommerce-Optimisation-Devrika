# Google Fonts Hosted Local

## Ce face
Descarca fonturile Google Fonts pe serverul propriu si le serveste local, eliminand 1-3 request-uri externe catre fonts.googleapis.com. Reduce TTFB, elimina GDPR dependency pe Google, imbunatateste LCP cu ~100-200ms.

## Cand se aplica
- Orice site care foloseste Google Fonts (Poppins, Roboto, Lato, Nunito etc.)
- Prioritar cand DevTools Network arata request-uri catre fonts.googleapis.com sau fonts.gstatic.com
- Nu se aplica daca fonturile sunt deja self-hosted (verifica mai intai)

## Inainte sa incepi
- Identifica ce fonturi sunt folosite: DevTools > Network > filter "font" sau "googleapis"
- Noteaza weight-urile folosite (400, 600, 700 etc.) — nu descarca ce nu folosesti
- Verifica daca tema are setare nativa de "local fonts" (XStore, Astra etc. au aceasta optiune in settings)

## Implementare

### Pasul 1 — Identifica fonturile
```bash
curl -s https://domain.ro/ | grep -o 'fonts.googleapis.com[^"]*' | head -5
```

### Pasul 2 — Descarca fonturile
Foloseste https://gwfh.mranftl.com/fonts (Google Webfonts Helper) sau snippetul PHP de mai jos.

### Pasul 3 — Upload pe server
Fisierele `.woff2` merg in `/wp-content/uploads/fonts/`

### Pasul 4 — Adauga CSS @font-face
Snippet CSS-type in WPCode cu declaratia @font-face locala.

### Pasul 5 — Dezactiveaza incarcarea Google Fonts din tema
Tema > Customizer sau setarile temei > Typography > "Load Google Fonts" = OFF

## Cod

**Snippet PHP — descarca automat la primul acces admin (one-time):**
```php
add_action('admin_init', function() {
    if (get_option('client_local_fonts_v1')) return; // ruleaza o singura data

    $fonts = [
        'poppins-400' => 'https://fonts.gstatic.com/s/poppins/v21/pxiEyp8kv8JHgFVrJJfedw.woff2',
        'poppins-600' => 'https://fonts.gstatic.com/s/poppins/v21/pxiByp8kv8JHgFVrLEj6Z1xlFQ.woff2',
        'poppins-700' => 'https://fonts.gstatic.com/s/poppins/v21/pxiByp8kv8JHgFVrLCz7Z1xlFQ.woff2',
    ];

    $dir = WP_CONTENT_DIR . '/uploads/fonts/';
    wp_mkdir_p($dir);

    foreach ($fonts as $name => $url) {
        $file = $dir . $name . '.woff2';
        if (!file_exists($file)) {
            $response = wp_remote_get($url, ['timeout' => 30]);
            if (!is_wp_error($response)) {
                file_put_contents($file, wp_remote_retrieve_body($response));
            }
        }
    }

    update_option('client_local_fonts_v1', '1');
});
```

**Snippet CSS — @font-face local (CSS-type in WPCode):**
```css
@font-face {
    font-family: 'Poppins';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('/wp-content/uploads/fonts/poppins-400.woff2') format('woff2');
}

@font-face {
    font-family: 'Poppins';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('/wp-content/uploads/fonts/poppins-600.woff2') format('woff2');
}

@font-face {
    font-family: 'Poppins';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('/wp-content/uploads/fonts/poppins-700.woff2') format('woff2');
}
```

**Dezactiveaza Google Fonts din WordPress (PHP):**
```php
// Elimina toate enqueue-urile catre fonts.googleapis.com
add_action('wp_print_styles', function() {
    global $wp_styles;
    foreach ($wp_styles->queue as $handle) {
        $src = $wp_styles->registered[$handle]->src ?? '';
        if (str_contains($src, 'fonts.googleapis.com')) {
            wp_dequeue_style($handle);
        }
    }
}, 100);
```

## Cum se aplica corect (Best Practice)
- Snippet PHP de descarcare = **ONE-SHOT** — sterge-l dupa ce fonturile sunt pe server
- `font-display: swap` obligatoriu — previne FOIT (Flash of Invisible Text)
- Descarca **doar** weight-urile efectiv folosite pe site (nu toate 9 weights)
- Verifica ca fisierele `.woff2` exista pe server inainte de a activa CSS-ul
- Daca tema are setare nativa de local fonts (XStore, Astra) — foloseste aceea, nu snippet custom
- URL-urile Google Fonts se schimba periodic — verifica la 6-12 luni

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Snippet PHP ramas activ dupa descarcare | Descarca de N ori la fiecare vizita admin | Sterge snippet dupa prima rulare |
| Weight-uri lipsa in @font-face | Browser descarca Google Fonts pentru weight-urile lipsa | Adauga toate weight-urile folosite |
| Fisiere fonts nu exista pe server | 404 pe font, browser fallback la system font | Verifica existenta fisierelor inainte de CSS |
| Google Fonts nu dezactivat din tema | Doua surse de font incarcate simultan | Dezactiveaza din Customizer sau PHP dequeue |

## Verificare
- DevTools > Network > filter "font" — nu trebuie sa apara requests catre `fonts.googleapis.com`
- DevTools > Network > filter "font" — `.woff2` se incarca de pe domeniu propriu
- PageSpeed Insights — dispare avertizarea "Elimina resursele care blocheaza randarea"

## Timp estimat
45-60 minute
