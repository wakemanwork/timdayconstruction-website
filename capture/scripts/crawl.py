import json,re,os,urllib.request,hashlib
from bs4 import BeautifulSoup
from markdownify import markdownify as md
UA={'User-Agent':'Mozilla/5.0 (Macintosh) migration-capture'}
B='https://timdayconstruction.co.uk'
def fetch(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60)
    return r.status,r.read().decode('utf-8','replace')
def slugpath(u):
    p=u.replace(B,'').strip('/') or 'index'
    return p.replace('/','__')
urls=[l.strip() for l in open('capture/urls.txt') if l.strip()]
inv=[]
for u in urls:
    st,h=fetch(u); n=slugpath(u)
    open(f'capture/html/{n}.html','w').write(h)
    s=BeautifulSoup(h,'lxml')
    def m(sel,attr='content'):
        t=s.select_one(sel); return t.get(attr) if t else None
    jl=[json.loads(x.string) for x in s.select('script[type="application/ld+json"]') if x.string]
    body=s.body.get('class',[]) if s.body else []
    meta=dict(url=u,status=st,bytes=len(h),
      title=s.title.string if s.title else None,
      description=m('meta[name="description"]'),
      robots=m('meta[name="robots"]'),
      canonical=m('link[rel="canonical"]','href'),
      og={t.get('property'):t.get('content') for t in s.select('meta[property^="og:"]')},
      twitter={t.get('name'):t.get('content') for t in s.select('meta[name^="twitter:"]')},
      h1=[x.get_text(' ',strip=True) for x in s.select('h1')],
      body_class=body, jsonld=jl,
      images=[dict(src=i.get('src') or i.get('data-src'),alt=i.get('alt')) for i in s.select('img')],
      links=sorted({a.get('href') for a in s.select('a[href]')}))
    json.dump(meta,open(f'capture/meta/{n}.json','w'),indent=1)
    # main content = between header and footer
    for t in s.select('script,style,noscript,header,footer,.entrance-animation,.device-menu'): t.decompose()
    main=s.body
    text=md(str(main),heading_style='ATX',strip=['span']) if main else ''
    text=re.sub(r'\n{3,}','\n\n',text).strip()
    fm=f"---\nurl: {u}\ntitle: {json.dumps(meta['title'])}\ndescription: {json.dumps(meta['description'])}\n---\n\n"
    open(f'capture/md/{n}.md','w').write(fm+text+'\n')
    inv.append(dict(url=u,status=st,title=meta['title'],template=[c for c in body if c.startswith(('page-template','single-','archive','category','author','home','page-id','blog'))],words=len(text.split()),desc=bool(meta['description']),canonical_ok=meta['canonical']==u, h1=len(meta['h1']), schema=[x.get('@type') for j in jl for x in j.get('@graph',[j])]))
    print(st,n,len(text.split()))
json.dump(inv,open('capture/inventory.json','w'),indent=1)
# extras
for p in ['robots.txt','feed/','comments/feed/','sitemap_index.xml','post-sitemap.xml','page-sitemap.xml','project-sitemap.xml','sector-sitemap.xml','testimonial-sitemap.xml','category-sitemap.xml','author-sitemap.xml','main-sitemap.xsl']:
    try:
        st,h=fetch(B+'/'+p); os.makedirs('capture/extras',exist_ok=True)
        open('capture/extras/'+p.strip('/').replace('/','__'),'w').write(h); print('extra',p,st)
    except Exception as e: print('extra',p,e)
