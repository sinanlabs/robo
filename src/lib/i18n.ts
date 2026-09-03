import zh from '../i18n/zh-CN.json';
import en from '../i18n/en.json';

export type Lang = 'zh-cn' | 'en';
const dict: Record<Lang, any> = { 'zh-cn': zh, en };

export function t(lang: Lang, key: string): string {
  const parts = key.split('.');
  let cur: any = dict[lang];
  for (const p of parts) cur = cur?.[p];
  if (cur === undefined) {
    let fb: any = dict['zh-cn'];
    for (const p of parts) fb = fb?.[p];
    return typeof fb === 'string' ? fb : key;
  }
  return typeof cur === 'string' ? cur : JSON.stringify(cur);
}
export function tl(lang: Lang, key: string): string[] {
  const parts = key.split('.');
  let cur: any = dict[lang];
  for (const p of parts) cur = cur?.[p];
  return Array.isArray(cur) ? cur : [];
}
export function langFromUrl(url: URL): Lang {
  return url.pathname === '/en' || url.pathname.startsWith('/en/') ? 'en' : 'zh-cn';
}
/** 生成对应语言的路径。zh-cn 无前缀，en 加 /en */
export function href(lang: Lang, path: string): string {
  const clean = path.startsWith('/') ? path : '/' + path;
  if (lang === 'en') return clean === '/' ? '/en' : '/en' + clean;
  return clean;
}
export function otherLang(lang: Lang): Lang { return lang === 'en' ? 'zh-cn' : 'en'; }
/** 把当前路径切换到另一语言 */
export function switchPath(lang: Lang, pathname: string): string {
  const stripped = pathname.replace(/^\/en(?=\/|$)/, '') || '/';
  return href(otherLang(lang), stripped);
}
