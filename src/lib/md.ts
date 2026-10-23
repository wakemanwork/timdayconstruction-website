// Render markdown strings from frontmatter/JSON (CTA bodies, FAQ answers) to HTML at build time.
import { marked } from 'marked';
marked.setOptions({ gfm: true, breaks: false });
export const mdToHtml = (s: string | null | undefined) => (s ? (marked.parse(s, { async: false }) as string) : '');
export const mdInline = (s: string | null | undefined) => (s ? (marked.parseInline(s, { async: false }) as string) : '');
/** Plain text from markdown, for JSON-LD answers and meta. */
export const mdText = (s: string | null | undefined) =>
  mdToHtml(s).replace(/<[^>]+>/g, ' ').replace(/&amp;/g, '&').replace(/&#39;/g, '’').replace(/&quot;/g, '"').replace(/\s+/g, ' ').trim();
