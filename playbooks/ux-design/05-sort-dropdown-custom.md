# Sort Dropdown Custom Styled

## Ce face
Inlocuieste sort dropdown-ul nativ `<select>` al WooCommerce (vizual diferit pe fiecare browser/OS) cu un element custom styled care arata uniform pe toate platformele, pastrând functionalitatea nativa.

## Cand se aplica
- Site-uri WooCommerce cu pagini de arhiva/categorie
- Cand dropdown-ul de sortare arata diferit pe Windows/Mac/mobile
- Nu necesita jQuery sau plugin suplimentar

## Inainte sa incepi
- Verifica ca `form.woocommerce-ordering` exista pe paginile de arhiva
- Identifica selectorul complet: DevTools > inspect dropdown sort > copia selectorul

## Implementare

### Pasul 1 — Creeaza snippet JS-type in WPCode
Titlu: `Client — Sort Dropdown Custom UI`
Location: `Frontend Only`

### Pasul 2 — Adauga codul JS

### Pasul 3 — Creeaza snippet CSS-type pentru stilizare
Titlu: `Client — Sort Dropdown CSS`

### Pasul 4 — Verifica pe pagina categorie

## Cod

**JS snippet (JS-type in WPCode):**
```javascript
(function() {
    // Guard: ruleaza doar pe pagini de arhiva WooCommerce
    if (!document.body.classList.contains('archive') &&
        !document.body.classList.contains('tax-product_cat') &&
        !document.body.classList.contains('woocommerce-shop')) return;

    function buildSortUI() {
        var form = document.querySelector('form.woocommerce-ordering');
        var sel  = form && form.querySelector('select.orderby, select[name="orderby"]');
        if (!sel || document.querySelector('.puria-sort-display')) return;

        var selectedText = sel.options[sel.selectedIndex]
            ? sel.options[sel.selectedIndex].text
            : 'Sorteaza';

        // Display div vizibil
        var display = document.createElement('div');
        display.className = 'sort-display-custom';
        display.textContent = selectedText;

        // Arrow
        var arrow = document.createElement('span');
        arrow.className = 'sort-arrow';
        arrow.innerHTML = '&#9660;';
        display.appendChild(arrow);

        // Wrapper
        var wrapper = document.createElement('div');
        wrapper.className = 'sort-wrapper-custom';

        // Select nativ deasupra, invizibil — dar functional
        sel.classList.add('sort-native-hidden');
        wrapper.appendChild(display);
        wrapper.appendChild(sel);
        form.insertBefore(wrapper, form.firstChild);

        sel.addEventListener('change', function() {
            var txt = sel.options[sel.selectedIndex]
                ? sel.options[sel.selectedIndex].text
                : 'Sorteaza';
            display.firstChild.textContent = txt;
            form.submit();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildSortUI);
    } else {
        buildSortUI();
    }
})();
```

**CSS snippet (CSS-type in WPCode):**
```css
/* Sort dropdown custom */
.sort-wrapper-custom {
    position: relative;
    display: inline-block;
    vertical-align: middle;
}

.sort-display-custom {
    border: 2px solid #16a34a; /* culoare brand */
    border-radius: 8px;
    padding: 8px 36px 8px 14px;
    background: #fff;
    color: #1f2937;
    font-size: 14px;
    font-weight: 500;
    min-width: 180px;
    cursor: pointer;
    position: relative;
    display: inline-block;
    box-sizing: border-box;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    user-select: none;
}

.sort-arrow {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #6b7280;
    font-size: 10px;
}

.sort-native-hidden {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 2;
    margin: 0;
    padding: 0;
}
```

## Cum se aplica corect (Best Practice)
- **Pastreaza `<select>` nativ** pozitionat absolut si invizibil — asigura accesibilitate si functionalitate pe mobile (mobile deschide native picker la click pe `<select>`)
- Guard `archive/tax-product_cat` obligatoriu — altfel ruleaza pe toate paginile
- Verifica dupa AJAX filter update: daca theme-ul reincarca form-ul dupa filtrare, JS-ul trebuie re-executat (adauga listener pe `woocommerce_update_product_count`)
- Nu folosi un `<div>` custom click handler ca inlocuitor complet al `<select>` — pierde functionalitate mobile

## Greseli cunoscute

| Greseala | Efect | Fix |
|----------|-------|-----|
| `document.querySelector('.puria-sort-display')` hardcodat | Nu gaseste elementul daca clasa e diferita | Schimba clasa cu cea definita in codul tau |
| Form reincarca dupa AJAX filter, UI dispare | Dropdown custom dispare dupa filtrare | Re-executa `buildSortUI()` pe `jQuery(document).on('woocommerce_update_product_count')` |
| Select nativ nu e invizibil complet | User vede doua dropdownuri | `opacity: 0` + `position: absolute` + `z-index: 2` |

## Verificare
- Pagina categorie: dropdown custom stilizat vizibil
- Click dropdown: deschide optiunile nativ (browser/OS)
- Schimba optiune: pagina se reincarca cu sortarea selectata
- Mobile: click deschide native picker

## Timp estimat
30 minute
