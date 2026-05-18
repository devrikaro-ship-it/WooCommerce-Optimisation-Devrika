import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # Test multiple category URLs to find working ones
        test_urls = [
            'https://puria.ro/pisici/',
            'https://puria.ro/caini/',
            'https://puria.ro/product-category/pisici/',
            'https://puria.ro/product-category/caini/',
        ]

        for url in test_urls:
            await page.goto(url, wait_until='domcontentloaded')
            await page.wait_for_timeout(1500)
            result = await page.evaluate("""() => ({
                url: window.location.href,
                bodyClasses: document.body.className.split(' ').slice(0, 10),
                h1: (document.querySelector('h1') || {}).textContent?.trim().substring(0,30) || 'none',
                productCount: document.querySelectorAll('.etheme-product-grid-item').length
            })""")
            print(f"URL: {result['url']}")
            print(f"  Body: {result['bodyClasses'][:5]}")
            print(f"  H1: {result['h1']}")
            print(f"  Products: {result['productCount']}")
            print()

        # Use the page with products
        await page.goto('https://puria.ro/caini/', wait_until='domcontentloaded')
        await page.wait_for_timeout(2500)

        final_url = await page.evaluate("() => window.location.href")
        print(f"\nFinal URL: {final_url}")

        data = await page.evaluate("""() => {
            // Breadcrumb detection
            const breadcrumbSelectors = [
                '.woocommerce-breadcrumb',
                '.rank-math-breadcrumb',
                '[class*="breadcrumb"]',
                'nav[aria-label*="bread"]',
                '.breadcrumbs',
                '[typeof="BreadcrumbList"]'
            ];
            const bcFound = {};
            for (const sel of breadcrumbSelectors) {
                const el = document.querySelector(sel);
                if (el) {
                    bcFound[sel] = {
                        class: el.className.substring(0,60),
                        text: el.textContent.trim().substring(0,50),
                        y: Math.round(el.getBoundingClientRect().top)
                    };
                }
            }

            // H1
            const h1 = document.querySelector('h1');

            // Sort
            const sortEls = {};
            const sortSels = [
                'form.woocommerce-ordering',
                '.woocommerce-ordering',
                'select[name="orderby"]',
                '[class*="sort"]',
                '[class*="toolbar"]',
                '.et-shop-sort',
                '.ordering'
            ];
            for (const sel of sortSels) {
                const el = document.querySelector(sel);
                if (el) {
                    sortEls[sel] = {
                        tag: el.tagName,
                        class: el.className.substring(0,60),
                        display: getComputedStyle(el).display,
                        y: Math.round(el.getBoundingClientRect().top),
                        html: el.outerHTML.substring(0,100)
                    };
                }
            }

            // Images on category page
            const imgs = Array.from(document.querySelectorAll('.etheme-product-grid-item .etheme-product-grid-image img')).slice(0,4);
            const imgData = imgs.map(img => ({
                fit: getComputedStyle(img).objectFit,
                pad: getComputedStyle(img).padding,
                dw: Math.round(img.getBoundingClientRect().width),
                dh: Math.round(img.getBoundingClientRect().height)
            }));

            // SEO text
            const seoSels = ['.category-seo-sec', '.category-description', '.term-description', '[class*="seo"]'];
            const seoFound = {};
            for (const sel of seoSels) {
                const el = document.querySelector(sel);
                if (el) seoFound[sel] = { y: Math.round(el.getBoundingClientRect().top), text: el.textContent.trim().substring(0,40) };
            }

            const bodyClasses = document.body.className.split(' ').filter(c => c.length);

            return {
                bcFound,
                h1: h1 ? { text: h1.textContent.trim().substring(0,30), y: Math.round(h1.getBoundingClientRect().top), class: h1.className.substring(0,60) } : null,
                sortEls,
                imgData,
                seoFound,
                bodyClasses: bodyClasses.slice(0,20),
                productCount: document.querySelectorAll('.etheme-product-grid-item').length
            };
        }""")

        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))

        await browser.close()

asyncio.run(main())
