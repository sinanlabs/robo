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

// 逐格证据覆盖：data/compat_overrides.json（人工复核过的原文证据，每格带 URL）
const ovPath = path.join(root, 'data/compat_overrides.json');
if (fs.existsSync(ovPath)) {
  const ov = JSON.parse(fs.readFileSync(ovPath, 'utf8'));
  for (const o of ov) {
    const cell = compat.find((c) => c.model_id === o.model_id && c.embodiment_id === o.embodiment_id);
    if (!cell) { console.warn('override 找不到格：', o.model_id, o.embodiment_id); continue; }
    cell.status = o.status; cell.evidence = o.evidence ?? []; if (o.note) cell.note = o.note;
  }
  console.log(`适配矩阵证据覆盖：${ov.length} 格`);
}


// 社区复现（后台核验通过的众测记录）：跑通 / 需微调 → 该格升为 community_verified，并附证据链接；未跑通只作记录不改状态
const rpP = path.join(root, 'data/compat_repro.json');
let repro = [];
if (fs.existsSync(rpP)) {
  repro = JSON.parse(fs.readFileSync(rpP, 'utf8')).items || [];
  let up = 0;
  for (const r of repro) {
    if (!['works', 'finetune'].includes(r.outcome)) continue;
    const cell = compat.find((c) => c.model_id === r.model_id && c.embodiment_id === r.embodiment_id); if (!cell) continue;
    if (cell.status === 'unknown' || cell.status === 'theoretical') { cell.status = 'community_verified'; up++; }
    cell.evidence.push({ field: 'status', url: r.evidence_url || ('https://compute.sinanlab.com/api/robo/repro?model=' + r.model_id), source_type: 'official', fetched: r.verified_at, note: `社区复现 #${r.id}：${r.outcome === 'works' ? '跑通' : '需微调后跑通'}${r.setting ? '（' + (r.setting === 'real' ? '真机' : '仿真') + '）' : ''}${r.note ? ' · ' + String(r.note).slice(0, 120) : ''}` });
  }
  console.log(`社区复现：${repro.length} 条，升格 ${up} 格`);
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


// 活性信号：data/activity/latest.json + history.jsonl（scripts/activity.py 每日生成；只记录数字，不评价）
const activity = [];
const actP = path.join(root, 'data/activity/latest.json'), histP = path.join(root, 'data/activity/history.jsonl');
if (fs.existsSync(actP)) {
  const A = JSON.parse(fs.readFileSync(actP, 'utf8'));
  const hist = fs.existsSync(histP) ? fs.readFileSync(histP, 'utf8').split('\n').filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
  const cutoff = new Date(Date.now() - 30 * 864e5).toISOString().slice(0, 10);
  for (const m of models) {
    const r = A.items[m.id]; if (!r) continue;
    const series = hist.filter((h) => h.id === m.id && h.d >= cutoff).sort((a, b) => a.d.localeCompare(b.d)).map((h) => ({ d: h.d, stars: h.stars ?? null, hf30: h.hf30 ?? null, c90: h.c90 ?? null }));
    const first = series[0], last = series[series.length - 1];
    const delta = first && last && first.d !== last.d ? { days: Math.round((new Date(last.d) - new Date(first.d)) / 864e5), stars: last.stars != null && first.stars != null ? last.stars - first.stars : null, hf30: last.hf30 != null && first.hf30 != null ? last.hf30 - first.hf30 : null } : null;
    activity.push({ id: m.id, fetched: r.fetched, github: r.github ?? { ok: false }, hf: r.hf ?? { ok: false }, modelscope: r.modelscope ?? { ok: false }, series, delta });
  }
  console.log(`活性信号：${activity.length} 个模型（${A.generated}）`);
}


// 部署配方：data/recipes.json（来自 bench/ 真正跑通的脚本与日志）
let recipes = [], recipesMeta = [];
const rcP = path.join(root, 'data/recipes.json');
if (fs.existsSync(rcP)) {
  const R = JSON.parse(fs.readFileSync(rcP, 'utf8'));
  recipes = (R.recipes || []).map((r) => ({ id: r.model_id, ...r }));
  recipesMeta = [{ id: 'meta', generated: R._meta?.generated ?? null, machine: R._meta?.machine ?? null, common: R.common || [], envs: R.envs || [], not_reproduced: R.not_reproduced || [] }];
  console.log(`部署配方：${recipes.length} 篇 · 未复现 ${recipesMeta[0].not_reproduced.length}`);
}


// 周报：data/weekly/<周>.json（scripts/weekly_brief.py 每周一生成）
let weekly = [];
const wkDir = path.join(root, 'data/weekly');
if (fs.existsSync(wkDir)) {
  weekly = fs.readdirSync(wkDir).filter((f) => f.endsWith('.json')).map((f) => { const w = JSON.parse(fs.readFileSync(path.join(wkDir, f), 'utf8')); return { id: w.week, ...w }; }).sort((a, b) => b.week.localeCompare(a.week));
  console.log(`周报：${weekly.length} 期`);
}


// 公开基准分数与数据集索引：data/benchmarks.json · data/datasets.json（scripts/merge_mine.py 合并研究结果生成；缺文件则为空）
let benchDefs = [], scores = [], datasets = [];
const bdP = path.join(root, 'data/benchmark_defs.json'), bP = path.join(root, 'data/benchmarks.json'), dP = path.join(root, 'data/datasets.json');
if (fs.existsSync(bP)) { const B = JSON.parse(fs.readFileSync(bP, 'utf8')); benchDefs = B.benchmarks || []; scores = B.scores || []; }
else if (fs.existsSync(bdP)) benchDefs = JSON.parse(fs.readFileSync(bdP, 'utf8')).benchmarks || [];
if (fs.existsSync(dP)) datasets = JSON.parse(fs.readFileSync(dP, 'utf8')).datasets || [];
console.log(`基准分数：${scores.length} 条 · 数据集：${datasets.length} 个`);


// 月报：data/reports/<月>.json（结构块）+ <月>.analysis.md / .analysis.en.md（署名分析）
let reports = [];
const rpDir = path.join(root, 'data/reports');
if (fs.existsSync(rpDir)) {
  reports = fs.readdirSync(rpDir).filter((f) => /^\d{4}-\d{2}\.json$/.test(f)).map((f) => {
    const r = JSON.parse(fs.readFileSync(path.join(rpDir, f), 'utf8')); const m = f.slice(0, 7);
    const rd = (x) => (fs.existsSync(path.join(rpDir, x)) ? fs.readFileSync(path.join(rpDir, x), 'utf8') : '');
    return { id: m, ...r, analysis_zh: rd(m + '.analysis.md'), analysis_en: rd(m + '.analysis.en.md') };
  }).sort((a, b) => b.month.localeCompare(a.month));
  console.log(`月报：${reports.length} 期`);
}

const write = (name, data) => fs.writeFileSync(path.join(out, `${name}.json`), JSON.stringify(data, null, 2));
write('models', models);
write('embodiments', embodiments);
write('hardware', hardware);
write('compat', compat);
write('measurements', measurements);
write('activity', activity);
write('recipes', recipes);
write('recipes_meta', recipesMeta);
write('weekly', weekly);
write('benchmarks', benchDefs);
write('scores', scores);
write('datasets', datasets);
write('reports', reports);
write('repro', repro.map((r) => ({ id: String(r.id), ...r })));
write('meta', { ...seed._meta, imported_at: new Date().toISOString() });

console.log(`导入完成：模型 ${models.length} · 本体 ${embodiments.length} · 硬件 ${hardware.length} · 矩阵格 ${compat.length} · 测量 ${measurements.length}`);
