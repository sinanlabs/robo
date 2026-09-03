export type Evidence = { field: string; url: string; source_type: 'literature' | 'news' | 'hub' | 'official'; fetched: string; sha256?: string | null; note?: string };

const PENDING = /待核实|待定|TBA/;

/** 字段值是否“待核实”：null / 空 / 含待核实字样 / 空数组 */
export function isPending(v: unknown): boolean {
  if (v === null || v === undefined) return true;
  if (typeof v === 'string') return v.trim() === '' || PENDING.test(v);
  if (Array.isArray(v)) return v.length === 0 || v.every(isPending);
  return false;
}

/** 值里若含“(...待核实...)”括注，拆成 主值 + 备注 */
export function splitPending(v: unknown): { main: string; note: string | null } {
  if (typeof v !== 'string') return { main: String(v ?? ''), note: null };
  const m = v.match(/^(.*?)\s*[（(]([^()（）]*(?:待核实|待定)[^()（）]*)[)）]\s*$/);
  if (m) return { main: m[1].trim(), note: m[2].trim() };
  return { main: v, note: PENDING.test(v) ? v : null };
}

/** 哪些 evidence 覆盖了这个字段 */
export function evidenceFor(list: Evidence[] | undefined, field: string): Evidence[] {
  return (list ?? []).filter((e) => e.field.split(',').map((s) => s.trim()).includes(field));
}

/** 统计一条记录里必填字段的待核实数量 */
export function pendingCount(rec: Record<string, unknown>, fields: string[]): { pending: number; total: number } {
  let pending = 0;
  for (const f of fields) if (isPending(rec[f])) pending++;
  return { pending, total: fields.length };
}

export function isUrl(v: unknown): v is string {
  return typeof v === 'string' && /^https?:\/\/\S+$/.test(v.trim());
}

export function hostOf(url: string): string {
  try { return new URL(url).host.replace(/^www\./, ''); } catch { return url; }
}
