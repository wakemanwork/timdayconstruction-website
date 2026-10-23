import json,re,os,glob,urllib.request,urllib.parse
from concurrent.futures import ThreadPoolExecutor
B='https://timdayconstruction.co.uk'
urls=set()
pat=re.compile(r'(?:https?:)?//timdayconstruction\.co\.uk(/wp-content/[^"\'\s\)<>,]+)|["\'\(](/wp-content/[^"\'\s\)<>,]+)')
for f in glob.glob('capture/html/*.html')+glob.glob('capture/extras/*'):
    for a,b in pat.findall(open(f,errors='ignore').read()): urls.add(a or b)
for m in json.load(open('capture/rest/media.json')):
    urls.add(urllib.parse.urlparse(m['source_url']).path)
    for s in (m.get('media_details') or {}).get('sizes',{}).values():
        urls.add(urllib.parse.urlparse(s['source_url']).path)
urls={u.split('?')[0].split('#')[0] for u in urls}
urls={u.replace('&#038;','&') for u in urls if not u.endswith('/')}
print('candidates',len(urls))
def dl(p):
    out='public'+urllib.parse.unquote(p)
    if os.path.exists(out): return p,'cached'
    os.makedirs(os.path.dirname(out),exist_ok=True)
    try:
        r=urllib.request.urlopen(urllib.request.Request(B+urllib.parse.quote(urllib.parse.unquote(p)),headers={'User-Agent':'Mozilla/5.0'}),timeout=120)
        open(out,'wb').write(r.read()); return p,r.status
    except Exception as e: return p,str(e)
res=list(ThreadPoolExecutor(12).map(dl,sorted(urls)))
bad=[r for r in res if r[1] not in (200,'cached')]
print('ok',len(res)-len(bad),'failed',len(bad))
for b in bad: print(b)
json.dump(sorted(urls),open('capture/asset-urls.json','w'),indent=0)
