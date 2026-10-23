"""Extraction for the blog area: /blog/, /feed/ data, /privacy-policy/, /cookies/.

Run: python3 -I scripts/extract_blog.py
Writes:
  src/data/pages/blog.json            blog index banner + SEO (from capture/html/blog.html, capture/rest/pages.json)
  src/data/pages/posts.json           per-post feed GUID (WordPress ?p=<id>, kept so feed readers don't re-show items)
                                      and the drafted meta description (F10, awaiting Simon's approval)
  src/data/pages/privacy-policy.json  Privacy text restored verbatim from REST content.rendered (F1)
  src/data/pages/cookies.json         Cookies text restored from REST, with the cookie list updated (F1, TDC sign-off)
Post bodies themselves were extracted by scripts/extract.py (src/content/posts/*.md).
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extractlib import *  # noqa: F401,F403
from extractlib import applied  # noqa: F401
from bs4 import BeautifulSoup

PAGES = DATA / 'pages'
PAGES.mkdir(parents=True, exist_ok=True)
wp_pages = {p['slug']: p for p in rest('pages')}
wp_posts = {p['slug']: p for p in rest('posts')}


def dump(name, obj):
    (PAGES / f'{name}.json').write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n')


def gmt(s):
    return s + 'Z'


# ---------- /blog/ ----------
s = soup(CAP / 'html' / 'blog.html')
banner = s.select_one('.page-title-banner')
blog = wp_pages['blog']
dump('blog', {
    'title': txt(banner.select_one('.page-title-banner__title'), 'blog'),
    'bannerImage': rel(banner.select_one('.page-title-banner__image')['src']),
    'published': gmt(blog['date_gmt']),
    'modified': gmt(blog['modified_gmt']),
    'seo': {
        **meta('blog'),
        # F10 draft (VOICE.md 7.8), awaiting Simon's approval
        'description': 'Practical guides from Tim Day Construction on veterinary and clinical fit-outs, Passive House principles and building in Kent. Read the latest.',
    },
})

# ---------- posts: feed GUIDs + drafted meta descriptions (F10) ----------
DESCRIPTIONS = {  # drafts per VOICE.md 7.8, 140–155 characters, awaiting Simon's approval
    'common-challenges-on-kent-building-sites':
        'Planning delays, weather and supply chains: the common challenges on Kent building sites and how Tim Day Construction plans around them from day one.',
    'fire-safety-requirements-in-veterinary-practices':
        'Fire doors, detection, materials and evacuation plans for animals and staff: what fire safety means in a veterinary fit-out, from Tim Day Construction.',
    'how-to-plan-a-successful-veterinary-practice-refurbishment':
        'Set clear objectives, assess your space and plan for growth. How to plan a veterinary practice refurbishment, from the team behind Vet Shack, Canterbury.',
    'how-to-plan-a-veterinary-fit-out-project-from-concept-to-completion':
        'Design, compliance, construction and specialist installations: how Tim Day Construction runs a veterinary fit-out from concept to completion. Talk to us.',
    'key-safety-considerations-in-veterinary-practice-fit-outs':
        'X-ray shielding, hygienic surfaces, ventilation, flooring and clinical waste: the safety essentials of a veterinary fit-out, from Tim Day Construction.',
    'maximising-efficiency-space-planning-tips-for-veterinary-practices':
        'Smart layouts, well-placed consultation rooms and room to grow: space planning tips for veterinary practices from Kent fit-out specialists Tim Day.',
    'the-core-principles-of-a-passive-house':
        'Super-insulation, airtightness, triple glazing, MVHR and thermal bridge-free design: the five Passive House principles, explained by a certified builder.',
    'what-are-the-benefits-of-working-with-a-main-contractor-from-start-to-finish':
        'One point of contact, clear accountability and fewer delays: why appointing one main contractor from concept to completion makes your build run smoother.',
    'what-is-a-passive-house':
        'What is a Passive House and why does it matter? Tim Day, a Certified Passive House Tradesperson in Kent, explains the standard and how it benefits you.',
    'what-makes-a-veterinary-fitout-different-from-other-commercial-builds':
        'Hygiene, animal comfort and specialist services set a veterinary fit-out apart from other commercial builds. Tim Day Construction explains the difference.',
    'what-should-you-consider-before-starting-a-clinical-fit-out':
        'When to involve a contractor, choosing a building, workflow and equipment: Tim Day answers the questions to ask before you start a clinical fit-out.',
    'why-does-ventilation-and-air-quality-matter-in-veterinary-practices':
        'Ventilation protects staff, clients and animals. Why air quality, filtration and heat recovery matter in veterinary practices, from Tim Day Construction.',
    'why-should-you-choose-a-specialist-veterinary-fit-out-contractor':
        'Specialist equipment, clinical workflow and compliance: why a veterinary fit-out needs a specialist contractor, from the Kent team behind Vet Shack.',
}
posts = {}
for f in sorted((OUT / 'posts').glob('*.md')):
    t = f.read_text()
    slug = re.search(r'^slug: "([^"]+)"', t, re.M).group(1)
    wp_slug = re.search(r'^wpSlug: "([^"]+)"', t, re.M).group(1)
    wp = wp_posts[wp_slug]
    posts[slug] = {'guid': wp['guid']['rendered'], 'description': DESCRIPTIONS[slug]}
for k, v in DESCRIPTIONS.items():
    assert 140 <= len(v) <= 155, (k, len(v))
    print(len(v), k)
dump('posts', posts)


# ---------- legal pages (F1) ----------
def clean(name):
    """REST content.rendered -> tidy HTML: no block classes, relative internal links, F19 fixes."""
    page = wp_pages[name]
    b = BeautifulSoup(page['content']['rendered'], 'lxml').body
    for el in b.find_all(True):
        el.attrs.pop('class', None)
    for h in b.find_all(['h2', 'h3']):  # bold wrappers inside headings add nothing
        for st in h.find_all('strong'):
            st.unwrap()
    for a in b.find_all('a', href=True):
        a['href'] = rel(a['href'])
    return page, b


def heading(b, text):
    return next(h for h in b.find_all(['h2', 'h3']) if h.get_text(strip=True) == text)


def frag(html):
    return list(BeautifulSoup(html, 'lxml').body.children)


def finish(name, page, b, published, modified, description):
    html = re.sub(r'\n{2,}', '\n', b.decode_contents()).strip()
    dump(name, {
        'title': page['title']['rendered'],
        'published': published,
        'modified': modified,
        'seo': {**meta(name), 'description': description},
        'html': fix(html, name),
    })


# Privacy: text verbatim. Heading levels only: the live content opens with H3s and has one H2
# ("Your Data") part-way down, which would skip a level under the page H1. The H3s before
# "Your Data" become H2 (siblings of it); the H3s after it stay H3 (its subsections).
page, b = clean('privacy-policy')
for h in b.find_all(['h2', 'h3']):
    if h.name == 'h2':  # "Your Data": everything after it keeps its level
        break
    h.name = 'h2'
finish('privacy-policy', page, b, gmt(page['date_gmt']), gmt(page['modified_gmt']),
       # F10 draft, awaiting approval
       'How Tim Day Construction collects, uses and protects personal data from this website, including contact form details, and how to exercise your rights.')

# Cookies: text verbatim apart from the cookie list (F1). Every change below is listed in the
# build report for TDC to sign off. All headings are H3 in WordPress; they become H2 (no skip).
page, b = clean('cookies')
for h in b.find_all('h3'):
    h.name = 'h2'


def replace_section_body(title, new_html):
    h = heading(b, title)
    sib = h.find_next_sibling()
    while sib is not None and sib.name not in ('h2', 'h3'):
        nxt = sib.find_next_sibling()
        sib.decompose()
        sib = nxt
    for node in reversed(frag(new_html)):
        h.insert_after(node)


# CHANGE 1: the old category list (Essential, Statistics, Marketing, Functional, Preferences)
# described cookies this site doesn't set (log-ins, baskets, advertising). Replaced with the
# cookies the new site actually uses (ConsentBanner.astro, EntranceAnimation.astro).
COOKIE_LIST = (
    '<p>These are the cookies our website uses:</p>'
    '<ul>'
    '<li><strong>tdc_consent</strong> (strictly necessary, 6 months): stores your choice to accept or reject analytics cookies, so we don’t ask you again on every page.</li>'
    '<li><strong>first_visit</strong> (functional, 1 year): makes sure the introduction animation on our home page only plays on your first visit.</li>'
    '<li><strong>_ga</strong> and <strong>_ga_&lt;ID&gt;</strong> (analytics, Google Analytics, up to 2 years): count visits and show us which pages are used, without identifying you. These are only set after you accept analytics cookies.</li>'
    '<li><strong>_li_id.&lt;ID&gt;</strong> (analytics, VisitorQueue, 2 years) and <strong>_li_ses.&lt;ID&gt;</strong> (analytics, VisitorQueue, until you close your browser): tell us whether a visit is new or returning and which pages were viewed. VisitorQueue’s scripts may set other cookies for the same purpose. These are only set after you accept analytics cookies.</li>'
    '</ul>'
)
replace_section_body('What type of Cookies do we use?', COOKIE_LIST)

# CHANGE 2: the old text described comment cookies; the site has no comments.
replace_section_body('How long do Cookies Last?',
                     '<p>How long each cookie lasts is shown in the list above. Cookies that last for a session are deleted when you close your browser.</p>')

# CHANGE 3: new sentence pointing to the footer's "Cookie settings" link.
first = heading(b, 'Can I control Cookie preferences?').find_next_sibling('p')
for node in reversed(frag('<p>To change your choice on this website at any time, use the “Cookie settings” link in the footer of any page.</p>')):
    first.insert_after(node)

finish('cookies', page, b, gmt(page['date_gmt']), '2026-10-23T12:00:00Z',
       # F10 draft, awaiting approval
       'The cookies the Tim Day Construction website uses, what each one does and how long it lasts, and how to accept, reject or change your analytics choice.')

save_fixes('blog')
print('blog: wrote', ', '.join(sorted(p.name for p in PAGES.glob('*.json'))))
