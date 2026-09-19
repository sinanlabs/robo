// 英文页数据词典：构建后把 dist/en/**/*.html 里仍是中文的文本节点 / 属性按 src/i18n/data_en.json 整句替换（{n} 匹配数字）。
// 视图里的界面文案已在模板里分中英；这里补的是数据字段（机构名、本体名、证据备注、租价来源等）。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
const dictP = path.join(root, 'src/i18n/data_en.json');
if (!fs.existsSync(dictP)) { console.log('en_apply: 没有 data_en.json，跳过'); process.exit(0); }
const dict = JSON.parse(fs.readFileSync(dictP, 'utf8'));
const CJK = /[一-鿿]/;
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const rules = Object.entries(dict).filter(([k, v]) => v && v !== k).map(([k, v]) => {
  if (!k.includes('{n}')) return { exact: k, v };
  const parts = k.split('{n}').map(esc); const re = new RegExp('^' + parts.join('(\\d[\\d,\\.]*)') + '$');
  return { re, v };
}).sort((a, b) => (b.exact || '').length - (a.exact || '').length);
const exact = new Map(rules.filter((r) => r.exact).map((r) => [r.exact, r.v]));
const regs = rules.filter((r) => r.re);
function tr(t) {
  const s = t.replace(/\s+/g, ' ').trim(); if (!CJK.test(s)) return null;
  if (exact.has(s)) return exact.get(s);
  for (const r of regs) { const m = s.match(r.re); if (m) { let i = 1; return r.v.replace(/\{n\}/g, () => m[i++]); } }
  return null;
}
function walk(dir, out = []) { for (const f of fs.readdirSync(dir)) { const p = path.join(dir, f); fs.statSync(p).isDirectory() ? walk(p, out) : f.endsWith('.html') && out.push(p); } return out; }
let files = 0, hits = 0, left = new Map();
for (const f of walk(path.join(root, 'dist/en'))) {
  let h = fs.readFileSync(f, 'utf8'); let changed = false;
  // 文本节点：>…< 之间（跳过 script/style）
  h = h.replace(/(<(script|style)[^>]*>[\s\S]*?<\/\2>)|>([^<]+)</g, (m, sc, _t, txt) => {
    if (sc) return sc; if (!CJK.test(txt)) return m;
    const lead = txt.match(/^\s*/)[0], trail = txt.match(/\s*$/)[0]; const v = tr(txt);
    if (v == null) { left.set(txt.trim().replace(/\d[\d,\.]*/g, '{n}'), (left.get(txt.trim()) || 0) + 1); return m; }
    changed = true; hits++; return '>' + lead + v + trail + '<';
  });
  h = h.replace(/(placeholder|title|alt)="([^"]*[一-鿿][^"]*)"/g, (m, a, v) => { const t = tr(v); if (t == null) return m; changed = true; hits++; return `${a}="${t.replace(/"/g, '&quot;')}"`; });
  if (changed) { fs.writeFileSync(f, h); files++; }
}
console.log(`en_apply: 改 ${files} 个文件 · 替换 ${hits} 处 · 未翻唯一串 ${left.size}`);
if (process.argv.includes('--report')) for (const [k, v] of [...left.entries()].sort((a, b) => b[1] - a[1]).slice(0, 40)) console.log(' ', v, '×', k.slice(0, 90));
