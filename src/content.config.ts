import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const seo = z.object({
  title: z.string().nullable(),
  description: z.string().nullable(),
  ogImage: z.string().nullable().optional(),
});

const cta = z.object({ title: z.string(), body: z.string(), button: z.string() });

const posts = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    wpSlug: z.string(),
    date: z.coerce.date(),
    modified: z.coerce.date(),
    author: z.string(),
    wpAuthor: z.string().nullable().optional(),
    categories: z.array(z.string()),
    featuredImage: z.string().nullable(),
    seo,
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    modified: z.coerce.date(),
    location: z.string().nullable(),
    client: z.string().nullable(),
    typeOfWork: z.string().nullable(),
    architect: z.string().nullable(),
    status: z.string().nullable(),
    categories: z.array(z.string()),
    bannerImage: z.string(),
    thumbnail: z.string().nullable(),
    cardLocation: z.string().nullable(),
    gallery: z.array(z.string()),
    cta,
    seo,
  }),
});

const sectors = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/sectors' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    modified: z.coerce.date(),
    bannerImage: z.string(),
    introHeading: z.string(),
    introImage: z.string().nullable(),
    projects: z.array(z.string()),
    faqLabel: z.string().nullable(),
    faqTitle: z.string().nullable(),
    faq: z.array(z.object({ q: z.string(), a: z.string() })),
    cta,
    seo,
  }),
});

const testimonials = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/testimonials' }),
  schema: z.object({
    name: z.string(),
    date: z.coerce.date(),
    modified: z.coerce.date(),
    quote: z.string().nullable(),
    image: z.string().nullable(),
    company: z.string().nullable(),
    order: z.number(),
    seo,
  }),
});

export const collections = { posts, projects, sectors, testimonials };
