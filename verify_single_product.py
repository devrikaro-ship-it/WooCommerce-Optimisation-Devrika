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

        # Get a real single product URL from the category
        await page.goto('https://puria.ro/caini/hrana-umeda-caini/', wait_until='domcontentloaded')
        await page.wait_for_timeout(1000)

        product_url = await page.evaluate("""() => {
            // Find links that go to individual products (have more path segments)
            const links = document.querySelectorAll('a[href]');
            for (const a of links) {
                const h = a.href;
                const path = new URL(h).pathname;
                const segments = path.split('/').filter(Boolean);
                // Product URLs have 2+ segments and don't end with known patterns
                if (segments.length >= 2 && !path.endsWith('/caini/') &&
                    !h.includes('?') && !h.includes('#') &&
                    (h.includes('/hrana-') || h.includes('/bautura-') || h.includes('/snack-') || h.includes('/recompense-'))) {
                    return h;
                }
            }
            return null;
        }""")
        print(f'Product URL: {product_url}')

        if not product_url:
            # Use the URL from the screenshot directly
            product_url = 'https://puria.ro/caini/hrana-umeda-caini/bautura-umeda-caini-macs-paw-power-vita-200g-796-suc-carne-15-carne-vita-90695/'

        await page.goto(product_url, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        print(f'Loaded: {page.url}')

        result = await page.evaluate("""() => {
            const body_classes = document.body.className;
            const is_single = body_classes.includes('single-product');

            // CSS style tag
            const style_tag = !!document.querySelector('#puria-product-ux');

            // SKU
            const sku_el = document.querySelector('.sku_wrapper');
            const sku_display = sku_el ? getComputedStyle(sku_el).display : 'not_found';

            // CTA button
            const cta = document.querySelector('button[name="add-to-cart"], .single_add_to_cart_button');
            const cta_info = cta ? {
                text: cta.textContent.trim().substring(0,30),
                width: getComputedStyle(cta).width,
                class: cta.className.substring(0,80)
            } : null;

            // Availability / delivery
            const avail_els = document.querySelectorAll('.stock, .availability, [class*="stock"]');
            const avail_texts = Array.from(avail_els)
                .map(e => e.textContent.trim())
                .filter(t => t.length > 2 && t.length < 100);

            // Reviews / comments
            const reviews_tab = document.querySelector('.reviews_tab, [data-target="#tab-reviews"]');
            const review_form = document.querySelector('#commentform');
            const review_section = document.querySelector('#reviews, .woocommerce-Reviews');

            // Related products
            const related = document.querySelector('.related');
            const related_items = related ? Array.from(related.querySelectorAll('h2, .woocommerce-loop-product__title, [class*="title"]')).map(e => e.textContent.trim().substring(0,50)) : [];

            // Breadcrumb
            const bc = document.querySelector('.woocommerce-breadcrumb');
            const bc_text = bc ? bc.textContent.trim().substring(0,100) : 'not found';

            return {
                is_single, style_tag, sku_display,
                cta_info, avail_texts: avail_texts.slice(0,5),
                has_reviews_tab: !!reviews_tab,
                has_review_form: !!review_form,
                has_review_section: !!review_section,
                related_items: related_items.slice(0,6),
                bc_text, body_classes: body_classes.substring(0,100)
            };
        }""")

        print(f'\nbody classes: {result["body_classes"]}')
        print(f'is_single_product: {result["is_single"]}')
        print(f'style tag #puria-product-ux: {result["style_tag"]}')
        print(f'SKU display: "{result["sku_display"]}" (want: none)')
        print(f'CTA button: {result["cta_info"]}')
        print(f'Availability/delivery: {result["avail_texts"]}')
        print(f'Reviews tab: {result["has_reviews_tab"]} | form: {result["has_review_form"]} | section: {result["has_review_section"]}')
        print(f'Related products: {result["related_items"]}')
        print(f'Breadcrumb: {result["bc_text"]}')

        await browser.close()

asyncio.run(main())
