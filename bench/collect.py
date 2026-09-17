# -*- coding: utf-8 -*-
"""把 results/*.json 合并成 Robo 站的 data/measurements/bench.json（去掉原始逐步延迟，保留摘要与证据）。"""
import os, io, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
rows = []
for f in sorted(glob.glob(os.path.join(HERE, "results", "*.json"))):
    r = json.load(io.open(f, encoding="utf-8")); r.pop("raw_latency_ms", None); r.pop("env", None); r.pop("model_info", None); r["metrics"].pop("load_s", None); rows.append(r)
os.makedirs(os.path.join(ROOT, "data", "measurements"), exist_ok=True)
json.dump(rows, io.open(os.path.join(ROOT, "data", "measurements", "bench.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("measurements: %d 条 → data/measurements/bench.json" % len(rows))
