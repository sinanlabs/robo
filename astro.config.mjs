import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://robo.sinanlab.com',
  output: 'static',
  integrations: [sitemap({ i18n: { defaultLocale: 'zh-cn', locales: { 'zh-cn': 'zh-CN', en: 'en' } } })],
  trailingSlash: 'never',
  build: { format: 'file' },
  i18n: {
    defaultLocale: 'zh-cn',
    locales: ['zh-cn', 'en'],
    routing: { prefixDefaultLocale: false },
  },
});
