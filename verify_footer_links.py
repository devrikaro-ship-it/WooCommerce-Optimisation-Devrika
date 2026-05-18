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
        await page.goto('https://puria.ro/', wait_until='domcontentloaded')

        links = await page.evaluate("""() => {
            const footer = document.querySelector('section.elementor-element-77d01b66');
            if (!footer) return {error: 'footer not found'};
            const anchors = footer.querySelectorAll('a[href]');
            return Array.from(anchors).map(a => ({
                text: a.textContent.trim().substring(0, 40),
                href: a.getAttribute('href')
            }));
        }""")

        if isinstance(links, dict) and links.get('error'):
            print(f'Error: {links["error"]}')
        else:
            print(f'Footer links ({len(links)}):')
            for l in links:
                print(f'  {l["text"][:35]:35} -> {l["href"]}')

        # Check specific URLs
        print()
        for url in ['/pasari-rozatoare/', '/pasari-si-rozatoare/', '/promotii/', '/promotii-si-oferte/']:
            resp = await page.goto(f'https://puria.ro{url}', wait_until='domcontentloaded')
            print(f'{url}: HTTP {resp.status} (final: {resp.url})')

        await browser.close()

asyncio.run(main())
