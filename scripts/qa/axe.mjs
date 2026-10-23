// axe-core scan (WCAG 2 A/AA + best practice) of local build pages. Usage: node scripts/qa/axe.mjs / /about/ ...
import { chromium } from '/opt/npm-tools/node_modules/playwright/index.mjs';
import { readFileSync } from 'node:fs';
const axe = readFileSync(process.env.AXE || '/tmp/claude-0/-home-claude/ba82769c-2614-56c5-a373-51e20a4e55b0/scratchpad/axe/node_modules/axe-core/axe.min.js', 'utf8');
const LOCAL = process.env.LOCAL || 'http://localhost:4321';
const b = await chromium.launch();
let total = 0;
for (const w of [1440, 390]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 900 } });
  await ctx.addCookies([{ name: 'first_visit', value: 'true', domain: new URL(LOCAL).hostname, path: '/' }]);
  const p = await ctx.newPage();
  for (const u of process.argv.slice(2)) {
    await p.goto(LOCAL + u, { waitUntil: 'networkidle' });
    await p.addScriptTag({ content: axe });
    const v = await p.evaluate(async () => (await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'] })).violations.map((x) => ({ id: x.id, impact: x.impact, n: x.nodes.length, t: x.nodes.slice(0, 3).map((n) => n.target.join(' ') + ' :: ' + (n.failureSummary || '').split('\n')[1]) })));
    total += v.length;
    console.log(`${u} @${w}: ${v.length ? '' : 'no violations'}`);
    v.forEach((x) => console.log(`  ${x.id} [${x.impact}] x${x.n}\n    ${x.t.join('\n    ')}`));
  }
  await ctx.close();
}
await b.close();
process.exit(total ? 1 : 0);
