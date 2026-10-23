B=https://timdayconstruction.co.uk
probe(){ curl -sS -m 20 -o /dev/null -w "%{http_code}\t%{redirect_url}\t$1\n" "$B$1"; }
for p in /about /contact /blog /portfolio /project/vet-shack /index.php /?p=1 /?page_id=7 /?p=99999 \
 /blog/page/2/ /page/2/ /feed/ /feed /comments/feed/ /category/uncategorized/feed/ /author/connor/feed/ /project/feed/ /project/ /sector/ /testimonial/ \
 /vet-shack/ /pure-vet-ashford/ /stables/ /preston /placeholder /passive-house/ /what-is-a-passive-house/ /veterinary-fit-outs/ /new-builds/ /canterbury/ /whitstable/ \
 /services/ /projects/ /our-work/ /news/ /home/ /sample-page/ /hello-world/ /privacy/ /cookie-policy/ /contact-us/ /about-us/ /team/ /gallery/ \
 /tag/kent/ /2025/ /2026/10/ /wp-json/ /xmlrpc.php /wp-login.php /sitemap.xml /wp-sitemap.xml /sitemap_index.xml /llms.txt \
 /type/image/ /search/kent/ "/?s=kent" /attachment/ /tim-day-construction/ /wp-content/uploads/2024/12/separator.jpg ; do probe "$p"; done
# attachment pages for media
python3 -c "
import json;[print(m['link']) for m in json.load(open('capture/rest/media.json'))[:8]]" | while read u; do curl -sS -m 20 -o /dev/null -w "%{http_code}\t%{redirect_url}\t$u\n" "$u"; done
