# Build brief: remaining templates (Phase 3, parallel)

You are building part of the static Astro rebuild of timdayconstruction.co.uk. The **home page is the approved reference**. Match its approach exactly. Read these first, in this order:

1. `CLAUDE.md`: non-negotiables and how the build works.
2. `docs/DESIGN.md`: tokens, components and accessibility rules (protected).
3. `docs/VOICE.md`: only for the copy you are asked to draft.
4. `docs/MIGRATION-BASELINE.md`: the fix log (F1–F22) with decisions.
5. The reference implementation: `src/pages/index.astro`, `src/components/home/*`, `src/components/{PageBanner,ProjectBlocks,Faq,CtaBand,ImageCarousel,SectorCards,TestimonialCarousel}.astro`, `src/lib/{seo,md,alt,carousels}.ts`, `scripts/extract.py` + `scripts/extractlib.py`.

## Setup in your worktree

```bash
. /tmp/claude-0/-home-claude/ba82769c-2614-56c5-a373-51e20a4e55b0/scratchpad/env.sh   # Node 24 on PATH (it also cd's to the main repo, so cd back to your worktree)
cd <your worktree>
ln -s /home/claude/tdc/node_modules node_modules      # shared deps; never npm install
npx astro build && node scripts/postbuild.mjs         # must succeed before you start
(cd dist && nohup python3 -m http.server <PORT> >/dev/null 2>&1 &)   # your own port, below
```

## Hard rules

- **Never edit shared files.** These are: `src/layouts/**`, `src/styles/**`, `src/lib/**`, `src/content.config.ts`, the existing components listed in step 5 above, `src/components/{Header,Footer,ConsentBanner,EntranceAnimation,Img,Icon}.astro`, `src/data/{site,home,alt-text,image-sizes}.json`, `scripts/{extract,extractlib,postbuild,redirects,port_css,image-sizes}.*`, `scripts/qa/**`, `middleware.js`, `vercel.json`, `package*.json`, `CLAUDE.md`, `docs/**`. Existing files in `src/content/**` may be **read** but not edited. If you need a change to a shared file, don't make it: put the exact change you need in your report.
- **Your files only:** `src/pages/<your routes>`, `src/components/<your-area>/*.astro`, `src/data/pages/<page>.json`, `src/data/alt/<your-area>.json`, `scripts/extract_<your-area>.py` (and `api/` for the contact agent only).
- **Never retype copy.** All page text comes from `capture/html/*.html` through your `scripts/extract_<your-area>.py`. Import the helpers with:
  `import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from extractlib import *; from extractlib import applied`.
  Use `fix()`/`md()`/`txt()`/`inner()` so the agreed F19 corrections apply, and call `save_fixes('<your-area>')` at the end.
- **Markup mirrors the live page's classes and structure** (inspect `capture/html/<page>.html`), so the ported CSS in `src/styles/theme/` applies unchanged. Page-specific deviations go in your component's `<style is:global>`, scoped by the section id, each with a comment citing its reason.
- **Headings:** exactly one `<h1>` (PageBanner or the blog title banner) and no skipped levels. If you change a heading's tag for order, copy the old selector's styles to the new tag (see `Intro.astro` and `CtaBand.astro`).
- **Images:** always `<Img>` (not `<img>`) for uploads. Give content photos descriptive alt text in `src/data/alt/<your-area>.json` (look at them: make a contact sheet and Read it). Decorative images get `alt=""`. Name a project or place only if you are certain.
- **SEO per page:** `pageTitle(wpTitle, name)` from `lib/seo.ts`; description = the live Yoast description, or if it's missing (F10) a draft written to VOICE.md section 7.8 (140–155 characters), **listed in your report for Simon's approval**. `ogImage` = the page's lead photo. JSON-LD via `graph(webPage(...), breadcrumbs(...), …)` plus the type that fits (see your section). `published`/`modified` from REST data where it exists.
- **No new dependencies, fonts or third-party scripts.**

## Quality gates (all must pass before you report)

Run against your own server (`LOCAL=http://localhost:<PORT>`):

1. `npx astro build && node scripts/postbuild.mjs`: no errors or warnings from your pages.
2. `python3 -I scripts/qa/textdiff.py <each of your paths>` (it reads dist/): **0 UNEXPECTED** for every page. Anything else must be either an agreed fix (logged via `save_fixes`) or a deliberate change you explain in the report.
3. `LOCAL=... node scripts/qa/axe.mjs <your paths>`: **no violations** at 1440 and 390.
4. `LOCAL=... node scripts/qa/compare.mjs <your paths>`: then **look at** `qa/compare/<slug>-1440.png` and `-390.png` (downscale and crop to read them). They must match the live page apart from agreed fixes. Report the pixel-diff % and explain anything above ~3%. If a difference is a capture artefact (lazy images, carousel position), confirm with a normal viewport screenshot.
5. Check the JSON-LD of one page per template parses (`JSON.parse`) and contains the expected types.
6. `git add` your files and commit in your worktree with a clear message ending:
   ```
   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
   Claude-Session: https://claude.ai/code/session_018Ey2PsfdZmMn76b9DSdZpX
   ```

## Report back (short)

- The routes built, and the gate results per page (text diff, axe, pixel %).
- Deviations from live and why.
- Drafted copy needing Simon's approval (meta descriptions, any new copy), verbatim.
- Exact change requests for shared files, if any.
- Your branch or worktree path and commit hash.
