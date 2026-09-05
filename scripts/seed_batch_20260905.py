# -*- coding: utf-8 -*-
"""2026-09-05 第三批：HPT、LAPA、LLaVA-VLA、RoboVLMs、Magma、V-JEPA 2-AC、DexVLA、GR-1、Spirit v1.5、GalaxeaVLA G0.5（替换 announced 的星海图占位条目）；
GR00T N1.6 补模型卡参数与许可证线索。全部按 GitHub README + Hugging Face 模型卡 API 核实；许可证抄原文。
未纳入（原因）：WholebodyVLA（未开源权重）、HybridVLA（权重只在百度网盘）、TinyVLA（仓库迁移、元数据缺）、3D-VLA（许可证与参数均缺）。"""
import io, json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_v0.json")
D = json.load(io.open(P, encoding="utf-8"))
F = "2026-09-05"
def ev(field, url, note, st="official"): return {"field": field, "url": url, "source_type": st, "fetched": F, "note": note}
HF = "https://huggingface.co/api/models/"

MODELS = [
 dict(id="hpt", name="HPT（Heterogeneous Pre-trained Transformers）", org="MIT（Lirui Wang, Kaiming He 等）", release_date="2024-09", params_b=0.227, arch_type="transformer_policy",
      arch_notes="把不同本体对齐到共享潜空间的 Transformer 主干；XLarge 226.8M / Large 50.5M / Base 12.6M / Small 3.1M；NeurIPS 2024 Spotlight", license="MIT（代码仓库）；模型卡未标注许可证", commercial_ok=None,
      weights_url="https://huggingface.co/liruiw/hpt-xlarge", code_url="https://github.com/liruiw/HPT", paper_url="https://arxiv.org/abs/2409.20537",
      modalities_in=["rgb", "state", "language"], action_space="各本体自有动作头", cross_embodiment="多本体数据混合预训练（README 未列具体清单）", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("params_b,license,arch_notes,code_url", "https://github.com/liruiw/HPT", "README：HPT-XLarge 226.8M / Large 50.5M / Base 12.6M / Small 3.1M；MIT license；NeurIPS 2024 Spotlight"),
        ev("weights_url", HF + "liruiw/hpt-xlarge", "模型卡无 license 字段；createdAt 2024-05-15", "hub")],
      verify_note="权重许可证未标注"),
 dict(id="lapa", name="LAPA", org="KAIST / 华盛顿大学 等（Latent Action Pretraining）", release_date="2024-11", params_b=7.0, arch_type="monolithic_autoregressive",
      arch_notes="从无动作标注视频学潜在动作再预训练 VLA；基于 LWM-Chat-1M（Large World Model）；ICLR 2025", license="MIT（代码与模型卡均标注）", commercial_ok=True,
      weights_url="https://huggingface.co/latent-action-pretraining/LAPA-7B-openx", code_url="https://github.com/LatentActionPretraining/LAPA", paper_url="https://arxiv.org/abs/2410.11758",
      modalities_in=["rgb", "language"], action_space="潜在动作 → 微调后映射真实动作", cross_embodiment="Open X-Embodiment 预训练；SIMPLER 评测", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,cross_embodiment,code_url", "https://github.com/LatentActionPretraining/LAPA", "README：weights released 2024-11-22；MIT License；Open-X Embodiment；ICLR 2025"),
        ev("weights_url,license", HF + "latent-action-pretraining/LAPA-7B-openx", "模型卡 license: mit；base_model LargeWorldModel/LWM-Chat-1M-Jax", "hub")],
      verify_note="参数量按模型名 7B，模型卡未给 safetensors 计数"),
 dict(id="llava-vla", name="LLaVA-VLA", org="OpenHelix 团队", release_date="2025-06", params_b=7.0, arch_type="monolithic_autoregressive",
      arch_notes="直接基于 LLaVA-v1.5-7B / LLaVA-OneVision 0.5B 的 VLA；ICRA 2026", license="MIT（代码与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/chenpyyy/LLaVA-VLA", code_url="https://github.com/OpenHelix-Team/LLaVA-VLA", paper_url="https://arxiv.org/abs/2602.22663",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪", cross_embodiment="CALVIN 微调；RoboTwin 评测", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/OpenHelix-Team/LLaVA-VLA", "README：2025-06-17 发布代码与权重、2025-07-05 发 0.5B；MIT license；基于 LLaVA"),
        ev("weights_url,license", HF + "chenpyyy/LLaVA-VLA", "模型卡 license: MIT；createdAt 2025-06-16", "hub")],
      verify_note=None),
 dict(id="robovlms", name="RoboVLMs（KosMos P.H.）", org="清华大学 / 字节跳动 Research / 中科院自动化所 等", release_date="2024-12", params_b=None, arch_type="vlm_plus_action_expert",
      arch_notes="把任意 VLM 变成 VLA 的框架；表现最好的是 KosMos 主干 + 策略头；Nature Machine Intelligence 2026", license="Apache-2.0（代码与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/robovlms/RoboVLMs", code_url="https://github.com/Robot-VLAs/RoboVLMs", paper_url="https://arxiv.org/abs/2412.14058",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪", cross_embodiment="Open X-Embodiment 预训练；CALVIN / SimplerEnv / 真机", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/Robot-VLAs/RoboVLMs", "README：initial release 12/11/24；Apache-2.0 license；KosMos VLM backbone；Nature Machine Intelligence"),
        ev("weights_url,license", HF + "robovlms/RoboVLMs", "模型卡 license: apache-2.0；checkpoints kosmos_ph_oxe-pretrain.pt 等", "hub")],
      verify_note="参数量未标注"),
 dict(id="magma", name="Magma-8B", org="Microsoft Research", release_date="2025-02", params_b=8.9, arch_type="monolithic_autoregressive",
      arch_notes="Llama-3-8B-Instruct + ConvNeXt 视觉；Set-of-Mark / Trace-of-Mark 预训练；同时做 UI 导航与机器人操作", license="MIT（代码与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/microsoft/Magma-8B", code_url="https://github.com/microsoft/Magma", paper_url="https://arxiv.org/abs/2502.13130",
      modalities_in=["rgb", "language"], action_space="7-DoF 末端位姿增量 + 夹爪", cross_embodiment="Open X-Embodiment + Ego4D 等；WidowX / Bridge、LIBERO 评测", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,code_url", "https://github.com/microsoft/Magma", "README：2025-02-25 发布；MIT；LLama-3-8B-Instruct + ConvNeXt；7 DoF；WidowX/Bridge、LIBERO"),
        ev("params_b,weights_url,license", HF + "microsoft/Magma-8B", "safetensors 8,903,066,496；license: MIT", "hub")],
      verify_note="通用多模态智能体模型，机器人只是其中一类任务"),
 dict(id="vjepa2-ac", name="V-JEPA 2-AC", org="Meta FAIR", release_date="2025-06", params_b=1.0, arch_type="villa",
      arch_notes="自监督视频世界模型 V-JEPA 2（ViT-g 1B）之上加动作条件预测器，通过规划实现零样本抓取/放置；权重在 HF 上为受限（gated）访问", license="MIT 为主，部分文件 Apache-2.0（README 原文）；HF 权重需申请访问", commercial_ok=None,
      weights_url="https://huggingface.co/collections/facebook/v-jepa-2-6841bad8413014e185b497a6", code_url="https://github.com/facebookresearch/vjepa2", paper_url="https://arxiv.org/abs/2506.09985",
      modalities_in=["rgb", "state"], action_space="末端位姿（基于图像目标的规划）", cross_embodiment="在 Franka 上做 reaching / grasping / pick-and-place 规划", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,code_url", "https://github.com/facebookresearch/vjepa2", "README：V-JEPA 2 2025-06-25；majority licensed under MIT, portions under separate terms；ViT-g/16 1B；Franka arm planning"),
        ev("weights_url", "https://huggingface.co/api/models/facebook/vjepa2-ac-vitg-384", "模型卡 API 返回 401（受限访问）", "hub")],
      verify_note="世界模型 + 规划路线，不是端到端 VLA；权重受限访问"),
 dict(id="dexvla", name="DexVLA", org="美的 AI 研究院 等（DexVLA 团队）", release_date="2025-02", params_b=3.0, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen2-VL-2B 主干 + 插件式 ScaleDP 扩散专家（1B 或 410M）", license="代码 MIT；ScaleDP 预训练权重模型卡标 CC BY-NC 4.0", commercial_ok=False,
      weights_url="https://huggingface.co/lesjie/scale_dp_h", code_url="https://github.com/juruobenruo/DexVLA", paper_url="https://arxiv.org/abs/2502.05855",
      modalities_in=["rgb", "language", "state"], action_space="双臂 / 灵巧手关节（扩散）", cross_embodiment="ALOHA 脚本、AgileX 评测；README 未列训练小时数", pretrain_hours=None,
      target_embodiments=["dual_arm", "dexterous_hand"], evidence=[
        ev("release_date,arch_notes,license,code_url", "https://github.com/juruobenruo/DexVLA", "README：2025-02-17 发布；Qwen2-VL-2B + 1B ScaleDP（另有 410M）；MIT LICENSE 文件"),
        ev("weights_url,license", HF + "lesjie/scale_dp_h", "模型卡 license: cc-by-nc-4.0；createdAt 2025-02-24", "hub")],
      verify_note="代码 MIT 与权重 CC BY-NC 4.0 不一致，按权重定为禁商用"),
 dict(id="gr-1", name="GR-1", org="字节跳动 Research", release_date="2023-12", params_b=None, arch_type="villa",
      arch_notes="GPT 式模型：输入语言 + 观测序列 + 状态，同时预测动作与未来帧；大规模视频生成式预训练；ICLR 2024", license="Apache-2.0（代码仓库）", commercial_ok=None,
      weights_url="https://lf-robot-opensource.bytetos.com/obj/lab-robot-public/gr1_code_release/", code_url="https://github.com/bytedance/GR-1", paper_url="https://arxiv.org/abs/2312.13139",
      modalities_in=["rgb", "language", "state"], action_space="末端位姿增量 + 夹爪", cross_embodiment="CALVIN 微调（ABCD / ABC 两组权重）", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,weights_url,code_url", "https://github.com/bytedance/GR-1", "README：ICLR 2024；Apache-2.0 License；权重 snapshot_ABCD.pt / snapshot_ABC.pt 在字节对象存储；GPT-style video generative pre-training")],
      verify_note="权重不在 Hugging Face；参数量未标注；GR-2 未公开权重故未收录"),
 dict(id="spirit-v1.5", name="Spirit v1.5", org="千寻智能（Spirit AI）", release_date="2026-01", params_b=5.4, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen3-VL 主干 + DiT 动作头 + policy API；2026-01-11 起在 RoboChallenge Table30 榜单排名第一（站方自述）", license="代码 MIT（README）；模型卡标 apache-2.0", commercial_ok=True,
      weights_url="https://huggingface.co/Spirit-AI-robotics/Spirit-v1.5", code_url="https://github.com/Spirit-AI-Team/spirit-v1.5", paper_url="https://www.spirit-ai.com/en/blog/spirit-v1-5",
      modalities_in=["rgb", "language", "state"], action_space="动作块（chunk）输出", cross_embodiment="Table30 基准任务；README 未列本体清单与训练小时", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/Spirit-AI-Team/spirit-v1.5", "README：2026-01 发布；MIT；Qwen3-VL backbone + DiT head；#1 on RoboChallenge Table30 as of Jan 11, 2026"),
        ev("params_b,weights_url,license", HF + "Spirit-AI-robotics/Spirit-v1.5", "safetensors 5,400,901,236（F32）；license: apache-2.0；createdAt 2026-01-11", "hub")],
      verify_note="代码 MIT 与模型卡 apache-2.0 均允许商用；榜单名次为站方自述，本站不复核"),
 dict(id="galaxea-g0.5", name="Galaxea G0.5", org="星海图（Galaxea）", release_date="2026-06", params_b=2.0, arch_type="monolithic_autoregressive",
      arch_notes="Qwen3.5 2B VLM，单一自回归流同时输出推理与动作；前代 G0Plus 3B / G0Tiny 250M（2026-01）", license="G0.5 Community License（非商用 + 有限专利许可；模型卡 license: other）；2026-01-04 前版本为 Apache-2.0", commercial_ok=False,
      weights_url="https://huggingface.co/OpenGalaxea/G05", code_url="https://github.com/OpenGalaxea/GalaxeaVLA", paper_url="https://arxiv.org/abs/2608.11739",
      modalities_in=["rgb", "language", "state"], action_space="移动操作（底盘 + 双臂）", cross_embodiment="14 种本体；R1 Lite / R1 Pro / SO-100/101 / DROID-Franka；Galaxea Open-World Dataset 500+ 小时", pretrain_hours=500,
      target_embodiments=["dual_arm_wheeled", "single_arm"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,pretrain_hours,code_url", "https://github.com/OpenGalaxea/GalaxeaVLA", "README：G0.5 checkpoint 2026-06-16、论文 2026-08-12；G0.5 Community License (Non-Commercial + Limited Patent License)；Qwen3.5 2B；14 embodiments；500+ hours"),
        ev("weights_url,license", HF + "OpenGalaxea/G05", "模型卡 license: other (G05-Community-License)；createdAt 2026-06-16", "hub")],
      verify_note="替换原 announced 占位条目 galaxea-foundation-model-tba"),
]

by = {m["id"]: m for m in D["models"]}
D["models"] = [m for m in D["models"] if m["id"] != "galaxea-foundation-model-tba"]
by = {m["id"]: m for m in D["models"]}
for m in MODELS:
    if m["id"] in by: by[m["id"]].update(m)
    else: D["models"].append(m)

# GR00T N1.6：补模型卡参数与许可证线索
g = by.get("gr00t-n1.6-3b")
if g:
    g.update(params_b=3.29, license="模型卡标 NVIDIA License（链接 LICENSE 文件，条款待逐字核实）", commercial_ok=None)
    g.setdefault("evidence", []).append(ev("params_b", HF + "nvidia/GR00T-N1.6-3B", "safetensors 3,286,608,832；createdAt 2025-12-01；模型卡 API 无 license 字段", "hub"))
    g.setdefault("evidence", []).append(ev("license", "https://huggingface.co/nvidia/GR00T-N1.6-3B", "模型卡页面写 Nvidia License，具体条款需读 LICENSE 文件", "hub"))
    g["verify_note"] = "许可证条款待逐字核实（N1.7 已确认为 NVIDIA Open Model License）"

D["_meta"]["generated"] = F
D["_meta"]["notes"] += " 2026-09-05：第三批 10 个模型（HPT、LAPA、LLaVA-VLA、RoboVLMs、Magma、V-JEPA 2-AC、DexVLA、GR-1、Spirit v1.5、Galaxea G0.5）；未纳入 WholebodyVLA/HybridVLA/TinyVLA/3D-VLA（权重不可得或元数据缺失）。"
io.open(P, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, indent=1))
print("模型 %d · 本体 %d · 硬件 %d" % (len(D["models"]), len(D["embodiments"]), len(D["hardware"])))
