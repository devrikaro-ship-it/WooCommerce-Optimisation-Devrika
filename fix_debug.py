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

        # List all WPCode snippets
        result = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wpcode/v1/snippets?per_page=20&orderby=id&order=desc', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")
        print(f'Snippets API: {result["status"]}')

        # Try WP posts API for wpcode_snippet post type
        result2 = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            const res = await fetch('/wp-json/wp/v2/wpcode_snippet?per_page=10&orderby=id&order=desc', {
                headers: {'X-WP-Nonce': nonce}
            });
            return {status: res.status, body: await res.text()};
        }""")
        print(f'WPCode post type API: {result2["status"]}')

        # Navigate to WPCode list page and get snippet IDs
        await page.goto('https://puria.ro/wp-admin/admin.php?page=wpcode', wait_until='networkidle')
        snippets = await page.evaluate("""() => {
            const rows = document.querySelectorAll('tr[id^="post-"]');
            const results = [];
            rows.forEach(row => {
                const id = row.id.replace('post-', '');
                const titleEl = row.querySelector('.snippet-title a, .row-title');
                const title = titleEl?.innerText?.trim() || '';
                const activeEl = row.querySelector('.wpcode-status-toggle input');
                const active = activeEl?.checked;
                results.push({id, title, active});
            });
            return results;
        }""")
        print(f'\nWPCode snippets ({len(snippets)}):')
        for s in snippets:
            print(f'  ID {s["id"]} | Active: {s["active"]} | {s["title"][:60]}')

        # Check if llms.txt file exists via PHP check
        check = await page.evaluate("""async () => {
            const nonce = window.wpApiSettings?.nonce || '';
            // Check option to see if snippet ran
            const res = await fetch('/wp-admin/admin-ajax.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=wpcode_test'
            });
            return res.status;
        }""")

        # Try visiting admin to trigger admin_init again
        await page.goto('https://puria.ro/wp-admin/index.php', wait_until='networkidle')
        await page.wait_for_timeout(3000)

        # Check llms.txt
        llms = await page.evaluate("""async () => {
            const res = await fetch('/llms.txt', {cache: 'no-store'});
            return {status: res.status, body: (await res.text()).substring(0, 100)};
        }""")
        print(f'\nllms.txt after admin trigger: {llms["status"]} — {llms["body"][:80]}')

        # Check ItemList on caini page
        itemlist = await page.evaluate("""async () => {
            const res = await fetch('/caini/', {cache: 'no-store'});
            const html = await res.text();
            const hasItemList = html.includes('ItemList');
            const schemaCount = (html.match(/application\/ld\+json/g) || []).length;
            return {hasItemList, schemaCount};
        }""")
        print(f'ItemList on /caini/: {itemlist}')

        await browser.close()

asyncio.run(main())
