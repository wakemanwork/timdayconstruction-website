# DESIGN.md: Tim Day Construction

The protected basis for every page and template on timdayconstruction.co.uk. It is measured from the live WordPress theme (`tim-day-custom-theme` v1.0, The Digital Lookout), captured 23 October 2026. Nothing here is guessed.

**The rule:** new pages are built from the tokens and components below. Don't invent new colours, font sizes, spacing values or card styles. If something genuinely new is needed, add it here first, then build it.

Sources: `capture/theme-source/style.css` (original, unminified, 3,963 lines), computed styles in `capture/computed/`, baseline screenshots in `capture/screenshots/` (1440 and 390px, all 13 templates). Line numbers below refer to that `style.css`.

---

## 1. Principles

1. **Teal and white, nothing else.** One brand hue in four strengths, plus white and a neutral grey. Photography supplies all the other colour.
2. **Big, square, confident.** Square corners everywhere. The only radii are the footer charity button (10px) and the round contact-method icons on the Contact page (100%). Large photo-led cards, full-bleed teal panels, generous vertical space (4 to 8rem between sections).
3. **Light body, heavier heads.** Montserrat body at weight 300, headings at 500 to 700. This contrast is the typographic signature, so don't make body text heavier.
4. **Two-tone headings.** Section headings often set one phrase in a lighter teal ("A team **who care** about every project"). This is the main brand device; see 2.2 for the colour rules.
5. **The TDC monogram as texture.** A huge faded TDC icon sits behind hero, intro, CTA, banner and footer panels at 3 to 10% opacity.

## 2. Tokens

The live CSS hard-codes hex values. In the Astro build they become custom properties in `src/styles/tokens.css`. Values are unchanged unless marked **(changed)**.

### 2.1 Colour

| Token | Value | Used for |
|---|---|---|
| `--teal` | `#1c5156` | Primary. Headings and body text on white, panels, buttons, footer, overlays (79 uses) |
| `--teal-mid` | `#2a6d73` | FAQ question bars, secondary panels, links in body copy |
| `--teal-dark` | `#153b3f` | Blog title banner background (with dot-grid pattern); link colour in location and "why choose TDC" copy |
| `--teal-deep` | `#1d464b` | Grid lines of the blog title banner pattern only |
| `--teal-light` | `#c6d8db` | Button hover fill, light panels, card hover |
| `--teal-light-text` | `#c5d5d8` | Highlight words **on teal backgrounds only** |
| `--teal-highlight-on-light` **(changed)** | `#5f969c` | Highlight words **on white/grey backgrounds**. Replaces `#c5d5d8` there (1.47:1 → 3.3:1). Agreed 23 Oct, F15 |
| `--teal-pale` | `#d9e9ec` | Founder-quote panel background (home) |
| `--teal-overlay` | `rgba(28, 81, 86, 0.75)` | Image overlays on project cards and the hero |
| `--white` | `#ffffff` | Page background, text on teal |
| `--grey-bg` | `#f3f3f3` | `.grey-bg` sections (CTA bands) |
| `--grey-hover` | `#e6e6e6` | Desktop nav link hover background |
| `--ink` | `#222222` | Mobile menu icon only |

**Contrast (measured):** teal on white 8.9:1, mid teal on white 5.94:1, light teal on teal 6.03:1, teal on light-teal button 6.03:1, teal on pale 7.12:1. All pass AA. Highlight-on-white at `#5f969c` is 3.3:1, which passes AA for large text only, so **use it only in headings of 24px or more** (or 18.66px bold). Never use it for body text or small labels.

### 2.2 The highlight span

```html
<h2 class="section-title--large">A team <span class="hl">who care</span> about every project</h2>
```

`.hl` resolves its colour from its surface: `--teal-highlight-on-light` on white/grey sections, `--teal-light-text` on teal panels. Implement it with a `--hl` custom property set by the surface class (`.surface-light`, `.surface-teal`), so authors never pick the colour by hand. This replaces the theme's `.light-teal-txt`.

### 2.3 Typography

- **Family:** Montserrat (Google Fonts, variable). **Self-host** the latin subset with weights 200, 300, 400, 500, 600 and 700 only (the live site loads 100 to 900). `font-display: swap`. Fallback: `sans-serif`, with a size-adjusted Arial fallback to avoid layout shift.
- **Base:** `body { line-height: 1.5 }`. Headings `line-height: 1.2`. Paragraphs `font-weight: 300`. `h3` defaults to 600.
- **Root size:** 16px (`1rem`). All sizes are rem.

Type scale (desktop ≥1801px → ≤1800 → ≤1360 → ≤560). Computed on the live site at 1440px unless noted.

| Role | Class / element | ≥1801 | ≤1800 | ≤1360 | ≤560 | Weight |
|---|---|---|---|---|---|---|
| Page banner title (H1) | `.page-title-banner__title` | 3.5rem | 3.5rem | 3rem | 2.6rem | 700 |
| Home hero title (H1) | `.hero__title` | 2.6vw, line-height 3vw, width 65% | (same) | 2vw, width 45% (from ≤1440) | see mobile rules 847–978 | 700 |
| Section title large | `.section-title--large` | 2.5rem | 2rem | 2rem | 1.8rem | 600 |
| Section title medium | `.section-title--medium` | 2rem | 1.6rem | 1.6rem | 1.6rem | 600 |
| Card title (project overlay) | `.project-block-overlay__title` | 2.2rem | 1.8rem | 1.6rem | | 500 |
| Card subtitle (location) | `.project-block-overlay__location` | 1.6rem | 1.2rem | 1.1rem | | 200 |
| Sector card title | `.sector-card h3` | 1.2rem | 1.1rem | 1.1rem | 1.2rem | 600 |
| FAQ question | `.sector-faq__header h3` (white) | 1.17em of 1.1rem | 1.17em of 1rem (18.72px) | | | 600 |
| Body | `p` | 1rem / 1.8 line-height in content areas | | | | 300 |
| Nav link | `header nav a` | 1rem uppercase | 0.9rem | 1rem | (mobile menu 2.5rem) | 400 |
| Button | `.btn` | 1rem | 0.9rem | | | 400 |
| Blog post title (H1) | `.blog-title-banner__title` | 3.4rem / 1.4 | 3.2rem | 2.8rem | 2.4rem | 700 |
| Small print | footer `.copyright` | 0.7rem (at ≤1360) | | | | 300 |

Sizes in use across the theme: 0.7, 0.8, 0.85, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2, 2.2, 2.4, 2.5, 2.6, 2.8, 3, 3.2, 3.4 and 3.5rem, plus 10, 14 and 20rem for the faded monogram. **New work picks from the role table above, not from this list.**

### 2.4 Spacing

- **Scale:** the theme's utility steps are 1, 2, 3, 4 and 5rem (`.mt-*`, `.mb-*`). Keep these as `--space-1`…`--space-5`, plus `--space-6: 6rem` and `--space-8: 8rem` for section padding.
- **Section padding (vertical):** `8rem 0` (major sections), `4rem 0` (listing grids), `6rem 0 4rem` (CTA bands). On mobile (≤560) these drop to `5rem 0 3rem` / `6rem 0 5rem`.
- **Card gaps:** 2rem desktop, 1rem at ≤1800 for the 5-up sector grid.

### 2.5 Layout

| Container | Rule |
|---|---|
| `.width-container` | `width: 85%; max-width: 1800px; margin: 0 auto`. 90% at ≤1360 |
| Inset panels (hero, page banner, footer panel) | `width: 97%` (95% footer), centred, square corners. Full width at ≤560 |
| `header nav` | `width: 97%`, 90% at ≤560 |
| `.two-col-grid` | `1fr 1fr`, `gap: 8rem` |
| Blog article column | `.blog-width-container` (see style.css 3333) |

**Breakpoints** (all `max-width`): `2200px` (one use), `1800px` (large desktop → desktop), `1440px` (two uses), `1360px` (desktop → tablet: grids collapse), `560px` (tablet → mobile: nav becomes the slide-in menu). Keep these exact values so layouts match the baseline screenshots.

### 2.6 Motion

- Default transition: `all 0.2s ease` on hover states. Mobile menu `0.5s ease`, with links staggered 150ms.
- Page banner reveal: a teal `:before` wipes from 100% to 0 width (`0.6s ease`, 0.2s delay).
- Entrance animation (home, first visit only): full-screen teal panel with the white TDC icon. The icon fades at 1.5s and the panel wipes away at 3s. Gated by a `first_visit=true` cookie (1 year). **Kept for v1**, but:
  - skipped entirely under `prefers-reduced-motion: reduce`;
  - the cookie is listed in the cookie policy as strictly necessary/functional.
- AOS fade-ups on scroll and GSAP parallax on the hero image and portfolio images. Both are disabled under `prefers-reduced-motion`.
- The live site only removes smooth scroll under reduced motion. The rebuild must also disable the entrance animation, AOS and parallax there.

### 2.7 Elevation

There's only one shadow: the sticky header after 100px of scroll, `box-shadow: 0 10px 15px rgba(128,128,128,0.11)`. Nothing else uses shadows.

## 3. Iconography and brand marks

| Asset | Path (kept) | Use |
|---|---|---|
| Logo (wordmark + monogram) | `/wp-content/uploads/2024/12/tim-day-logo-darker.png` (286×42) | Header. Width 250px, 210px at ≤1800, 200px at ≤560. **Convert to SVG** if a source exists; otherwise serve the PNG at 2×. |
| TDC monogram, light | `/wp-content/themes/tim-day-custom-theme/assets/images/tim-day-icon.svg` | Faded background texture, entrance animation |
| TDC monogram, dark | `…/tim-day-icon-dark.svg` | Texture on light sections |
| Favicon set | `/wp-content/uploads/2024/12/cropped-favicon-{32,180,192,270}.png` | Keep the paths |
| Accreditations | FMB, NHBC, SMAS Worksafe (links to compliance PDF), Passive House Tradesperson seal | Hero (home) and footer. Always all four, in that order |
| Charity | Zarach logo + "Find out more here" | Footer only |
| UI icons | Material Symbols Outlined, weight 200, FILL 0: `menu`, `close`, `arrow_back` (rotated 135° = ↗), `arrow_forward`, `call`, `mail`, `expand_more`; Font Awesome: `quote-left/right`, `facebook`, `linkedin-in` | **Replace both icon fonts with inline SVGs** of the same glyphs (identical look, ~300KB less) |

Faded monogram opacities: 0.03 (`.background-faded-icon`), 0.1 (page banner), 0.05 to 0.1 (CTA panels, footer).

## 4. Imagery

- **Photography only:** real TDC sites and finished buildings, plus the drone shots (`DJI_…`). No stock or illustration.
- **Treatment:** `object-fit: cover`, square corners. On teal panels the image sits under a `--teal` overlay at 0.75 to 0.85 opacity (page banners, hero, project hover).
- **Card hover:** the sector card image goes `grayscale(100%)` and its title bar turns `--teal-light`.
- **Fixed heights** (desktop / ≤1800 / ≤1360 / ≤560):
  - Sector card images: 450 / 350 / 300px
  - Project blocks: 700 / 550 / 450 / 500px
  - Home hero: 92vh
- **Delivery in the rebuild:** originals stay at their `/wp-content/uploads/` paths for old links and OG images. Rendered pages use Astro-generated AVIF/WebP with `srcset` and explicit `width`/`height`. The hero image is eager with `fetchpriority="high"`; everything else is `loading="lazy"`.
- **Alt text:** describe what the photo shows and where ("Reception desk at Vet Shack, Canterbury"). Accreditation logos are named ("FMB member"). Purely decorative monograms get `alt=""` and `aria-hidden="true"`.

## 5. Templates

| Template | Live example | Built from |
|---|---|---|
| Home | `/` | Hero (split) → Intro → Design & Build split → Sector cards → Three blocks → Founder quote → How we work → Large image → Testimonial carousel → Footer |
| Service page | `/clinical-veterinary-fit-outs/`, `/new-homes-and-residential/` | Page banner → Sector intro → Project blocks → FAQ → CTA band |
| Sector | `/sector/*` | Page banner → Sector intro → Project blocks → Sector CTA → FAQ |
| Project | `/project/*` | Page banner → Project content + details panel → Project image carousel → Project CTA |
| Location | `/locations/canterbury/` | Page banner → Where we work (content, location list, map image) → CTA |
| Locations hub **(new)** | `/locations/` | Page banner → intro → location cards (sector-card style) → CTA |
| Portfolio | `/portfolio/` | Page banner → Portfolio intro → Portfolio category rows (title, body, parallax image) |
| Category archive **(new content)** | `/category/*` | Page banner → short intro → Project blocks for that category → CTA (F7) |
| Blog index | `/blog/` | Page banner → Blog cards (3 / 2 / 1 columns) |
| Post | `/<slug>/` | Blog title banner (title + date) → Featured image → Content column |
| About | `/about/` | Page banner → Meet the founder → About content → About image carousel → About contact (with form) |
| Contact | `/contact/` | Contact page: titles, contact methods, socials, form |
| Design & Build | `/design-and-build/` | Page banner → Intro + list → Timeline (scroll progress) → RIBA stages carousel → Timeline bottom text |
| Testimonial **(new content)** | `/testimonial/*` | Page banner → quote block (Founder-quote style) + photo → link to project → CTA (F8) |
| Legal | `/privacy-policy/`, `/cookies/` | Page banner → Blog content column |

## 6. Components

Each component maps to one `.astro` file in `src/components/`. Its CSS is ported from the listed `style.css` lines with values unchanged; only the colours become tokens. Names follow the theme's class names so the CSS ports cleanly.

### 6.1 Header (`Header.astro`) · style.css 186–349
- Fixed, white, `z-index: 900`. Gets the shadow after 100px of scroll.
- Logo left. Nav right: About, Portfolio, Blog, Get in touch. Uppercase, teal, link padding 2rem (1.5rem at ≤1800, `2rem 1rem` at ≤1360).
- Hover: `#e6e6e6` background with a 1.5px teal bottom border (no border at ≤1360).
- ≤560: links hidden. A 50×50 menu button opens a full-screen white slide-in menu with 2.5rem links staggered in.
- **Fixes:** the button gets `aria-expanded` and `aria-controls` (the live site wrongly puts `aria-expanded` on the `<div>`); focus is trapped while the menu is open; Esc closes it. Mark the current page with `aria-current="page"`.

### 6.2 Footer (`Footer.astro`) · 388–575
- Inset teal panel (95% width, padding `5rem 4rem 2rem`) on white. Full-bleed teal at ≤560.
- Title "Get in touch to discuss your project", phone and email with icons, Facebook and LinkedIn, Cookies and Privacy links.
- Accreditation row plus the charity block (Zarach, a 10px-radius button). Company number, VAT number and © line in small print.
- Faded TDC monogram behind.
- **Fixes:** social links get accessible names; logos get alt text; `tel:` link uses `+441227281749`.

### 6.3 Button (`Button.astro`) · 350–387
- `padding: 1rem 2rem; border: 2px solid var(--teal)`, square.
- Variants:
  - `--dark`: teal fill, white text; hover light-teal fill with teal text.
  - `--light`: white fill, teal text; hover opacity 0.6.
  - `--transparent`: white border and text; hover white fill with teal text.
- Rendered as `<a>` for navigation and `<button>` for actions.

### 6.4 Page title banner (`PageBanner.astro`) · 578–684
- Inset 97% panel. Background photo with a teal overlay at 0.85.
- White H1, 700 weight, sizes per 2.3. Faded monogram bottom-right at 0.1.
- Teal wipe reveal on load.
- Top padding 16rem (13 / 10 / 12rem) to clear the fixed header.

### 6.5 Home hero (`HomeHero.astro`) · 746–1007
- Hero H1 is sized in **viewport units** (2.6vw, 2vw at ≤1440). That's why it collides with the logos at some widths. Keep the vw sizing for the look but bound it with `clamp()` and give the H1 its own grid column.
- 92vh inset panel split into two photo halves: Clinical & Veterinary (left) and Residential (right).
- Each half has an H2, H3, paragraph and a `--light` button.
- Teal gradient overlay. The H1 "‘Concept to completion’ construction & project management" sits bottom-left with the accreditation logos bottom-right.
- **Fix F9:** the H1 and the logo row must not overlap at any width. Constrain the H1 to the left column and let the logos wrap.
- The hero `<h2>/<h3>` order is kept, but the visual hierarchy is unchanged.

### 6.6 Intro split (`Intro.astro`) · 1008–1083
Full-bleed teal section with a faded monogram. Left: H3 lead with a highlight span, short paragraph and `--light` button. Right: longer body copy in light text.

### 6.7 Media split (`MediaSplit.astro`) · 1587–1650, 1311–1393, 1651–1777
- A two-column image + text pattern used for Design & Build, the founder quote and Meet the founder.
- Image side is `object-fit: cover`. The text side has its heading, body and a button.
- **Quote variant:** `--teal-pale` text panel with large Font Awesome quote marks (opening top-left, closing bottom-right) beside a photo of Tim.

### 6.8 Sector cards (`SectorCards.astro`) · 1084–1191
- 5-up grid (1 column at ≤1360). Each card is a photo (fixed heights per 4) with a teal title bar below (min-height 92px) and a 50×50 teal arrow tile top-right (arrow rotated 135°).
- Hover: image greyscale, title bar and tile turn light teal, arrow rotates.
- **Fix:** the arrow is decorative (`aria-hidden`) and the link name is the card title. Hover styles also apply on `:focus-visible`.

### 6.9 Three blocks (`ThreeBlocks.astro`) · 1192–1310
Three photo tiles with a teal overlay, a title bottom-left, a line icon bottom-right and an arrow tile. They link to /about/.

### 6.10 Process blocks (`ProcessBlocks.astro`) · 1394–1456
Three white cards on a teal band (H3 + paragraph). They're used for "How we work".

### 6.11 Testimonial carousel (`TestimonialCarousel.astro`) · 1480–1586
- Swiper carousel of photo cards. A teal overlay holds the quote, the name (H4) and the company.
- **Fix:** remove the empty `<img src="">` logo element (render it only when a logo exists). Add carousel controls with accessible names, and pause autoplay on hover/focus.

### 6.12 FAQ (`Faq.astro`) · 3183–3270
- Already native `<details>/<summary>`. Sits in a full-bleed teal section. Mid-teal question bars (padding `3rem 2rem`, white `h3` text, Font Awesome chevron rotates when open) and white answer panels in teal text.
- List width 60% (70% at ≤2200, 90% at ≤1360).
- **Adds FAQPage JSON-LD** from the same data (F5). Questions are `h3` inside `summary`.

### 6.13 Project blocks (`ProjectBlocks.astro`) · 2966–3080
- Two-column photo grid (1 column at ≤560). Fixed heights per 4.
- Overlay `--teal-overlay` with the white title (500) and location (200). The overlay shows on hover at desktop and is always visible at ≤1360.
- **Fix:** the overlay also shows on `:focus-visible`/`:focus-within`, so keyboard users see titles.

### 6.14 Project detail (`ProjectDetail.astro`) · 2638–2746
- Left: content column (body copy, client quote in italics).
- Right: teal details panel with label/value pairs (Location, Client, Type of Work, Status, plus Architect when present) and the monogram bottom-right.
- **Rule:** omit any row whose value is empty. The live site does this in JS for Architect; the rebuild does it at build time.

### 6.15 Image carousel (`ImageCarousel.astro`) · 2196–2260, 2747–2801
- Full-width Swiper gallery with square prev/next buttons bottom-right (white, teal arrows).
- Empty slides are removed at build time (the live site does it in JS).
- Used on project pages and About.

### 6.16 CTA band (`CtaBand.astro`) · 2802–2900, 3081–3182
- Grey (`#f3f3f3`) band with a faded monogram.
- Centred two-tone heading ("Looking for **trusted builders in Kent?**"), a body paragraph and a `--dark` button with an arrow.
- **The highlight uses `--teal-highlight-on-light`** (F15).

### 6.17 Blog cards (`BlogCards.astro`) · 3271–3332
3 / 2 / 1-column grid. Each card is a photo, the title as a link and the date. Hover changes the title colour.

### 6.18 Article (`Article.astro`) · 3333–3476
- Title banner (title + date), featured image, then a narrow content column.
- Inside it: `h2` with a top margin, `h3`, paragraphs at weight 300 with 1.8 line-height, inline links in mid teal (underlined in the rebuild, which fixes the axe `link-in-text-block` failure), and bulleted lists.
- Used for posts and legal pages.

### 6.19 Timeline (`Timeline.astro`) · 3525–3655
- Vertical centre line with a teal progress fill driven by scroll position. Milestones alternate left and right.
- Under reduced motion the progress line is full height and static.

### 6.20 RIBA stages carousel (`RibaStages.astro`) · 3656–end
Horizontal carousel of numbered stage cards with prev/next buttons in the title row.

### 6.21 Contact form (`ContactForm.astro`) · 2261–2478, 2058–2195
- Fields: Name, Email, Subject, Message (all required except Subject, matching CF7).
- Sits on a teal panel. Inputs are filled `--teal-mid` with white text, a 2px `--teal-mid` border that turns `--teal-light` on focus, 1rem padding, 1.1rem text, 2rem gap, and white labels above. Submit is white with teal text (hover opacity 0.6).
- Posts to `/api/contact` (Vercel function). Spam protection is a hidden honeypot plus Turnstile.
- Success and error messages go in an `aria-live="polite"` region.
- On success it fires a GA4 `generate_lead` event (replacing Site Kit's CF7 tracking), but only if analytics consent was given.
- Used on Contact and About.

### 6.22 Consent banner (`ConsentBanner.astro`) **(new)**
- Bottom bar, white, with a teal top border. Text in body style; buttons are "Accept" (`--dark`) and "Reject" (`--dark` too, so both choices are equal), plus a link to /cookies/.
- Nothing from GA4 or VisitorQueue loads until the visitor accepts. The choice is stored in a `tdc_consent` cookie for 6 months.
- There's a "Cookie settings" link in the footer to reopen it.

### 6.23 Entrance animation (`EntranceAnimation.astro`) · 702–745
See 2.6. It's home-only and first-visit-only, it's skipped under reduced motion, and it's `aria-hidden`.

## 7. Accessibility rules (target: Lighthouse 100)

1. One `<h1>` per page. No skipped heading levels inside `<main>`, though visual size may differ from level.
2. Landmarks: `<header>`, `<nav aria-label="Main">`, `<main id="main">`, `<footer>`, plus a "Skip to content" link (`.sr-only:focus` styling).
3. Every link and button has an accessible name. Icon-only controls get `aria-label`; whole-card links take the card title.
4. Focus is always visible: `outline: 3px solid var(--teal-mid); outline-offset: 3px` on light surfaces, and white on teal surfaces. This **replaces** the live site's 4px red border (agreed 23 Oct). It doesn't shift layout.
5. Hover-only reveals also trigger on `:focus-visible`/`:focus-within`.
6. Colour contrast follows 2.1. The highlight-on-light colour is for large headings only.
7. Images follow the alt-text rules in section 4.
8. Motion: everything in 2.6 respects `prefers-reduced-motion: reduce`.
9. Forms: visible labels, `autocomplete` attributes, errors linked with `aria-describedby`, and a live region for status.
10. Carousels: keyboard-operable buttons with names. No autoplay without pause.

## 8. Performance budget (target: Lighthouse 95+)

- **Fonts:** one self-hosted Montserrat variable woff2 (latin subset), preloaded.
- **JS:** none on content pages except where needed.
  - Swiper only on pages that have carousels.
  - GSAP and AOS only on home, portfolio and Design & Build, loaded after first paint.
  - Analytics only after consent.
- **CSS:** inlined critical CSS per page from the component styles; no icon fonts.
- **Images:** see section 4. LCP image preloaded.
- **Removed:** WP emoji script, Font Awesome, Material Symbols font, lazysizes, CF7 scripts, jQuery-era bundles.

## 9. Changing this file

Changes to tokens or components are recorded in the changelog below with a date and reason. Content-only pages never need a change here.

| Date | Change | Reason |
|---|---|---|
| 2026-10-23 | Initial capture from live theme. Added `--teal-highlight-on-light` `#5f969c` | F15 contrast decision |
| 2026-10-23 | Focus indicator: teal/white 3px outline replaces red 4px border | Agreed with Simon; on-brand, no layout shift |
