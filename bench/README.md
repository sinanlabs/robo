# Sinan Robo · 推理基准（bench v1）

同一套固定输入、同一套流程，量每个开源具身模型在每张卡上的单步推理延迟（p50 / p95）、吞吐（动作块/秒）、显存峰值，按算力账本的实时租价折成每千次推理成本。只报测量值，不评价动作好坏。

## 协议
- 输入：确定性合成 RGB 图（seed 20260902，默认 224×224）+ 固定指令 + 零状态向量。不用真实数据集，避免"谁的数据"之争，只测推理开销。
- 流程：加载 → 预热 50 步 → 计时 500 步，每步 `torch.cuda.synchronize()`。
- 精度：默认 bf16；模型只支持 fp16/fp32 时如实标注。
- 记录：GPU 型号与驱动、CUDA、torch、权重版本（HF 仓库 sha）、加载耗时。
- 输出：`results/<model>__<hardware>__<precision>__<date>.json`，字段与站内 `measurements` 集合一致；`python3 collect.py` 合并进 `data/measurements/bench.json`，`npm run build` 即上站。

## 在 AutoDL 上跑
1. 镜像选 PyTorch 2.5 / CUDA 12.4 / Python 3.12，数据盘 ≥100 GB。
2. `bash setup_autodl.sh`（装依赖、设 hf-mirror；必须 `HF_HUB_DISABLE_XET=1`，镜像不支持 Xet 传输，否则部分仓库下载会 401）。
3. `bash run_matrix.sh rtx-4090`（第一批 9 个 HF 可直接加载的模型）。
4. 需要专用运行时的模型（GR00T、RDT、CogACT、UniVLA、X-VLA、Octo）按各自 README 装好后补 `adapters/<name>.py` 的三个函数，跑不通就记"未能复现"，同样是有价值的结果。

## 复现
任何人在同型号卡上按上面步骤跑，应得到同一数量级的数字；差异主要来自驱动、库版本与并发，我们把这些都记在证据字段里。

## 众测上传（可选）

跑分加 `--upload`，结束后把 **指标与硬件指纹** 发到 Sinan Robo 的众测队列；不发图像、不发数据、不发任何密钥或本地路径：

```bash
python bench.py --model smolvla --hardware rtx-4090 --precision bf16 --upload
```

上传的字段：`model_id`、`precision`、`config`（batch / 分辨率 / 动作块 / 预热 / 步数）、`metrics`（p50 / p95 / 吞吐 / 显存峰值）、`env`（显卡型号、驱动、CUDA、torch、系统、权重版本）。
规则：匿名可用；每个来源每天 20 条；同一 模型×显卡×精度 每天只记最后一条；步数少于 100 拒收；入库先"待核验"，维护者核验后才出现在站上，并标为"众测"来源。
自建镜像可用环境变量 `SINAN_ROBO_ENDPOINT` 改上传地址。
