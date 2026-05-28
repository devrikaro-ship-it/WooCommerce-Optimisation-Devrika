const { chromium } = require('playwright');

const WP_URL = 'https://puria.ro';
const WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare';
const WP_USER = 'vlad';
const WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&';

// Mappings: WooCommerce category ID -> Google Product Category string
const CATEGORY_MAPPINGS = {
  // Caini - Hrana Uscata (ID 10836, 153 products)
  '10836': 'Animals & Pet Supplies > Pet Food > Dog Food > Dry Dog Food',
  // Caini - Hrana Umeda (ID 10837, 209 products)
  '10837': 'Animals & Pet Supplies > Pet Food > Dog Food > Wet Dog Food',
  // Caini - Recompense si Snackuri (ID 10840, 101 products)
  '10840': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Treats',
  // Caini - Suplimente si Vitamine (ID 10841, 64 products)
  '10841': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Health Supplies',
  // Caini - Cosmetica si Igiena (ID 10842, 41 products)
  '10842': 'Animals & Pet Supplies > Pet Supplies > Dog Supplies > Dog Grooming Supplies',
  // Pisici - Hrana Uscata (ID 10845, 66 products)
  '10845': 'Animals & Pet Supplies > Pet Food > Cat Food > Dry Cat Food',
  // Pisici - Hrana Umeda (ID 10846, 122 products)
  '10846': 'Animals & Pet Supplies > Pet Food > Cat Food > Wet Cat Food',
  // Pisici - Recompense si Snackuri (ID 10849, 10 products)
  '10849': 'Animals & Pet Supplies > Pet Supplies > Cat Supplies > Cat Treats',
};

async function run() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled']
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  console.log('Logging in...');
  await page.goto(WP_LOGIN, { waitUntil: 'networkidle' });
  await page.fill('#user_login', WP_USER);
  await page.fill('#user_pass', WP_PASS);
  await page.click('#wp-submit');
  await page.waitForURL('**/wp-admin/**', { timeout: 15000 });
  console.log('Logged in. URL:', page.url());

  // Navigate to admin page to get nonce
  await page.goto(`${WP_URL}/wp-admin/admin.php?page=wp-xml-feed`, { waitUntil: 'networkidle' });

  // Get current mapping
  const currentMapping = await page.evaluate(async () => {
    const nonce = window.wpApiSettings?.nonce || '';
    const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
      headers: { 'X-WP-Nonce': nonce }
    });
    const text = await res.text();
    return { status: res.status, body: text };
  });

  console.log('Current mapping status:', currentMapping.status);
  if (currentMapping.status !== 200) {
    console.log('Body:', currentMapping.body.substring(0, 500));
  }

  let existingMappings = {};
  try {
    const parsed = JSON.parse(currentMapping.body);
    existingMappings = parsed || {};
    console.log('Existing mapping keys:', Object.keys(existingMappings).length);
    console.log('Sample:', JSON.stringify(Object.entries(existingMappings).slice(0, 3)));
  } catch (e) {
    console.log('Parse error, raw:', currentMapping.body.substring(0, 300));
  }

  // Merge new mappings with existing
  const updatedMappings = { ...existingMappings };
  for (const [catId, gCategory] of Object.entries(CATEGORY_MAPPINGS)) {
    updatedMappings[catId] = gCategory;
    console.log(`Setting ${catId} -> ${gCategory}`);
  }

  // PUT updated mapping
  const putResult = await page.evaluate(async (mappings) => {
    const nonce = window.wpApiSettings?.nonce || '';
    const res = await fetch('/wp-json/ctxfeed/v1/category_mapping', {
      method: 'PUT',
      headers: {
        'X-WP-Nonce': nonce,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ feed_id: 2, mapping: mappings })
    });
    const text = await res.text();
    return { status: res.status, body: text };
  }, updatedMappings);

  console.log('\nPUT result status:', putResult.status);
  console.log('PUT result body:', putResult.body.substring(0, 500));

  // Try POST if PUT fails
  if (putResult.status !== 200) {
    console.log('\nTrying POST...');
    const postResult = await page.evaluate(async (mappings) => {
      const nonce = window.wpApiSettings?.nonce || '';
      const res = await fetch('/wp-json/ctxfeed/v1/category_mapping', {
        method: 'POST',
        headers: {
          'X-WP-Nonce': nonce,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ feed_id: 2, mapping: mappings })
      });
      const text = await res.text();
      return { status: res.status, body: text };
    }, updatedMappings);
    console.log('POST result status:', postResult.status);
    console.log('POST result body:', postResult.body.substring(0, 500));
  }

  // Verify: check a specific category in the mapping
  const verifyResult = await page.evaluate(async () => {
    const nonce = window.wpApiSettings?.nonce || '';
    const res = await fetch('/wp-json/ctxfeed/v1/category_mapping?feed_id=2', {
      headers: { 'X-WP-Nonce': nonce }
    });
    const text = await res.text();
    return { status: res.status, body: text };
  });

  console.log('\nVerification:');
  try {
    const parsed = JSON.parse(verifyResult.body);
    const checkIds = ['10836', '10837', '10845', '10846', '10840'];
    for (const id of checkIds) {
      console.log(`  ${id}: ${parsed[id] || '(not set)'}`);
    }
  } catch (e) {
    console.log('Verify raw:', verifyResult.body.substring(0, 300));
  }

  await browser.close();
}

run().catch(console.error);
