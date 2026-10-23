# CUTOVER.md: timdayconstruction.co.uk go-live runbook

Moves the website from WordPress on SiteGround to the Astro build on Vercel (project `timdayconstruction-website`, team SBBT). **Only the website's A and www records change. Email is untouched.** Written 23 October 2026 from live DNS lookups and Vercel's domain configuration.

## 0. Current state (recorded 23 Oct 2026)

| Record | Host | Current value | TTL |
|---|---|---|---|
| NS | timdayconstruction.co.uk | ns1050.ui-dns.de / .biz / .org / .com (IONOS) | 21600 |
| A | timdayconstruction.co.uk | **35.214.58.37** (SiteGround) | 300 |
| A | www.timdayconstruction.co.uk | **35.214.58.37** (SiteGround; WordPress 301s www → apex) | 300 |
| MX | timdayconstruction.co.uk | 10 mx00.ionos.co.uk, 10 mx01.ionos.co.uk | 3600 |
| TXT (SPF) | timdayconstruction.co.uk | `v=spf1 include:_spf-eu.ionos.com ~all` | 21600 |
| TXT (DMARC) | _dmarc.timdayconstruction.co.uk | `v=DMARC1; p=none;` | 300 |
| AAAA, CAA | (both) | none | |

The A record TTLs are **already 300**, so no TTL lowering is needed. (Lesson: lower to 300 at least one old-TTL period ahead; already done here.)

DNS is hosted at **IONOS**, not SiteGround. Cancelling SiteGround later does not affect DNS or email.

## 1. Pre-flight (all must be ticked before the change window)

- [ ] Simon has approved the preview and every item in `docs/APPROVALS.md`. TDC has signed off the Cookies changes.
- [ ] Contact form environment variables are set in Vercel (Production): `RESEND_API_KEY`, `CONTACT_FROM`, `CONTACT_TO` (optional), `TURNSTILE_SECRET_KEY`, `PUBLIC_TURNSTILE_SITE_KEY`. A redeploy has run since they were set.
- [ ] The Resend sending domain is verified. Its records are added at IONOS **on a sending subdomain** (for example `send.timdayconstruction.co.uk`), so the root MX, SPF and DMARC are not touched.
- [ ] The Turnstile widget's hostnames include `timdayconstruction.co.uk`.
- [ ] Test submission from the preview reaches info@ (F4).
- [ ] `scripts/qa/smoke.sh <preview>` passes, with `VERCEL_BYPASS` set.
- [ ] Lighthouse on the preview: mobile performance ≥95 on every template (warm cache), accessibility and best practices 100. SEO is capped on previews by Vercel's noindex header; it is checked again after go-live.
- [ ] GA4 property `GT-577ZJN8M` still receives data from the preview after accepting cookies (DebugView).
- [ ] Simon or TDC has the IONOS login open and can edit DNS for timdayconstruction.co.uk.
- [ ] Google Search Console access for timdayconstruction.co.uk is confirmed (domain property preferred).
- [ ] A WordPress fallback is in place for two weeks. Ask SiteGround for the site's temporary URL (Site Tools › Domain › Temporary Domain), or take an All-in-One WP Migration export. The DNS change itself doesn't delete anything on SiteGround.
- [ ] Choose a quiet window: a weekday morning, not a Friday.

## 2. The change (about 10 minutes, at IONOS)

IONOS › Domains & SSL › timdayconstruction.co.uk › DNS. **Use the full host name if the editor rejects `@`** (lesson from Krystal/cPanel). In IONOS the apex is the empty or `@` host.

1. **Apex A record:** edit the A record for `timdayconstruction.co.uk`
   - from `35.214.58.37`
   - to **`216.198.79.1`**, then **add** a second A record **`64.29.17.1`** (both are Vercel's current recommendation for this project)
   - TTL 300 (or the lowest IONOS allows)
   - If IONOS only allows one A record, use **`76.76.21.21`** (Vercel's alternative single IP).
2. **www:** delete the A record `www → 35.214.58.37` and add **CNAME `www` → `70dacfcf1551ec5f.vercel-dns-017.com.`** (Vercel's project-specific CNAME; the alternative is `cname.vercel-dns.com.`). TTL 300.
3. If IONOS has an **AAAA** record for the apex or www, delete it. None existed on 23 Oct.
4. **Do not touch:** NS, MX, the SPF TXT, `_dmarc`, any `_domainkey`, autodiscover/mail records, or anything not listed above.
5. Save, and note the exact time.

Vercel project domains are **already added and verified**:
- `timdayconstruction.co.uk`: production
- `www.timdayconstruction.co.uk`: 301 → apex

## 3. Immediately after (within 5 minutes; stay at the keyboard)

1. Watch DNS:
   ```bash
   dig +short timdayconstruction.co.uk @8.8.8.8
   dig +short www.timdayconstruction.co.uk @1.1.1.1
   ```
2. **Check the SSL certificate straight away.** Lesson from mallardhq.com: Vercel did not auto-issue it and visitors saw a security error for about 45 minutes.
   - Vercel › Project › Settings › Domains: both domains should show "Valid Configuration" and a certificate.
   - Or Claude: `list_certs` for team SBBT, looking for `timdayconstruction.co.uk` and `www.timdayconstruction.co.uk`.
   - **If the certificate is missing, issue it now** (Claude: `issue_cert` for both names; or `vercel certs issue timdayconstruction.co.uk www.timdayconstruction.co.uk --scope sbbt`).
   - Confirm with:
     ```bash
     curl -sSI https://timdayconstruction.co.uk/ | head -5
     curl -sSI https://www.timdayconstruction.co.uk/   # expect 301 to the apex
     ```
3. Smoke test the real domain:
   ```bash
   scripts/qa/smoke.sh https://timdayconstruction.co.uk
   ```
   All 41 checks must pass. The noindex header must be **gone**: check `curl -sI https://timdayconstruction.co.uk/ | grep -i x-robots` shows nothing, and the page carries `<meta name="robots" content="index, follow…">`.
4. Warm the image cache, so first visitors don't wait on image resizing:
   ```bash
   curl -s https://timdayconstruction.co.uk/sitemap_index.xml   # then request each page once, e.g.:
   for u in $(curl -s https://timdayconstruction.co.uk/{page,post,project,sector,category,testimonial}-sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//'); do curl -s -o /dev/null "$u"; done
   ```
   Then open the home page on a phone and on a desktop.
5. Submit the contact form on the live domain and confirm it arrives at info@.
6. Accept cookies and confirm GA4 Realtime shows the visit.
7. Send an email **to** info@timdayconstruction.co.uk from an outside address and confirm it arrives. This proves mail is unaffected.

## 4. Rollback (if anything is wrong and can't be fixed in 15 minutes)

At IONOS, put the two records back exactly as they were:
- A `timdayconstruction.co.uk` → `35.214.58.37` (delete the Vercel A records)
- delete CNAME `www`, then add A `www` → `35.214.58.37`

With TTL 300, most visitors are back on WordPress within about 5–10 minutes. Nothing on SiteGround has changed, so WordPress serves exactly as before. Vercel keeps the domains attached, ready for a retry.

## 5. After go-live

**Day 0**
- Google Search Console:
  - submit `https://timdayconstruction.co.uk/sitemap_index.xml`
  - inspect the home page and request indexing
  - check "Page indexing" over the next week
- Revoke the Vercel automation bypass secret created for QA (Project › Settings › Deployment Protection), or ask Claude to (`update_project_protection_bypass` with `revoke`).

**Days 1–14**
- Check Vercel logs and Search Console for **404s** every few days. Add a 301 for any real old URL: edit `scripts/redirects.mjs`, run `npm run redirects`, push. The redirect map is in MIGRATION-BASELINE.md section 5.
- Keep the WordPress fallback reachable for two weeks.

**Day 14+**
- When there are no unexplained 404s or Search Console errors, SiteGround hosting can be cancelled. DNS is at IONOS, so cancelling SiteGround is safe. Download a final full backup first.
- Remove the agency's access to anything TDC owns (IONOS, Google Analytics, Search Console, Site Kit-connected Google accounts) as appropriate.

**Separately (not part of this cutover):**
- DMARC is `p=none` (F18). Recommend moving to `p=quarantine` once DKIM is confirmed at IONOS and reports look clean. That's a separate email-security task.

## 6. Who does what

| Step | Who |
|---|---|
| Approvals, Vercel env vars, Resend and Turnstile accounts | Simon |
| IONOS DNS edits (section 2) | TDC (Becca or Tim), with Simon or Claude on the call reading values |
| Certificate check and issue, smoke tests, warm-up, Search Console | Claude / Simon |
| Decision to roll back | Simon |
