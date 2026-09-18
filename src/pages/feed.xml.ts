// RSS：每期周报一条（英文短句 + 中文摘要），供订阅器与 dlvr.it 一类转发服务使用。
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
const esc = (s: string) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export const GET: APIRoute = async () => {
  const items = (await getCollection('weekly')).map((w) => w.data as any).sort((a, b) => b.week.localeCompare(a.week)).slice(0, 30);
  const body = items.map((w) => `<item><title>${esc(w.x_en || `Open VLA weekly ${w.week}`)}</title><link>https://robo.sinanlab.com/weekly/${w.week}</link><guid isPermaLink="true">https://robo.sinanlab.com/weekly/${w.week}</guid><pubDate>${new Date(w.generated).toUTCString()}</pubDate><description>${esc(w.summary?.zh || '')}</description></item>`).join('');
  const xml = `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Sinan Robo · weekly</title><link>https://robo.sinanlab.com/weekly</link><description>Weekly change record of the open VLA index: new models, weights updates, licence changes, measurements. Numbers only.</description>${body}</channel></rss>`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
