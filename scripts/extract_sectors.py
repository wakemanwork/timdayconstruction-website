"""Extract the two service pages (WordPress template-service.php) into src/data/pages/<slug>.json.

Sources: capture/html/<slug>.html (rendered page), capture/meta/<slug>.json (Yoast SEO),
capture/rest/pages.json (dates). Sector pages come from src/content/sectors (scripts/extract.py).
Run: python3 -I scripts/extract_sectors.py
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *; from extractlib import applied

PAGES = ['clinical-veterinary-fit-outs', 'new-homes-and-residential']
REST = {p['slug']: p for p in rest('pages')}
OUT_DIR = DATA / 'pages'
OUT_DIR.mkdir(parents=True, exist_ok=True)

for slug in PAGES:
    s = soup(CAP / 'html' / f'{slug}.html')
    r = REST[slug]

    # Intro (#meet-the-founder markup): heading, paragraphs (inner HTML kept as live, including
    # the leading <br> and the empty trailing paragraph, which set the live spacing), image.
    mf = s.select_one('#meet-the-founder')
    intro = {
        'title': inner(mf.select_one('.text-side .section-title'), slug),
        'paragraphs': [inner(p, slug) for p in mf.select('.text-side .content p')],
        'image': rel(mf.select_one('.image-side img')['src']),
    }

    # Alternating teal/white text sections (.about.green-bg / .about.white-bg)
    sections = []
    for sec in s.select('section.about'):
        sections.append({
            'tone': 'green' if 'green-bg' in sec['class'] else 'white',
            'title': inner(sec.select_one('.about__section-title'), slug),
            'body': md(sec.select_one('.about__body').decode_contents(), slug),
        })

    sp = s.select_one('#service-projects')
    projects = {
        'title': inner(sp.find('h3', recursive=False), slug),
        'slugs': [rel(a['href']).strip('/').split('/')[-1] for a in sp.select('.project-block a[href]')],
    }

    fq = s.select_one('#sector-faq')
    faq = {
        'label': txt(fq.select_one('.section-label')),
        'title': txt(fq.select_one('h2')),
        'items': [{'q': txt(d.select_one('summary'), slug), 'a': md(d.select_one('.sector-faq__panel').decode_contents(), slug)}
                  for d in fq.select('details.sector-faq')],
    }

    cta = s.select_one('#sector-cta')
    data = {
        'title': inner(s.select_one('.page-title-banner__title'), slug),
        'bannerImage': rel(s.select_one('.page-title-banner__image')['src']),
        'published': r['date_gmt'] + 'Z',
        'modified': r['modified_gmt'] + 'Z',
        'intro': intro,
        'sections': sections,
        'projects': projects,
        'faq': faq,
        'cta': {
            'title': inner(cta.select_one('.sector-cta__title'), slug),
            'body': md(cta.select_one('.sector-cta__body').decode_contents(), slug),
            'button': inner(cta.select_one('.sector-cta__btn'), slug),
            'href': rel(cta.select_one('.sector-cta__btn')['href']),
        },
        'seo': meta(slug),
    }
    (OUT_DIR / f'{slug}.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(slug, len(sections), 'sections,', len(faq['items']), 'FAQs,', len(projects['slugs']), 'projects')

save_fixes('sectors')
print('fixes applied:', len(applied))
