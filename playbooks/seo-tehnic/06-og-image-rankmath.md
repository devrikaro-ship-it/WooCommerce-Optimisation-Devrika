# OG Image — Social Share

## Ce face
Adauga imaginea de previzualizare (og:image) care apare cand site-ul e distribuit pe Facebook, WhatsApp, LinkedIn, Twitter/X. Fara ea, share-ul social apare fara imagine — CTR social scade cu 50-70%.

## Cand se aplica
- Orice site fara og:image configurata
- Verifica cu: `curl -s https://domain.ro/ | grep og:image`
- Daca returneaza gol sau o imagine necorespunzatoare (logo mic, imagine random)

## Inainte sa incepi
- Ai nevoie de o imagine 1200x630px reprezentativa pentru brand
- Format JPG sau PNG, max 1MB
- Rank Math sau Yoast instalat si activ

## Implementare

### Pasul 1 — Creeaza imaginea OG
Dimensiuni: **1200x630px**. Include: logo, culori brand, tagline. Fara text important la margini (15px safe zone).

### Pasul 2 — Upload in Media Library
Media > Adauga fisier nou > nota URL-ul imaginii

### Pasul 3 — Seteaza in Rank Math
Rank Math > Titluri si Meta > Global Meta > Social Meta > Default Thumbnail > selecteaza imaginea

### Pasul 4 — Seteaza si pe pagini individuale importante
Homepage, pagini categorii principale: editeaza pagina > Rank Math panel > Social > Custom Image

### Pasul 5 — Verifica
Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/

## Cod

**Fallback PHP daca Rank Math nu seteaza corect (rar necesar):**
```php
add_action('wp_head', function() {
    if (is_front_page() || is_home()) {
        $og_image = 'https://domain.ro/wp-content/uploads/og-homepage.jpg';
        echo '<meta property="og:image" content="' . esc_url($og_image) . '">' . "\n";
        echo '<meta property="og:image:width" content="1200">' . "\n";
        echo '<meta property="og:image:height" content="630">' . "\n";
    }
}, 5); // priority 5 = inainte de Rank Math
```

**Seteaza og:image via Rank Math REST API (pentru pagini existente):**
```bash
curl -X POST "https://domain.ro/wp-json/rankmath/v1/updateMeta" \
  -H "Content-Type: application/json" \
  -u "username:application_password" \
  -d '{"objectID": PAGE_ID, "objectType": "post", "meta": {"rank_math_facebook_image": "IMAGE_URL"}}'
```

## Cum se aplica corect (Best Practice)
- Imaginea OG **nu e acelasi lucru** cu favicon sau logo — creeaza una dedicata 1200x630
- Fiecare categorie principala ar trebui sa aiba og:image custom (produs reprezentativ)
- Dupa schimbarea imaginii: refresh in Facebook Debugger altfel FB serveste varianta cache
- Pentru WooCommerce: produsele cu imagine principala au og:image automat din Rank Math — nu le suprascrie
- Verifica periodic (la 6 luni) ca imaginile nu au dat 404

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Imagine sub 200x200px | Facebook/WhatsApp nu o afiseaza | Minim 600x315px, recomandat 1200x630px |
| Imagine peste 8MB | Facebook nu o proceseaza | Compresie la max 1MB |
| Cache Facebook nu e refreshat | Apare vechea imagine dupa update | https://developers.facebook.com/tools/debug/ > Scrape Again |
| og:image setat si din PHP si din Rank Math | Duplicate meta tags | Verifica sursa, dezactiveaza una |

## Verificare
- `curl -s https://domain.ro/ | grep og:image` — URL imagine prezent
- Facebook Debugger: https://developers.facebook.com/tools/debug/
- WhatsApp: trimite link in conversatie privata si verifica preview
- Twitter Card Validator: https://cards-dev.twitter.com/validator

## Timp estimat
45 minute (creare imagine + implementare)
