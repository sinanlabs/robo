// 公开数据文件：/data/models.json · compat.json · embodiments.json · hardware.json · measurements.json · activity.json —— 与网页同批次生成，字段说明见 compute.sinanlab.com/api-docs
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import fs from 'node:fs';
const NAMES = ['models', 'compat', 'embodiments', 'hardware', 'measurements', 'activity', 'weekly'] as const;
export function getStaticPaths() { return NAMES.map((name) => ({ params: { name } })); }
export const GET: APIRoute = async ({ params }) => {
  const name = params.name as (typeof NAMES)[number];
  const rows = (await getCollection(name)).map((e) => e.data);
  let meta: any = {}; try { meta = JSON.parse(fs.readFileSync('src/content/generated/meta.json', 'utf8')); } catch {}
  const body = { name, generated_at: new Date().toISOString(), schema_version: meta.schema_version || '0.1', source: 'https://robo.sinanlab.com', license: 'CC BY 4.0 · 注明"数据：司南实验室 robo.sinanlab.com"', note: '未核实的字段为 null；每条记录的 evidence 数组给出字段来源。只陈述测量与来源，不含推荐。', count: rows.length, items: rows };
  return new Response(JSON.stringify(body), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
};
