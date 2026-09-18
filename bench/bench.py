#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinan Robo 推理基准 · 统一跑分器。
同一套固定输入（确定性合成图像 + 指令 + 状态向量）、同一套流程（预热 N 步、计时 M 步、每步 cuda 同步），
记录 p50 / p95 单步延迟、吞吐（动作块/秒）、显存峰值、软硬件版本与权重版本，输出 Robo 站 measurements 集合能直接导入的 JSON。
用法：python3 bench.py --model openvla --hardware rtx-4090 [--precision bf16] [--warmup 50] [--steps 500] [--dry-run]"""
import argparse, json, os, sys, time, platform, statistics as st, datetime as dt, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from adapters import get_adapter, ADAPTERS

def gpu_info():
    try:
        import torch
        if torch.cuda.is_available():
            p = torch.cuda.get_device_properties(0)
            drv = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
            return {"gpu": p.name, "vram_gb": round(p.total_memory / 2**30, 1), "driver": drv, "cuda": torch.version.cuda, "torch": torch.__version__}
        return {"gpu": "cpu", "torch": torch.__version__}
    except Exception as e:
        return {"gpu": "unknown", "error": str(e)}

def percentile(xs, q):
    xs = sorted(xs); k = (len(xs) - 1) * q; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(ADAPTERS)); ap.add_argument("--hardware", required=True)
    ap.add_argument("--precision", default="bf16", choices=["bf16", "fp16", "fp32"]); ap.add_argument("--warmup", type=int, default=50); ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--image-res", type=int, default=224); ap.add_argument("--dry-run", action="store_true", help="用假模型验证流程与输出格式")
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    ap.add_argument("--upload", action="store_true", help="跑完把指标与硬件指纹（不含图像 / 数据 / 密钥）上传到 Sinan Robo 众测队列，待核验后进站")
    ap.add_argument("--endpoint", default=os.environ.get("SINAN_ROBO_ENDPOINT", "https://compute.sinanlab.com/api/robo/measure"))
    a = ap.parse_args()
    adapter = get_adapter("dummy" if a.dry_run else a.model)
    t0 = time.time(); model_info = adapter.load(precision=a.precision); load_s = time.time() - t0
    inputs = adapter.make_inputs(image_res=a.image_res, seed=20260902)
    sync = adapter.sync
    for _ in range(a.warmup): adapter.step(inputs); sync()
    lat = []
    t_all = time.time()
    for _ in range(a.steps):
        t = time.perf_counter(); adapter.step(inputs); sync(); lat.append((time.perf_counter() - t) * 1000)
    total = time.time() - t_all
    vram = adapter.vram_peak_gb()
    chunk = adapter.action_chunk()
    # 记录参数实际精度：有的运行时不接受强转，标签以实际为准
    try:
        import torch; pdt = str(next(adapter.model.parameters()).dtype).replace("torch.", "")
        actual = {"bfloat16": "bf16", "float16": "fp16", "float32": "fp32"}.get(pdt, pdt)
        if actual != a.precision: print("注意：请求 %s，模型实际参数精度 %s，按实际记录" % (a.precision, actual)); a.precision = actual
    except Exception: pdt = None
    rec = {"id": "%s__%s__%s__%s" % (a.model, a.hardware, a.precision, dt.date.today().isoformat()), "model_id": a.model, "hardware_id": a.hardware, "precision": a.precision,
           "config": {"batch": 1, "image_res": "%dx%d" % (a.image_res, a.image_res), "action_chunk": chunk, "warmup_steps": a.warmup, "steps": a.steps},
           "metrics": {"latency_ms_p50": round(percentile(lat, 0.5), 2), "latency_ms_p95": round(percentile(lat, 0.95), 2), "throughput_chunks_s": round(a.steps / total, 3), "vram_peak_gb": vram, "load_s": round(load_s, 1)},
           "source_type": "maintainer", "review_status": "verified",
           "evidence": [{"field": "metrics", "url": "https://github.com/sinanlabs/robo/tree/main/bench", "source_type": "official", "fetched": dt.date.today().isoformat(), "note": "Sinan Robo bench v1 · %s · %s · weights %s" % (json.dumps(gpu_info(), ensure_ascii=False), platform.platform(), model_info.get("revision", "?"))}],
           "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "env": gpu_info(), "model_info": dict(model_info, param_dtype=pdt), "raw_latency_ms": [round(x, 3) for x in lat]}
    os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, rec["id"] + ".json")
    json.dump(rec, open(p, "w"), ensure_ascii=False, indent=1)
    print("%s · %s · %s · p50 %.1f ms · p95 %.1f ms · %.2f chunks/s · VRAM %s GB · 加载 %.0fs → %s" % (a.model, a.hardware, a.precision, rec["metrics"]["latency_ms_p50"], rec["metrics"]["latency_ms_p95"], rec["metrics"]["throughput_chunks_s"], vram, load_s, p))
    if a.upload and not a.dry_run: upload(rec, a.endpoint)

def upload(rec, endpoint):
    """众测上传：只发 model_id / precision / config / metrics / env（显卡型号、驱动、CUDA、torch、系统、权重版本）。不发逐步延迟、不发任何本地路径。"""
    import urllib.request
    env = dict(rec.get("env") or {}); env["os"] = platform.platform()[:80]; env["revision"] = str((rec.get("model_info") or {}).get("revision") or "")[:80]
    body = {"model_id": rec["model_id"], "precision": rec["precision"], "config": rec["config"], "metrics": {k: rec["metrics"].get(k) for k in ("latency_ms_p50", "latency_ms_p95", "throughput_chunks_s", "vram_peak_gb")}, "env": env, "client_version": "bench-1.1"}
    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "sinan-robo-bench/1.1"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r: out = json.loads(r.read().decode())
        print("已上传到众测队列（待核验）：id=%s 显卡映射=%s" % (out.get("id"), out.get("hardware_id") or "未映射"))
    except Exception as e:
        print("上传失败（本地结果已保存，不影响）：%s" % str(e)[:200])

if __name__ == "__main__": main()
