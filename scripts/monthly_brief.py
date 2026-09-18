# -*- coding: utf-8 -*-
"""
Robo 月报的自动结构块：一个月里索引与生态的可数变化，全部来自本仓库数据（seed / activity / measurements / benchmarks / datasets / recipes）。
数字与分析分开：这里只产数字；分析写在 data/reports/<月>.analysis.md（zh）与 .analysis.en.md，页面把两者拼起来。
用法：python3 scripts/monthly_brief.py            当前北京月份
      python3 scripts/monthly_brief.py 2026-09    指定月份
"""
import io, os, re, sys, json, datetime as dt
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
BJ = dt.timezone(dt.timedelta(hours=8))
J = lambda *p: os.path.join(ROOT, *p)
load = lambda p, d: json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else d


def main():
    month = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(BJ).strftime("%Y-%m")
    y, m = int(month[:4]), int(month[5:7]); start = dt.date(y, m, 1); end = (dt.date(y + (m == 12), (m % 12) + 1, 1) - dt.timedelta(days=1))
    seed = load(J("data", "seed_v0.json"), {"models": [], "embodiments": [], "hardware": []}); models = seed["models"]
    A = load(J("data", "activity", "latest.json"), {"items": {}})["items"]
    meas = load(J("data", "measurements", "bench.json"), [])
    B = load(J("data", "benchmarks.json"), {"scores": [], "benchmarks": []}); D = load(J("data", "datasets.json"), {"datasets": []}); R = load(J("data", "recipes.json"), {"recipes": [], "not_reproduced": []})
    hist = []
    hp = J("data", "activity", "history.jsonl")
    if os.path.exists(hp):
        for ln in io.open(hp, encoding="utf-8"):
            try: hist.append(json.loads(ln))
            except Exception: pass
    name = lambda i: next((x["name"] for x in models if x["id"] == i), i)
    # 索引构成
    cn = [x for x in models if re.search(r"[一-鿿]", x.get("org", "")) and not re.search(r"Stanford|Berkeley|MIT|KAIST|Meta|Microsoft|NVIDIA|Google|Allen|Physical|Hugging|Declare|Apple", x.get("org", ""))]
    lic = {"yes": sum(1 for x in models if x.get("commercial_ok") is True), "no": sum(1 for x in models if x.get("commercial_ok") is False), "unk": sum(1 for x in models if x.get("commercial_ok") is None)}
    params = [x["params_b"] for x in models if x.get("params_b")]
    size = {"lt1": sum(1 for p in params if p < 1), "b1_4": sum(1 for p in params if 1 <= p < 4), "b4_8": sum(1 for p in params if 4 <= p < 8), "ge8": sum(1 for p in params if p >= 8)}
    years = Counter(x["release_date"][:4] for x in models if x.get("release_date") and x["release_date"][:4].isdigit())
    new_this_month = [{"id": x["id"], "name": x["name"], "org": x["org"]} for x in models if (x.get("release_date") or "").startswith(month)]
    # 活性
    gh = [(k, v["github"]) for k, v in A.items() if (v.get("github") or {}).get("ok")]
    hf = [(k, v["hf"]) for k, v in A.items() if (v.get("hf") or {}).get("ok")]
    stale = sorted([{"id": k, "name": name(k), "days": g.get("days_since_push"), "pushed": g.get("pushed_at")} for k, g in gh if (g.get("days_since_push") or 0) > 180], key=lambda x: -x["days"])
    zero90 = [k for k, g in gh if g.get("commits_90d") == 0]
    active = sorted([{"id": k, "name": name(k), "c90": g.get("commits_90d"), "capped": g.get("commits_90d_capped")} for k, g in gh if (g.get("commits_90d") or 0) > 0], key=lambda x: -x["c90"])
    dl = sorted([{"id": k, "name": name(k), "dl30": h.get("downloads_30d") or 0, "repo": h.get("repo")} for k, h in hf], key=lambda x: -x["dl30"])
    dl_total = sum(x["dl30"] for x in dl); top3 = sum(x["dl30"] for x in dl[:3])
    stars = sorted([{"id": k, "name": name(k), "stars": g.get("stars") or 0} for k, g in gh], key=lambda x: -x["stars"])
    ms = [k for k, v in A.items() if (v.get("modelscope") or {}).get("ok")]
    gated = [k for k, h in hf if h.get("gated")]
    # 实测
    m_month = [x for x in meas if (x.get("created_at") or "")[:7] == month]
    by_hw = {}
    for x in meas: by_hw.setdefault(x["hardware_id"], []).append({"model_id": x["model_id"], "name": name(x["model_id"]), "p50": x["metrics"]["latency_ms_p50"], "p95": x["metrics"].get("latency_ms_p95"), "vram": x["metrics"].get("vram_peak_gb"), "precision": x.get("precision")})
    for v in by_hw.values(): v.sort(key=lambda r: r["p50"])
    # 分数 / 数据集
    sc = B.get("scores", []); ds = D.get("datasets", [])
    bench_cov = Counter(s["benchmark_id"] for s in sc); models_with_score = len(set(s["model_id"] for s in sc))
    ds_hours = sum((d.get("hours") or 0) for d in ds); ds_eps = sum((d.get("episodes") or 0) for d in ds)
    ds_forms = Counter(t for d in ds for t in (d.get("form_tags") or [])); ds_lic = Counter("yes" if d.get("commercial_ok") is True else "no" if d.get("commercial_ok") is False else "unk" for d in ds)
    ds_mirror = sum(1 for d in ds if d.get("mirror_url")); ds_top = sorted([{"id": d["id"], "name": d["name"], "hours": d.get("hours"), "episodes": d.get("episodes")} for d in ds if d.get("hours")], key=lambda x: -x["hours"])[:5]
    out = {"month": month, "from": start.isoformat(), "to": end.isoformat(), "generated": dt.datetime.now(BJ).isoformat(timespec="seconds"),
           "index": {"models": len(models), "embodiments": len(seed.get("embodiments", [])), "hardware": len(seed.get("hardware", [])), "chinese_org": len(cn), "license": lic, "size": size, "release_years": dict(years), "new_this_month": new_this_month},
           "activity": {"repos": len(gh), "stale_180": len(stale), "stale_list": stale[:10], "zero_commits_90": len(zero90), "active_list": active[:10], "hf_repos": len(hf), "dl30_total": dl_total, "dl30_top3_share": round(top3 / dl_total, 3) if dl_total else None, "dl_top": dl[:8], "stars_top": stars[:6], "modelscope_mirrors": len(ms), "gated": gated, "snapshot_days": len(set(h["d"] for h in hist))},
           "measurements": {"total": len(meas), "this_month": len(m_month), "by_hardware": by_hw, "recipes": len(R.get("recipes", [])), "not_reproduced": [x["model_id"] for x in R.get("not_reproduced", [])]},
           "benchmarks": {"scores": len(sc), "models_with_score": models_with_score, "by_benchmark": dict(bench_cov)},
           "datasets": {"count": len(ds), "hours_total": ds_hours, "episodes_total": ds_eps, "forms": dict(ds_forms), "license": dict(ds_lic), "mirrors": ds_mirror, "top_hours": ds_top}}
    os.makedirs(J("data", "reports"), exist_ok=True)
    json.dump(out, io.open(J("data", "reports", month + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("monthly %s: 模型 %d · 停更 %d/%d · 实测 %d · 分数 %d · 数据集 %d → data/reports/%s.json" % (month, len(models), len(stale), len(gh), len(meas), len(sc), len(ds), month))


if __name__ == "__main__":
    main()
