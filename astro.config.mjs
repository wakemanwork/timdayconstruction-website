import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://timdayconstruction.co.uk',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  compressHTML: true,
  prefetch: false,
});
