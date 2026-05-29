# AI Crawlers in robots.txt

## Ce face
Permite explicit crawlerilor AI (GPTBot, ClaudeBot, Google-Extended, PerplexityBot) sa indexeze continutul site-ului pentru a fi citat in raspunsurile AI (ChatGPT, Claude, Perplexity, Google AI Overviews). Impact direct pe vizibilitatea GEO (Generative Engine Optimization).

## Cand se aplica
- Pe orice site care vrea vizibilitate in AI search
- Obligatoriu pe site-uri e-commerce cu produse de nisa (hranire animale, beauty, tech)
- Nu se aplica daca clientul refuza explicit indexarea de catre AI (ex: continut proprietar, date sensibile)

## Inainte sa incepi
- Verifica robots.txt curent: `curl https://domain.ro/robots.txt`
- Cauta daca exista `Disallow: /` pentru user-agents AI
- Verifica daca robots.txt e fisier fizic sau generat dinamic (Rank Math/Yoast)

## Implementare

### Pasul 1 — Verifica starea curenta
```bash
curl https://domain.ro/robots.txt | grep -i "gptbot\|claudebot\|google-extended\|perplexity"
```

### Pasul 2 — Daca robots.txt e generat dinamic (Rank Math/Yoast)
Adauga via PHP filter — snippet PHP in WPCode.

### Pasul 3 — Daca robots.txt e fisier fizic pe server
Editeaza direct fisierul sau foloseste `file_put_contents` ONE-SHOT.

### Pasul 4 — Verifica
```bash
curl https://domain.ro/robots.txt
```

## Cod

**Optiunea 1 — PHP filter (recomandat pentru robots.txt dinamic):**
```php
add_filter('robots_txt', function($output) {
    $ai_crawlers = [
        'GPTBot',
        'ChatGPT-User',
        'CCBot',
        'anthropic-ai',
        'ClaudeBot',
        'Claude-Web',
        'Google-Extended',
        'PerplexityBot',
        'Applebot-Extended',
        'Bytespider',
        'cohere-ai',
    ];

    $additions = "\n# AI Crawlers — Allow for GEO visibility\n";
    foreach ($ai_crawlers as $bot) {
        $additions .= "User-agent: {$bot}\nAllow: /\n\n";
    }

    return $output . $additions;
}, 10, 1);
```

**Optiunea 2 — fisier fizic ONE-SHOT (cand Rank Math nu genereaza corect):**
```php
// ONE-SHOT: ruleaza o data, apoi sterge snippet-ul
add_action('init', function() {
    if (isset($_GET['update_robots']) && current_user_can('manage_options')) {
        $current = file_get_contents(ABSPATH . 'robots.txt');
        $additions = "\n# AI Crawlers\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n";
        file_put_contents(ABSPATH . 'robots.txt', $current . $additions);
        die('robots.txt updated');
    }
});
// Acceseaza: https://domain.ro/?update_robots=1 (o singura data)
```

## Cum se aplica corect (Best Practice)
- Foloseste PHP filter (`robots_txt`) daca robots.txt e generat de Rank Math — mai sigur decat fisier fizic
- Fisierul fizic are prioritate fata de filtrul PHP — daca exista `/robots.txt` pe server, filtrul e ignorat
- Verifica daca fisier fizic exista: `curl -I https://domain.ro/robots.txt | grep "x-robots-tag\|last-modified"`
- Adauga `llms.txt` pe langa robots.txt — crawler-ii AI il citesc explicit (vezi playbook llms-txt)
- Nu bloca niciodata Googlebot, Bingbot, main crawleri — verifica ca nu existi Disallow pe ei

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Fisier fizic robots.txt suprascrie filtrul PHP | Crawlerii AI raman blocati | Editeaza fisierul fizic direct |
| Rank Math robots.txt editor nu salveaza pe fisier fizic | Filtrul PHP nu se aplica | Foloseste `file_put_contents` ONE-SHOT |
| `Allow: /` lipseste (doar User-agent fara directive) | Ambiguitate — unii crawleri interpreteaza diferit | Adauga intotdeauna `Allow: /` explicit |

## Verificare
- `curl https://domain.ro/robots.txt | grep -A2 "GPTBot"` — trebuie sa apara `Allow: /`
- https://domain.ro/robots.txt in browser — vizualizare directa
- Dupa 2-4 saptamani: cauta `site:domain.ro` in Perplexity sau intreaba ChatGPT despre brand

## Timp estimat
20 minute
