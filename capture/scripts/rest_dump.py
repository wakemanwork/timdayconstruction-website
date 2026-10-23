import json, urllib.request, sys, os
B='https://timdayconstruction.co.uk/wp-json/wp/v2/'
out='capture/rest'
def get(path):
    items=[];page=1
    while True:
        sep='&' if '?' in path else '?'
        u=f"{B}{path}{sep}per_page=100&page={page}"
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 migration-capture'}),timeout=60)
        except urllib.error.HTTPError as e:
            if e.code==400: break
            print(path,e.code); break
        d=json.load(r); items+=d
        tp=int(r.headers.get('X-WP-TotalPages','1'))
        if page>=tp: break
        page+=1
    return items
for t in ['posts','pages','project','sector','testimonial','media','categories','tags','users','menu-items','blocks']:
    try:
        d=get(t+'?context=view')
    except Exception as e:
        print(t,'ERR',e); continue
    json.dump(d,open(f'{out}/{t}.json','w'),indent=1)
    print(t,len(d))
# taxonomies list
for p in ['taxonomies','types']:
    d=json.load(urllib.request.urlopen(B+p,timeout=60)); json.dump(d,open(f'{out}/{p}.json','w'),indent=1)
    print(p,list(d))
