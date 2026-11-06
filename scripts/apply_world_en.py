# -*- coding: utf-8 -*-
"""英文页用：把 data/world_en.json（中文原文 → 英文）对上的字段写成 *_en（org_en、realtime_claim_en、evidence[].note_en …）。
用法：python3 scripts/apply_world_en.py [新增译文.json]   —— 有参数时先把新译文并进 data/world_en.json。
没有译文的字段留空，英文页退回显示原文；scripts/validate.mjs 不管 *_en。"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, DICT = os.path.join(ROOT, "data", "world_models.json"), os.path.join(ROOT, "data", "world_en.json")
FIELDS = ["org", "family", "base_model", "realtime_claim", "resolution_claim", "length_claim", "vram_note", "license_code", "license_weights"]
CJK = re.compile(r"[一-鿿]")

tr = json.load(io.open(DICT, encoding="utf-8")) if os.path.exists(DICT) else {}
if len(sys.argv) > 1:
    tr.update(json.load(io.open(sys.argv[1], encoding="utf-8")))
    json.dump(dict(sorted(tr.items())), io.open(DICT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
D = json.load(io.open(DATA, encoding="utf-8"))
hit = miss = 0
def en(v):
    global hit, miss
    if not isinstance(v, str) or not CJK.search(v): return None
    if v in tr: hit += 1; return tr[v]
    miss += 1; return None
for m in D["items"]:
    for k in FIELDS:
        x = en(m.get(k))
        if x: m[k + "_en"] = x
        else: m.pop(k + "_en", None)
    if isinstance(m.get("api"), dict):
        for k in ("provider", "price_note"):
            x = en(m["api"].get(k))
            if x: m["api"][k + "_en"] = x
    for e in m.get("evidence", []):
        x = en(e.get("note"))
        if x: e["note_en"] = x
json.dump(D, io.open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("英文：对上 %d 处 · 缺译文 %d 处（英文页显示原文）" % (hit, miss))
