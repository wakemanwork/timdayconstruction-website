// Generates vercel.json: redirect map (MIGRATION-BASELINE.md section 5), headers, image optimisation.
// Every old WordPress URL that isn't a page on the new site gets a 301. Re-run after content changes:
//   node scripts/redirects.mjs
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname;
const rest = async (n) => JSON.parse(await readFile(join(ROOT, 'capture/rest', `${n}.json`), 'utf8'));
const path = (u) => new URL(u).pathname;
const r = (source, destination, extra = {}) => ({ source, destination, statusCode: 301, ...extra });
const redirects = [];

// --- agreed moves (Phase 0 / fix log) ---
redirects.push(r('/placeholder-blog-post-6/', '/what-is-a-passive-house/'));            // F2
redirects.push(r('/author/:name/feed/', '/feed/'), r('/author/:name/', '/blog/'));         // F3
redirects.push(r('/category/uncategorized/feed/', '/feed/'), r('/category/uncategorized/', '/blog/'));
redirects.push(r('/category/:cat/feed/', '/feed/'));
redirects.push(r('/comments/feed/', '/feed/'), r('/feed/rss2/', '/feed/'), r('/feed/atom/', '/feed/'), r('/:slug/feed/', '/feed/'));

// --- WordPress behaviours that won't exist on a static site ---
redirects.push(r('/blog/page/:n/', '/blog/'), r('/page/:n/', '/blog/'));                   // F16
redirects.push(r('/:y(\\d{4})/', '/blog/'), r('/:y(\\d{4})/:m(\\d{2})/', '/blog/'), r('/:y(\\d{4})/:m(\\d{2})/:d(\\d{2})/', '/blog/'));
redirects.push(r('/search/:q*', '/'), r('/', '/', { has: [{ type: 'query', key: 's' }] }));
redirects.push(r('/index.php', '/'));
redirects.push(r('/sitemap.xml', '/sitemap_index.xml'), r('/wp-sitemap.xml', '/sitemap_index.xml'), r('/author-sitemap.xml', '/sitemap_index.xml'));
redirects.push(r('/privacy/', '/privacy-policy/'));                                        // probed: WP guessed this

// --- ?p=ID and ?page_id=ID links resolve to the item (WordPress does this) ---
const items = [...(await rest('posts')), ...(await rest('project')), ...(await rest('sector')), ...(await rest('testimonial'))];
for (const it of items) {
  let dest = path(it.link);
  if (dest === '/placeholder-blog-post-6/') dest = '/what-is-a-passive-house/';
  redirects.push(r('/', dest, { has: [{ type: 'query', key: 'p', value: String(it.id) }] }));
}
for (const pg of await rest('pages')) {
  redirects.push(r('/', path(pg.link), { has: [{ type: 'query', key: 'page_id', value: String(pg.id) }] }));
}

// --- bare slugs WordPress "guessed": /vet-shack/ -> /project/vet-shack/ etc. ---
const seen = new Set(['/']);
const pagePaths = new Set((await rest('pages')).map((p) => path(p.link)));
for (const it of [...(await rest('project')), ...(await rest('sector')), ...(await rest('testimonial')), ...(await rest('pages'))]) {
  const canon = path(it.link);
  const bare = `/${it.slug}/`;
  if (bare !== canon && !pagePaths.has(bare) && !seen.has(bare)) { redirects.push(r(bare, canon)); seen.add(bare); }
}

// --- attachment pages -> the file (Yoast behaviour) ---
for (const m of await rest('media')) {
  const from = path(m.link), to = path(m.source_url);
  if (from !== to && !seen.has(from)) { redirects.push(r(from, to)); seen.add(from); }
}

// --- trailing slash: WordPress 301s /about -> /about/ (Vercel's trailingSlash option would 308) ---
redirects.push(r('/:path((?!api/|api$|_vercel/|_astro/)(?:[^/.]+/)*[^/.]+)', '/:path/'));

const config = {
  $schema: 'https://openapi.vercel.sh/vercel.json',
  framework: 'astro',
  buildCommand: 'npm run build',
  outputDirectory: 'dist',
  cleanUrls: false,
  redirects,
  // Astro writes the RSS feed to /feed/index.xml; Vercel only auto-serves index.html for folder URLs
  rewrites: [{ source: '/feed/', destination: '/feed/index.xml' }],
  headers: [
    { source: '/feed/', headers: [{ key: 'Content-Type', value: 'application/rss+xml; charset=utf-8' }] },
    { source: '/feed/index.xml', headers: [{ key: 'Content-Type', value: 'application/rss+xml; charset=utf-8' }] },
    { source: '/_astro/(.*)', headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }] },
    { source: '/wp-content/(.*)', headers: [{ key: 'Cache-Control', value: 'public, max-age=2592000, stale-while-revalidate=86400' }] },
    { source: '/(.*)\\.md', headers: [{ key: 'Content-Type', value: 'text/markdown; charset=utf-8' }, { key: 'X-Robots-Tag', value: 'noindex' }] },
    { source: '/llms(-full)?\\.txt', headers: [{ key: 'Content-Type', value: 'text/plain; charset=utf-8' }] },
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
        { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
        { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
      ],
    },
  ],
  images: {
    sizes: [480, 768, 1080, 1440, 1920, 2560],
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 2678400,
    qualities: [75],
    localPatterns: [{ pathname: '^/wp-content/uploads/.*$', search: '' }],
  },
};
await writeFile(join(ROOT, 'vercel.json'), JSON.stringify(config, null, 2) + '\n');
console.log(`vercel.json: ${redirects.length} redirects`);
