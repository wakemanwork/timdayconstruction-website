#!/usr/bin/env bash
# Lighthouse mobile + desktop for each path. Usage: scripts/qa/lighthouse.sh BASE_URL /path/ [/path2/ ...]
# Needs: CHROME_PATH, LH (path to the lighthouse binary). Writes qa/lighthouse/<slug>-<form>.json
base=$1; shift; mkdir -p qa/lighthouse
for path in "$@"; do
  slug=$(echo "$path" | sed 's#^/##; s#/$##; s#/#__#g'); slug=${slug:-home}
  for ff in mobile desktop; do
    extra=""; [ $ff = desktop ] && extra="--preset=desktop"
    "$LH" "$base$path" --chrome-flags="--headless=new --no-sandbox" $extra --output=json --output-path="qa/lighthouse/$slug-$ff.json" --quiet >/dev/null 2>&1
    python3 -I - "$slug" "$ff" <<'P'
import json, sys
slug, ff = sys.argv[1], sys.argv[2]
r = json.load(open(f'qa/lighthouse/{slug}-{ff}.json')); a = r['audits']
s = {k: round(v['score'] * 100) for k, v in r['categories'].items()}
print(f"{slug} {ff}: {s}  LCP {a['largest-contentful-paint']['displayValue']}  TBT {a['total-blocking-time']['displayValue']}  CLS {a['cumulative-layout-shift']['displayValue']}")
for k, v in a.items():
    if v.get('score') is not None and v['score'] < 0.9 and v.get('scoreDisplayMode') in ('binary', 'numeric', 'metricSavings'):
        print(f"   - {k}: {v.get('displayValue', '')} {v['title'][:90]}")
P
  done
done
