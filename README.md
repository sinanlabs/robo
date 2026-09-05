# Sinan Robo · 司南·机脑

**An auditable index of open / open-weight embodied models (VLA).**
开源具身模型的可审计索引：许可证、权重、代码、参数量、目标本体 —— 每个字段带来源，没核实的写"待核实"，不猜。

🌐 https://robo.sinanlab.com · 🇬🇧 https://robo.sinanlab.com/en/ · 📇 [Model index](https://robo.sinanlab.com/models) · 🧩 [Model × body matrix](https://robo.sinanlab.com/matrix) · 🧾 [Methodology](https://robo.sinanlab.com/methodology)

---

## Why / 为什么做

Picking a robot foundation model today means reading ten READMEs, three model cards and a licence file that contradicts the paper. Sinan Robo does that reading once, keeps the receipts, and shows you a table:

- **Licence, exactly as written** — code licence and weight licence are recorded separately. When they disagree (Apache-2.0 code, Gemma-bound weights; MIT code, CC BY-NC-SA weights) we say so and leave "commercial OK" as *unverified* instead of guessing.
- **Parameter count from the model card**, not the marketing number (MolmoAct "7B" is 8.12B in safetensors; SmolVLA is 0.45B).
- **Target embodiments as declared** — single arm, dual arm, wheeled, humanoid, dexterous hand — and a model × body matrix where only cells with evidence are coloured.
- **Every field has an `evidence` entry**: URL, source type (official / hub / literature / news), fetch date, note.

## Coverage / 覆盖

| | |
|---|---|
| Models | 25 (GR00T N1.6/N1.7, π0/π0.5, OpenVLA, Octo, RDT-1B, CogACT, SpatialVLA, UniVLA, MolmoAct, EO-1, X-VLA, LingBot-VLA, WALL-OSS, InternVLA-M1, GraspVLA, GO-1, Being-H0, SmolVLA, RynnVLA-001, NORA, VLA-Adapter …) |
| Robot bodies | 12 (Unitree G1/H1, AgiBot G1, Galaxea R1 Pro, AgileX Piper, ALOHA 2 / Cobot Magic, Franka FR3 / Panda, WidowX 250 S, SO-101, Google Robot, Fourier GR) |
| Hardware | 4 reference GPUs / edge devices with rental price references |
| Measurements | latency / cost-per-1k-inferences layer is in place, awaiting reproducible runs |

Target for 2026-Q4: 40+ models, 25+ bodies, first reproducible latency measurements.

## Data / 数据

All content is generated from [`data/seed_v0.json`](data/seed_v0.json) — one JSON file, one entry per model / body / hardware item, each with an `evidence` array. Pull requests that add a model **must** include evidence URLs for every non-null field; `npm run validate` enforces the schema.

```bash
npm install
npm run build      # import seed → validate → astro build (zh-CN + en)
npm run dev
```

Stack: Astro 5, zod content collections, no client framework. Deployed on Cloudflare Pages.

## Contribute a model / 提交模型

Open an issue or PR with:

1. Official repo / model card URL
2. Licence text location for code **and** weights
3. Parameter count source (model card safetensors metadata preferred)
4. Declared target embodiments and the page that says so

We do not accept benchmark claims without the table and paper they come from.

## What we do not do / 我们不做什么

No rankings, no "best model", no money from any vendor listed ([why trust us](https://sinanlab.com/constitution)). Fields we could not verify say so.

---

Part of **Sinan Lab / 司南实验室**. Sister project: [Sinan Compute](https://github.com/sinanlabs/compute) — effective-price comparison for model API relay sites.
