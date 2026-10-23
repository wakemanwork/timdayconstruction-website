// Visual side-by-side: live baseline vs local build. Usage: node scripts/qa/compare.mjs /path/ [/path2/ ...]
// Needs the build served at http://localhost:4321 (npx serve dist / python http.server).
// Output: qa/compare/<slug>-<w>.png (live | new) and a pixel-diff % per width.
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import { mkdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
const LIVE = 'https://timdayconstruction.co.uk', LOCAL = process.env.LOCAL || 'http://localhost:4321';
const paths = process.argv.slice(2);
mkdirSync('qa/compare', { recursive: true });
const browser = await chromium.launch();
async function shot(base, path, w, out) {
  const ctx = await browser.newContext({ viewport: { width: w, height: w > 500 ? 900 : 844 } });
  const host = new URL(base).hostname;
  await ctx.addCookies([{ name: 'first_visit', value: 'true', domain: host, path: '/' }, { name: 'tdc_consent', value: 'rejected', domain: host, path: '/' }]);
  const p = await ctx.newPage();
  await p.goto(base + path, { waitUntil: 'networkidle', timeout: 90000 });
  await p.evaluate(async () => { const s = (ms) => new Promise((r) => setTimeout(r, ms)); for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await s(100); } window.scrollTo(0, 0); });
  await p.evaluate(() => { document.querySelectorAll('img').forEach((i) => { i.loading = 'eager'; if (i.dataset.src) i.src = i.dataset.src; }); document.querySelectorAll('[data-aos]').forEach((e) => e.classList.add('aos-animate')); document.querySelectorAll('.swiper').forEach((s) => s.swiper?.autoplay?.stop()); });
  await p.evaluate(async () => { await Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))); });
  // freeze carousels at slide 0 so both sides match
  await p.evaluate(() => document.querySelectorAll('.swiper').forEach((s) => { s.swiper?.autoplay?.stop(); s.swiper?.slideToLoop?.(0, 0); }));
  await p.evaluate(async () => { document.querySelectorAll('img').forEach((i) => { i.loading = 'eager'; }); await Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))); await Promise.all([...document.images].map((i) => i.decode().catch(() => 0))); });
  await p.addStyleTag({ content: '*{animation:none!important;transition:none!important} header{position:absolute!important}' });
  await p.waitForTimeout(600);
  await p.screenshot({ path: out, fullPage: true });
  await ctx.close();
}
for (const path of paths) {
  const slug = path.replace(/^\/|\/$/g, '').replace(/\//g, '__') || 'home';
  for (const w of (process.env.WIDTHS || '1440,390').split(',').map(Number)) {
    const a = `qa/compare/${slug}-${w}-live.png`, b = `qa/compare/${slug}-${w}-new.png`;
    if (!existsSync(a) || process.env.REFRESH) await shot(LIVE, path, w, a);
    await shot(LOCAL, path, w, b);
    const r = execFileSync('python3', ['-I', 'scripts/qa/sidebyside.py', a, b, `qa/compare/${slug}-${w}.png`]).toString().trim();
    console.log(`${path} @${w}: ${r}`);
  }
}
await browser.close();
