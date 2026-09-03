# Sinan Robo · Sprint 0 开发任务书(交给 Claude Code 执行)

> 依据:《具身模型中立层_可开发PRD_v1.md》M1-M5 + 种子数据 `sinan_robo_seed_v0.json`
> 目标:两周内上线 `robo.sinanlab.com` 的 v0.1——可审计的开源 VLA 索引 + 适配矩阵 + 延迟/成本层骨架 + 订阅。
> 原则:每个数字可回溯来源;未核实字段前台显示"待核实"徽标,不隐藏、不猜测。

---

## 0. 给 Claude Code 的开场指令(可直接粘贴)

```
你是 Sinan Robo 的开发者。请在仓库 sinanlab/robo 中按本任务书实现 Sprint 0。
技术栈:Astro(静态+岛组件)+ TypeScript;数据先用仓库内 JSON/YAML(content collections),
第二阶段再迁 Postgres。部署目标 Cloudflare Pages,域名 robo.sinanlab.com。
硬性要求:
1) 所有实体字段支持 evidence(来源URL/抓取时间/快照哈希),前台可点开;
2) 值为 null 或含"待核实"的字段渲染为醒目徽标,禁止用默认值填充;
3) 中英双语(zh-CN 默认,en 切换),文案放 i18n 文件;
4) 不引入 cookie 追踪,统计用 Cloudflare Web Analytics 片段(占位);
5) 每个页面有 canonical、OG、sitemap、robots;
6) 提供 `npm run validate` 校验 JSON schema 与 evidence 完整性;
7) 完成后输出:变更摘要、未决问题清单、部署说明。
先阅读 ./docs/PRD.md 与 ./data/seed_v0.json,再给出实施计划,经确认后开始。
```

---

## 1. 仓库结构

```
sinanlab/robo
├── src/
│   ├── pages/                # index, models/[id], embodiments/[id], compare, hardware/[id], methodology, subscribe, about
│   ├── components/           # EvidenceBadge, VerifyBadge(待核实), CompatMatrix, LatencyCard, CompareTable
│   ├── content/              # Astro content collections(models, embodiments, hardware, benchmarks, tutorials)
│   ├── i18n/                 # zh-CN.json, en.json
│   └── lib/                  # schema.ts(zod), cost.ts(成本公式), evidence.ts
├── data/
│   ├── seed_v0.json          # 首批种子数据(从 sinan_robo_seed_v0.json 拷入)
│   ├── measurements/         # CLI 上传的延迟测量(JSON,按日期分目录)
│   └── snapshots/            # 来源快照索引(哈希→R2 key)
├── scripts/
│   ├── validate.ts           # schema + evidence 校验
│   ├── import-seed.ts        # seed → content collections
│   └── fetch-snapshot.ts     # 抓取来源页并计算 sha256(手动触发)
├── docs/
│   ├── PRD.md                # 拷入可开发PRD
│   ├── METHODOLOGY.md        # 测量方法论(公开)
│   └── DECISIONS.md          # 决策记录(单一事实源)
├── public/                   # favicon, og, robots.txt
└── astro.config.mjs / package.json / wrangler.toml(如需)
```

---

## 2. 数据 Schema(zod,摘要)

- `Model`:见 PRD §4;必填 `id,name,org,license,weights_url|待核实`;`params_b` 可 null;`evidence: Evidence[]`
- `Embodiment`:`id,name,vendor,form,dof|null,end_effector,sdk_url,price_range_cny,data_formats[]`
- `Compatibility`:`model_id,embodiment_id,status ∈ {official, community_verified, theoretical, unsupported, unknown},evidence`
- `Hardware`:`id,name,vram_gb,type,rental_cny_per_hour_ref|null,rental_ref_source,rental_ref_url`
- `LatencyMeasurement`:PRD M4 输出 schema;`source_type ∈ {literature, maintainer, crowd}`;`review_status ∈ {pending, verified, rejected}`
- `Evidence`:`field,url,source_type ∈ {literature,news,hub,official},fetched,sha256|null,note`

成本公式(`lib/cost.ts`):
```
cost_per_1k_infer_cny = latency_ms_p50/1000 * (rental_cny_per_hour_ref/3600) * 1000
```
无延迟或无租价时显示"—"并给出原因徽标。

---

## 3. 页面与验收(AC)

| 页面 | 内容 | AC |
|---|---|---|
| `/` 首页 | 一句话定位;三入口:模型索引 / 适配矩阵 / 硬件延迟;"最近更新";订阅框;中立宪法摘要与链接(指向母站) | 首屏 <2s;移动端可读 |
| `/models` | 列表+筛选(本体、许可证、商用可否、显存、跨本体)+排序 | 11 条种子全部渲染;筛选可用 |
| `/models/[id]` | 全字段+evidence 可点开+适配矩阵切片+延迟/成本卡+教程链接+更新历史 | 任一数字两步回溯来源;"待核实"徽标醒目 |
| `/compare?ids=a,b,c` | 最多 4 模型并排 | URL 可分享 |
| `/embodiments` 与 `/embodiments/[id]` | 本体目录+该本体可用模型 | 7 条种子渲染 |
| `/matrix` | 模型×本体矩阵,颜色=状态,点击看证据 | ≥60 格有状态(初期多为 unknown,允许) |
| `/hardware/[id]` | 该硬件上所有模型的延迟与成本排名 | 4090/5090 有租价引用与来源 |
| `/methodology` | 测量方法论 v0.1(从 PRD §5 扩写) | 公开可读 |
| `/subscribe` | 邮箱订阅(Cloudflare Worker + KV/D1 或第三方表单)+ RSS + Webhook 说明 | 提交成功有确认 |
| `/about` | Sinan Lab / 中立宪法 / 联系 hello@sinanlab.com | 页脚全站可达 |

---

## 4. CLI v0(可选,本 Sprint 只做骨架)

- 包名 `sinan-bench`(PyPI 预留);命令 `sinan-bench hw`(硬件指纹)与 `sinan-bench run --model <id>` 的接口定义与占位实现;真实模型适配放 Sprint 1。
- 输出 schema 与 PRD M4 一致;`upload` 先写入本地文件,不接服务端。

---

## 5. 内容与 IP 联动(与开发并行,Eric 负责)

- 首篇教程选题:"在共绩/算家云的 4090 上跑通 GR00T N1.7 / GO-1(任选其一)"——产出实测延迟,回填 `measurements/`;
- 首期《机脑行情》:LingBot-VLA 2.0、GR00T N1.7、星海图 WRC 开源前瞻、COSA 0.5 三层架构解读;
- 上线当天:母站互链、知乎/公众号发布、GitHub 仓库 README 指向方法论。

---

## 6. 两周排期

| 天 | 任务 |
|---|---|
| D1-2 | 仓库、Astro 骨架、schema、i18n、seed 导入、validate 脚本 |
| D3-5 | 模型列表/详情/对比页、Evidence/待核实徽标组件 |
| D6-7 | 本体页、适配矩阵(初始多为 unknown)、硬件页与成本公式 |
| D8-9 | 方法论页、订阅(Worker)、about、SEO(sitemap/OG/robots) |
| D10 | 部署 Cloudflare Pages,绑定 robo.sinanlab.com,Web Analytics |
| D11-12 | 核实清单:补齐至少 5 个模型的许可证与权重链接 evidence;首篇教程实测回填 |
| D13-14 | 验收、修 bug、上线、内容发布 |

---

## 7. 待核实清单(上线前至少完成前 5 项)

1. GR00T N1.7 的具体许可证名称与 HF 权重路径、发布月份
2. LingBot-VLA 2.0 的参数量、许可证、权重与代码链接
3. GO-1 的权重/代码链接与许可证
4. π0 / π0.5 权重许可(openpi 仓库 vs 权重许可可能不同)
5. SmolVLA 参数量与许可证
6. OpenVLA、Octo、X-VLA 的权重/代码链接与许可证
7. 各本体的自由度、SDK 链接、公开价格
8. A100 等数据中心卡的租价(接 Sinan Compute 价格库)
