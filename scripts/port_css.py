"""Port the live theme's style.css into tokenised partials, values unchanged.

Splits capture/theme-source/style.css by the component line ranges recorded in
docs/DESIGN.md and swaps hard-coded colours for the tokens in src/styles/tokens.css.
Agreed deviations (focus ring, highlight colour) live in src/styles/overrides.css,
not here, so this output stays a faithful port. Re-run only if the source changes.

Run: python3 -I scripts/port_css.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'capture' / 'theme-source' / 'style.css'
OUT = ROOT / 'src' / 'styles' / 'theme'

SECTIONS = [  # (first line, name) — each runs to the line before the next
    (7, 'base'), (186, 'header'), (350, 'button'), (388, 'footer'), (578, 'page-banner'),
    (685, 'layout'), (702, 'entrance'), (746, 'home-hero'), (1008, 'intro'), (1084, 'sector-cards'),
    (1192, 'three-blocks'), (1311, 'quote'), (1394, 'how-we-work'), (1457, 'large-image'),
    (1480, 'testimonials'), (1587, 'design-and-build-section'), (1651, 'meet-the-founder'),
    (1778, 'where-we-work'), (1976, 'about'), (2058, 'about-contact'), (2196, 'about-carousel'),
    (2261, 'contact-page'), (2479, 'location-map'), (2501, 'portfolio-intro'),
    (2562, 'portfolio-category'), (2638, 'project'), (2747, 'project-carousel'),
    (2802, 'project-cta'), (2901, 'sector-intro'), (2966, 'project-blocks'), (3081, 'sector-cta'),
    (3183, 'faq'), (3271, 'blog-cards'), (3333, 'article'), (3477, 'section-heading'),
    (3488, 'design-and-build-page'), (3525, 'timeline'), (3656, 'riba-stages'), (3725, 'error-404'),
    (3782, 'location-content'), (3893, 'location-projects'), (3916, 'why-choose-tdc'),
    (3952, 'service-projects'),
]

COLOURS = [  # order matters: rgba before rgb
    (r'rgba\(\s*28,\s*81,\s*86,\s*0?\.75\)', 'var(--teal-overlay)'),
    (r'rgb\(\s*28,\s*81,\s*86\s*,\s*0?\.75\)', 'var(--teal-overlay)'),
    (r'rgb\(\s*28,\s*81,\s*86\s*\)', 'var(--teal)'),
    (r'#1c5156\b', 'var(--teal)'),
    (r'#2a6d73\b', 'var(--teal-mid)'),
    (r'#153b3f\b', 'var(--teal-dark)'),
    (r'#1d464b\b', 'var(--teal-deep)'),
    (r'#c6d8db\b', 'var(--teal-light)'),
    (r'#c5d5d8\b', 'var(--teal-light-text)'),
    (r'#d9e9ec\b', 'var(--teal-pale)'),
    (r'rgb\(\s*243,\s*243,\s*243\s*\)', 'var(--grey-bg)'),
    (r'rgb\(\s*230,\s*230,\s*230\s*\)', 'var(--grey-hover)'),
]

lines = SRC.read_text().split('\n')
OUT.mkdir(parents=True, exist_ok=True)
imports = []
for i, (start, name) in enumerate(SECTIONS):
    end = SECTIONS[i + 1][0] - 1 if i + 1 < len(SECTIONS) else len(lines)
    css = '\n'.join(lines[start - 1:end])
    for pat, rep in COLOURS:
        css = re.sub(pat, rep, css, flags=re.I)
    if name == 'base':  # agreed 23 Oct: red focus border replaced (see overrides.css)
        css = css.replace('border: solid 4px red !important;', '/* red focus border removed: see overrides.css */')
    fname = f'{i:02d}-{name}.css'
    (OUT / fname).write_text(f'/* Ported from live style.css lines {start}-{end}. Do not edit values here; see docs/DESIGN.md. */\n{css.strip()}\n')
    imports.append(f"@import './theme/{fname}';")
(ROOT / 'src' / 'styles' / 'theme.css').write_text('\n'.join(imports) + '\n')
print(len(SECTIONS), 'partials written')
