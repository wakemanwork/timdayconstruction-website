"""Extract page data for the projects area: /portfolio/, the project details labels and the
project category names. Project bodies themselves come from scripts/extract.py (src/content/projects).
Run: python3 -I scripts/extract_projects.py
Writes src/data/pages/{portfolio,project,categories}.json. Drafted copy (F7 intros, F10 meta
descriptions) is not extracted; it lives in src/data/pages/projects-drafts.json for approval.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *
from extractlib import applied

PAGES = DATA / 'pages'
PAGES.mkdir(exist_ok=True)

def dump(name, obj):
    (PAGES / f'{name}.json').write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n')

# ---------------- PORTFOLIO ----------------
name = 'portfolio'
s = soup(CAP / 'html' / f'{name}.html')
intro = s.select_one('.portfolio-page-intro__content')
rows = []
for cat in s.select('.portfolio-category'):
    btn = cat.select_one('.portfolio-category-column a.btn')
    href = rel(btn['href'])
    # Live "Listed Buildings" button points at an unpublished sector (/?post_type=sector&p=66, a 404).
    # It now goes to the listed-buildings category archive built under F7.
    if 'post_type=sector' in href:
        href = '/category/listed-buildings/'
    img_wrap = cat.find_next_sibling(class_='portfolio-category__image')
    rows.append({
        'title': txt(cat.select_one('.portfolio-category__title'), name),
        'tone': 'green' if 'green-bg' in cat['class'] else 'grey',
        'button': {'label': txt(btn, name), 'href': href},
        'body': [txt(p, name) for p in cat.select('.portfolio-category__body p')],
        'image': rel(img_wrap.select_one('img')['src']),
    })
page = next(p for p in rest('pages') if p['slug'] == 'portfolio')
dump('portfolio', {
    'title': txt(s.select_one('.page-title-banner__title'), name),
    'bannerImage': rel(s.select_one('.page-title-banner__image')['src']),
    'intro': {
        'heading': txt(intro.select_one('h2'), name),
        'body': [txt(p, name) for p in intro.select('p')],
    },
    'categories': rows,
    'date': page['date'], 'modified': page['modified'],
    'seo': meta(name),
})

# ---------------- PROJECT TEMPLATE LABELS ----------------
s = soup(CAP / 'html' / 'project__vet-shack.html')
dump('project', {
    'detailLabels': [txt(h) for h in s.select('.details-column .project-info__type')],
})
# DESIGN.md 6.14: rows with an empty value are omitted at build time. The live HTML still carries the
# empty "Architect" row (removed in the browser by theme JS), so log it for the text diff.
for p in rest('project'):
    name = f"project__{p['slug']}"
    for row in soup(CAP / 'html' / f'{name}.html').select('.details-column .project-info'):
        if not txt(row.select_one('.project-info__value')):
            applied.append({'where': name, 'from': txt(row.select_one('.project-info__type')), 'to': '',
                            'count': 1, 'note': 'empty details row omitted (live theme removed it in JS)'})

# ---------------- CATEGORIES (F7) ----------------
cats = []
for c in rest('categories'):
    if c['slug'] == 'uncategorized':  # 301 -> /blog/ (F3)
        continue
    cats.append({
        'slug': c['slug'],
        'name': htmllib.unescape(c['name']),
        'seo': meta(f"category__{c['slug']}"),
    })
dump('categories', cats)

save_fixes('projects')
print('portfolio rows:', len(rows), '| labels ok | categories:', len(cats), '| fixes applied:', len(applied))
