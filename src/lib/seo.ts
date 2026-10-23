// SEO helpers shared by every page. Rules: docs/MIGRATION-BASELINE.md (F10, F11) and CLAUDE.md.
import site from '../data/site.json';

export const SITE = 'https://timdayconstruction.co.uk';
export const ORG_ID = `${SITE}/#organization`;
export const WEBSITE_ID = `${SITE}/#website`;
const YOAST_SUFFIX = ' - Building Contractor | Canterbury, Kent';

/** F11: keep the WordPress title verbatim unless it runs past 60 characters,
 *  then swap the Yoast suffix for the brand, and drop it if still too long. */
export function pageTitle(wpTitle: string | null | undefined, fallback: string): string {
  const t = (wpTitle ?? '').trim() || `${fallback}${YOAST_SUFFIX}`;
  if (t.length <= 60) return t;
  const base = t.endsWith(YOAST_SUFFIX) ? t.slice(0, -YOAST_SUFFIX.length) : t;
  const branded = `${base} | Tim Day Construction`;
  return branded.length <= 60 ? branded : base;
}

export function abs(path: string): string {
  return path.startsWith('http') ? path : SITE + path;
}

export const DEFAULT_OG = '/wp-content/uploads/2026/10/DSCF9417-scaled.jpg';

export function organization() {
  return {
    '@type': ['Organization', 'GeneralContractor'],
    '@id': ORG_ID,
    name: 'Tim Day Construction',
    legalName: 'Tim Day Construction Ltd',
    url: `${SITE}/`,
    telephone: '+441227281749',
    email: site.email,
    logo: {
      '@type': 'ImageObject',
      '@id': `${SITE}/#/schema/logo/image/`,
      url: `${SITE}/wp-content/uploads/2024/12/tim-day-logo-darker.png`,
      contentUrl: `${SITE}/wp-content/uploads/2024/12/tim-day-logo-darker.png`,
      width: 286, height: 42, caption: 'Tim Day Construction',
    },
    image: { '@id': `${SITE}/#/schema/logo/image/` },
    address: { '@type': 'PostalAddress', addressLocality: 'Canterbury', addressRegion: 'Kent', addressCountry: 'GB' },
    areaServed: ['Canterbury', 'Whitstable', 'Herne Bay', 'Faversham', 'Ashford', 'Thanet', 'Kent'].map((name) => ({ '@type': 'Place', name })),
    sameAs: site.socials.map((s) => s.href),
    memberOf: [
      { '@type': 'Organization', name: 'Federation of Master Builders', url: 'https://www.fmb.org.uk' },
    ],
    identifier: { '@type': 'PropertyValue', propertyID: 'Companies House', value: '06456326' },
    vatID: 'GB928901208',
    slogan: '‘Concept to completion’ construction and project management',
  };
}

export function website() {
  return {
    '@type': 'WebSite',
    '@id': WEBSITE_ID,
    url: `${SITE}/`,
    name: 'Tim Day Construction',
    description: '‘Concept to completion’ construction and project management',
    publisher: { '@id': ORG_ID },
    inLanguage: 'en-GB',
  };
}

export type Crumb = { name: string; path: string };

export function breadcrumbs(path: string, crumbs: Crumb[]) {
  return {
    '@type': 'BreadcrumbList',
    '@id': `${SITE}${path}#breadcrumb`,
    itemListElement: crumbs.map((c, i) => ({
      '@type': 'ListItem', position: i + 1, name: c.name,
      ...(i < crumbs.length - 1 ? { item: abs(c.path) } : {}),
    })),
  };
}

export function webPage(path: string, name: string, description: string | null, opts: { published?: Date; modified?: Date; image?: string | null; type?: string } = {}) {
  return {
    '@type': opts.type ?? 'WebPage',
    '@id': `${SITE}${path}`,
    url: `${SITE}${path}`,
    name,
    isPartOf: { '@id': WEBSITE_ID },
    about: { '@id': ORG_ID },
    ...(description ? { description } : {}),
    ...(opts.published ? { datePublished: opts.published.toISOString() } : {}),
    ...(opts.modified ? { dateModified: opts.modified.toISOString() } : {}),
    ...(opts.image ? { primaryImageOfPage: { '@type': 'ImageObject', url: abs(opts.image) } } : {}),
    breadcrumb: { '@id': `${SITE}${path}#breadcrumb` },
    inLanguage: 'en-GB',
  };
}

export function faqPage(path: string, items: { q: string; aText: string }[]) {
  return {
    '@type': 'FAQPage',
    '@id': `${SITE}${path}#faq`,
    mainEntity: items.map((i) => ({
      '@type': 'Question', name: i.q,
      acceptedAnswer: { '@type': 'Answer', text: i.aText },
    })),
  };
}

export function graph(...nodes: object[]) {
  return { '@context': 'https://schema.org', '@graph': [organization(), website(), ...nodes] };
}
