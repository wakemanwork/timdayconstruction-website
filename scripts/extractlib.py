"""Shared helpers for extraction scripts (scripts/extract.py and scripts/extract_*.py).

Sources: capture/html/*.html (rendered pages, the truth for ACF-driven fields),
capture/rest/*.json (post/project bodies, dates, categories), capture/meta/*.json (SEO).
Copy is never retyped. Agreed corrections (fix log F19/F20) go through FIXES and are
logged to capture/fixes-applied.json so the text-diff report can account for them.

Usage, from a script in scripts/ run with python3 -I:
    import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extractlib import *; from extractlib import applied     # soup, md, txt, inner, meta, write_md, rest, rel, fix, save_fixes, ...
Call save_fixes('<name>') at the end so the text-diff knows about agreed corrections.
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

def inner(el, where=''):
    """Inner HTML with whitespace collapsed (keeps highlight spans such as .light-teal-txt)."""
    if el is None:
        return None
    for a in el.find_all('a', href=True):
        a['href'] = rel(a['href'])
    h = re.sub(r'\s+', ' ', el.decode_contents()).strip()
    return fix(h, where) if where else h

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


def save_fixes(name):
    """Write the corrections applied by this script to capture/fixes/<name>.json (read by scripts/qa/textdiff.py)."""
    d = CAP / 'fixes'; d.mkdir(exist_ok=True)
    (d / f'{name}.json').write_text(json.dumps(applied, indent=1, ensure_ascii=False))
