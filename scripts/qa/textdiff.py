"""Word-level text diff: live page (capture/html) vs built page (dist). Usage:
    python3 -I scripts/qa/textdiff.py /            # one page
    python3 -I scripts/qa/textdiff.py --all        # every captured URL that exists in dist
Compares the visible text of everything between the header and the footer (header and footer
are shared components, checked once via the home page). Typographic normalisation (curly vs
straight quotes, whitespace) is ignored. Differences matching an agreed fix (capture/fixes/*.json)
are reported as EXPECTED; anything else is UNEXPECTED and must be explained or fixed.
Exit code 1 if any page has unexpected differences.
"""
import sys, re, json, difflib
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
CAP, DIST = ROOT / 'capture' / 'html', ROOT / 'dist'
FIXES = [x for f in sorted((ROOT / 'capture' / 'fixes').glob('*.json')) for x in json.loads(f.read_text())]
fix_words = set()
for f in FIXES:
    for side in ('from', 'to', 'text'):
        if f.get(side):
            fix_words.update(w.lower() for w in re.findall(r"[\w’']+", f[side]))

DROP = 'script,style,noscript,header,footer,.entrance-animation,.device-menu,.sr-only,.consent,svg,.material-symbols-outlined,form'

def words(html, built=False):
    s = BeautifulSoup(html, 'lxml')
    for t in s.select(DROP):
        t.decompose()
    root = s.select_one('main') if built else s.body
    text = root.get_text(' ') if root else ''
    text = (text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
                .replace('\xa0', ' ').replace('–', '-').replace('&', ' and '))
    text = re.sub(r'["]', ' ', text)
    return re.findall(r"[\w']+|[^\w\s']", text)

def slug_of(url_path):
    p = url_path.strip('/')
    return (p.replace('/', '__') or 'index')

def diff(path):
    cap = CAP / f'{slug_of(path)}.html'
    built = DIST / path.strip('/') / 'index.html' if path != '/' else DIST / 'index.html'
    if not cap.exists() or not built.exists():
        return None
    a, b = words(cap.read_text()), words(built.read_text(), built=True)
    sm = difflib.SequenceMatcher(None, [w.lower() for w in a], [w.lower() for w in b], autojunk=False)
    expected, unexpected = [], []
    ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
    deleted = [' '.join(a[i1:i2]).lower() for op, i1, i2, j1, j2 in ops if op == 'delete']
    inserted = [' '.join(b[j1:j2]).lower() for op, i1, i2, j1, j2 in ops if op == 'insert']
    for op, i1, i2, j1, j2 in ops:
        old, new = ' '.join(a[i1:i2]), ' '.join(b[j1:j2])
        if (op == 'delete' and old.lower() in inserted) or (op == 'insert' and new.lower() in deleted):
            expected.append(f'moved (same text, new position): "{old or new}"')
            continue
        ctx = ' '.join(a[max(0, i1 - 6):i1])
        changed = {w.lower() for w in re.findall(r"[\w']+", old + ' ' + new)}
        punct_only = not changed
        item = f'{op}: "{old}" → "{new}"   (after: …{ctx})'
        (expected if punct_only or changed <= fix_words else unexpected).append(item)
    return len(a), len(b), round(sm.ratio() * 100, 2), expected, unexpected

paths = sys.argv[1:]
if paths == ['--all']:
    paths = ['/' if f.stem == 'index' else '/' + f.stem.replace('__', '/') + '/' for f in sorted(CAP.glob('*.html'))]
bad = 0
for p in paths:
    r = diff(p)
    if r is None:
        print(f'{p}: not built yet'); continue
    na, nb, ratio, exp, unexp = r
    print(f'{p}: live {na} tokens, new {nb}, {ratio}% identical, {len(exp)} expected, {len(unexp)} UNEXPECTED')
    for x in unexp: print('   UNEXPECTED', x)
    if '-v' in sys.argv or len(paths) == 1:
        for x in exp: print('   expected  ', x)
    bad += bool(unexp)
sys.exit(1 if bad else 0)
