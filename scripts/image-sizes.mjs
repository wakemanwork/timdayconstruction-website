// Writes src/data/image-sizes.json: { "/wp-content/uploads/...jpg": [width, height] }
// for every raster image under public/wp-content, so <Img> can set width/height (no CLS).
// Run: node scripts/image-sizes.mjs   (fast: reads headers only)
import sharp from 'sharp';
import { readdir, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const base = join(root, 'public');
const out = {};
async function walk(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) await walk(p);
    else if (/\.(jpe?g|png|webp|gif)$/i.test(e.name)) {
      try {
        const m = await sharp(p).metadata();
        const w = m.autoOrient?.width ?? m.width, h = m.autoOrient?.height ?? m.height;
        out['/' + relative(base, p)] = [w, h];
      } catch { /* unreadable file: skip */ }
    }
  }
}
await walk(join(base, 'wp-content'));
await writeFile(join(root, 'src/data/image-sizes.json'), JSON.stringify(out));
console.log(Object.keys(out).length, 'images measured');
