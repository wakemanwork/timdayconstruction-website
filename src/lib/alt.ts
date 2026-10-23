// Alt text for content images (F14). Base file plus one file per contributor in src/data/alt/*.json,
// merged so parallel work never edits the same file.
import base from '../data/alt-text.json';
const extra = import.meta.glob('../data/alt/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, string>>;
const ALT: Record<string, string> = Object.assign({}, base, ...Object.values(extra));
/** Alt text for a content image. Falls back to the given text, then to ''. */
export function alt(src: string | null | undefined, fallback = ''): string {
  if (!src) return fallback;
  return ALT[src] ?? fallback;
}
