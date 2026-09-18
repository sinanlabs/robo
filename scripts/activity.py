# -*- coding: utf-8 -*-
"""
活性信号：每天抓一次每个模型的 GitHub / Hugging Face / ModelScope 公开指标，只记录、不评价。
  GitHub（gh CLI 已登录）：stars、forks、未关闭 issue、最近一次推送、近 90 天提交数（上限 100）、最新 release、是否归档
  Hugging Face：近 30 天下载、累计下载、likes、权重最后修改时间、是否需要申请（gated）
  ModelScope：是否有同路径镜像；没有就按仓库名搜同名镜像（标注非官方）
产出：
  data/activity/latest.json          今日快照（按 model_id）
  data/activity/history.jsonl        逐日一行一模型（画 30 天走势、算周变化；同日重跑会覆盖当日）
用法：python3 scripts/activity.py            全部模型
      python3 scripts/activity.py openvla    只跑一个（调试）
"""
import io, os, sys, json, re, subprocess, urllib.request, urllib.parse, datetime as dt, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SEED = os.path.join(ROOT, "data", "seed_v0.json")
OUT = os.path.join(ROOT, "data", "activity"); os.makedirs(OUT, exist_ok=True)
TODAY = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
SINCE_90 = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00Z")
UA = "sinan-robo-activity/0.1 (+https://robo.sinanlab.com)"


def gh(path):
    """gh api 包装：404 返回 None，其它错误抛出。"""
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        if "404" in r.stderr or "Not Found" in r.stderr: return None
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout) if r.stdout.strip() else None


def http_json(url, method="GET", body=None, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}; h.update(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    if data is not None: h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception: return e.code, None
    except Exception as e:
        return 0, {"_err": str(e)[:120]}


def gh_repo(url):
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", url or ""); return (m.group(1), m.group(2).removesuffix(".git")) if m else None


def hf_repo(url):
    m = re.match(r"https?://huggingface\.co/(?!collections/|datasets/|spaces/)([^/]+)/([^/#?]+)", url or ""); return (m.group(1) + "/" + m.group(2)) if m else None


def fetch_github(owner, repo):
    d = gh("repos/%s/%s" % (owner, repo))
    if not d: return {"ok": False, "why": "not_found"}
    out = {"ok": True, "repo": owner + "/" + repo, "stars": d.get("stargazers_count"), "forks": d.get("forks_count"), "open_issues": d.get("open_issues_count"),
           "pushed_at": (d.get("pushed_at") or "")[:10] or None, "archived": bool(d.get("archived")), "license": (d.get("license") or {}).get("spdx_id"), "default_branch": d.get("default_branch")}
    try:
        c = gh("repos/%s/%s/commits?since=%s&per_page=100" % (owner, repo, SINCE_90)) or []
        out["commits_90d"] = len(c); out["commits_90d_capped"] = len(c) >= 100
    except Exception as e:
        out["commits_90d"] = None; out["commits_90d_capped"] = False
    try:
        rel = gh("repos/%s/%s/releases/latest" % (owner, repo))
        out["latest_release"] = {"tag": rel.get("tag_name"), "at": (rel.get("published_at") or "")[:10]} if rel else None
    except Exception:
        out["latest_release"] = None
    if out["pushed_at"]:
        out["days_since_push"] = (dt.date.fromisoformat(TODAY) - dt.date.fromisoformat(out["pushed_at"])).days
    return out


def fetch_hf(repo):
    st, d = http_json("https://huggingface.co/api/models/%s?expand[]=downloads&expand[]=downloadsAllTime&expand[]=likes&expand[]=lastModified&expand[]=gated&expand[]=private" % urllib.parse.quote(repo, safe="/"))
    if st != 200 or not isinstance(d, dict): return {"ok": False, "why": "http_%s" % st, "repo": repo}
    return {"ok": True, "repo": repo, "downloads_30d": d.get("downloads"), "downloads_all": d.get("downloadsAllTime"), "likes": d.get("likes"),
            "last_modified": (d.get("lastModified") or "")[:10] or None, "gated": d.get("gated") or False}


def fetch_modelscope(hf_path):
    """先按同路径查；没有就按仓库名搜，只接受名字完全相同的（标注非官方镜像）。"""
    st, d = http_json("https://modelscope.cn/api/v1/models/%s" % hf_path)
    if st == 200 and isinstance(d, dict) and (d.get("Data") or {}).get("Path"):
        x = d["Data"]; return {"ok": True, "path": x["Path"] + "/" + x["Name"], "downloads": x.get("Downloads"), "updated": dt.datetime.fromtimestamp(x["LastUpdatedTime"], dt.timezone.utc).strftime("%Y-%m-%d") if x.get("LastUpdatedTime") else None, "official_org": True}
    name = hf_path.split("/", 1)[1]
    st, d = http_json("https://modelscope.cn/api/v1/dolphin/models", "PUT", {"PageSize": 10, "PageNumber": 1, "SortBy": "Default", "Target": "", "SingleCriterion": [], "Name": name})
    if st == 200 and isinstance(d, dict):
        for m in ((d.get("Data") or {}).get("Model") or {}).get("Models", []) or []:
            if (m.get("Name") or "").lower() == name.lower():
                return {"ok": True, "path": m["Path"] + "/" + m["Name"], "downloads": m.get("Downloads"), "updated": dt.datetime.fromtimestamp(m["LastUpdatedTime"], dt.timezone.utc).strftime("%Y-%m-%d") if m.get("LastUpdatedTime") else None, "official_org": False}
    return {"ok": False, "why": "none"}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    seed = json.load(io.open(SEED, encoding="utf-8"))
    latest_p = os.path.join(OUT, "latest.json")
    prev = json.load(io.open(latest_p, encoding="utf-8")) if os.path.exists(latest_p) else {"items": {}}
    items = dict(prev.get("items", {}))
    n_ok = 0
    for m in seed["models"]:
        if only and m["id"] != only: continue
        rec = {"model_id": m["id"], "fetched": TODAY, "license": m.get("license"), "weights_url": m.get("weights_url"), "code_url": m.get("code_url")}
        g = gh_repo(m.get("code_url"))
        try: rec["github"] = fetch_github(*g) if g else {"ok": False, "why": "no_github_url"}
        except Exception as e: rec["github"] = {"ok": False, "why": str(e)[:120]}
        h = hf_repo(m.get("weights_url"))
        rec["hf"] = fetch_hf(h) if h else {"ok": False, "why": "no_hf_repo"}
        rec["modelscope"] = fetch_modelscope(h) if h else {"ok": False, "why": "no_hf_repo"}
        items[m["id"]] = rec; n_ok += 1
        print("%-18s gh=%s hf=%s ms=%s" % (m["id"], (rec["github"].get("stars") if rec["github"].get("ok") else rec["github"].get("why")),
              (rec["hf"].get("downloads_30d") if rec["hf"].get("ok") else rec["hf"].get("why")), (rec["modelscope"].get("path") if rec["modelscope"].get("ok") else "-")))
        time.sleep(0.3)
    json.dump({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "items": items}, io.open(latest_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 逐日历史：同日重跑覆盖
    hist_p = os.path.join(OUT, "history.jsonl")
    rows = []
    if os.path.exists(hist_p):
        for ln in io.open(hist_p, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if not (r.get("d") == TODAY and (not only or r.get("id") == only)): rows.append(r)
    for mid, rec in items.items():
        if only and mid != only: continue
        if rec.get("fetched") != TODAY: continue
        g, h, ms = rec.get("github", {}), rec.get("hf", {}), rec.get("modelscope", {})
        rows.append({"d": TODAY, "id": mid, "stars": g.get("stars"), "forks": g.get("forks"), "issues": g.get("open_issues"), "c90": g.get("commits_90d"), "pushed": g.get("pushed_at"),
                     "hf30": h.get("downloads_30d"), "hfall": h.get("downloads_all"), "likes": h.get("likes"), "hfmod": h.get("last_modified"), "ms": ms.get("downloads") if ms.get("ok") else None,
                     "lic": rec.get("license"), "w": rec.get("weights_url")})
    rows.sort(key=lambda r: (r["d"], r["id"]))
    with io.open(hist_p, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("activity: %d 个模型 → data/activity/latest.json · history %d 行" % (n_ok, len(rows)))


if __name__ == "__main__":
    main()
