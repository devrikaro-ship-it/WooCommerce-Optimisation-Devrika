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

        # Find a product URL first
        await page.goto('https://puria.ro/caini/hrana-umeda/', wait_until='domcontentloaded')
        first_product = await page.evaluate("""() => {
            const a = document.querySelector('a.woocommerce-LoopProduct-link, .product-image-link, li.product a');
            return a ? a.href : null;
        }""")
        print(f'Test product URL: {first_product}')

        if not first_product:
            first_product = 'https://puria.ro/?p=90695'  # fallback by ID

        await page.goto(first_product, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)

        checks = await page.evaluate("""() => {
            // SKU
            const sku_el = document.querySelector('.sku_wrapper');
            const sku_visible = sku_el ? getComputedStyle(sku_el).display !== 'none' : false;

            // CTA button — find all buttons near add to cart
            const btns = document.querySelectorAll('button[name="add-to-cart"], .single_add_to_cart_button, [class*="add-to-cart"]');
            const btn_info = Array.from(btns).map(b => ({
                class: b.className.substring(0, 60),
                width: getComputedStyle(b).width,
                text: b.textContent.trim().substring(0, 30)
            }));

            // Related products
            const related_titles = Array.from(document.querySelectorAll('.related .product-title, .related h2.woocommerce-loop-product__title, .related .woocommerce-loop-product__title'))
                .map(el => el.textContent.trim().substring(0, 45));

            // Also try different selectors for related
            const related_links = Array.from(document.querySelectorAll('.related a.woocommerce-LoopProduct-link'))
                .map(a => a.href.split('/').filter(Boolean).pop());

            // Availability
            const avail = document.querySelector('.availability, .stock, [class*="availability"]');
            const avail_text = avail ? avail.textContent.trim() : 'not found';
            const avail_class = avail ? avail.className : '';

            // Reviews section
            const reviews_tab = document.querySelector('#tab-reviews, [href="#tab-reviews"], .reviews_tab');
            const review_form = document.querySelector('#review_form, #commentform');
            const review_count = document.querySelector('.woocommerce-Reviews-title');

            // Check CSS applied
            const style_tag = document.querySelector('#puria-product-ux');

            return {
                sku_visible,
                btns: btn_info,
                related_titles,
                related_links,
                avail_text,
                avail_class,
                has_reviews_tab: !!reviews_tab,
                has_review_form: !!review_form,
                review_count_text: review_count ? review_count.textContent : 'n/a',
                style_tag_present: !!style_tag,
                page_url: window.location.href
            };
        }""")

        print(f'\n=== Product UX verify: {checks["page_url"]} ===')
        print(f'Style tag present: {checks["style_tag_present"]}')
        print(f'SKU visible: {checks["sku_visible"]} (want False)')
        print(f'Availability: "{checks["avail_text"]}" (class: {checks["avail_class"][:50]})')
        print(f'Reviews tab: {checks["has_reviews_tab"]} | Review form: {checks["has_review_form"]}')
        print(f'Review title: {checks["review_count_text"]}')
        print(f'\nCTA buttons found:')
        for b in checks['btns']:
            print(f'  [{b["class"][:50]}] w={b["width"]} text="{b["text"]}"')
        print(f'\nRelated products (titles): {checks["related_titles"][:5]}')
        print(f'Related products (slugs): {checks["related_links"][:5]}')

        await browser.close()

asyncio.run(main())
