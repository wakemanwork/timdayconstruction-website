// RSS 2.0 at /feed/ (MIGRATION-BASELINE.md section 2: "/feed/ kept (all posts)").
// Lands in dist as /feed/index.xml. Vercel only serves index.html for a directory URL, so /feed/
// needs a rewrite to /feed/index.xml plus a Content-Type header (requested for scripts/redirects.mjs).
// Structure follows capture/extras/feed (the WordPress feed): channel title/link/description,
// atom:link self, lastBuildDate, image, then one item per post with dc:creator, guid, description
// and content:encoded. GUIDs keep WordPress's ?p=<id> so feed readers don't show old posts as new.
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import posts from '../../data/pages/posts.json';
import { SITE, website } from '../../lib/seo';

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const cdata = (s: string) => `<![CDATA[${s.replace(/]]>/g, ']]]]><![CDATA[>')}]]>`;
// Frontmatter dates are UTC wall-clock without a zone (see components/blog/PostDate.astro)
const asUtc = (x: Date) => new Date(Date.UTC(x.getFullYear(), x.getMonth(), x.getDate(), x.getHours(), x.getMinutes(), x.getSeconds()));
const rfc822 = (d: Date) => d.toUTCString().replace('GMT', '+0000');
// Same render-time corrections as src/pages/[slug].astro (one-item <ol> artefacts, dev-host link)
const tidy = (html: string) => html
  .replace(/<ol(?: start="(\d+)")?>\s*<li>([\s\S]*?)<\/li>\s*<\/ol>/g, (_m, n, t) => `<p>${n ?? 1}. ${t}</p>`)
  .replace(/https?:\/\/tim-day\.local\//g, '/');
const absolutise = (html: string) => tidy(html).replace(/(href|src)="\/(?!\/)/g, `$1="${SITE}/`);

export const GET: APIRoute = async () => {
  const entries = (await getCollection('posts')).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
  const meta = posts as Record<string, { guid: string; description: string }>;
  const site = website();
  const lastBuild = entries.map((e) => asUtc(e.data.modified)).sort((a, b) => b.getTime() - a.getTime())[0];

  const items = entries.map((e) => {
    const d = e.data;
    const url = `${SITE}/${d.slug}/`;
    return `	<item>
		<title>${esc(d.title.trim())}</title>
		<link>${url}</link>
		<dc:creator>${cdata(d.author)}</dc:creator>
		<pubDate>${rfc822(asUtc(d.date))}</pubDate>
		<guid isPermaLink="false">${esc(meta[d.slug].guid)}</guid>
		<description>${cdata(meta[d.slug].description)}</description>
		<content:encoded>${cdata(absolutise(e.rendered?.html ?? ''))}</content:encoded>
	</item>`;
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
	<title>${esc(site.name)}</title>
	<atom:link href="${SITE}/feed/" rel="self" type="application/rss+xml" />
	<link>${SITE}/</link>
	<description>${esc(site.description)}</description>
	<lastBuildDate>${rfc822(lastBuild)}</lastBuildDate>
	<language>en-GB</language>
	<image>
		<url>${SITE}/wp-content/uploads/2024/12/cropped-favicon-32x32.png</url>
		<title>${esc(site.name)}</title>
		<link>${SITE}/</link>
		<width>32</width>
		<height>32</height>
	</image>
${items.join('\n')}
</channel>
</rss>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
