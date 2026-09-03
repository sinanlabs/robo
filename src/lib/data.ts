import { isPending } from './evidence';

export const MODEL_REQUIRED = ['name', 'org', 'release_date', 'params_b', 'license', 'commercial_ok', 'weights_url', 'code_url'];
export const EMB_REQUIRED = ['name', 'vendor', 'form', 'dof', 'end_effector', 'sdk_url', 'price_range_cny'];
export const HW_REQUIRED = ['name', 'vram_gb', 'rental_cny_per_hour_ref'];

export function pendingOf(rec: Record<string, unknown>, fields: string[]) {
  let pending = 0; for (const f of fields) if (isPending(rec[f])) pending++;
  return { pending, total: fields.length, ok: fields.length - pending };
}

/** 许可证粗分类，仅用于筛选；展示仍用原文 */
export function licenseClass(lic: unknown): 'apache' | 'mit' | 'open_other' | 'pending' {
  if (isPending(lic)) {
    if (typeof lic === 'string' && /Apache/i.test(lic)) return 'apache';
    if (typeof lic === 'string' && /MIT/i.test(lic)) return 'mit';
    return 'pending';
  }
  const s = String(lic);
  if (/Apache/i.test(s)) return 'apache';
  if (/MIT/i.test(s)) return 'mit';
  return 'open_other';
}

export function crossClass(v: unknown): 'yes' | 'no' | 'pending' {
  if (isPending(v)) return 'pending';
  const s = String(v);
  if (/^是|^yes|多本体|Open X|覆盖/i.test(s)) return 'yes';
  if (/以.*为主/.test(s)) return 'no';
  return 'yes';
}

export function fmtParams(b: number | null): string {
  if (b == null) return '';
  return b >= 1 ? `${b}B` : `${Math.round(b * 1000)}M`;
}
