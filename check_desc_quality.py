import asyncio
import json, re
from playwright.async_api import async_playwright

WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare'
WP_USER = 'vlad'
WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(WP_LOGIN, wait_until='networkidle')
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_url('**/wp-admin/**', timeout=15000)
        await page.goto('https://puria.ro/wp-admin/', wait_until='networkidle')

        # Get products from different offsets to sample variety
        samples = []
        for offset in [0, 100, 300, 500, 700, 850]:
            result = await page.evaluate(f"""async () => {{
                const nonce = window.wpApiSettings?.nonce || '';
                const res = await fetch('/wp-json/wc/v3/products?per_page=3&offset={offset}&orderby=id&order=asc&status=publish', {{
                    headers: {{'X-WP-Nonce': nonce}}
                }});
                return await res.text();
            }}""")
            batch = json.loads(result)
            if isinstance(batch, list):
                samples.extend(batch)

        print(f'Sample: {len(samples)} produse din pozitii variate\n')

        # Patterns that suggest AI-generated / low quality
        ai_patterns = [
            r'\b(premium|exceptional|de exceptie|superior|optim|perfect)\b',
            r'\b(bunastare|vitalitate|prosperare|binele)\b',
            r'(este o alegere|reprezinta o alegere|este alegerea)',
            r'(pentru (caini|pisici) (de toate|cu|care))',
        ]

        has_diacritics = lambda t: bool(re.search(r'[șțăîâ]', t))

        for prod in samples:
            name = prod.get('name', '?')[:60]
            desc_html = prod.get('description', '')
            desc = re.sub(r'<[^>]+>', ' ', desc_html).strip()
            desc = re.sub(r'\s+', ' ', desc)
            words = len(desc.split())

            # Count AI buzzwords
            ai_score = sum(len(re.findall(p, desc, re.IGNORECASE)) for p in ai_patterns)

            # Check diacritics
            has_diac = has_diacritics(desc)

            # Check repetitive openings
            sentences = [s.strip() for s in re.split(r'[.!?]', desc) if len(s.strip()) > 20]
            first_words = [' '.join(s.split()[:3]).lower() for s in sentences[:5]]

            print(f'--- ID {prod.get("id")} | {words}w ---')
            print(f'Titlu: {name}')
            print(f'Diacritice: {"DA" if has_diac else "NU"} | AI buzzwords: {ai_score}')
            print(f'Inceput: {desc[:200]}')
            print()

        await browser.close()

asyncio.run(main())
