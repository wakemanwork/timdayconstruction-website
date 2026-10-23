// Postbuild (CLAUDE.md non-negotiable 5). Runs after `astro build` on dist/:
//  1. A markdown twin of every page: /about/ -> /about.md, / -> /index.md (served to agents by middleware.js)
//  2. Yoast-path XML sitemaps: /sitemap_index.xml + post/page/project/sector/testimonial/category children
//  3. /llms.txt (index) and /llms-full.txt (every page's markdown)
// Lastmod comes from content frontmatter (modified), else the WordPress REST capture, else build time.
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import TurndownService from 'turndown';

const ROOT = new URL('..', import.meta.url).pathname;
const DIST = join(ROOT, 'dist');
const SITE = 'https://timdayconstruction.co.uk';
const now = new Date().toISOString();

// ---------- collect built pages ----------
async function walk(dir, out = []) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    if (['wp-content', '_astro', '_vercel'].includes(e.name)) continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) await walk(p, out);
    else if (e.name === 'index.html') out.push(p);
  }
  return out;
}
const files = await walk(DIST);
const pages = [];
for (const f of files) {
  const html = await readFile(f, 'utf8');
  const path = f.slice(DIST.length).replace(/index\.html$/, '');
  const get = (re) => html.match(re)?.[1]?.replace(/&amp;/g, '&').replace(/&#39;/g, '’').replace(/&quot;/g, '"');
  pages.push({
    path, html,
    title: get(/<title>([^<]*)<\/title>/),
    description: get(/<meta name="description" content="([^"]*)"/),
    noindex: /<meta name="robots" content="noindex/.test(html),
    modified: get(/<meta property="article:modified_time" content="([^"]+)"/),
  });
}

// ---------- lastmod sources ----------
async function frontmatterDates(dir, key = (slug) => slug) {
  const map = {};
  try {
    for (const f of await readdir(join(ROOT, 'src/content', dir))) {
      const t = await readFile(join(ROOT, 'src/content', dir, f), 'utf8');
      const m = t.match(/^modified: "?([^"\n]+)"?/m);
      if (m) map[key(f.replace(/\.md$/, ''))] = new Date(m[1] + (m[1].endsWith('Z') ? '' : 'Z')).toISOString();
    }
  } catch { /* collection not present */ }
  return map;
}
const lastmod = {
  ...(await frontmatterDates('posts', (s) => `/${s}/`)),
  ...(await frontmatterDates('projects', (s) => `/project/${s}/`)),
  ...(await frontmatterDates('sectors', (s) => `/sector/${s}/`)),
  ...(await frontmatterDates('testimonials', (s) => `/testimonial/${s}/`)),
};
try {
  const wpPages = JSON.parse(await readFile(join(ROOT, 'capture/rest/pages.json'), 'utf8'));
  for (const p of wpPages) {
    const path = new URL(p.link).pathname;
    lastmod[path] ??= new Date(p.modified + 'Z').toISOString();
  }
} catch { /* no capture */ }
const postSlugs = new Set(Object.keys(await frontmatterDates('posts', (s) => `/${s}/`)));

// ---------- 1. markdown twins ----------
const td = new TurndownService({ headingStyle: 'atx', bulletListMarker: '-', codeBlockStyle: 'fenced' });
td.remove(['script', 'style', 'noscript', 'svg', 'form', 'button']);
td.addRule('images', {
  filter: 'img',
  replacement: (_c, n) => {
    const alt = n.getAttribute('alt') || '';
    if (!alt) return ''; // decorative
    let src = n.getAttribute('src') || '';
    if (src.startsWith('/_vercel/image')) src = decodeURIComponent(src.split('url=')[1].split('&')[0]);
    return `![${alt.replace(/ \(opens in a new tab\)$/, '')}](${abs(src)})`;
  },
});
td.addRule('absLinks', {
  filter: (n) => n.nodeName === 'A' && n.getAttribute('href'),
  replacement: (c, n) => (c.trim() ? `[${c.trim()}](${abs(n.getAttribute('href'))})` : ''),
});
function abs(u) { return !u ? '' : u.startsWith('http') || u.startsWith('mailto:') || u.startsWith('tel:') ? u : SITE + u; }
function mainOf(html) {
  const m = html.match(/<main[^>]*>([\s\S]*)<\/main>/);
  return (m ? m[1] : '').replace(/<(script|style)[\s\S]*?<\/\1>/g, '').replace(/<[^>]+class="[^"]*sr-only[^"]*"[^>]*>[\s\S]*?<\/[^>]+>/g, '');
}
const mdPages = [];
for (const p of pages) {
  const body = td.turndown(mainOf(p.html)).replace(/\n{3,}/g, '\n\n').trim();
  const url = SITE + p.path;
  const md = `---\ntitle: ${JSON.stringify(p.title ?? '')}\nurl: ${url}\n${p.description ? `description: ${JSON.stringify(p.description)}\n` : ''}---\n\n${body}\n`;
  const mdPath = p.path === '/' ? '/index.md' : p.path.replace(/\/$/, '') + '.md';
  await writeFile(join(DIST, mdPath), md);
  if (!p.noindex && p.path !== '/404/') mdPages.push({ ...p, mdPath, md });
}

// ---------- 2. sitemaps at Yoast paths ----------
const groups = { post: [], page: [], project: [], sector: [], testimonial: [], category: [] };
for (const p of pages) {
  if (p.noindex || p.path === '/404/') continue;
  const g = p.path.startsWith('/project/') ? 'project'
    : p.path.startsWith('/sector/') ? 'sector'
    : p.path.startsWith('/testimonial/') ? 'testimonial'
    : p.path.startsWith('/category/') ? 'category'
    : postSlugs.has(p.path) ? 'post' : 'page';
  groups[g].push({ loc: SITE + p.path, lastmod: lastmod[p.path] ?? p.modified ?? now });
}
const xml = (body) => `<?xml version="1.0" encoding="UTF-8"?>\n${body}\n`;
const index = [];
for (const [g, urls] of Object.entries(groups)) {
  if (!urls.length) continue;
  urls.sort((a, b) => (a.loc === SITE + '/' ? -1 : b.loc === SITE + '/' ? 1 : b.lastmod.localeCompare(a.lastmod)));
  await writeFile(join(DIST, `${g}-sitemap.xml`), xml(`<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map((u) => `  <url><loc>${u.loc}</loc><lastmod>${u.lastmod}</lastmod></url>`).join('\n')}\n</urlset>`));
  index.push({ loc: `${SITE}/${g}-sitemap.xml`, lastmod: urls.map((u) => u.lastmod).sort().at(-1) });
}
await writeFile(join(DIST, 'sitemap_index.xml'), xml(`<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${index.map((s) => `  <sitemap><loc>${s.loc}</loc><lastmod>${s.lastmod}</lastmod></sitemap>`).join('\n')}\n</sitemapindex>`));

// ---------- 3. llms.txt / llms-full.txt ----------
const section = (title, filter) => {
  const items = mdPages.filter(filter).sort((a, b) => a.path.localeCompare(b.path));
  return items.length ? `## ${title}\n\n${items.map((p) => `- [${(p.title ?? p.path).replace(/ [|-] (Tim Day Construction|Building Contractor.*)$/, '')}](${SITE}${p.mdPath})${p.description ? `: ${p.description}` : ''}`).join('\n')}\n` : '';
};
const isPost = (p) => postSlugs.has(p.path);
const llms = `# Tim Day Construction

> Building contractor based near Canterbury, Kent, delivering ‘concept to completion’ construction and project management. Specialists in veterinary and clinical fit-outs and in residential new builds across Kent (Canterbury, Whitstable, Herne Bay, Faversham, Ashford, Thanet). FMB member, NHBC registered builder, SMAS Worksafe accredited and Certified Passive House Tradesperson.

Contact: 01227 281 749 · info@timdayconstruction.co.uk · ${SITE}/contact/

Every page is also available as markdown: add \`.md\` to the path (for example ${SITE}/about.md), send \`Accept: text/markdown\`, or add \`?output_format=md\`. The full site in one file: ${SITE}/llms-full.txt

${section('Key pages', (p) => !isPost(p) && !/^\/(project|sector|testimonial|category|locations)\//.test(p.path))}
${section('Services and sectors', (p) => p.path.startsWith('/sector/'))}
${section('Locations', (p) => p.path.startsWith('/locations/'))}
${section('Projects', (p) => p.path.startsWith('/project/'))}
${section('Articles', isPost)}
${section('Client testimonials', (p) => p.path.startsWith('/testimonial/'))}
## Optional

${section('Project categories', (p) => p.path.startsWith('/category/')).replace(/^## .*\n\n/, '')}`.replace(/\n{3,}/g, '\n\n');
await writeFile(join(DIST, 'llms.txt'), llms);
await writeFile(join(DIST, 'llms-full.txt'), `# Tim Day Construction: full site content\n\nSource: ${SITE}/ · Generated ${now}\n\n` + mdPages.map((p) => p.md.replace(/^---[\s\S]*?---\n/, `\n\n---\n\n# ${p.title}\n\nURL: ${SITE}${p.path}\n`)).join('\n'));

console.log(`postbuild: ${pages.length} pages, ${mdPages.length} markdown twins indexed, sitemaps: ${index.map((i) => i.loc.split('/').pop()).join(', ')}`);
