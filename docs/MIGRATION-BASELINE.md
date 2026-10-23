# Migration baseline: timdayconstruction.co.uk

WordPress (SiteGround) → static Astro on Vercel. Captured 23 October 2026 from the public site and REST API (no WordPress admin access, per Phase 0 decision 7).

## 1. Summary

| | |
|---|---|
| Live host | SiteGround (A 35.214.58.37, TTL 300) |
| DNS + email | IONOS nameservers (`ns1050.ui-dns.*`), MX `mx00/mx01.ionos.co.uk`. TDC holds the login |
| Theme | `tim-day-custom-theme` v1.0 by The Digital Lookout. Hand-written CSS (`style.css`, 3,963 lines), no page builder |
| Content | 13 posts, 13 pages, 14 projects, 5 sectors, 5 testimonials, 7 categories (posts all in Uncategorized; the other 6 tag projects), 3 authors, 0 tags |
| Sitemap URLs | 60 (Yoast: post, page, project, sector, testimonial, category, author sitemaps) |
| Media | 186 library items; 1,108 upload files (102 MB) incl. all generated sizes, mirrored at original `/wp-content/uploads/` paths |
| Capture location | `capture/` (html, meta+JSON-LD, markdown, REST JSON, screenshots, computed styles, axe report, redirect probe) |

## 2. What the site does under the hood, and how each function carries over

| Function | Today (WordPress) | In Astro / Vercel |
|---|---|---|
| Pages, posts, projects, sectors, testimonials | Custom post types + ACF (ACF **not** exposed in REST, so the rendered HTML is the source of truth) | Content collections (markdown + frontmatter) for posts, projects, sectors, testimonials; `.astro` pages for one-off pages |
| SEO meta, canonicals, OG, Twitter | Yoast | Per-page frontmatter → shared `<SEO>` component. Titles/descriptions copied verbatim, gaps filled per fix log |
| JSON-LD | Yoast graph: WebPage, BreadcrumbList, WebSite, Organization (+ Article, Person on posts) | Rebuilt graph, same types; Organization upgraded to `GeneralContractor` with address/phone; **FAQPage added** on 7 pages with FAQ accordions (F5) |
| XML sitemaps | Yoast `sitemap_index.xml` + 7 child sitemaps; `/sitemap.xml` and `/wp-sitemap.xml` 301 to index | Postbuild script writes the same paths; keep both 301s |
| RSS | `/feed/` (10 items), category/author/comment feeds | `/feed/` kept (all posts). Comment, category and author feeds 301 → `/feed/` |
| Contact forms | Contact Form 7 on `/contact/` and `/about/` (name, email, subject, message), no spam protection, recipient unverified | Vercel function → email to info@ via Resend/Postmark, honeypot + Cloudflare Turnstile (Phase 0 #3) |
| Analytics | GA4 `GT-577ZJN8M` via Site Kit; VisitorQueue (`9a2db577-…`), no consent | Both loaded only after opt-in via a lightweight consent banner (Phase 0 #4) |
| Carousels | Swiper 11 (home testimonials, about images, project galleries) | Swiper 11, self-hosted, loaded only on pages that use it |
| Animations | GSAP + ScrollTrigger, AOS 2.3.1, full-screen entrance logo animation | Kept for v1 (Phase 0 #10); self-hosted, respects `prefers-reduced-motion` |
| FAQ accordions | Custom JS (`.sector-faq`) | Native `<details>/<summary>` with same styling (no JS) |
| Icons and fonts | Font Awesome 6.6 (full CSS), Material Symbols (variable font, full axis range), Montserrat 100–900 from Google | Self-hosted Montserrat (used weights only); inline SVG for the ~10 icons used. Same look, far less weight |
| Lazy loading | SiteGround Optimizer lazysizes + combined JS/CSS | Native `loading="lazy"`, width/height attributes, responsive `srcset` via Astro image pipeline (originals kept at old paths) |
| Search | WP search live at `/?s=` and `/search/…/` but no search UI anywhere | Dropped; `/search/*` 301 → `/` |
| Date archives, blog pagination | `/2025/`, `/2026/10/` etc. resolve; `/blog/page/2/` duplicates page 1; `/page/2/` resolves | 301 → `/blog/` (all 13 posts fit on one page) |
| Attachment pages | Yoast redirects attachment URLs to the file | 301 rules for the 186 attachment URLs → file |
| Short-slug guessing | WP redirects `/vet-shack/` → `/project/vet-shack/`, `/canterbury/` → `/locations/canterbury/`, `/privacy/` → `/privacy-policy/`, no-slash → slash, `/index.php`, `/?page_id=7`, `/tim-day-construction/` → `/` | Explicit 301s for every slug of every published item (bare slug → canonical), plus the probed cases |
| Admin, XML-RPC, REST | `/wp-admin/`, `/wp-login.php`, `/xmlrpc.php`, `/wp-json/` | Not present (404). No redirects |
| Security, caching | SG Security, SG Optimizer | Vercel CDN; security headers set in `vercel.json` |
| Plugins with no front-end effect | Duplicate Post, All-in-One WP Migration | Not needed |
| Markdown / AI access | None (`/llms.txt` 404) | `llms.txt`, `llms-full.txt`, `.md` copy of every page; `?output_format=md` and `Accept: text/markdown` via Routing Middleware |

## 3. Design capture (input to DESIGN.md)

- **Fonts:** Montserrat throughout. Body copy 16px / **weight 300** / 1.8 line-height. Headings 500–700. Material Symbols for UI icons.
- **Palette** (hard-coded hex, no CSS variables): primary teal `#1c5156` (79 uses), mid teal `#2a6d73`, dark teal `#153b3f`, light teal `#c6d8db` / `#c5d5d8`, pale `#d9e9ec`, ink `#222`, greys `#f3f3f3` / `#f7f7f7`.
- **Breakpoints:** 2200, 1800, 1440, 1360, 560px (max-width).
- **Contrast:** every pairing passes AA **except light-teal highlight words on white (`#c6d8db` on `#fff` = 1.47:1)**. Used in "who care", "satisfaction", "trusted builders in Kent" and similar. Decision for Phase 2.
- **Screenshots:** 13 templates × 1440/390 in `capture/screenshots/`, taken after scrolling and forcing lazy images to load. Computed styles per element in `capture/computed/`.

## 4. URL inventory (60 sitemap URLs)

| # | URL | Type | Words | Meta desc | Action |
|---|---|---|---|---|---|
| 1 | `/placeholder-blog-post-6/` | post | 445 | – | New slug /what-is-a-passive-house/ + 301 (F2) |
| 2 | `/how-to-plan-a-veterinary-fit-out-project-from-concept-to-completion/` | post | 442 | – | Keep |
| 3 | `/what-are-the-benefits-of-working-with-a-main-contractor-from-start-to-finish/` | post | 472 | – | Keep |
| 4 | `/the-core-principles-of-a-passive-house/` | post | 566 | – | Keep |
| 5 | `/what-makes-a-veterinary-fitout-different-from-other-commercial-builds/` | post | 714 | – | Keep |
| 6 | `/common-challenges-on-kent-building-sites/` | post | 615 | – | Keep |
| 7 | `/key-safety-considerations-in-veterinary-practice-fit-outs/` | post | 759 | – | Keep |
| 8 | `/maximising-efficiency-space-planning-tips-for-veterinary-practices/` | post | 470 | – | Keep |
| 9 | `/fire-safety-requirements-in-veterinary-practices/` | post | 646 | – | Keep |
| 10 | `/why-does-ventilation-and-air-quality-matter-in-veterinary-practices/` | post | 545 | – | Keep |
| 11 | `/how-to-plan-a-successful-veterinary-practice-refurbishment/` | post | 1079 | – | Keep |
| 12 | `/why-should-you-choose-a-specialist-veterinary-fit-out-contractor/` | post | 587 | – | Keep |
| 13 | `/what-should-you-consider-before-starting-a-clinical-fit-out/` | post | 840 | – | Keep |
| 14 | `/` | page | 737 | yes | Keep (reference page) |
| 15 | `/privacy-policy/` | page | 0 | – | Restore stored text (F1) |
| 16 | `/cookies/` | page | 0 | – | Restore + update cookie list (F1) |
| 17 | `/contact/` | page | 72 | – | Keep |
| 18 | `/portfolio/` | page | 578 | – | Keep |
| 19 | `/blog/` | page | 179 | – | Keep |
| 20 | `/design-and-build/` | page | 675 | – | Keep |
| 21 | `/locations/` | page | 0 | – | New hub page (F1) |
| 22 | `/about/` | page | 845 | yes | Keep |
| 23 | `/locations/canterbury/` | locations | 364 | – | Keep |
| 24 | `/locations/whitstable/` | locations | 176 | – | Keep |
| 25 | `/new-homes-and-residential/` | page | 796 | yes | Keep |
| 26 | `/clinical-veterinary-fit-outs/` | page | 888 | yes | Keep |
| 27 | `/project/preston-parade/` | project | 281 | yes | Keep |
| 28 | `/project/south-foreland-lighthouse/` | project | 409 | yes | Keep |
| 29 | `/project/stables/` | project | 236 | yes | Keep |
| 30 | `/project/riverside-social/` | project | 305 | yes | Keep |
| 31 | `/project/old-dover-road/` | project | 324 | yes | Keep |
| 32 | `/project/whitstable-road/` | project | 301 | yes | Keep |
| 33 | `/project/pett-cottage/` | project | 264 | yes | Keep |
| 34 | `/project/king-post-elham/` | project | 246 | yes | Keep |
| 35 | `/project/middle-wall-whitstable/` | project | 337 | – | Keep |
| 36 | `/project/shipwright/` | project | 323 | yes | Keep |
| 37 | `/project/valkyrie-road/` | project | 289 | – | Keep |
| 38 | `/project/castle-road-whitstable/` | project | 318 | – | Keep |
| 39 | `/project/pure-vet-ashford/` | project | 414 | – | Keep |
| 40 | `/project/vet-shack/` | project | 378 | yes | Keep |
| 41 | `/sector/change-of-use/` | sector | 556 | – | Keep |
| 42 | `/sector/remodelling/` | sector | 580 | – | Keep |
| 43 | `/sector/extensions/` | sector | 747 | – | Keep |
| 44 | `/sector/veterinary-fit-outs/` | sector | 635 | – | Keep |
| 45 | `/sector/new-builds/` | sector | 694 | – | Keep |
| 46 | `/testimonial/national-trust/` | testimonial | 7 | – | Keep, fill with quote + photo (F8) |
| 47 | `/testimonial/andy-boorman/` | testimonial | 7 | – | Keep, fill with quote + photo (F8) |
| 48 | `/testimonial/mr-l-reddy/` | testimonial | 8 | – | Keep, fill with quote + photo (F8) |
| 49 | `/testimonial/vetshack/` | testimonial | 6 | – | Keep, fill with quote + photo (F8) |
| 50 | `/testimonial/mr-bryan-joyce/` | testimonial | 8 | – | Keep, fill with quote + photo (F8) |
| 51 | `/category/change-of-use/` | category | 0 | – | Project list per category (F7) |
| 52 | `/category/clinical-veterinary-fit-outs/` | category | 0 | – | Project list per category (F7) |
| 53 | `/category/extensions/` | category | 0 | – | Project list per category (F7) |
| 54 | `/category/listed-buildings/` | category | 0 | – | Project list per category (F7) |
| 55 | `/category/new-build-residential/` | category | 0 | – | Project list per category (F7) |
| 56 | `/category/refurbishments/` | category | 0 | – | Project list per category (F7) |
| 57 | `/category/uncategorized/` | category | 0 | – | 301 → /blog/ (Phase 0 #2) |
| 58 | `/author/becca-kenny/` | author | 0 | – | 301 → /blog/ (Phase 0 #2) |
| 59 | `/author/connor/` | author | 0 | – | 301 → /blog/ (Phase 0 #2) |
| 60 | `/author/maddiepitchacaren/` | author | 0 | – | 301 → /blog/ (Phase 0 #2) |

Plus non-sitemap URLs carried over: `/feed/`, `/robots.txt`, `/sitemap_index.xml` and the 7 child sitemaps, all `/wp-content/uploads/…` files, theme images under `/wp-content/themes/tim-day-custom-theme/assets/images/`.

## 5. Redirect map (to be generated as `vercel.json` / middleware rules)

No Redirection plugin is installed, so there is no CSV to import. Every rule below comes from the probe (`capture/redirect-probe.tsv`) or the Phase 0 decisions.

1. Bare slug → canonical for every project, sector, location and page (WordPress currently guesses these).
2. `/placeholder-blog-post-6/` → `/what-is-a-passive-house/` (F2).
3. `/category/uncategorized/`, `/author/*` → `/blog/`. Their feeds → `/feed/`.
4. `/blog/page/*`, `/page/*`, date archives `/YYYY/`, `/YYYY/MM/` → `/blog/`.
5. `/search/*` and `/?s=` → `/`. `/index.php`, `/?page_id=7`, `/tim-day-construction/` → `/`.
6. 186 attachment page URLs → their file.
7. `/sitemap.xml`, `/wp-sitemap.xml` → `/sitemap_index.xml`. `/comments/feed/` → `/feed/`.
8. After go-live: watch Vercel 404 logs and Search Console, and add rules as they appear.

## 6. Fix log

Status: **Agreed** = decided in Phase 0. **Proposed** = my recommendation, awaiting your decision. **Auto** = standard correction applied without changing meaning.

| # | Issue found | Fix | Status |
|---|---|---|---|
| F1 | `/privacy-policy/`, `/cookies/` and `/locations/` serve an 81-byte blank page (the theme has no template for them). Privacy (650 words) and Cookies (780 words) text exists in WP, dated Feb 2025 | Restore Privacy verbatim. Restore Cookies with the cookie list updated for GA4, VisitorQueue and the consent banner (TDC sign-off). Build a short `/locations/` hub linking Canterbury and Whitstable (copy for your approval) | Agreed |
| F2 | Post "What is a Passive House?" is live at `/placeholder-blog-post-6/` | New slug `/what-is-a-passive-house/` + 301 | Agreed |
| F3 | Author archives for Becca, Connor and Maddie; Uncategorized category published | 301 to `/blog/`. Post byline becomes Tim Day Construction | Agreed |
| F4 | Contact forms have no spam protection; recipient can't be verified without admin access | Vercel function to info@, honeypot + Turnstile. Test send before cutover | Agreed |
| F5 | 7 pages have FAQ accordions (54 Q&As) but no FAQPage schema | Add FAQPage JSON-LD from the visible Q&As | Auto |
| F6 | GA4 and VisitorQueue load with no consent | Consent banner; scripts load on opt-in only | Agreed |
| F7 | All 7 category archives render empty (header and footer only, no H1, no description). The 6 real categories tag **projects**, not posts | Keep the 6 URLs and render each as a list of the projects in that category (H1, short intro, project cards). Alternative: 301 all to `/portfolio/` | **Agreed** (23 Oct) |
| F8 | The 5 `/testimonial/…` pages are empty shells: name, date and a broken empty `<img>` (6–8 words) | Keep the URLs (Phase 0 #10) but render the quote, client name and photo already used in the home carousel, so each page has real content | **Agreed** (23 Oct) |
| F9 | Home hero H1 ("…construction &") runs underneath the FMB logo at 1440px | Reflow so the H1 and logos don't overlap, keeping the design | **Agreed** (23 Oct) |
| F10 | 46 of 60 URLs have no meta description; 57 have no OG image | Write descriptions in TDC's voice for every indexable page; use the page's lead image as OG image (default: brand image) | **Agreed** (23 Oct) |
| F11 | Titles on 37 URLs exceed 60 characters (posts up to 118) because of the " - Building Contractor \| Canterbury, Kent" suffix | Keep titles verbatim but drop the suffix where it pushes beyond ~60 characters (brand name stays) | **Agreed** (23 Oct) |
| F12 | 13 pages lack an H1 (all the empty archives and blank pages) | Resolved by F1, F3 and F7 | Auto |
| F13 | Accessibility (axe, 12 templates): 91 links without accessible names (icon-only cards, social links, logos); 12 invalid `aria-expanded` on the mobile-menu `<div>`; 8 invalid ARIA attributes; 20 contrast failures; no `<main>` landmark on 6 templates; heading-order skips on 5; one malformed list | Fix all in the new components: accessible names, valid ARIA, `<main>`, heading order, alt text. Contrast depends on the Phase 2 decision | Auto |
| F14 | Images: empty `alt` on 36 home images and about 20 per project; accreditation logos link out with no label | Descriptive alt text for content images; `alt=""` stays on purely decorative ones; logos get accessible names | Auto |
| F15 | Light-teal highlight on white is 1.47:1 (fails AA) | Keep or darken: decision in Phase 2 | Phase 2 |
| F16 | `/blog/page/2/` duplicates page 1; date archives and search results are indexable | 301s in section 5 | Auto |
| F17 | Heavy third-party CSS/JS: full Font Awesome, full Material Symbols variable font, Montserrat 100–900, Swiper/GSAP/AOS on every page, WP emoji script | Self-host and subset; load per page | Auto |
| F18 | DMARC is `p=none` at IONOS (no spoofing protection) | **Not touched in the cutover.** Flag to TDC separately | Flag only |

## 7. Unverified (no admin access)

- Contact Form 7 recipient address(es) and autoresponder (if any).
- Whether any unpublished drafts, private pages or scheduled posts exist (the REST API only shows published items; the media count difference of 189 vs 186 suggests 3 private/unattached items).
- ACF field definitions. Content was taken from the rendered HTML, which is what visitors see.
- Server-level redirects in `.htaccess` (none were detected by the probe).
