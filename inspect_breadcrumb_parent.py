import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1440, 'height': 900}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto('https://puria.ro/caini/', wait_until='domcontentloaded')
        await page.wait_for_timeout(2500)

        data = await page.evaluate("""() => {
            const bc = document.querySelector('.rank-math-breadcrumb');
            const h1 = document.querySelector('h1');

            function getAncestors(el, maxLevels) {
                const result = [];
                let cur = el;
                for (let i = 0; i < maxLevels && cur; i++) {
                    cur = cur.parentElement;
                    if (!cur) break;
                    result.push({
                        tag: cur.tagName,
                        id: cur.id || '',
                        class: cur.className.substring(0, 80),
                        y: Math.round(cur.getBoundingClientRect().top)
                    });
                }
                return result;
            }

            const bcAncestors = bc ? getAncestors(bc, 8) : [];
            const h1Ancestors = h1 ? getAncestors(h1, 8) : [];

            // Find common parent
            const bcElWidget = bc ? bc.closest('.elementor-element') : null;
            const h1ElWidget = h1 ? h1.closest('.elementor-element') : null;
            const sameParent = bcElWidget && h1ElWidget &&
                bcElWidget.parentElement === h1ElWidget.parentElement;

            // Sort form details
            const sortForm = document.querySelector('form.woocommerce-ordering');
            const sortSelect = document.querySelector('select.orderby, select[name="orderby"]');
            const sortStyle = sortSelect ? {
                display: getComputedStyle(sortSelect).display,
                border: getComputedStyle(sortSelect).border.substring(0,50),
                borderColor: getComputedStyle(sortSelect).borderColor,
                minWidth: getComputedStyle(sortSelect).minWidth,
                padding: getComputedStyle(sortSelect).padding,
                background: getComputedStyle(sortSelect).backgroundColor
            } : null;

            return {
                bcAncestors,
                h1Ancestors,
                sameParent,
                bcWidgetClass: bcElWidget ? bcElWidget.className.substring(0, 80) : null,
                h1WidgetClass: h1ElWidget ? h1ElWidget.className.substring(0, 80) : null,
                sortFormClass: sortForm ? sortForm.className : null,
                sortStyle
            };
        }""")

        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
