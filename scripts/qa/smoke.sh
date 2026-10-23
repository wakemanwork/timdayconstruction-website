#!/usr/bin/env bash
# Smoke test against a deployment or the live domain. Usage: scripts/qa/smoke.sh https://host
# Optional: VERCEL_BYPASS=<automation bypass secret> for protected previews.
B=${1:?base url}; H=(); [ -n "$VERCEL_BYPASS" ] && H=(-H "x-vercel-protection-bypass: $VERCEL_BYPASS" -H "x-vercel-set-bypass-cookie: true")
fail=0
check() { # path expected_status [expected_location_or_content_type_substring]
  out=$(curl -s -o /dev/null -w "%{http_code} %{redirect_url} %{content_type}" "${H[@]}" "$B$1")
  code=${out%% *}; rest=${out#* }
  if [ "$code" != "$2" ] || { [ -n "$3" ] && [[ "$rest" != *"$3"* ]]; }; then echo "FAIL $1 -> $out (want $2 $3)"; fail=1; else echo "ok   $1 -> $code ${3:+($3)}"; fi
}
for p in / /about/ /contact/ /portfolio/ /blog/ /design-and-build/ /locations/ /locations/canterbury/ /clinical-veterinary-fit-outs/ \
         /project/vet-shack/ /sector/new-builds/ /testimonial/vetshack/ /category/extensions/ /what-is-a-passive-house/ /privacy-policy/ /cookies/; do check "$p" 200 text/html; done
check /feed/ 200 rss
check /sitemap_index.xml 200 xml
check /project-sitemap.xml 200 xml
check /llms.txt 200 text/plain
check /llms-full.txt 200 text/plain
check /about.md 200 markdown
check "/about/?output_format=md" 200 markdown
check /robots.txt 200 text/plain
check /wp-content/uploads/2024/12/separator.jpg 200 image/jpeg
check "/_vercel/image?url=%2Fwp-content%2Fuploads%2F2024%2F12%2Fseparator.jpg&w=768&q=75" 200 image/
check /this-page-does-not-exist/ 404
# redirects (301 + target)
check /about 301 /about/
check /placeholder-blog-post-6/ 301 /what-is-a-passive-house/
check /author/connor/ 301 /blog/
check /category/uncategorized/ 301 /blog/
check /blog/page/2/ 301 /blog/
check /2025/ 301 /blog/
check /vet-shack/ 301 /project/vet-shack/
check /canterbury/ 301 /locations/canterbury/
check /privacy/ 301 /privacy-policy/
check /sitemap.xml 301 /sitemap_index.xml
check /comments/feed/ 301 /feed/
check "/?s=kent" 301
check "/?page_id=7" 301
check /index.php 301
check /myworksafecompliancepack-1/ 301 /wp-content/uploads/2026/10/myWorksafeCompliancePack-1.pdf
exit $fail
