# CLAUDE.md: timdayconstruction.co.uk

Static Astro site for Tim Day Construction (Canterbury, Kent), deployed on Vercel from this repo. It was migrated from WordPress in October 2026. Edits are made by Claude and git only; there is no CMS.

## Read before changing anything

| File | Read it when |
|---|---|
| `docs/DESIGN.md` | Any change to layout, styling, components or images. **Protected:** build new pages only from its tokens and components. If something new is genuinely needed, add it to DESIGN.md (with a changelog line) first. |
| `docs/VOICE.md` | Writing or editing any copy: pages, posts, projects, FAQs, meta titles and descriptions. Run its pre-publish checklist. |
| `docs/MIGRATION-BASELINE.md` | Anything touching URLs, redirects, SEO, schema or the original WordPress behaviour. Contains the URL inventory, redirect map and numbered fix log (F1–F22) with decisions. |
| `docs/CUTOVER.md` | DNS, domains, SSL, go-live or rollback (written in Phase 4). |

## Non-negotiables

1. **URLs never change.** Trailing slashes always (`trailingSlash: "always"`, `build.format: "directory"`). If a page must move, add a 301 and record it in MIGRATION-BASELINE.md section 5.
2. **Uploads stay at `/wp-content/uploads/…`.** Old links, OG images and Google Images point there. Never rename or move files in `public/wp-content/`.
3. **Content is never retyped.** Converted copy came from scripts; edits are surgical. Client quotes are verbatim and never invented. Facts about projects, clients and accreditations come from TDC, not from Claude.
4. **Every indexable page** has a unique title (within 60 characters), a meta description (140–155 characters), a canonical, OG and Twitter tags, JSON-LD, and exactly one H1. FAQ sections emit FAQPage schema.
5. **Postbuild outputs stay intact:** Yoast-path sitemaps (`/sitemap_index.xml` plus children), `/feed/`, `/llms.txt`, `/llms-full.txt` and a `.md` twin of every page.
6. **Markdown for agents** is served by Routing Middleware (`middleware.js`) for `?output_format=md` and `Accept: text/markdown`. Not `vercel.json` rewrites: static files win over rewrites on Vercel. Test on a real Vercel preview.
7. **Analytics only after consent.** GA4 (`GT-577ZJN8M`) and VisitorQueue load only once the visitor has accepted in the consent banner. Any new third-party script needs a cookie-policy update.
8. **Targets:** Lighthouse 95+ performance and 100 accessibility, best practices and SEO, on mobile, for every template. Don't merge a change that drops a template below them.
9. **Never touch email DNS.** MX, SPF, DKIM and DMARC at IONOS are out of scope for website work.

## Common tasks

- **New blog post:** add `src/content/posts/<slug>.md` with frontmatter (title, slug, date, description, featuredImage, categories, author "Tim Day Construction"). Follow VOICE.md's blog pattern and add internal links to a sector or service page and a project.
- **New project:** add `src/content/projects/<slug>.md` (title, location, client, typeOfWork, architect?, status, categories, gallery[], quote?, description). It appears automatically on the portfolio, its sector and its category archive pages.
- **New page:** compose from existing components in `src/components/`. No one-off CSS.
- **Images:** put originals in `public/wp-content/uploads/YYYY/MM/` (new uploads use the current year/month) and reference them through the image component so AVIF/WebP and `srcset` are generated.

## Checks before committing

Runtime: **Node 24** (Astro 7 needs ≥22.23; Vercel uses Node 24 via `engines`). Serve `dist/` locally (for example `npx serve dist -l 4321`) for the QA scripts.

- `npm run build`: Astro build, then `scripts/postbuild.mjs` (markdown twins, Yoast-path sitemaps, llms.txt, llms-full.txt).
- `npm run redirects`: regenerates `vercel.json` (redirect map, headers, image optimisation). Run it after adding or removing pages.
- `npm run check:text`: word-level diff of every built page against the WordPress capture. Unexpected differences fail.
- `npm run check:a11y -- / /about/`: axe at 1440 and 390. Must report no violations.
- `npm run check:visual -- /about/`: live vs new screenshots side by side in `qa/compare/`, with pixel-diff %.
- `scripts/qa/lighthouse.sh <base> /path/`: mobile and desktop scores. Run it against the Vercel preview, because local numbers miss Vercel image optimisation and caching.

## How the build works (gotchas)

- **CSS is a port, not a rewrite.** `src/styles/theme/*.css` is the live theme's `style.css` split by component with colours tokenised (`scripts/port_css.py`). Agreed deviations live in `src/styles/overrides.css` or in a component's own `<style>` with a comment citing the decision. Don't edit values in `theme/`.
- **The live home page is served an older build of the theme CSS** (SiteGround bundle `13f6a833`) for `#hero.new`. `HomeHero.astro` matches what visitors saw. Everywhere else `style.css` and the served bundles agree.
- **Images:** originals stay in `public/wp-content/uploads/`. `<Img>` emits `/_vercel/image` srcsets on Vercel (AVIF/WebP) and plain originals locally. Width and height come from `src/data/image-sizes.json` (`npm run image-sizes` after adding images). Alt text lives in `src/data/alt-text.json`.
- **Content** in `src/content/` and `src/data/` was generated by `scripts/extract.py` from `capture/`. After launch, edit the markdown and JSON directly; never re-run extract over edited content.
- **Markup mirrors the WordPress theme's classes** so the ported CSS applies. Headings may change level for accessibility, but then the old selector's styles are copied for the new tag.

## Repo map

- `capture/`: frozen snapshot of the WordPress site (HTML, markdown, REST JSON, screenshots, computed CSS, axe report, redirect probe). Reference only; don't edit.
- `docs/`: the guides above.
- `public/wp-content/`: mirrored WordPress uploads and theme images at their original paths.
- `src/`: the Astro site (Phase 3).
