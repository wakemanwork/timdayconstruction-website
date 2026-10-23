"""Extract /about/ and /contact/ page data from capture/html into src/data/pages/{about,contact}.json.
Run: python3 -I scripts/extract_about.py
Copy is never retyped: every string comes from the capture through fix()/md()/txt()/inner(),
so the agreed F19 corrections apply and are logged to capture/fixes/about.json.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *
from extractlib import applied, FIXES

# F19 fix in scope for this area, not in the shared list: the broken sentence on About
# ("…Veterinary practices Based just outside Canterbury…"). Appended at runtime so fix() applies and logs it.
FIXES.append(('We have experience in Veterinary practices Based just outside Canterbury',
              'We have experience in veterinary practices. Based just outside Canterbury'))
# The shared "30 years’ of" fix misses the body copy, where "of" opens a <strong> run (markdown "30 years’ **of").
FIXES.append(('30 years’ **of', '30 years **of'))

PAGES = DATA / 'pages'
PAGES.mkdir(parents=True, exist_ok=True)


def tel(href):
    return href.replace(' ', '')


def form_fields(form):
    """Labels, names, required flags and limits of the live CF7 form (DESIGN.md 6.21)."""
    out = []
    for lab in form.select('label'):
        ctl = lab.select_one('input, textarea')
        if ctl is None or ctl.get('type') == 'submit':
            continue
        out.append({
            'label': txt(lab),
            'cf7Name': ctl.get('name'),
            'type': 'textarea' if ctl.name == 'textarea' else ctl.get('type', 'text'),
            'required': ctl.get('aria-required') == 'true',
            'maxlength': int(ctl['maxlength']) if ctl.get('maxlength') else None,
            'autocomplete': ctl.get('autocomplete'),
        })
    submit = form.select_one('input[type=submit]')
    return {'fields': out, 'submit': submit.get('value')}


# ---------------- ABOUT ----------------
name = 'about'
s = soup(CAP / 'html' / 'about.html')

founder = s.select_one('#meet-the-founder')
fcontent = founder.select_one('.content')
lead = fcontent.select_one('h3')
founder_data = {
    'title': txt(founder.select_one('.section-title'), name),
    'lead': txt(lead, name),
    'body': md(''.join(str(p) for p in fcontent.select('p')), name),
    'image': rel(founder.select_one('.image-side img')['src']),
}

www = s.select_one('#where-we-work')
locs = []
for li in www.select('.work-location'):
    a = li.select_one('a')
    href = rel(a.get('href')) if a and a.get('href') else None
    locs.append({
        'name': txt(li.select_one('.work-location__name'), name),
        'description': txt(li.select_one('.work-location__description'), name),
        'href': href,  # live renders empty-href links with pointer-events:none; we render those as plain text
    })
btn = www.select_one('.text-side .btn')
mapblk = www.select_one('.where-we-work-map')
where = {
    'title': txt(www.select_one('.section-title'), name),
    'body': md(www.select_one('.text-side .content').decode_contents(), name),
    'button': {'label': txt(btn, name), 'href': rel(btn['href'])},
    'locations': locs,
    'mapImage': rel(mapblk.select_one('img')['src']),
    'mapBody': md(mapblk.select_one('.content').decode_contents(), name),
}

sections = []
for sec in s.select('section.about'):
    surface = 'green' if 'green-bg' in sec['class'] else 'white'
    title_el = sec.select_one('.about__section-title')
    sections.append({
        'surface': surface,
        'icon': sec.select_one('.background-faded-icon')['src'].rsplit('/', 1)[-1],
        'title': inner(title_el, name),  # HTML: keeps the .light-teal-txt highlight span
        'body': md(sec.select_one('.about__body').decode_contents(), name),
    })

ac = s.select_one('.about-contact')
cols = ac.select('.about-contact__column')
methods = []
for m in cols[0].select('.contact-method'):
    a = m.select_one('a')
    icon = txt(m.select_one('.material-symbols-outlined'))
    methods.append({'icon': 'mail' if icon == 'email' else icon, 'label': txt(a), 'href': tel(a['href'])})
about_contact = {
    'title': inner(cols[0].select_one('.about-contact__title'), name),
    'methods': methods,
    'formTitle': txt(cols[1].select_one('h3'), name),
    'form': form_fields(cols[1].select_one('form')),
}

carousel = [rel(i['src']) for i in s.select('.about-image-carousel .swiper-slide img') if i.get('src')]

m = meta(name)
about = {
    'banner': {'title': txt(s.select_one('.page-title-banner__title'), name),
               'image': rel(s.select_one('.page-title-banner__image')['src'])},
    'founder': founder_data,
    'where': where,
    'sections': sections,
    'contact': about_contact,
    'carousel': carousel,
    'seo': {**m, 'description': fix(m['description'], name) if m['description'] else None},
}
(PAGES / 'about.json').write_text(json.dumps(about, indent=2, ensure_ascii=False))

# ---------------- CONTACT ----------------
name = 'contact'
s = soup(CAP / 'html' / 'contact.html')
cp = s.select_one('.contact-page')
titles = cp.select_one('.contact-page-titles')
methods = []
for c in cp.select('.contact-method__container'):
    i = c.select_one('.contact-method__icon i')
    a = c.select_one('.contact-method a')
    methods.append({
        'icon': 'phone' if 'fa-phone' in i['class'] else 'envelope',
        'label': txt(c.select_one('.contact-method h4'), name),
        'value': txt(a),
        'href': tel(a['href']),
    })
socials = cp.select_one('.contact-page-socials')
cf = cp.select_one('.contact-form')
contact = {
    'banner': {'title': txt(s.select_one('.page-title-banner__title'), name),
               'image': rel(s.select_one('.page-title-banner__image')['src'])},
    'title': txt(titles.select_one('h2'), name),
    'intro': txt(titles.select_one('p'), name),
    'methods': methods,
    'socialsTitle': txt(socials.select_one('h2'), name),
    'socials': [{'href': a['href'], 'label': 'Facebook' if 'facebook' in a['href'] else 'LinkedIn'}
                for a in socials.select('.social-icons a')],
    'formTitle': txt(cf.select_one('h2'), name),
    'form': form_fields(cf.select_one('form')),
    'mapImage': rel(s.select_one('.location-map img')['src']),
    'seo': meta(name),
}
(PAGES / 'contact.json').write_text(json.dumps(contact, indent=2, ensure_ascii=False))

# textdiff.py compares with curly apostrophes folded to straight ones, but builds its fix-word list
# without folding, so the "30 years’ of" fix above can't be matched. Log the same fix once more in
# its folded form so the report recognises it (no extra change to the copy).
if any(a['from'] in ('30 years’ of', '30 years’ **of') for a in applied):
    applied.append({'where': 'about', 'from': "30 years' of", 'to': '30 years of', 'count': 0,
                    'note': 'same F19 fix, apostrophe folded for textdiff matching'})
save_fixes('about')
print('about + contact written; fixes applied:', len(applied))
for a in applied:
    print(' ', a['where'], '|', a['from'], '->', a['to'])
