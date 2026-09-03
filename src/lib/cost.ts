/**
 * 每千次推理成本（元）= 延迟 p50(ms) / 1000 × 租价(元/小时) / 3600 × 1000
 * 任一输入缺失返回 null，并给出原因码，前台渲染为“— + 原因徽标”。
 */
export type CostResult = { cny: number | null; why: 'ok' | 'noLatency' | 'noRent' };

export function costPer1k(latencyMsP50: number | null | undefined, rentalCnyPerHour: number | null | undefined): CostResult {
  if (latencyMsP50 == null || !(latencyMsP50 > 0)) return { cny: null, why: 'noLatency' };
  if (rentalCnyPerHour == null || !(rentalCnyPerHour > 0)) return { cny: null, why: 'noRent' };
  const cny = (latencyMsP50 / 1000) * (rentalCnyPerHour / 3600) * 1000;
  return { cny, why: 'ok' };
}

export function fmtCny(v: number | null): string {
  if (v == null) return '—';
  if (v < 0.01) return v.toFixed(4);
  if (v < 1) return v.toFixed(3);
  return v.toFixed(2);
}

export function fmtMs(v: number | null | undefined): string {
  if (v == null) return '—';
  return v < 10 ? v.toFixed(1) : Math.round(v).toString();
}
