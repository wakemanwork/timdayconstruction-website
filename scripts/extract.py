"""Extract posts, projects, sectors, testimonials, home and site data from capture/ into src/.
Run: python3 -I scripts/extract.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *
from extractlib import applied

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
            'title': inner(cta.select_one('.project-cta__title'), name),
            'body': md(cta.select_one('.project-cta__body').decode_contents(), name),
            'button': inner(cta.select_one('.project-cta__btn'), name),
            'href': rel(cta.select_one('.project-cta__btn')['href']),
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
            'title': inner(cta.select_one('.sector-cta__title'), name),
            'body': md(cta.select_one('.sector-cta__body').decode_contents(), name),
            'button': inner(cta.select_one('.sector-cta__btn'), name),
            'href': rel(cta.select_one('.sector-cta__btn')['href']),
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

save_fixes('collections')
print('projects', len(list((OUT / 'projects').glob('*.md'))), 'sectors', len(list((OUT / 'sectors').glob('*.md'))),
      'posts', len(list((OUT / 'posts').glob('*.md'))), 'testimonials', len(list((OUT / 'testimonials').glob('*.md'))))
print('fixes applied', len(applied))
