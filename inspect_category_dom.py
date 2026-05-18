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

        await page.goto('https://puria.ro/pisici/hrana-uscata/', wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)

        data = await page.evaluate("""() => {
            // Breadcrumb detection
            const bcSelectors = [
                '.woocommerce-breadcrumb',
                '[class*="breadcrumb"]',
                '[id*="breadcrumb"]',
                'nav[aria-label*="bread"]',
                '.breadcrumbs',
                '.breadcrumb',
                '[typeof="BreadcrumbList"]'
            ];
            const bcFound = {};
            for (const sel of bcSelectors) {
                const el = document.querySelector(sel);
                if (el) {
                    bcFound[sel] = {
                        class: el.className.substring(0,80),
                        text: el.textContent.trim().substring(0,60),
                        y: Math.round(el.getBoundingClientRect().top)
                    };
                }
            }

            // H1
            const h1 = document.querySelector('h1');
            const h1Data = h1 ? {
                class: h1.className.substring(0,60),
                text: h1.textContent.trim().substring(0,40),
                y: Math.round(h1.getBoundingClientRect().top)
            } : null;

            // Sort/ordering
            const sortSelectors = [
                '.woocommerce-ordering',
                '.woocommerce-ordering select',
                'form.woocommerce-ordering',
                '[class*="ordering"]',
                '[class*="sort"]',
                'select[name="orderby"]',
                '.product-count',
                '.woocommerce-result-count'
            ];
            const sortFound = {};
            for (const sel of sortSelectors) {
                const el = document.querySelector(sel);
                if (el) {
                    sortFound[sel] = {
                        tag: el.tagName,
                        class: el.className.substring(0,60),
                        display: getComputedStyle(el).display,
                        y: Math.round(el.getBoundingClientRect().top),
                        vis: el.offsetParent !== null
                    };
                }
            }

            // Body classes
            const bodyClasses = document.body.className.split(' ').filter(c => c.length > 0);

            // First 3 products - check their structure
            const products = Array.from(document.querySelectorAll('.etheme-product-grid-item')).slice(0,3);
            const productData = products.map(p => {
                const img = p.querySelector('img');
                const imgContainer = p.querySelector('.etheme-product-grid-image');
                return {
                    imgFit: img ? getComputedStyle(img).objectFit : 'no-img',
                    containerH: imgContainer ? Math.round(imgContainer.getBoundingClientRect().height) : -1,
                    containerW: imgContainer ? Math.round(imgContainer.getBoundingClientRect().width) : -1
                };
            });

            // Filter bar / AJAX filter area
            const filterAreas = document.querySelectorAll('[class*="filter"], [class*="toolbar"], .woocommerce-result-count, .yith-woo');
            const filterData = Array.from(filterAreas).slice(0,5).map(el => ({
                class: el.className.substring(0,60),
                y: Math.round(el.getBoundingClientRect().top)
            }));

            return {
                bcFound,
                h1: h1Data,
                sortFound,
                bodyClasses: bodyClasses.slice(0,20),
                products: productData,
                filterAreas: filterData
            };
        }""")

        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))

        await browser.close()

asyncio.run(main())
