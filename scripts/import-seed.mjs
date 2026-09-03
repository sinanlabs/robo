// seed → 内容集合（src/content/generated/*.json）
// 原则：只搬运、不补值。null / "待核实" 原样保留，由前台渲染成醒目徽标。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const seed = JSON.parse(fs.readFileSync(path.join(root, 'data/seed_v0.json'), 'utf8'));
const out = path.join(root, 'src/content/generated');
fs.mkdirSync(out, { recursive: true });

const PENDING = /待核实|待定|TBA|tba/;
export function isPending(v) {
  if (v === null || v === undefined) return true;
  if (typeof v === 'string') return v.trim() === '' || PENDING.test(v);
  if (Array.isArray(v)) return v.length === 0 || v.every(isPending);
  return false;
}

// 模型
const models = seed.models.map((m) => ({ ...m, evidence: m.evidence ?? [] }));
// 本体
const embodiments = seed.embodiments.map((e) => ({ ...e, evidence: e.evidence ?? [] }));
// 硬件
const hardware = seed.hardware.map((h) => ({ ...h, evidence: h.evidence ?? [] }));

// 适配矩阵：种子里没有逐格证据，一律 unknown；target_embodiments 只作为“厂商声明的目标形态”标注，不升格为适配状态。
const compat = [];
for (const m of models) {
  for (const e of embodiments) {
    const declared = (m.target_embodiments ?? []).some((f) => e.form === f || (f === 'dual_arm' && e.form === 'dual_arm_wheeled'));
    compat.push({
      id: `${m.id}__${e.id}`,
      model_id: m.id,
      embodiment_id: e.id,
      status: 'unknown',
      declared_target_form: declared,
      evidence: [],
    });
  }
}

// 延迟测量：Sprint 0 无数据，写空数组让页面走“— / 原因徽标”路径
const measurements = [];

// 手动维护的附加数据（若存在）：data/measurements/*.json
const mdir = path.join(root, 'data/measurements');
if (fs.existsSync(mdir)) {
  for (const f of fs.readdirSync(mdir).filter((x) => x.endsWith('.json'))) {
    const arr = JSON.parse(fs.readFileSync(path.join(mdir, f), 'utf8'));
    for (const r of Array.isArray(arr) ? arr : [arr]) measurements.push(r);
  }
}

const write = (name, data) => fs.writeFileSync(path.join(out, `${name}.json`), JSON.stringify(data, null, 2));
write('models', models);
write('embodiments', embodiments);
write('hardware', hardware);
write('compat', compat);
write('measurements', measurements);
write('meta', { ...seed._meta, imported_at: new Date().toISOString() });

console.log(`导入完成：模型 ${models.length} · 本体 ${embodiments.length} · 硬件 ${hardware.length} · 矩阵格 ${compat.length} · 测量 ${measurements.length}`);
