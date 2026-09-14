# -*- coding: utf-8 -*-
"""适配矩阵证据挖掘：抓每个模型的 GitHub README（raw）与 arXiv 摘要页，按本体关键词找"在哪个机器人上跑过"的原文片段。
只产出候选（带 URL + 原文片段）到 data/mine/compat_candidates.json，由人复核后写入 data/compat_overrides.json。不自动改矩阵。"""
import json, re, io, os, time, html
import httpx
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(io.open(os.path.join(ROOT, "data", "seed_v0.json"), encoding="utf-8"))
KW = {
    "unitree-g1": [r"unitree\s*g1", r"\bG1\b.{0,20}humanoid", r"宇树\s*G1"],
    "unitree-h1": [r"unitree\s*h1", r"\bH1\b.{0,20}humanoid"],
    "agibot-genie-g1": [r"genie[- ]?1\b", r"agibot\s*g1", r"精灵\s*G1", r"agibot\s*world"],
    "agilex-piper": [r"\bpiper\b", r"agilex\s*piper", r"松灵"],
    "so-101": [r"so[- ]?10[01]\b"],
    "franka-fr3": [r"\bfr3\b", r"franka\s*research\s*3"],
    "franka-panda": [r"franka(?!\s*research)", r"\bpanda\s*(arm|robot)"],
    "fourier-gr": [r"fourier", r"\bgr-?[12]\b.{0,20}(humanoid|fourier)"],
    "widowx-250s": [r"widowx", r"bridge\s*(v2|data)", r"bridgedata"],
    "google-robot": [r"google\s*robot", r"everyday\s*robots?", r"fractal20220817", r"rt-1\s*(dataset|data)"],
    "aloha-2": [r"\baloha\b", r"cobot\s*magic", r"trossen"],
    "galaxea-r1pro": [r"galaxea", r"\br1[- ]?pro\b"],
}
SIM = re.compile(r"simpler[- ]?env|libero|simulation|simulated|\bsim\b|isaac\s*(lab|sim)|mujoco|maniskill|robocasa|calvin", re.I)
def raw_readme(code_url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/#]+)", code_url or "")
    if not m: return []
    o, r = m.group(1), m.group(2)
    return ["https://raw.githubusercontent.com/%s/%s/main/README.md" % (o, r), "https://raw.githubusercontent.com/%s/%s/master/README.md" % (o, r)]
def fetch(c, url):
    try:
        r = c.get(url)
        if r.status_code == 200 and len(r.text) > 200: return r.text
    except Exception: pass
    return None
out = {}
with httpx.Client(timeout=25, follow_redirects=True, headers={"User-Agent": "sinan-robo-compat-miner/0.1 (+https://robo.sinanlab.com/methodology)"}) as c:
    for m in d["models"]:
        texts = []
        for u in raw_readme(m.get("code_url")):
            t = fetch(c, u)
            if t: texts.append((u, t)); break
        if m.get("paper_url") and "arxiv.org" in m["paper_url"]:
            t = fetch(c, m["paper_url"].replace("/pdf/", "/abs/"))
            if t:
                t = html.unescape(re.sub(r"<[^>]+>", " ", t)); texts.append((m["paper_url"], t))
        cands = []
        for emb, pats in KW.items():
            for src, t in texts:
                for p in pats:
                    for mm in re.finditer(p, t, re.I):
                        s0 = max(0, mm.start() - 160); s1 = min(len(t), mm.end() + 160)
                        snip = re.sub(r"\s+", " ", t[s0:s1]).strip()
                        cands.append({"embodiment": emb, "src": src, "pattern": p, "snippet": snip, "sim_context": bool(SIM.search(snip))})
                        if sum(1 for x in cands if x["embodiment"] == emb and x["src"] == src) >= 3: break
        out[m["id"]] = {"name": m["name"], "sources": [u for u, _ in texts], "candidates": cands}
        print("%-20s 源 %d · 候选 %d · 本体 %s" % (m["id"], len(texts), len(cands), sorted({x["embodiment"] for x in cands})))
        time.sleep(0.5)
io.open(os.path.join(ROOT, "data", "mine", "compat_candidates.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
