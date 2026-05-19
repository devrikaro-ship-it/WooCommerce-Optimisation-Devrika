const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const WP_LOGIN = 'https://puria.ro/wp-login.php?sgs-token=logare';
const WP_USER = 'vlad';
const WP_PASS = 'ZziLe@qpS!trOhII%6E#0pO&';
const SESSION_DIR = '/tmp/puria-session-js';


async function ensureLoggedIn(page) {
  await page.goto('https://puria.ro/wp-admin/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  if (page.url().includes('wp-admin') && !page.url().includes('login')) {
    console.log('Session OK — already logged in');
    return;
  }
  console.log('Logging in...');
  await page.goto(WP_LOGIN, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.click('#user_login');
  await page.type('#user_login', WP_USER, { delay: 80 });
  await page.waitForTimeout(300);
  await page.click('#user_pass');
  await page.type('#user_pass', WP_PASS, { delay: 80 });
  await page.waitForTimeout(400);
  await page.click('#wp-submit');
  await page.waitForTimeout(3000);
  try {
    await page.waitForURL('**/wp-admin/**', { timeout: 25000 });
  } catch {
    if (!page.url().includes('wp-admin')) throw new Error(`Login failed: ${page.url()}`);
  }
  console.log(`Logged in: ${page.url()}`);
}


async function saveCssSnippet(page, title, code) {
  await page.goto(
    'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
    { waitUntil: 'networkidle' }
  );
  await page.waitForTimeout(600);
  await page.evaluate(() => {
    for (const h of document.querySelectorAll('h3')) {
      if (h.textContent.includes('CSS')) { h.click(); return; }
    }
  });
  await page.waitForTimeout(800);
  const ti = await page.$('input[name="wpcode_snippet_title"]');
  if (ti) await ti.fill(title);
  await page.evaluate((c) => {
    const cm = document.querySelector('.CodeMirror');
    if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
    const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
    if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', { bubbles: true })); }
  }, code);
  await page.evaluate(() => {
    const cb = document.querySelector('input[name="wpcode_active"]');
    if (cb && !cb.checked) cb.click();
  });
  return page.evaluate(async ([c, t]) => {
    const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
    const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
    const fd = new FormData();
    fd.append('wpcode_snippet_title', t);
    fd.append('wpcode_snippet_type', 'css');
    fd.append('wpcode_snippet_code', c);
    fd.append('wpcode_active', '1');
    fd.append('wpcode_auto_insert', '1');
    fd.append('wpcode_auto_insert_location', 'site_wide_footer');
    fd.append('wpcode-save-snippet-nonce', nonce);
    fd.append('_wp_http_referer', httpRef);
    fd.append('button', 'publish');
    const res = await fetch(window.location.href, { method: 'POST', body: fd });
    const m = res.url.match(/snippet_id=(\d+)/);
    return { status: res.status, id: m ? m[1] : null };
  }, [code, title]);
}


async function saveJsSnippet(page, title, code) {
  await page.goto(
    'https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&custom=1',
    { waitUntil: 'networkidle' }
  );
  await page.waitForTimeout(600);
  await page.evaluate(() => {
    for (const h of document.querySelectorAll('h3')) {
      if (h.textContent.includes('JavaScript') || h.textContent.includes('JS')) { h.click(); return; }
    }
  });
  await page.waitForTimeout(800);
  const ti = await page.$('input[name="wpcode_snippet_title"]');
  if (ti) await ti.fill(title);
  await page.evaluate((c) => {
    const cm = document.querySelector('.CodeMirror');
    if (cm?.CodeMirror) { cm.CodeMirror.setValue(c); return; }
    const ta = document.querySelector('textarea[name="wpcode_snippet_code"]');
    if (ta) { ta.value = c; ta.dispatchEvent(new Event('input', { bubbles: true })); }
  }, code);
  await page.evaluate(() => {
    const cb = document.querySelector('input[name="wpcode_active"]');
    if (cb && !cb.checked) cb.click();
  });
  return page.evaluate(async ([c, t]) => {
    const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value || '';
    const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
    const fd = new FormData();
    fd.append('wpcode_snippet_title', t);
    fd.append('wpcode_snippet_type', 'js');
    fd.append('wpcode_snippet_code', c);
    fd.append('wpcode_active', '1');
    fd.append('wpcode_auto_insert', '1');
    fd.append('wpcode_auto_insert_location', 'site_wide_footer');
    fd.append('wpcode-save-snippet-nonce', nonce);
    fd.append('_wp_http_referer', httpRef);
    fd.append('button', 'publish');
    const res = await fetch(window.location.href, { method: 'POST', body: fd });
    const m = res.url.match(/snippet_id=(\d+)/);
    return { status: res.status, id: m ? m[1] : null };
  }, [code, title]);
}


async function deactivateSnippet(page, snippetId) {
  const url = `https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id=${snippetId}`;
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });
    await page.waitForTimeout(600);
    const result = await page.evaluate(async () => {
      const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value;
      if (!nonce) return { error: 'no nonce - session expired?', url: window.location.href };
      const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
      const title = document.querySelector('input[name="wpcode_snippet_title"]')?.value || '';
      const cm = document.querySelector('.CodeMirror');
      const code = cm?.CodeMirror ? cm.CodeMirror.getValue()
        : (document.querySelector('textarea[name="wpcode_snippet_code"]')?.value || '');
      let snipType = 'css';
      for (const inp of document.querySelectorAll('input[name="wpcode_snippet_type"]')) {
        if (inp.checked) { snipType = inp.value; break; }
      }
      const fd = new FormData();
      fd.append('wpcode_snippet_title', title);
      fd.append('wpcode_snippet_type', snipType);
      fd.append('wpcode_snippet_code', code);
      fd.append('wpcode_auto_insert', '0');
      fd.append('wpcode_auto_insert_location', 'site_wide_footer');
      fd.append('wpcode-save-snippet-nonce', nonce);
      fd.append('_wp_http_referer', httpRef);
      fd.append('button', 'publish');
      const res = await fetch(window.location.href, { method: 'POST', body: fd });
      return { status: res.status, url: res.url.substring(0, 80) };
    });
    console.log(`[${snippetId}] deactivated:`, result);
    return result;
  } catch (e) {
    console.log(`[${snippetId}] ERROR:`, e.message);
    return null;
  }
}


async function activateSnippet(page, snippetId) {
  const url = `https://puria.ro/wp-admin/admin.php?page=wpcode-snippet-manager&snippet_id=${snippetId}`;
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });
    await page.waitForTimeout(600);
    const result = await page.evaluate(async () => {
      const nonce = document.querySelector('#wpcode-save-snippet-nonce')?.value;
      if (!nonce) return { error: 'no nonce', url: window.location.href };
      const httpRef = document.querySelector('input[name="_wp_http_referer"]')?.value || '';
      const title = document.querySelector('input[name="wpcode_snippet_title"]')?.value || '';
      const cm = document.querySelector('.CodeMirror');
      const code = cm?.CodeMirror ? cm.CodeMirror.getValue()
        : (document.querySelector('textarea[name="wpcode_snippet_code"]')?.value || '');
      let snipType = 'css';
      for (const inp of document.querySelectorAll('input[name="wpcode_snippet_type"]')) {
        if (inp.checked) { snipType = inp.value; break; }
      }
      const fd = new FormData();
      fd.append('wpcode_snippet_title', title);
      fd.append('wpcode_snippet_type', snipType);
      fd.append('wpcode_snippet_code', code);
      fd.append('wpcode_active', '1');
      fd.append('wpcode_auto_insert', '1');
      fd.append('wpcode_auto_insert_location', 'site_wide_footer');
      fd.append('wpcode-save-snippet-nonce', nonce);
      fd.append('_wp_http_referer', httpRef);
      fd.append('button', 'publish');
      const res = await fetch(window.location.href, { method: 'POST', body: fd });
      return { status: res.status, url: res.url.substring(0, 80) };
    });
    console.log(`[${snippetId}] activated:`, result);
    return result;
  } catch (e) {
    console.log(`[${snippetId}] ERROR:`, e.message);
    return null;
  }
}


async function verifySite(page, path = '/caini/') {
  await page.goto(`https://puria.ro${path}?nocache=1`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(4000);
  const check = await page.evaluate(() => {
    const imgs = Array.from(document.querySelectorAll(
      '.etheme-product-grid-item .etheme-product-grid-image img'
    )).slice(0, 4);
    return {
      title: document.title.substring(0, 60),
      h1: document.querySelector('h1')?.textContent.trim().substring(0, 40) || 'NOT FOUND',
      imgs: imgs.map(i => ({
        fit: getComputedStyle(i).objectFit,
        w: Math.round(i.getBoundingClientRect().width),
        h: Math.round(i.getBoundingClientRect().height),
      })),
    };
  });
  console.log(`\n--- ${path} ---`);
  console.log(`Title: ${check.title}`);
  console.log(`H1: ${check.h1}`);
  check.imgs.forEach((img, i) => {
    const ok = img.fit === 'contain' ? 'OK' : 'FAIL';
    console.log(`  img[${i}] ${ok} fit=${img.fit} ${img.w}x${img.h}px`);
  });
  return check;
}


async function main() {
  // Clean stale Singleton locks
  if (fs.existsSync(SESSION_DIR)) {
    fs.readdirSync(SESSION_DIR)
      .filter(f => f.startsWith('Singleton'))
      .forEach(f => { try { fs.unlinkSync(path.join(SESSION_DIR, f)); } catch {} });
  }

  const context = await chromium.launchPersistentContext(SESSION_DIR, {
    headless: false,
    args: ['--disable-blink-features=AutomationControlled'],
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
  });
  await context.addInitScript("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})");
  const page = context.pages()[0] || await context.newPage();

  await ensureLoggedIn(page);

  // --- adaugă operații noi de la această linie în jos ---

  await verifySite(page, '/caini/');

  // ---

  await context.close();
}

main().catch(console.error);
