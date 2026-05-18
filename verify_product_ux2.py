import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # Get first product URL from category
        await page.goto('https://puria.ro/caini/hrana-umeda/', wait_until='domcontentloaded')
        await page.wait_for_timeout(1000)

        urls = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/caini/"]');
            const found = [];
            for (const a of links) {
                const h = a.href;
                if (h.includes('/caini/') && !h.endsWith('/caini/') && !h.includes('?') && !h.includes('#')) {
                    found.push(h);
                }
                if (found.length >= 3) break;
            }
            return found;
        }""")
        print(f'Product URLs found: {urls}')

        product_url = urls[0] if urls else 'https://puria.ro/caini/hrana-umeda/bautura-umeda-caini-macs-paw-power-vita-200g-796-suc-carne-15-carne-vita-90695/'

        await page.goto(product_url, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        print(f'Testing: {page.url}')

        checks = await page.evaluate("""() => {
            const sku_el = document.querySelector('.sku_wrapper');
            const sku_display = sku_el ? getComputedStyle(sku_el).display : 'element_not_found';

            // All buttons
            const all_btns = Array.from(document.querySelectorAll('button, input[type=submit]'))
                .filter(b => b.offsetParent !== null)
                .map(b => ({
                    class: b.className.substring(0, 80),
                    width: getComputedStyle(b).width,
                    text: (b.textContent || b.value || '').trim().substring(0, 40)
                }))
                .filter(b => b.text.length > 0);

            // Related section — try all selectors
            const related_section = document.querySelector('.related, section.related, [class*="related"]');
            const related_html = related_section ? related_section.innerHTML.substring(0, 300) : 'NOT FOUND';
            const related_titles = Array.from(document.querySelectorAll('[class*="related"] [class*="title"], [class*="related"] h2'))
                .map(e => e.textContent.trim().substring(0, 50));

            // Availability
            const all_avail = Array.from(document.querySelectorAll('[class*="avail"], [class*="stock"], .in-stock, .out-of-stock'))
                .map(e => ({class: e.className.substring(0,50), text: e.textContent.trim().substring(0,60)}));

            // Reviews
            const comments_section = document.querySelector('#comments, #reviews, .woocommerce-Reviews, [id*="review"]');
            const review_form = document.querySelector('#commentform, #review_form, form[action*="comment"]');

            // Style tag
            const puria_style = document.querySelector('#puria-product-ux');

            return {
                sku_display,
                all_btns: all_btns.slice(0, 8),
                related_titles,
                related_html_preview: related_html,
                all_avail,
                has_comments: !!comments_section,
                has_review_form: !!review_form,
                style_tag: !!puria_style,
                is_product_page: document.body.classList.toString().includes('single-product')
            };
        }""")

        print(f'\nis_product page: {checks["is_product_page"]}')
        print(f'style tag #puria-product-ux: {checks["style_tag"]}')
        print(f'SKU display: "{checks["sku_display"]}"')
        print(f'Reviews section: {checks["has_comments"]} | Form: {checks["has_review_form"]}')
        print(f'\nAvailability elements: {checks["all_avail"]}')
        print(f'\nButtons:')
        for b in checks['all_btns']:
            print(f'  w={b["width"]:>8} | {b["text"][:40]} | class: {b["class"][:60]}')
        print(f'\nRelated titles: {checks["related_titles"][:6]}')
        if not checks["related_titles"]:
            print(f'Related HTML preview: {checks["related_html_preview"]}')

        await browser.close()

asyncio.run(main())
