// Vercel Routing Middleware: serve the markdown twin of a page to AI agents.
// GET /about/?output_format=md  or  Accept: text/markdown  ->  /about.md
// (Static files win over vercel.json rewrites on Vercel, so this must be middleware. Lesson from mallardhq.com.)
import { rewrite, next } from '@vercel/functions';

export const config = {
  // Pages only: skip assets, uploads, image optimiser and anything with a file extension
  matcher: ['/((?!_astro/|_vercel/|wp-content/|api/|.*\\.[a-zA-Z0-9]+$).*)'],
};

export default function middleware(request) {
  const url = new URL(request.url);
  const wantsMd =
    url.searchParams.get('output_format') === 'md' ||
    (request.headers.get('accept') || '').toLowerCase().includes('text/markdown');
  if (!wantsMd) return next({ headers: { Vary: 'Accept' } });
  const path = url.pathname === '/' ? '/index' : url.pathname.replace(/\/$/, '');
  return rewrite(new URL(`${path}.md`, url), {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8', Vary: 'Accept', 'X-Robots-Tag': 'noindex' },
  });
}
