# -*- coding: utf-8 -*-
"""
每晚：把线上 D1 里 Robo 众测的两张表拉下来（只拉后台核验通过的）：
  robo_measurement（review_status='verified'）→ data/measurements/crowd.json   （measurements 集合直接导入；source_type=crowd）
  robo_repro（review_status='verified'）      → data/compat_repro.json          （import-seed 把对应格子升为 community_verified，并附证据链接）
拉不到（额度用尽 / 网络）就保留上次文件，不让构建失败。
"""
import io, os, json, subprocess, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
J = lambda *p: os.path.join(ROOT, *p)


def d1(sql):
    r = subprocess.run(["npx", "wrangler", "d1", "execute", "sinan-users", "--remote", "--json", "--command", sql], capture_output=True, text=True, cwd=os.path.join(ROOT, "..", "compass"), timeout=120)
    if r.returncode != 0: raise RuntimeError((r.stderr or r.stdout)[-300:])
    return json.loads(r.stdout)[0]["results"]


def main():
    try:
        rows = d1("SELECT id, model_id, hardware_id, gpu_name, precision, config_json, metrics_json, env_json, client_version, reviewed_at, created_at FROM robo_measurement WHERE review_status='verified' ORDER BY created_at")
        reps = d1("SELECT id, model_id, embodiment_id, outcome, setting, evidence_url, note, reviewed_at, created_at FROM robo_repro WHERE review_status='verified' ORDER BY created_at")
    except Exception as e:
        print("Robo 众测拉取失败（沿用上次文件）：", str(e)[:200]); return
    meas = []
    for x in rows:
        if not x.get("hardware_id"): continue   # 映射不到索引硬件的先不进站（后台可手工改 hardware_id）
        cfg = json.loads(x["config_json"] or "{}"); met = json.loads(x["metrics_json"] or "{}"); env = json.loads(x["env_json"] or "{}")
        meas.append({"id": "crowd-%d__%s__%s__%s" % (x["id"], x["model_id"], x["hardware_id"], x["precision"]), "model_id": x["model_id"], "hardware_id": x["hardware_id"], "precision": x["precision"],
                     "config": {"batch": int(cfg.get("batch") or 1), "image_res": str(cfg.get("image_res") or ""), "action_chunk": int(cfg.get("action_chunk") or 0), "warmup_steps": int(cfg.get("warmup_steps") or 0), "steps": int(cfg.get("steps") or 0)},
                     "metrics": {"latency_ms_p50": float(met.get("latency_ms_p50")), "latency_ms_p95": met.get("latency_ms_p95"), "throughput_chunks_s": met.get("throughput_chunks_s"), "vram_peak_gb": met.get("vram_peak_gb")},
                     "source_type": "crowd", "review_status": "verified",
                     "evidence": [{"field": "metrics", "url": "https://compute.sinanlab.com/api/robo/measure?model=" + x["model_id"], "source_type": "official", "fetched": (x.get("reviewed_at") or x["created_at"])[:10],
                                   "note": "众测上传 #%d · %s · driver %s · CUDA %s · torch %s · %s · 权重 %s · 后台核验 %s" % (x["id"], x["gpu_name"], env.get("driver") or "?", env.get("cuda") or "?", env.get("torch") or "?", env.get("os") or "?", env.get("revision") or "?", (x.get("reviewed_at") or "")[:10])}],
                     "created_at": x["created_at"].replace(" ", "T") + "+00:00"})
    os.makedirs(J("data", "measurements"), exist_ok=True)
    json.dump(meas, io.open(J("data", "measurements", "crowd.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    repro = [{"id": x["id"], "model_id": x["model_id"], "embodiment_id": x["embodiment_id"], "outcome": x["outcome"], "setting": x.get("setting"), "evidence_url": x.get("evidence_url"), "note": x.get("note"), "verified_at": (x.get("reviewed_at") or x["created_at"])[:10], "created_at": x["created_at"]} for x in reps]
    json.dump({"generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "items": repro}, io.open(J("data", "compat_repro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Robo 众测：实测 %d 条（核验通过）· 复现记录 %d 条 → data/measurements/crowd.json · data/compat_repro.json" % (len(meas), len(repro)))


if __name__ == "__main__":
    main()
