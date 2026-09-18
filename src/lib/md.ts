/** 极简 Markdown → HTML：标题、段落、列表、表格、粗体、链接、行内代码。够月报分析稿用；不处理 HTML 原文（先转义）。 */
const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function inline(s: string): string {
  return esc(s)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|\/[^)\s]*)\)/g, '<a href="$2" rel="noopener">$1</a>');
}
export function mdToHtml(md: string): string {
  const lines = md.replace(/\r/g, '').split('\n');
  const out: string[] = []; let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) { i++; continue; }
    const h = l.match(/^(#{1,4})\s+(.*)$/);
    if (h) { const lv = h[1].length + 1; out.push(`<h${lv}>${inline(h[2])}</h${lv}>`); i++; continue; }
    if (/^\|/.test(l)) {
      const rows: string[] = []; while (i < lines.length && /^\|/.test(lines[i])) rows.push(lines[i++]);
      const cells = (r: string) => r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const head = cells(rows[0]); const body = rows.slice(1).filter((r) => !/^\|\s*:?-+/.test(r));
      out.push('<div class="tablewrap"><table><thead><tr>' + head.map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>' + body.map((r) => '<tr>' + cells(r).map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>');
      continue;
    }
    if (/^\s*[-*]\s+/.test(l)) { const items: string[] = []; while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*[-*]\s+/, '')); out.push('<ul>' + items.map((x) => `<li>${inline(x)}</li>`).join('') + '</ul>'); continue; }
    if (/^\s*\d+[.)]\s+/.test(l)) { const items: string[] = []; while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) items.push(lines[i++].replace(/^\s*\d+[.)]\s+/, '')); out.push('<ol>' + items.map((x) => `<li>${inline(x)}</li>`).join('') + '</ol>'); continue; }
    if (/^>\s?/.test(l)) { const q: string[] = []; while (i < lines.length && /^>\s?/.test(lines[i])) q.push(lines[i++].replace(/^>\s?/, '')); out.push(`<blockquote>${inline(q.join(' '))}</blockquote>`); continue; }
    const p: string[] = []; while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|\||\s*[-*]\s|\s*\d+[.)]\s|>)/.test(lines[i])) p.push(lines[i++]);
    out.push(`<p>${inline(p.join(' '))}</p>`);
  }
  return out.join('\n');
}
/** 把 "## [key] 标题" 分节：返回 {key, title, html}[]；没有 [key] 的节 key 为空。 */
export function sections(md: string): { key: string; title: string; html: string }[] {
  const parts = md.replace(/\r/g, '').split(/^## /m).filter((x) => x.trim());
  return parts.map((p) => { const nl = p.indexOf('\n'); const head = nl >= 0 ? p.slice(0, nl) : p; const body = nl >= 0 ? p.slice(nl + 1) : ''; const m = head.match(/^\[([^\]]+)\]\s*(.*)$/); return { key: m ? m[1] : '', title: m ? m[2] : head.trim(), html: mdToHtml(body) }; });
}
