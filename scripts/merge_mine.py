# -*- coding: utf-8 -*-
"""
把研究子任务写在 data/mine/ 里的原始文件合并成正式数据：
  data/mine/benchmarks_batch*.json  →  data/benchmarks.json  （分数逐条校验：模型 id 存在、基准 id 在定义表、数字可解析、有 source_url）
  data/mine/datasets_batch*.json    →  data/datasets.json    （字段规整、id 去重、每条至少一条 evidence）
只搬运、不补值；不合格的条目写进 data/mine/rejected.json 供人工看。
用法：python3 scripts/merge_mine.py
"""
import io, os, re, json, glob, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
J = lambda *p: os.path.join(ROOT, *p)
TODAY = dt.date.today().isoformat()


def load(p):
    try: return json.load(io.open(p, encoding="utf-8"))
    except Exception as e: print("跳过（读不出）", p, e); return None


def num(v):
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        m = re.search(r"-?\d+(?:\.\d+)?", v.replace(",", ""))
        return float(m.group(0)) if m else None
    return None


UNIT_MAP = {"fraction (as printed)": "fraction", "score (0-1)": "score 0-1", "task completion score (0-1)": "score 0-1", "progress score (max 1.0)": "score 0-1", "% (progress score)": "% progress", "% task progress": "% progress", "% (printed without unit; success rate)": "%", "% (printed without unit)": "%"}
def norm_unit(u):
    u = (u or "%").strip(); return UNIT_MAP.get(u, u)


def main():
    seed = load(J("data", "seed_v0.json")); model_ids = {m["id"] for m in seed["models"]}
    defs = load(J("data", "benchmark_defs.json")); bench_ids = {b["id"] for b in defs["benchmarks"]}
    rejected = {"scores": [], "datasets": []}
    # ---- 分数 ----
    scores, seen = [], set()
    for f in sorted(glob.glob(J("data", "mine", "benchmarks_batch*.json"))):
        d = load(f) or {}
        for s in d.get("scores", []):
            why = []
            mid = s.get("model_id"); bid = s.get("benchmark_id") or "other"
            if mid not in model_ids: why.append("model_id 不在索引")
            if bid not in bench_ids: why.append("benchmark_id 不在定义表")
            v = num(s.get("score"))
            if v is None: why.append("score 不可解析")
            if not (s.get("source_url") or "").startswith("http"): why.append("缺 source_url")
            if s.get("source_type") not in ("paper", "official", "third_party"): why.append("source_type 非法")
            if why: rejected["scores"].append({**s, "_why": why, "_file": os.path.basename(f)}); continue
            key = (mid, s.get("variant") or "", bid, s.get("subset") or "", s.get("source_url"))
            if key in seen: continue
            seen.add(key)
            scores.append({"id": "%s__%s__%s__%s__%d" % (mid, bid, (s.get("subset") or "na").replace(" ", "_"), (s.get("variant") or "base").replace(" ", "_").replace("/", "-"), len(scores)),
                           "model_id": mid, "variant": s.get("variant") or None, "benchmark_id": bid, "benchmark_name": s.get("benchmark_name") or None, "subset": s.get("subset") or None,
                           "score": v, "unit": norm_unit(s.get("unit")), "source_type": s["source_type"], "source_url": s["source_url"], "source_ref": s.get("source_ref") or "", "eval_notes": s.get("eval_notes") or "", "date": s.get("date") or None})
    json.dump({"generated": TODAY, "benchmarks": defs["benchmarks"], "scores": scores}, io.open(J("data", "benchmarks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # ---- 数据集 ----
    datasets, ids = [], set()
    FORMS = {"single_arm", "dual_arm", "humanoid", "mobile_manipulator", "wheeled", "quadruped", "human_hand", "human_video", "multi", "sim"}
    for f in sorted(glob.glob(J("data", "mine", "datasets_batch*.json"))):
        d = load(f) or {}
        for x in d.get("datasets", []):
            why = []
            sid = re.sub(r"[^a-z0-9.-]+", "-", (x.get("id") or x.get("name") or "").lower()).strip("-")
            if not sid: why.append("缺 id")
            if not (x.get("url") or "").startswith("http"): why.append("缺 url")
            ev = [e for e in (x.get("evidence") or []) if (e.get("url") or "").startswith("http")]
            if not ev: why.append("缺 evidence")
            if why: rejected["datasets"].append({**x, "_why": why, "_file": os.path.basename(f)}); continue
            if sid in ids: continue
            ids.add(sid)
            forms = [t for t in (x.get("form_tags") or []) if t in FORMS]
            rec = {"id": sid, "name": x.get("name"), "org": x.get("org"), "url": x["url"], "hf_url": x.get("hf_url") or None, "mirror_url": x.get("mirror_url") or None,
                   "embodiments": x.get("embodiments") or [], "form_tags": forms, "episodes": num(x.get("episodes")), "hours": num(x.get("hours")), "frames": num(x.get("frames")),
                   "tasks": x.get("tasks") if x.get("tasks") not in ("", None) else None, "scenes": x.get("scenes") if x.get("scenes") not in ("", None) else None,
                   "modalities": x.get("modalities") or [], "format": x.get("format") or None, "license": x.get("license") or None,
                   "commercial_ok": x.get("commercial_ok") if isinstance(x.get("commercial_ok"), bool) else None, "release_date": x.get("release_date") or None,
                   "size_gb": num(x.get("size_gb")), "evidence": [{"field": e.get("field", ""), "url": e["url"], "source_type": e.get("source_type", "official"), "fetched": e.get("fetched") or TODAY, "note": e.get("note", "")} for e in ev], "notes": x.get("notes") or ""}
            for k in ("episodes", "frames"):
                if rec[k] is not None: rec[k] = int(rec[k])
            datasets.append(rec)
    datasets.sort(key=lambda r: (-(r["hours"] or 0), -(r["episodes"] or 0)))
    json.dump({"generated": TODAY, "datasets": datasets}, io.open(J("data", "datasets.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(rejected, io.open(J("data", "mine", "rejected.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("分数 %d 条（拒 %d）· 数据集 %d 个（拒 %d）→ data/benchmarks.json · data/datasets.json" % (len(scores), len(rejected["scores"]), len(datasets), len(rejected["datasets"])))


if __name__ == "__main__":
    main()
