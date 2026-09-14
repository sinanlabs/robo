// 构建时从 Sinan Compute 读取每日算力租赁账本（公开 JSON），给硬件页提供实时租价。
// 读不到就返回空，页面退回 seed 里的静态参考价；绝不因为对方站点抖动让 Robo 构建失败。
export type LiveRent = { cny: number; usd: number; platform: string; kind: string; ts: string; n: number };
const MAP: Record<string, string> = { 'rtx-4090': 'RTX 4090', 'rtx-5090': 'RTX 5090', 'a100-80g': 'A100 SXM4', 'h100-80g': 'H100 SXM' };
let cache: any | null | undefined;
async function ledger(): Promise<any | null> {
  if (cache !== undefined) return cache;
  try {
    const r = await fetch('https://compute.sinanlab.com/gpu.json', { signal: AbortSignal.timeout(8000) });
    cache = r.ok ? await r.json() : null;
  } catch { cache = null; }
  return cache;
}
/** 代表价：Vast.ai 按需中位（个人机主市场里真能租到的价）；没有就用 RunPod 社区云。 */
export async function liveRent(hardwareId: string): Promise<LiveRent | null> {
  const L = await ledger(); if (!L) return null;
  const name = MAP[hardwareId]; if (!name) return null;
  const g = (L.gpus || []).find((x: any) => x.gpu === name); if (!g) return null;
  const pick = g.quotes.find((q: any) => q.platform === 'vast' && q.kind === 'median') || g.quotes.find((q: any) => q.platform === 'runpod' && q.kind === 'community');
  if (!pick) return null;
  return { cny: pick.cny, usd: pick.usd, platform: pick.platform === 'vast' ? 'Vast.ai 按需中位' : 'RunPod 社区云', kind: pick.kind, ts: pick.ts, n: pick.n };
}
export async function allQuotes(hardwareId: string): Promise<{ platform: string; kind: string; usd: number; cny: number; n: number }[]> {
  const L = await ledger(); const name = MAP[hardwareId]; if (!L || !name) return [];
  const g = (L.gpus || []).find((x: any) => x.gpu === name); if (!g) return [];
  const PF: Record<string, string> = { runpod: 'RunPod', vast: 'Vast.ai', suanli: '共绩算力' };
  const KD: Record<string, string> = { secure: '安全云', community: '社区云', min: '按需最低', median: '按需中位', starting: '官网起步价' };
  return g.quotes.map((q: any) => ({ platform: PF[q.platform] || q.platform, kind: KD[q.kind] || q.kind, usd: q.usd, cny: q.cny, n: q.n }));
}
