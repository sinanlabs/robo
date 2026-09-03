// npm run validate —— 校验 schema 与 evidence 完整性。
// 规则：
//  1) 每条实体过 zod schema；
//  2) 必填字段若非 null / 非“待核实”，必须被某条 evidence 的 field 覆盖，否则报 “无来源的确定值”（这是最严重的一类）；
//  3) 统计每个实体的“待核实”字段数，输出完整率；
//  4) 有 --strict 时，任何“无来源的确定值”都让进程退出码 1（CI 用）。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const gen = path.join(root, 'src/content/generated');
const strict = process.argv.includes('--strict');
const read = (n) => JSON.parse(fs.readFileSync(path.join(gen, `${n}.json`), 'utf8'));

const PENDING = /待核实|待定|TBA/;
const isPending = (v) => v === null || v === undefined || (typeof v === 'string' && (v.trim() === '' || PENDING.test(v))) || (Array.isArray(v) && (v.length === 0 || v.every(isPending)));

const Evidence = z.object({
  field: z.string().min(1),
  url: z.string().min(1),
  source_type: z.enum(['literature', 'news', 'hub', 'official']),
  fetched: z.string().min(4),
  sha256: z.string().nullable().optional(),
  note: z.string().optional(),
});
const Model = z.object({
  id: z.string().regex(/^[a-z0-9.\-]+$/),
  name: z.string().min(1),
  org: z.string().min(1),
  release_date: z.string().nullable(),
  params_b: z.number().nullable(),
  arch_type: z.string().nullable(),
  arch_notes: z.string().nullable().optional(),
  license: z.string().nullable(),
  commercial_ok: z.boolean().nullable(),
  weights_url: z.string().nullable(),
  code_url: z.string().nullable(),
  paper_url: z.string().nullable(),
  modalities_in: z.array(z.string()),
  action_space: z.string().nullable(),
  cross_embodiment: z.string().nullable(),
  pretrain_hours: z.number().nullable(),
  target_embodiments: z.array(z.string()),
  evidence: z.array(Evidence),
});
const Embodiment = z.object({
  id: z.string(), name: z.string(), vendor: z.string(),
  form: z.enum(['humanoid', 'dual_arm', 'dual_arm_wheeled', 'single_arm', 'wheeled', 'quadruped', 'mobile_manipulator']),
  dof: z.number().nullable(), end_effector: z.string().nullable(), sdk_url: z.string().nullable(),
  price_range_cny: z.string().nullable(), data_formats: z.array(z.string()), evidence: z.array(Evidence),
});
const Hardware = z.object({
  id: z.string(), name: z.string(), vram_gb: z.number().nullable(), type: z.string(),
  rental_cny_per_hour_ref: z.number().nullable(), rental_ref_source: z.string().nullable(), rental_ref_url: z.string().nullable(),
  note: z.string().nullable().optional(), evidence: z.array(Evidence),
});
const Compat = z.object({
  id: z.string(), model_id: z.string(), embodiment_id: z.string(),
  status: z.enum(['official', 'community_verified', 'theoretical', 'unsupported', 'unknown']),
  declared_target_form: z.boolean(), evidence: z.array(Evidence),
});
const Measurement = z.object({
  id: z.string(), model_id: z.string(), hardware_id: z.string(), precision: z.string(),
  config: z.object({ batch: z.number(), image_res: z.string(), action_chunk: z.number(), warmup_steps: z.number(), steps: z.number() }),
  metrics: z.object({ latency_ms_p50: z.number(), latency_ms_p95: z.number().nullable(), throughput_chunks_s: z.number().nullable(), vram_peak_gb: z.number().nullable() }),
  source_type: z.enum(['literature', 'maintainer', 'crowd']),
  review_status: z.enum(['pending', 'verified', 'rejected']),
  evidence: z.array(Evidence), created_at: z.string(),
});

const REQUIRED = {
  models: ['name', 'org', 'release_date', 'params_b', 'license', 'commercial_ok', 'weights_url', 'code_url'],
  embodiments: ['name', 'vendor', 'form', 'dof', 'end_effector', 'sdk_url', 'price_range_cny'],
  hardware: ['name', 'vram_gb', 'rental_cny_per_hour_ref'],
};
// 无需来源即可成立的字段（本身就是标识或分类）
const SELF_EVIDENT = new Set(['name', 'org', 'vendor', 'form', 'id']);

let problems = 0, unsourced = 0;
const report = [];
function check(name, schema, rows) {
  let pending = 0, total = 0;
  for (const r of rows) {
    const res = schema.safeParse(r);
    if (!res.success) { problems++; report.push(`❌ ${name}/${r.id ?? '?'}: ${res.error.issues.map((i) => i.path.join('.') + ' ' + i.message).join('; ')}`); continue; }
    const req = REQUIRED[name] ?? [];
    const covered = new Set((r.evidence ?? []).flatMap((e) => e.field.split(',').map((s) => s.trim())));
    for (const f of req) {
      total++;
      if (isPending(r[f])) { pending++; continue; }
      if (!SELF_EVIDENT.has(f) && !covered.has(f)) { unsourced++; report.push(`⚠️ ${name}/${r.id}.${f} = ${JSON.stringify(r[f]).slice(0, 60)} —— 确定值但没有 evidence 覆盖`); }
    }
  }
  const rate = total ? Math.round((1 - pending / total) * 100) : 100;
  report.push(`· ${name}: ${rows.length} 条 · 必填字段完整率 ${rate}%（待核实 ${pending}/${total}）`);
}

check('models', Model, read('models'));
check('embodiments', Embodiment, read('embodiments'));
check('hardware', Hardware, read('hardware'));
check('compat', Compat, read('compat'));
check('measurements', Measurement, read('measurements'));

// 引用完整性
const mids = new Set(read('models').map((m) => m.id)), eids = new Set(read('embodiments').map((e) => e.id)), hids = new Set(read('hardware').map((h) => h.id));
for (const c of read('compat')) if (!mids.has(c.model_id) || !eids.has(c.embodiment_id)) { problems++; report.push(`❌ compat/${c.id} 引用了不存在的模型或本体`); }
for (const m of read('measurements')) if (!mids.has(m.model_id) || !hids.has(m.hardware_id)) { problems++; report.push(`❌ measurements/${m.id} 引用了不存在的模型或硬件`); }

console.log(report.join('\n'));
console.log(`\n结论：schema 错误 ${problems} · 无来源的确定值 ${unsourced}`);
if (problems > 0 || (strict && unsourced > 0)) process.exit(1);
