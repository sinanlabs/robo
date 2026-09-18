# -*- coding: utf-8 -*-
"""
Robo 周报（自动结构块）：把过去 7 天的活性快照、索引变化、实测新增汇总成一份 JSON，供 /weekly 页面、RSS 与社媒源使用。
只陈述变化与数字，不评价；每一项都能回溯到当日快照。
  输入：data/activity/history.jsonl · data/activity/latest.json · data/seed_v0.json · data/measurements/bench.json · data/recipes.json
  输出：data/weekly/<ISO 周>.json（同周重跑覆盖）
用法：python3 scripts/weekly_brief.py            以北京时间今天为截止日，窗口 = 前 7 天
      python3 scripts/weekly_brief.py 2026-09-21 指定截止日（调试 / 补发）
"""
import io, os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
BJ = dt.timezone(dt.timedelta(hours=8))
J = lambda *p: os.path.join(ROOT, *p)


def load_json(p, default):
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else default


def main():
    end = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(BJ).date()
    start = end - dt.timedelta(days=7)
    week = end.isocalendar(); wk = "%d-W%02d" % (week[0], week[1])
    seed = load_json(J("data", "seed_v0.json"), {"models": []}); models = {m["id"]: m for m in seed["models"]}
    latest = load_json(J("data", "activity", "latest.json"), {"items": {}})["items"]
    hist = []
    hp = J("data", "activity", "history.jsonl")
    if os.path.exists(hp):
        for ln in io.open(hp, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try: hist.append(json.loads(ln))
                except Exception: pass
    days = sorted(set(h["d"] for h in hist))
    in_win = [d for d in days if start.isoformat() <= d <= end.isoformat()]
    d0, d1 = (in_win[0], in_win[-1]) if in_win else (None, None)
    snap = lambda d: {h["id"]: h for h in hist if h["d"] == d} if d else {}
    S0, S1 = snap(d0), snap(d1)
    name = lambda mid: models.get(mid, {}).get("name", mid)
    org = lambda mid: models.get(mid, {}).get("org", "")

    # 1. 新收录：窗口末快照里有、窗口首快照里没有的模型（首个快照日之前的模型不算）
    new_models = [{"id": i, "name": name(i), "org": org(i), "release_date": models.get(i, {}).get("release_date")} for i in S1 if i not in S0 and i in models] if d0 and d0 != d1 else []
    # 2. 权重更新：HF 最后修改时间落在窗口内
    weights_updated = []
    for mid, r in latest.items():
        lm = (r.get("hf") or {}).get("last_modified")
        if lm and start.isoformat() < lm <= end.isoformat(): weights_updated.append({"id": mid, "name": name(mid), "repo": r["hf"].get("repo"), "last_modified": lm})
    weights_updated.sort(key=lambda x: x["last_modified"], reverse=True)
    # 3. 许可证文本变化 / 权重链接变化（对比窗口首末快照）
    license_changed, weights_moved = [], []
    for mid in S1:
        a, b = S0.get(mid), S1[mid]
        if not a: continue
        if (a.get("lic") or "") != (b.get("lic") or ""): license_changed.append({"id": mid, "name": name(mid), "from": a.get("lic"), "to": b.get("lic")})
        if (a.get("w") or "") != (b.get("w") or ""): weights_moved.append({"id": mid, "name": name(mid), "from": a.get("w"), "to": b.get("w")})
    # 4. 提交与 stars 变化
    commits = sorted([{"id": mid, "name": name(mid), "c90": r["github"].get("commits_90d"), "capped": r["github"].get("commits_90d_capped"), "pushed": r["github"].get("pushed_at")} for mid, r in latest.items() if (r.get("github") or {}).get("ok") and (r["github"].get("commits_90d") or 0) > 0], key=lambda x: -x["c90"])[:10]
    stars_gain = []
    for mid in S1:
        a, b = S0.get(mid), S1[mid]
        if a and a.get("stars") is not None and b.get("stars") is not None and b["stars"] - a["stars"] != 0: stars_gain.append({"id": mid, "name": name(mid), "delta": b["stars"] - a["stars"], "stars": b["stars"]})
    stars_gain.sort(key=lambda x: -x["delta"]); stars_gain = stars_gain[:10]
    downloads = sorted([{"id": mid, "name": name(mid), "dl30": r["hf"].get("downloads_30d"), "repo": r["hf"].get("repo")} for mid, r in latest.items() if (r.get("hf") or {}).get("ok") and r["hf"].get("downloads_30d") is not None], key=lambda x: -x["dl30"])[:10]
    # 5. 停更提示：> 180 天无推送（事实）
    stale = sorted([{"id": mid, "name": name(mid), "days": r["github"].get("days_since_push"), "pushed": r["github"].get("pushed_at"), "archived": r["github"].get("archived")} for mid, r in latest.items() if (r.get("github") or {}).get("ok") and (r["github"].get("days_since_push") or 0) > 180], key=lambda x: -x["days"])
    # 6. 实测新增
    meas = load_json(J("data", "measurements", "bench.json"), [])
    new_meas = [{"model_id": m["model_id"], "name": name(m["model_id"]), "hardware_id": m["hardware_id"], "precision": m.get("precision"), "p50": m["metrics"].get("latency_ms_p50"), "p95": m["metrics"].get("latency_ms_p95"), "vram": m["metrics"].get("vram_peak_gb"), "date": m.get("created_at", "")[:10]} for m in meas if start.isoformat() < m.get("created_at", "")[:10] <= end.isoformat()]
    new_meas.sort(key=lambda x: (x["hardware_id"], x["p50"] or 0))
    recipes = load_json(J("data", "recipes.json"), {"recipes": []})
    # 7. 自动摘要（只数数）
    counts = {"models": len(models), "measurements": len(meas), "recipes": len(recipes.get("recipes", [])), "snap_days": len(in_win), "tracked": len(latest)}
    zh = "%s 至 %s：索引 %d 个模型；本周新收录 %d 个，权重在本周内更新的 %d 个，许可证文本变化 %d 个；实测新增 %d 条（累计 %d 条）；超过 180 天无推送的仓库 %d 个。数据取自 %d 天的每日快照。" % (
        start.isoformat(), end.isoformat(), counts["models"], len(new_models), len(weights_updated), len(license_changed), len(new_meas), counts["measurements"], len(stale), counts["snap_days"])
    en = "%s to %s: %d models indexed; %d newly indexed this week, %d with weights modified this week, %d licence-text changes; %d new measurements (%d total); %d repositories with no push for over 180 days. Based on %d daily snapshots." % (
        start.isoformat(), end.isoformat(), counts["models"], len(new_models), len(weights_updated), len(license_changed), len(new_meas), counts["measurements"], len(stale), counts["snap_days"])
    top = commits[0] if commits else None
    x_en = "Open VLA weekly %s: %d models tracked, %d weights updated, %d new latency measurements. Most commits in 90 d: %s (%s). Numbers only, sources on every row." % (
        wk, counts["tracked"], len(weights_updated), len(new_meas), top["name"] if top else "—", ("100+" if top and top.get("capped") else str(top["c90"])) if top else "—")
    out = {"week": wk, "from": start.isoformat(), "to": end.isoformat(), "generated": dt.datetime.now(BJ).isoformat(timespec="seconds"), "snapshot_days": in_win, "counts": counts,
           "new_models": new_models, "weights_updated": weights_updated, "license_changed": license_changed, "weights_moved": weights_moved, "commits": commits, "stars_gain": stars_gain,
           "downloads": downloads, "stale": stale, "new_measurements": new_meas, "summary": {"zh": zh, "en": en}, "x_en": x_en, "url": "https://robo.sinanlab.com/weekly/%s" % wk}
    os.makedirs(J("data", "weekly"), exist_ok=True)
    json.dump(out, io.open(J("data", "weekly", wk + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("weekly %s: 新收录 %d · 权重更新 %d · 许可证变化 %d · 实测新增 %d · 停更 %d → data/weekly/%s.json" % (wk, len(new_models), len(weights_updated), len(license_changed), len(new_meas), len(stale), wk))


if __name__ == "__main__":
    main()
