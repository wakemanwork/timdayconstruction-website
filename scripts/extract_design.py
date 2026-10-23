"""Extract Design & Build, the location pages, the locations hub and the 404 page into src/data/pages/.
Run: python3 -I scripts/extract_design.py [path/to/live-404.html]

Sources: capture/html/design-and-build.html, capture/html/locations__{canterbury,whitstable}.html,
capture/meta/*.json (titles, dates). The 404 page is not in capture/: fetch it with
  curl -sS -o 404.html https://timdayconstruction.co.uk/this-page-does-not-exist-xyz/
and pass the file path; without it the existing src/data/pages/error-404.json is kept.
Copy for the new /locations/ hub (F1) is drafted below (HUB_DRAFT) for Simon's approval; everything
else on that page is reused from captured copy.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *
from extractlib import applied

PAGES = DATA / 'pages'
PAGES.mkdir(parents=True, exist_ok=True)

# F10: these pages have no Yoast description. Drafts per VOICE.md 7.8, for Simon's approval.
DRAFT_DESCRIPTIONS = {
    'design-and-build': 'Design & Build with Tim Day Construction: one contract and one team from first enquiry '
                        'to handover, with professional indemnity cover. See our process.',
    'locations__canterbury': 'Tim Day Construction builds new homes, extensions and veterinary fit-outs in Canterbury, '
                             'including Vet Shack. See our local projects and get in touch.',
    'locations__whitstable': 'Tim Day Construction builds new homes and extensions in Whitstable, including Castle Road '
                             'and Middle Wall, on tight coastal sites. See our local projects.',
}


def seo(name):
    m = meta(name)
    m['description'] = m['description'] or DRAFT_DESCRIPTIONS.get(name)
    pub, mod = wp_dates(name)
    return {**m, 'published': pub, 'modified': mod}


def dump(name, data):
    (PAGES / f'{name}.json').write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')


def wp_dates(name):
    m = json.loads((CAP / 'meta' / f'{name}.json').read_text())
    for g in m.get('jsonld', []):
        for node in g.get('@graph', []):
            if node.get('@type') == 'WebPage':
                return node.get('datePublished'), node.get('dateModified')
    return None, None


def local_links(el):
    """The live Canterbury copy links to a developer host (http://tim-day.local/...). Point it at the site."""
    for a in el.find_all('a', href=True):
        a['href'] = re.sub(r'^https?://tim-day\.local', '', a['href'])
        if a['href'] == '/contact':
            a['href'] = '/contact/'
    return el


# ---------------- DESIGN & BUILD ----------------
name = 'design-and-build'
s = soup(CAP / 'html' / f'{name}.html')
intro = s.select_one('#design-and-build .intro .content')
timeline = s.select_one('.timeline-container')
riba = s.select_one('#riba-stages')
dump(name, {
    'seo': seo(name),
    'banner': {'title': inner(s.select_one('.page-title-banner__title'), name),
               'image': rel(s.select_one('.page-title-banner__image')['src'])},
    'intro': {
        'paragraphs': [inner(p, name) for p in intro.select('p')],
        'list': [inner(li, name) for li in intro.select('li')],
    },
    'timeline': {
        'heading': inner(timeline.select_one('.section-heading'), name),
        'milestones': [{'title': inner(li.select_one('h3'), name), 'body': inner(li.select_one('p'), name)}
                       for li in timeline.select('.milestone')],
    },
    'bottomText': [inner(p, name) for p in s.select('.timeline-bottom-text .content p')],
    'riba': {
        'heading': inner(riba.select_one('.section-heading'), name),
        'stages': [{'number': inner(li.select_one('.riba-stage__number'), name),
                    'heading': inner(li.select_one('.riba-stage__heading'), name),
                    'body': inner(li.select_one('.riba-stage__body'), name)}
                   for li in riba.select('.riba-stage')],
    },
})

# ---------------- LOCATION PAGES ----------------
locations = {}
for town in ('canterbury', 'whitstable'):
    name = f'locations__{town}'
    s = soup(CAP / 'html' / f'{name}.html')
    rows = []
    for row in s.select('.location-content'):
        content = local_links(row.select_one('.content'))
        img = row.select_one('.image-side img')
        rows.append({
            'heading': inner(row.select_one('h2'), name),
            'paragraphs': [inner(p, name) for p in content.select('p')],
            'image': rel(img['src']) if img else None,
        })
    lp = s.select_one('.location-projects')
    why = local_links(s.select_one('.why-choose-tdc'))
    btn = why.select_one('a.btn')
    data = {
        'seo': seo(name),
        'banner': {'title': inner(s.select_one('.page-title-banner__title'), name),
                   'image': rel(s.select_one('.page-title-banner__image')['src'])},
        'rows': rows,
        'projects': {
            'heading': inner(lp.select_one('h2'), name),
            'intro': inner(lp.select_one('.width-container p'), name),
            'cards': [{'title': txt(b.select_one('.project-block-overlay__title'), name),
                       'location': txt(b.select_one('.project-block-overlay__location'), name),
                       'href': rel(b.select_one('a')['href']),
                       'image': rel(b.select_one('img')['src'])}
                      for b in lp.select('.project-block')],
        },
        'why': {
            'heading': inner(why.select_one('h2'), name),
            'button': {'label': txt(btn, name), 'href': btn['href']},
            'paragraphs': [inner(p, name) for p in why.select('.content p')],
        },
    }
    dump(f'location-{town}', data)
    locations[town] = data

# ---------------- LOCATIONS HUB (new page, F1) ----------------
# Reused verbatim: the banner photo (both location pages use it), the town names, and the CTA
# heading/button used on 11 project pages. Drafted (for approval): intro, card images, CTA body.
cta_src = soup(CAP / 'html' / 'project__old-dover-road.html').select_one('#project-cta')
HUB_DRAFT = {
    'intro': ('Tim Day Construction is based just outside Canterbury. '
              'Choose a town to see how we work there and the projects we’ve completed nearby.'),
    'cardsTitle': 'Where We Work',  # the About page's heading for the same list
    'cardImages': {
        'canterbury': '/wp-content/uploads/2024/12/IMG_0443-scaled.jpg',   # Vet Shack, Canterbury
        'whitstable': '/wp-content/uploads/2024/12/front-from-beach-1.jpg',  # "Working in Whitstable" photo
    },
    'ctaBody': ('Based just outside Canterbury, we work across Kent, including Whitstable, Faversham, '
                'Herne Bay and the surrounding areas. Tell us about your project and we’ll talk you through the next steps.'),
    'description': ('Tim Day Construction is based near Canterbury and builds across Kent. '
                    'See our work and local projects in Canterbury and Whitstable, then get in touch.'),
}
dump('locations', {
    'seo': {'title': None, 'description': HUB_DRAFT['description'],
            'published': '2026-01-07T18:06:30+00:00', 'modified': None},
    'banner': {'title': 'Locations', 'image': locations['canterbury']['banner']['image']},
    'intro': HUB_DRAFT['intro'],
    'cards': {
        'title': HUB_DRAFT['cardsTitle'],
        'cards': [{'label': locations[t]['banner']['title'], 'href': f'/locations/{t}/',
                   'image': HUB_DRAFT['cardImages'][t]} for t in ('canterbury', 'whitstable')],
    },
    'cta': {
        'title': inner(cta_src.select_one('.project-cta__title'), 'locations'),
        'body': HUB_DRAFT['ctaBody'],
        'button': inner(cta_src.select_one('.project-cta__btn'), 'locations'),
        'href': rel(cta_src.select_one('.project-cta__btn')['href']),
    },
})

# ---------------- 404 ----------------
if len(sys.argv) > 1:
    s = soup(sys.argv[1])
    c = s.select_one('#error-404__container')
    btn = c.select_one('a.btn')
    dump('error-404', {
        'title': s.title.get_text(strip=True),
        'heading': txt(c.select_one('.error-404__title'), '404'),
        'subtitle': txt(c.select_one('.error-404__subtitle'), '404'),
        'button': {'label': txt(btn, '404'), 'href': rel(btn['href']) or '/'},
    })

save_fixes('design')
print('design: wrote', sorted(p.name for p in PAGES.glob('*.json')), '| fixes applied:', len(applied))
