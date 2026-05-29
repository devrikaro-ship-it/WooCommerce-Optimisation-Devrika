# Carousel Filter pe Taxonomie — JS

## Ce face
Filtreaza JS-side produsele dintr-un carousel Elementor pe pagina de produs, ascunzand produsele din alta specie/categorie decat produsul curent. Util cand carousel-ul "Related products" sau "You may also like" afiseaza produse din categorii gresite.

## Cand se aplica
- Site-uri cu carousel Elementor de related products pe pagina produs
- Cand filtrul PHP pe `woocommerce_related_products` nu e suficient (carousel incarca via AJAX)
- Ruleza doar pe `is_product()` — zero impact pe alte pagini

## Inainte sa incepi
- Verifica ca body class per specie e implementata (playbook 02-body-class-taxonomy)
- Identifica structura carousel: DevTools > inspect items carousel > selector `.swiper-slide` sau similar
- Identifica cum sunt marcate produsele cu specia lor (clasa CSS, data attribute)

## Implementare

### Pasul 1 — Verifica body class per specie activa
Fara body class, filtrul JS nu stie ce specie e produsul curent.

### Pasul 2 — Identifica structura carousel si marcajul produselor
```javascript
// DevTools Console pe pagina produs:
document.querySelectorAll('.related .product').forEach(p => {
    console.log(p.className, p.querySelector('a')?.href);
});
```

### Pasul 3 — Creeaza snippet PHP in WPCode
- PHP type (pentru a folosi `is_product()` server-side si a injecta JS doar pe pagini produs)

## Cod

```php
// JS filter carousel pe specie — rulat doar pe pagini produs
add_action('wp_footer', function() {
    if (!is_product()) return;
    ?>
<script>
(function() {
    // Keywordsul speciei din URL sau din body class
    var SPECIES_KEYWORDS = {
        'puria-species-caini': ['pisici', 'pasari', 'rozatoare'],   // exclude aceste keywords din titluri
        'puria-species-pisici': ['caini', 'pasari', 'rozatoare'],
        'puria-species-pasari-rozatoare': ['caini', 'pisici'],
    };

    // Detecteaza specia curenta din body class
    var currentSpecies = null;
    for (var sp in SPECIES_KEYWORDS) {
        if (document.body.classList.contains(sp)) {
            currentSpecies = sp;
            break;
        }
    }

    if (!currentSpecies) return; // produsul nu are specia definita

    var excludeKeywords = SPECIES_KEYWORDS[currentSpecies] || [];

    function filterCarousel() {
        // Ajusteaza selectorul la carousel-ul clientului
        var slides = document.querySelectorAll(
            '.related.products li.product, .upsells li.product, [class*="swiper-slide"] .product'
        );

        slides.forEach(function(slide) {
            var title = (slide.querySelector('.woocommerce-loop-product__title, h2, h3')?.textContent || '').toLowerCase();
            var link  = (slide.querySelector('a')?.href || '').toLowerCase();
            var text  = title + ' ' + link;

            var shouldHide = excludeKeywords.some(function(kw) {
                return text.includes(kw);
            });

            if (shouldHide) {
                slide.style.display = 'none';
                // Pentru Swiper: ascunde si wrapper-ul slide
                var swiperSlide = slide.closest('.swiper-slide');
                if (swiperSlide) swiperSlide.style.display = 'none';
            }
        });
    }

    // Ruleaza dupa DOM loaded si dupa posibil AJAX carousel
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', filterCarousel);
    } else {
        filterCarousel();
    }

    // Re-ruleaza daca carousel-ul se incarca via AJAX (ex: Elementor lazy)
    setTimeout(filterCarousel, 1500);
    setTimeout(filterCarousel, 3000);
})();
</script>
    <?php
});
```

## Cum se aplica corect (Best Practice)
- Filtrul JS e **complementar** filtrului PHP — nu inlocuieste `woocommerce_related_products` filter, doar curata ce scapa
- `setTimeout` e o solutie pragmatica pentru AJAX carousel — alternativa robusta e MutationObserver (risc de loop)
- Keywords-urile de excludere trebuie sa fie **in URL sau titlu** al produsului — nu in descriere (nu e incarcata in card)
- Testeaza pe produse din fiecare categorie: caini vede doar caini, pisici vede doar pisici
- Daca carousel-ul e complet gol dupa filtrare: problema e la filtrul PHP, nu la JS

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| Fara body class per specie | `currentSpecies` null, filtrul nu ruleaza | Implementa playbook 02-body-class-taxonomy mai intai |
| Keywords prea generice | Filtrare excesiva, carousel gol | Testeaza keywords pe titluri reale de produse |
| MutationObserver in loc de setTimeout | Risc de loop infinit | Foloseste `setTimeout` cu 2 iteratii |
| Selector carousel gresit | `slides.length === 0`, filtrul nu face nimic | Identifica selector cu DevTools |

## Verificare
- Pagina produs "caini": carousel arata doar produse cu "caini" in URL/titlu
- Pagina produs "pisici": carousel arata doar produse cu "pisici" in URL/titlu
- DevTools Console: fara erori JS

## Timp estimat
30 minute
