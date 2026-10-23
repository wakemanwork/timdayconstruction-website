"""Side-by-side (live | new) + pixel diff percentage. Usage: sidebyside.py live.png new.png out.png"""
import sys
from PIL import Image, ImageChops
a, b, out = Image.open(sys.argv[1]).convert('RGB'), Image.open(sys.argv[2]).convert('RGB'), sys.argv[3]
h = max(a.height, b.height); w = a.width
canvas = Image.new('RGB', (w * 2 + 20, h), 'red')
canvas.paste(a, (0, 0)); canvas.paste(b, (w + 20, 0))
canvas.save(out)
hh = min(a.height, b.height)
d = ImageChops.difference(a.crop((0, 0, w, hh)), b.crop((0, 0, w, hh))).convert('L').point(lambda v: 255 if v > 40 else 0)
pct = sum(d.histogram()[255:]) / (w * hh) * 100
print(f'height live {a.height} new {b.height} ({b.height - a.height:+d}px), pixels differing {pct:.1f}%')
