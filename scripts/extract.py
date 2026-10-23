"""Extract WordPress content from the Phase 1 capture into Astro content collections.

Sources: capture/html/*.html (rendered pages, the truth for ACF-driven fields),
capture/rest/*.json (post/project bodies, dates, categories), capture/meta/*.json (SEO).
Copy is never retyped. Agreed corrections (fix log F19/F20) go through FIXES and are
logged to capture/fixes-applied.json so the text-diff report can account for them.

Run: python3 -I scripts/extract.py
"""
import json, re, os, html as htmllib
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify

ROOT = Path(__file__).resolve().parent.parent
CAP = ROOT / 'capture'
OUT = ROOT / 'src' / 'content'
DATA = ROOT / 'src' / 'data'
SITE = 'https://timdayconstruction.co.uk'

# --- Agreed copy fixes (F19). (find, replace) applied to extracted text, logged. ---
FIXES = [
    ('yoru project', 'your project'),
    ('It providers cover', 'It provides cover'),
    ('recoveryto', 'recovery to'),
    ('We provide offer a concept to completion', 'We offer a concept to completion'),
    ('extensions to and change of use', 'extensions to change of use'),
    ('team include those', 'team includes those'),
    ('30 years’ of', '30 years of'),
    ('firmly embed in Kent', 'firmly embedded in Kent'),
    ('Why Should you Choose', 'Why Should You Choose'),
    ('wood fiber', 'wood fibre'),
    ('Veterinary Fitout', 'Veterinary Fit-Out'),
    ('veterinary fitouts', 'veterinary fit-outs'),
]
applied = []

def fix(text, where):
    for a, b in FIXES:
        if a in text:
            applied.append({'where': where, 'from': a, 'to': b, 'count': text.count(a)})
            text = text.replace(a, b)
    # straight apostrophes between letters -> curly (F19)
    new = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", '’', text)
    if new != text:
        applied.append({'where': where, 'from': "'", 'to': '’', 'count': len(re.findall(r"(?<=[A-Za-z])'(?=[A-Za-z])", text))})
    return new

def soup(path):
    return BeautifulSoup(Path(path).read_text(), 'lxml')

def rel(url):
    if not url:
        return url
    return url.replace(SITE, '') or '/'

def md(html_fragment, where, headings_from_bold=False):
    s = BeautifulSoup(html_fragment, 'lxml')
    for a in s.find_all('a', href=True):
        a['href'] = rel(a['href'])
    for img in s.find_all('img'):
        if img.get('src'):
            img['src'] = rel(img['src'])
    if headings_from_bold:  # F20: bold-only paragraphs become H2 (same words)
        for p in s.find_all('p'):
            kids = [k for k in p.contents if not (isinstance(k, str) and not k.strip())]
            if len(kids) == 1 and getattr(kids[0], 'name', None) in ('strong', 'b'):
                h = s.new_tag('h2'); h.string = kids[0].get_text(strip=True)
                p.replace_with(h)
                applied.append({'where': where, 'from': 'bold paragraph', 'to': 'h2', 'count': 1, 'text': h.string})
    body = s.body.decode_contents() if s.body else str(s)
    text = markdownify(body, heading_style='ATX', bullets='-', escape_underscores=False, escape_asterisks=False)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    text = text.replace('\xa0', ' ')
    return fix(text, where)

def txt(el, where=''):
    if el is None:
        return None
    t = re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).replace('\xa0', ' ').strip()
    t = re.sub(r'\s+([,.!?;:])', r'\1', t)
    return fix(t, where) if where else t

def meta(name):
    m = json.loads((CAP / 'meta' / f'{name}.json').read_text())
    og = m.get('og', {})
    title = m['title']
    return {
        'title': htmllib.unescape(title) if title else None,
        'description': m.get('description'),
        'ogImage': rel(og.get('og:image')),
    }

def yaml_val(v, indent=0):
    pad = '  ' * indent
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        if '\n' in v:
            return '|\n' + '\n'.join(pad + '  ' + line for line in v.split('\n'))
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        if not v:
            return '[]'
        out = []
        for item in v:
            if isinstance(item, dict):
                first = True
                for k, val in item.items():
                    prefix = pad + ('- ' if first else '  ')
                    out.append(f'{prefix}{k}: {yaml_val(val, indent + 2)}')
                    first = False
            else:
                out.append(f'{pad}- {yaml_val(item, indent + 1)}')
        return '\n' + '\n'.join(out)
    if isinstance(v, dict):
        return '\n' + '\n'.join(f'{pad}  {k}: {yaml_val(val, indent + 1)}' for k, val in v.items())
    raise TypeError(v)

def write_md(path, fm, body=''):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['---'] + [f'{k}: {yaml_val(v)}' for k, v in fm.items()] + ['---', '']
    path.write_text('\n'.join(lines) + (body.strip() + '\n' if body else ''))

def rest(name):
    return json.loads((CAP / 'rest' / f'{name}.json').read_text())

cats = {c['id']: c['slug'] for c in rest('categories')}
users = {u['id']: u['name'] for u in rest('users')}

# --- project thumbnails/locations as shown on cards anywhere on the site ---
cards = {}
for f in (CAP / 'html').glob('*.html'):
    s = soup(f)
    for blk in s.select('.project-block a[href]'):
        slug = rel(blk['href']).strip('/').split('/')[-1]
        img = blk.select_one('img')
        cards.setdefault(slug, {
            'thumbnail': rel(img.get('src')) if img else None,
            'cardTitle': txt(blk.select_one('.project-block-overlay__title')),
            'cardLocation': txt(blk.select_one('.project-block-overlay__location')),
        })

# ---------------- PROJECTS ----------------
for p in rest('project'):
    slug = p['slug']; name = f'project__{slug}'
    s = soup(CAP / 'html' / f'{name}.html')
    info = {}
    for row in s.select('.project-info'):
        k = txt(row.select_one('.project-info__type'))
        v = txt(row.select_one('.project-info__value'))
        info[k] = v or None
    gallery = [rel(i.get('src')) for i in s.select('.project-image-carousel .swiper-slide img') if i.get('src')]
    cta = s.select_one('#project-cta')
    body_html = s.select_one('.project-column-content').decode_contents()
    fm = {
        'title': fix(htmllib.unescape(p['title']['rendered']), name),
        'date': p['date'], 'modified': p['modified'],
        'location': info.get('Location'), 'client': info.get('Client'),
        'typeOfWork': info.get('Type Of Work'), 'architect': info.get('Architect'),
        'status': info.get('Status'),
        'categories': [cats[c] for c in p.get('categories', [])],
        'bannerImage': rel(s.select_one('.page-title-banner__image')['src']),
        'thumbnail': cards.get(slug, {}).get('thumbnail'),
        'cardLocation': cards.get(slug, {}).get('cardLocation'),
        'gallery': gallery,
        'cta': {
            'title': txt(cta.select_one('.project-cta__title'), name),
            'body': md(cta.select_one('.project-cta__body').decode_contents(), name),
            'button': txt(cta.select_one('.project-cta__btn'), name),
        },
        'seo': meta(name),
    }
    write_md(OUT / 'projects' / f'{slug}.md', fm, md(body_html, name))

# ---------------- SECTORS ----------------
for p in rest('sector'):
    slug = p['slug']; name = f'sector__{slug}'
    s = soup(CAP / 'html' / f'{name}.html')
    col = s.select_one('.sector-intro-column')
    heading = col.select_one('h2')
    heading_text = txt(heading, name)
    heading.decompose()
    intro_img = s.select_one('.sector-intro img:not([src$=".svg"])')
    faq = [{'q': txt(d.select_one('summary'), name), 'a': md(d.select_one('.sector-faq__panel').decode_contents(), name)}
           for d in s.select('details.sector-faq')]
    cta = s.select_one('#sector-cta')
    fm = {
        'title': fix(htmllib.unescape(p['title']['rendered']), name),
        'date': p['date'], 'modified': p['modified'],
        'bannerImage': rel(s.select_one('.page-title-banner__image')['src']),
        'introHeading': heading_text,
        'introImage': rel(intro_img['src']) if intro_img else None,
        'projects': [rel(a['href']).strip('/').split('/')[-1] for a in s.select('.project-block a[href]')],
        'faqLabel': txt(s.select_one('#sector-faq .section-label')),
        'faqTitle': txt(s.select_one('#sector-faq h2')),
        'faq': faq,
        'cta': {
            'title': txt(cta.select_one('.sector-cta__title'), name),
            'body': md(cta.select_one('.sector-cta__body').decode_contents(), name),
            'button': txt(cta.select_one('.sector-cta__btn'), name),
        },
        'seo': meta(name),
    }
    write_md(OUT / 'sectors' / f'{slug}.md', fm, md(col.decode_contents(), name))

# ---------------- POSTS ----------------
blog = soup(CAP / 'html' / 'blog.html')
post_imgs = {}
for card in blog.select('.blog-card'):
    a = card.select_one('a[href]')
    img = card.select_one('img')
    if a and img:
        post_imgs[rel(a['href']).strip('/')] = rel(img.get('src'))
for p in rest('posts'):
    slug = p['slug']; name = slug
    new_slug = 'what-is-a-passive-house' if slug == 'placeholder-blog-post-6' else slug  # F2
    s = soup(CAP / 'html' / f'{name}.html')
    feat = s.select_one('.blog-featured-img img, img.blog-featured-img')
    fm = {
        'title': fix(htmllib.unescape(p['title']['rendered']), name),
        'slug': new_slug, 'wpSlug': slug,
        'date': p['date'], 'modified': p['modified'],
        'author': 'Tim Day Construction', 'wpAuthor': users.get(p['author']),
        'categories': [cats[c] for c in p['categories']],
        'featuredImage': rel(feat['src']) if feat and feat.get('src') else post_imgs.get(slug),
        'seo': meta(name),
    }
    write_md(OUT / 'posts' / f'{new_slug}.md', fm, md(p['content']['rendered'], name, headings_from_bold=True))

# ---------------- TESTIMONIALS ----------------
home = soup(CAP / 'html' / 'index.html')
carousel = {}
for card in home.select('#testimonials .testimonial-card'):
    nm = txt(card.select_one('.testimonial__name'))
    carousel[nm] = {
        'quote': txt(card.select_one('.testimonial'), 'testimonial:' + nm).strip('"“”'),
        'image': rel(card.select_one('.testimonial__featured-image').get('src')),
        'company': txt(card.select_one('.testimonial__company')) or None,
    }
for i, p in enumerate(rest('testimonial')):
    slug = p['slug']; nm = htmllib.unescape(p['title']['rendered'])
    c = carousel.get(nm, {})
    write_md(OUT / 'testimonials' / f'{slug}.md', {
        'name': nm, 'date': p['date'], 'modified': p['modified'],
        'quote': c.get('quote'), 'image': c.get('image'), 'company': c.get('company'),
        'order': list(carousel).index(nm) if nm in carousel else 99,
        'seo': meta(f'testimonial__{slug}'),
    })

# ---------------- HOME (page data) ----------------
h = home
hero = h.select_one('#hero')
def half(sel):
    d = hero.select_one(sel)
    btn = d.select_one('a')
    return {'heading': txt(d.select_one('h2')), 'subheading': txt(d.select_one('h3')),
            'body': txt(d.select_one('p')), 'button': {'label': txt(btn), 'href': rel(btn['href'])}}
def logos(container):
    return [{'href': rel(a['href']), 'src': rel(a.select_one('img')['src'])} for a in container.select('a') if a.select_one('img')]
intro = h.select_one('#intro')
intro_cols = intro.select('.intro-column')
dab = h.select_one('#design-and-build-section')
q = h.select_one('#quote')
home_data = {
    'hero': {
        'images': [rel(hero.select_one('.hero__bg-img-1')['src']), rel(hero.select_one('.hero__bg-img-2')['src'])],
        'left': half('.content_left'), 'right': half('.content_right'),
        'title': hero.select_one('.hero__title').decode_contents().strip(),
        'logos': logos(hero.select_one('.hero__logos')),
    },
    'intro': {
        'lead': intro_cols[0].select_one('h3').decode_contents().strip(),
        'body': txt(intro_cols[0].select_one('p')),
        'button': {'label': txt(intro_cols[0].select_one('a')), 'href': rel(intro_cols[0].select_one('a')['href'])},
        'text': [fix(t.strip(), 'home intro') for t in intro_cols[1].select_one('p').decode_contents().split('<br/><br/>')],
    },
    'designAndBuild': {
        'image': rel(dab.select_one('.image-side img')['src']),
        'heading': txt(dab.select_one('h2')),
        'paragraphs': [txt(p) for p in dab.select('.content p') if not p.select_one('a')],
        'button': {'label': txt(dab.select_one('.btn')), 'href': rel(dab.select_one('.btn')['href'])},
    },
    'sectors': {
        'title': txt(h.select_one('#sectors h2')),
        'cards': [{'label': txt(li.select_one('h3')), 'href': rel(li.select_one('a')['href']),
                   'image': rel(li.select_one('img')['src'])} for li in h.select('#sectors .sector-card')],
    },
    'threeBlocks': {
        'title': h.select_one('#three-blocks h2').decode_contents().strip(),
        'blocks': [{'label': txt(b.select_one('h3')), 'href': rel(b['href']),
                    'image': rel(b.select_one('.three-blocks__block-img')['src']),
                    'icon': rel(b.select_one('.three-blocks__block-icon')['src'])} for b in h.select('.three-blocks__block')],
    },
    'quote': {
        'text': txt(q.select_one('blockquote')),
        'image': rel(q.select_one('.image-side img')['src']),
        'button': {'label': txt(q.select_one('.btn')), 'href': rel(q.select_one('.btn')['href'])},
    },
    'howWeWork': {
        'title': h.select_one('#how-we-work h2').decode_contents().strip(),
        'blocks': [{'heading': txt(b.select_one('h3')), 'body': txt(b.select_one('p'))} for b in h.select('.how-we-work__block')],
    },
    'largeImage': rel(h.select_one('.homepage-large-image img')['src']),
    'testimonials': {
        'title': h.select_one('#testimonials h2').decode_contents().strip(),
        'intro': txt(h.select_one('.testimonials-title p')),
    },
    'seo': meta('index'),
}
DATA.mkdir(parents=True, exist_ok=True)
(DATA / 'home.json').write_text(json.dumps(home_data, indent=2, ensure_ascii=False))

# ---------------- SITE (shared header/footer) ----------------
foot = h.select_one('footer')
site = {
    'nav': [{'label': txt(a), 'href': rel(a['href']).rstrip('/') + '/'} for a in h.select('header nav ul.menu > li > a')],
    'phone': '01227 281 749', 'email': 'info@timdayconstruction.co.uk',
    'footerTitle': txt(foot.select_one('.footer-title')),
    'socials': [{'href': a['href'], 'label': 'Facebook' if 'facebook' in a['href'] else 'LinkedIn'} for a in foot.select('.footer-socials a')],
    'policy': [{'label': txt(a), 'href': rel(a['href'])} for a in foot.select('.footer-policy-pages a')],
    'accreditations': logos(foot.select_one('.footer-accreditations')),
    'charity': {'href': foot.select_one('.footer__charity-logo a')['href'], 'image': '/wp-content/themes/tim-day-custom-theme/assets/images/zarach.png'},
    'legal': txt(foot.select_one('.copyright')),
}
site['accreditations'] = [a for a in site['accreditations'] if 'zarach' not in a['href']]
(DATA / 'site.json').write_text(json.dumps(site, indent=2, ensure_ascii=False))

(CAP / 'fixes-applied.json').write_text(json.dumps(applied, indent=1, ensure_ascii=False))
print('projects', len(list((OUT / 'projects').glob('*.md'))), 'sectors', len(list((OUT / 'sectors').glob('*.md'))),
      'posts', len(list((OUT / 'posts').glob('*.md'))), 'testimonials', len(list((OUT / 'testimonials').glob('*.md'))))
print('fixes applied', len(applied))
