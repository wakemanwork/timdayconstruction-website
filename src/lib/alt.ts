import altText from '../data/alt-text.json';
/** Alt text for a content image (F14). Falls back to the given text, then to ''. */
export function alt(src: string | null | undefined, fallback = ''): string {
  if (!src) return fallback;
  return (altText as Record<string, string>)[src] ?? fallback;
}
