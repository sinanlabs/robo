# -*- coding: utf-8 -*-
"""把核实好的世界模型条目（每批一个 JSON 数组）合并进 data/world_models.json。
用法：python3 scripts/merge_world.py 批次1.json [批次2.json ...]
- 同 id 以后来的为准（重新核实过的覆盖旧的）；不在本次批次里的旧条目保留。
- 页面上显示的原文摘录里，“推荐”改写成“建议”（司南措辞规则：我们的页面不出现“推荐”，原文意思不变）。
- robo_model_ids：世界模型 → 索引里基于它的机器人模型（手工维护的对应表，见 LINKS）。"""
import io, json, os, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "world_models.json")
LINKS = {"v-jepa-2-ac": ["vjepa2-ac"], "agibot-ge-base-v0-1": ["genie-envisioner"]}   # GE-Act 建在 GE-Base 上
SHOWN = ("realtime_claim", "resolution_claim", "length_claim", "vram_note", "notes")


def clean(m):
    for k in SHOWN:
        if isinstance(m.get(k), str): m[k] = m[k].replace("推荐", "建议")
    if isinstance(m.get("api"), dict) and isinstance(m["api"].get("price_note"), str):
        m["api"]["price_note"] = m["api"]["price_note"].replace("推荐", "建议")
    if m["id"] in LINKS: m["robo_model_ids"] = LINKS[m["id"]]
    return m


cur = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"_meta": {}, "items": []}
items = {m["id"]: m for m in cur.get("items", [])}
n = 0
for p in sys.argv[1:]:
    for m in json.load(io.open(p, encoding="utf-8")):
        items[m["id"]] = clean(m); n += 1
order = sorted(items.values(), key=lambda m: (str(m.get("release_date") or "0"), m["name"]), reverse=True)
cur["items"] = order
cur["_meta"]["updated"] = dt.date.today().isoformat()
json.dump(cur, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("合并 %d 条 → 共 %d 条（%s）" % (n, len(order), os.path.relpath(OUT, ROOT)))
