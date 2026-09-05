# -*- coding: utf-8 -*-
"""2026-09-04 第二批模型：按一手来源（GitHub README / Hugging Face 模型卡 API / arXiv）核实后写入 data/seed_v0.json。
规则：每个已填字段都要有 evidence；拿不到的字段留 null 或“待核实”；许可证只抄仓库/模型卡原文，不推断商用与否。
运行一次即可（幂等：按 id 覆盖）。"""
import io, json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_v0.json")
D = json.load(io.open(P, encoding="utf-8"))
F = "2026-09-04"
def ev(field, url, note, st="official"): return {"field": field, "url": url, "source_type": st, "fetched": F, "note": note}
HF = "https://huggingface.co/api/models/"

MODELS = [
 dict(id="openvla", name="OpenVLA", org="Stanford / UC Berkeley / TRI 等（OpenVLA 团队）", release_date="2024-06", params_b=7.54, arch_type="monolithic_autoregressive",
      arch_notes="Prismatic VLM：DINOv2 + SigLIP 双视觉编码器 + Llama-2 7B，动作离散为 token 自回归输出", license="MIT（代码与权重仓库标注）；权重衍生自 Llama-2，受 Llama 2 Community License 约束", commercial_ok=None,
      weights_url="https://huggingface.co/openvla/openvla-7b", code_url="https://github.com/openvla/openvla", paper_url="https://arxiv.org/abs/2406.09246",
      modalities_in=["rgb", "language"], action_space="7-DoF 末端位姿增量 + 夹爪（离散 token）", cross_embodiment="Open X-Embodiment 约 97 万条轨迹预训练", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("license,release_date,code_url", "https://github.com/openvla/openvla", "README：All code is made available under the MIT License；Models derive from Llama-2, subject to the Llama Community License；首发 2024-06-13"),
        ev("params_b,weights_url,license", HF + "openvla/openvla-7b", "safetensors 7,541,237,184；模型卡 license: mit；createdAt 2024-06-10", "hub"),
        ev("paper_url,cross_embodiment", "https://arxiv.org/abs/2406.09246", "OpenVLA: An Open-Source Vision-Language-Action Model；970K trajectories from Open X-Embodiment", "literature")],
      verify_note="代码 MIT；权重基于 Llama-2，商用需同时满足 Llama 2 社区许可，本站不替你判断，标待核实"),
 dict(id="octo", name="Octo", org="UC Berkeley RAIL 等", release_date="2024-05", params_b=0.093, arch_type="transformer_policy",
      arch_notes="Transformer 主干 + 扩散动作头；octo-base 93M、octo-small 27M", license="MIT（代码与权重仓库标注）", commercial_ok=True,
      weights_url="https://huggingface.co/rail-berkeley/octo-base-1.5", code_url="https://github.com/octo-models/octo", paper_url="https://arxiv.org/abs/2405.12213",
      modalities_in=["rgb", "language", "goal_image"], action_space="末端位姿增量 + 夹爪（扩散）", cross_embodiment="Open X-Embodiment 约 80 万条轨迹预训练", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("params_b,license,code_url,cross_embodiment", "https://github.com/octo-models/octo", "README：Octo-Base 93M Params / Octo-Small 27M；License: MIT；800k robot trajectories from Open X-Embodiment"),
        ev("weights_url,license,release_date", HF + "rail-berkeley/octo-base-1.5", "模型卡 license: mit；createdAt 2024-05-21", "hub")],
      verify_note=None),
 dict(id="rdt-1b", name="RDT-1B", org="清华大学 TSAIL（thu-ml）", release_date="2024-10", params_b=1.0, arch_type="transformer_policy",
      arch_notes="扩散 Transformer；输入语言 + 最多三路 RGB，一次预测 64 步动作；另有 RDT-170M 小版本", license="MIT（代码、权重、数据均为 MIT，README 原文）", commercial_ok=True,
      weights_url="https://huggingface.co/robotics-diffusion-transformer/rdt-1b", code_url="https://github.com/thu-ml/RoboticsDiffusionTransformer", paper_url="https://arxiv.org/abs/2410.07864",
      modalities_in=["rgb", "language", "state"], action_space="统一动作空间，覆盖单臂/双臂、关节/末端、位置/速度", cross_embodiment="100 万+ 多机器人 episodes 预训练，ALOHA 双臂 6K+ episodes 微调", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm", "mobile_manipulator"], evidence=[
        ev("license,params_b,cross_embodiment,code_url", "https://github.com/thu-ml/RoboticsDiffusionTransformer", "README：All the code, model weights, and data are licensed under MIT license；1B-parameter；1M+ multi-robot episodes"),
        ev("weights_url,license", HF + "robotics-diffusion-transformer/rdt-1b", "模型卡 license: mit；createdAt 2024-08-27", "hub"),
        ev("paper_url,release_date", "https://arxiv.org/abs/2410.07864", "RDT-1B: a Diffusion Foundation Model for Bimanual Manipulation，2024-10", "literature")],
      verify_note=None),
 dict(id="cogact", name="CogACT", org="Microsoft Research", release_date="2024-12", params_b=None, arch_type="vlm_plus_action_expert",
      arch_notes="VLM 主干（prism-dinosiglip-224px）+ DiT 扩散动作模块（DiT-S/B/L 三档）；一次输出 16 步 7-DoF 动作", license="MIT（代码、权重、数据均为 MIT，README 原文）", commercial_ok=True,
      weights_url="https://huggingface.co/CogACT/CogACT-Base", code_url="https://github.com/microsoft/CogACT", paper_url="https://arxiv.org/abs/2411.19650",
      modalities_in=["rgb", "language"], action_space="7-DoF 末端位姿增量 + 夹爪（扩散，16 步动作块）", cross_embodiment="Open X-Embodiment 预训练", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("license,release_date,arch_notes,code_url", "https://github.com/microsoft/CogACT", "README：released 2024-12-01；All the code, model weights, and data are licensed under MIT license；CogACT-Small/Base/Large，DiT-S/B/L"),
        ev("weights_url,license", HF + "CogACT/CogACT-Base", "模型卡 license: mit；createdAt 2024-11-29", "hub")],
      verify_note="三档参数量 README 未标注，params_b 留空"),
 dict(id="spatialvla", name="SpatialVLA", org="上海人工智能实验室 等", release_date="2025-01", params_b=4.03, arch_type="monolithic_autoregressive",
      arch_notes="PaliGemma2-3B 主干 + 空间位置编码与自适应动作网格；1.1M 真机 episodes 预训练", license="MIT（代码 README 与模型卡均标 MIT）", commercial_ok=True,
      weights_url="https://huggingface.co/IPEC-COMMUNITY/spatialvla-4b-224-pt", code_url="https://github.com/SpatialVLA/SpatialVLA", paper_url="https://arxiv.org/abs/2501.15830",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪（自适应离散网格）", cross_embodiment="Open X-Embodiment + RH20T 共 1.1M episodes", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,cross_embodiment,code_url", "https://github.com/SpatialVLA/SpatialVLA", "README：2025-01-29 发布；MIT license；1.1 Million real robot episodes from Open X-Embodiment and RH20T；Google Robot / WidowX / Franka"),
        ev("params_b,weights_url,license", HF + "IPEC-COMMUNITY/spatialvla-4b-224-pt", "safetensors 4,027,854,731；license: MIT；base_model google/paligemma2-3b-pt-224", "hub")],
      verify_note=None),
 dict(id="univla", name="UniVLA", org="OpenDriveLab（香港大学 等）", release_date="2025-05", params_b=7.54, arch_type="vlm_plus_action_expert",
      arch_notes="Prismatic 7B 主干 + 任务中心潜在动作（VQ-VAE 两阶段）+ 约 12M 参数动作解码器", license="Apache-2.0（代码仓库与模型卡均标注）", commercial_ok=True,
      weights_url="https://huggingface.co/qwbu/univla-7b", code_url="https://github.com/OpenDriveLab/UniVLA", paper_url="https://arxiv.org/abs/2505.06111",
      modalities_in=["rgb", "language"], action_space="潜在动作 → 各本体解码", cross_embodiment="Open X-Embodiment + Ego4D 人类视频子集；LIBERO / CALVIN / SimplerEnv / 导航 / AgileX 真机", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm", "wheeled"], evidence=[
        ev("license,release_date,arch_notes,cross_embodiment,code_url", "https://github.com/OpenDriveLab/UniVLA", "README：Apache-2.0；2025-05 代码发布；7B backbone，action decoder around 12M；OXE + Ego4D；AgiLex 真机"),
        ev("params_b,weights_url,license", HF + "qwbu/univla-7b", "safetensors 7,541,237,184；license: apache-2.0；createdAt 2025-05-06", "hub"),
        ev("paper_url", "https://arxiv.org/abs/2505.06111", "UniVLA: Learning to Act Anywhere with Task-centric Latent Actions", "literature")],
      verify_note=None),
 dict(id="molmoact", name="MolmoAct", org="Allen Institute for AI（Ai2）", release_date="2025-08", params_b=8.12, arch_type="monolithic_autoregressive",
      arch_notes="Molmo 系：SigLIP2 视觉 + Qwen2.5-7B 语言 + VQVAE 深度编码，先推理空间轨迹再出动作", license="Apache-2.0（代码与权重）", commercial_ok=True,
      weights_url="https://huggingface.co/allenai/MolmoAct-7B-D-0812", code_url="https://github.com/allenai/MolmoAct", paper_url="https://arxiv.org/abs/2508.07917",
      modalities_in=["rgb", "depth", "language"], action_space="末端位姿增量 + 夹爪", cross_embodiment="MolmoAct 自采 1 万 episodes（LeRobot 格式）+ 预训练混合", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,cross_embodiment,code_url", "https://github.com/allenai/MolmoAct", "README：2025-08-12 模型发布、2025-10-24 代码发布；Apache-2.0；10k robot episodes 自采；Google Robot / Franka"),
        ev("params_b,weights_url,license", HF + "allenai/MolmoAct-7B-D-0812", "safetensors 8,119,417,808（F32）；license: apache-2.0；base Qwen/Qwen2.5-7B + siglip2-so400m", "hub")],
      verify_note="名义 7B，模型卡参数计数 8.12B"),
 dict(id="rynnvla-001", name="RynnVLA-001", org="阿里巴巴达摩院", release_date="2025-08", params_b=7.01, arch_type="villa",
      arch_notes="以第一人称视频生成模型为主干（Chameleon 系），先做视频生成预训练再接轨迹建模与动作", license="Apache-2.0（代码与模型卡）；README 同时注明 research preview intended for non-commercial use ONLY", commercial_ok=None,
      weights_url="https://huggingface.co/Alibaba-DAMO-Academy/RynnVLA-001-7B-Base", code_url="https://github.com/alibaba-damo-academy/RynnVLA-001", paper_url="https://arxiv.org/abs/2509.15212",
      modalities_in=["rgb", "language"], action_space="机械臂关节/末端（LeRobot 格式数据）", cross_embodiment="第一人称人类视频预训练迁移到机械臂", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/alibaba-damo-academy/RynnVLA-001", "README：2025-08-08 发布；Apache 2.0；research preview intended for non-commercial use ONLY"),
        ev("params_b,weights_url,license", HF + "Alibaba-DAMO-Academy/RynnVLA-001-7B-Base", "safetensors 7,013,158,912；license: apache-2.0；base chameleon", "hub")],
      verify_note="许可证 Apache-2.0 与“仅限非商用”声明并存，商用与否置待核实"),
 dict(id="wall-oss", name="WALL-OSS", org="自变量机器人（X Square Robot）", release_date="2025-09", params_b=4.22, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen2.5-VL 主干 + MoE 动作专家（Qwen2_5_VLMoEForAction）；FLOW / FAST 两种动作头；2026-05 发布 0.5 版与世界模型 WALL-WM", license="Apache-2.0（代码仓库）；权重模型卡未标注许可证", commercial_ok=None,
      weights_url="https://huggingface.co/x-square-robot/wall-oss-flow", code_url="https://github.com/X-Square-Robot/wall-x", paper_url="https://arxiv.org/abs/2509.11766",
      modalities_in=["rgb", "language", "state"], action_space="双臂关节（flow matching / FAST token）", cross_embodiment="大规模多模态预训练 + 真机操作（README 未列本体清单）", pretrain_hours=None,
      target_embodiments=["dual_arm"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/X-Square-Robot/wall-x", "README：2025-09 WALL-OSS；2026-05 Wall-OSS-0.5 与 WALL-WM；Apache-2.0 license；Qwen2_5_VLMoEForAction"),
        ev("params_b,weights_url", HF + "x-square-robot/wall-oss-flow", "safetensors 4,224,041,072；模型卡无 license 字段；base qwen2_5_vl", "hub")],
      verify_note="权重许可证未标注，待核实"),
 dict(id="internvla-m1", name="InternVLA-M1", org="上海人工智能实验室 InternRobotics", release_date="2025-09", params_b=3.75, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen2.5-VL-3B 主干，空间引导 + 多模态多任务联合训练", license="代码 MIT；权重模型卡标 CC BY-NC-SA 4.0", commercial_ok=False,
      weights_url="https://huggingface.co/InternRobotics/InternVLA-M1", code_url="https://github.com/InternRobotics/InternVLA-M1", paper_url="https://arxiv.org/abs/2510.13778",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪", cross_embodiment="RT-1 / Bridge 预训练，LIBERO 与 SimplerEnv 微调", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("license,arch_notes,code_url", "https://github.com/InternRobotics/InternVLA-M1", "README：MIT license（代码）；Qwen2.5-VL backbone；0918 Release model weights"),
        ev("params_b,weights_url,license,release_date", HF + "InternRobotics/InternVLA-M1", "safetensors 3,754,622,976；license: cc-by-nc-sa-4.0；createdAt 2025-09-16；base Qwen2.5-VL-3B-Instruct", "hub"),
        ev("paper_url", "https://arxiv.org/abs/2510.13778", "InternVLA-M1 技术报告", "literature")],
      verify_note="权重 CC BY-NC-SA 4.0 明确禁止商用"),
 dict(id="graspvla", name="GraspVLA", org="北京大学 EPIC 实验室 / 银河通用", release_date="2025-07", params_b=None, arch_type="vlm_plus_action_expert",
      arch_notes="InternLM2-1.8B 语言 + DINOv2/SigLIP 视觉；十亿帧合成抓取数据 SynGrasp-1B 预训练", license="CC BY-NC 4.0（代码徽章与模型卡一致）", commercial_ok=False,
      weights_url="https://huggingface.co/vegebirrd/GraspVLA", code_url="https://github.com/PKU-EPIC/GraspVLA", paper_url="https://arxiv.org/abs/2505.03233",
      modalities_in=["rgb", "language"], action_space="抓取位姿 / 末端轨迹", cross_embodiment="合成数据 SynGrasp-1B（240 类、1 万+ 物体）", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,code_url", "https://github.com/PKU-EPIC/GraspVLA", "README：2025-07-25 模型发布；CC BY-NC 4.0；internlm2-1_8b + DINOv2/SigLIP；SynGrasp-1B"),
        ev("weights_url,license", HF + "vegebirrd/GraspVLA", "模型卡 license: cc-by-nc-4.0", "hub")],
      verify_note="非商用许可证；参数量未标注"),
 dict(id="being-h0", name="Being-H0", org="BeingBeyond（北京）", release_date="2025-08", params_b=8.11, arch_type="monolithic_autoregressive",
      arch_notes="InternVL 系 VLA，显式手部运动建模 + GRVQ 运动分词器；1B / 8B / 14B 三档", license="MIT（代码仓库与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/BeingBeyond/Being-H0-8B-2508", code_url="https://github.com/BeingBeyond/Being-H0", paper_url="https://arxiv.org/abs/2507.15597",
      modalities_in=["rgb", "language"], action_space="手部关节运动（灵巧手）", cross_embodiment="大规模人类手部视频预训练，后训练对齐机器人", pretrain_hours=None,
      target_embodiments=["dexterous_hand"], evidence=[
        ev("release_date,license,arch_notes,code_url", "https://github.com/BeingBeyond/Being-H0", "README：2025-08-02 代码与模型发布；MIT license；1B/8B/14B；dexterous hands"),
        ev("params_b,weights_url,license", HF + "BeingBeyond/Being-H0-8B-2508", "safetensors 8,114,397,181；license: MIT", "hub")],
      verify_note="面向灵巧手，本站本体库暂无对应条目"),
 dict(id="eo-1", name="EO-1", org="IPEC-COMMUNITY（上海人工智能实验室 系）", release_date="2025-08", params_b=3.77, arch_type="monolithic_autoregressive",
      arch_notes="单一解码器 Transformer，离散自回归 + 连续 flow matching 统一；Qwen2.5-VL-3B 主干；EO-Data1.5M 交错数据", license="MIT（模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/IPEC-COMMUNITY/EO-1-3B", code_url="https://github.com/IPEC-PUBLIC/EO-1", paper_url="https://arxiv.org/abs/2508.21112",
      modalities_in=["rgb", "language", "state"], action_space="关节/末端（flow matching）", cross_embodiment="AgiBotWorld + Open X-Embodiment + RoboMIND + SO100 社区数据；Franka Panda / WidowX 250S / AgiBot G-1 / SO100", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("arch_notes,cross_embodiment,code_url", "https://github.com/IPEC-PUBLIC/EO-1", "README：Qwen2.5-VL-3B-Instruct；EO-Data1.5M；Franka Panda, WidowX 250 S, AgiBot G-1, LeRobot SO100"),
        ev("params_b,weights_url,license,release_date", HF + "IPEC-COMMUNITY/EO-1-3B", "safetensors 3,771,607,072；license: MIT；createdAt 2025-08-28", "hub"),
        ev("paper_url", "https://arxiv.org/abs/2508.21112", "EO-1: An Open Unified Embodied Foundation Model for General Robot Control", "literature")],
      verify_note=None),
 dict(id="x-vla", name="X-VLA", org="清华大学 AIR（2toINF）", release_date="2025-10", params_b=0.88, arch_type="soft_prompted_transformer",
      arch_notes="Soft-Prompted Transformer，Florence-2-large 视觉；0.9B 规模；ICLR 2026", license="Apache-2.0（代码与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/2toINF/X-VLA-Pt", code_url="https://github.com/2toinf/X-VLA", paper_url="https://arxiv.org/abs/2510.10274",
      modalities_in=["rgb", "language", "state"], action_space="跨本体软提示，单臂/双臂", cross_embodiment="CALVIN / LIBERO / VLABench / RoboTwin2 / BridgeDataV2；Franka / AgiBot G1 / Google Robot / WidowX / AgileX", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("license,release_date,cross_embodiment,code_url", "https://github.com/2toinf/X-VLA", "README：Apache License 2.0；arXiv 2510.10274（2025-10）；ICLR 2026；Franka / Agibot-G1 / Google Robot / WidowX / Agilex"),
        ev("params_b,weights_url,license", HF + "2toINF/X-VLA-Pt", "safetensors 879,738,545；license: apache-2.0；base microsoft/Florence-2-large", "hub")],
      verify_note=None),
 dict(id="lingbot-vla-4b", name="LingBot-VLA 4B", org="蚂蚁灵波（Robbyant）", release_date="2026-01", params_b=4.20, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen2.5-VL-3B-Instruct 主干 + MoGe-2 深度组件；有 depth-free 与 depth-distilled 两版；2 万小时真机双臂数据", license="Apache-2.0（代码仓库）；权重模型卡未标注许可证", commercial_ok=None,
      weights_url="https://huggingface.co/robbyant/lingbot-vla-4b", code_url="https://github.com/robbyant/lingbot-vla", paper_url="https://arxiv.org/abs/2601.18692",
      modalities_in=["rgb", "language", "state"], action_space="双臂关节", cross_embodiment="9 种双臂构型 2 万小时真机数据；AgiBot G1 / AgileX / Galaxea R1Pro 实测", pretrain_hours=20000,
      target_embodiments=["dual_arm", "dual_arm_wheeled"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,pretrain_hours,code_url", "https://github.com/robbyant/lingbot-vla", "README：2026-01-27 技术报告与权重代码发布；Apache-2.0 License；Qwen2.5-VL-3B-Instruct；20,000 hours of real-world data from 9 dual-arm configurations；Agibot G1 / AgileX / Galaxea R1Pro"),
        ev("params_b,weights_url", HF + "robbyant/lingbot-vla-4b", "safetensors 4,197,425,739；模型卡无 license 字段；createdAt 2026-01-26", "hub")],
      verify_note="权重许可证未标注；LingBot-VLA 2.0 另有条目"),
 dict(id="nora", name="NORA", org="Declare Lab（新加坡科技设计大学）", release_date="2025-04", params_b=3.76, arch_type="monolithic_autoregressive",
      arch_notes="Qwen2.5-VL-3B 主干，动作 token 自回归；有 NORA-1.5 与 NORA-LONG 变体", license="仓库与模型卡均未标注许可证", commercial_ok=None,
      weights_url="https://huggingface.co/declare-lab/nora", code_url="https://github.com/declare-lab/nora", paper_url="https://arxiv.org/abs/2504.19854",
      modalities_in=["rgb", "language"], action_space="7-DoF（6 + 夹爪）", cross_embodiment="Open X-Embodiment 混合预训练；WidowX / BridgeData V2 评测", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("arch_notes,cross_embodiment,code_url", "https://github.com/declare-lab/nora", "README：built on Qwen2.5 VL；OXE mixture；WidowX / BridgeData V2；7-DoF"),
        ev("params_b,weights_url,release_date", HF + "declare-lab/nora", "safetensors 3,758,262,272；模型卡无 license 字段；createdAt 2025-04-28", "hub")],
      verify_note="许可证缺失，待核实"),
 dict(id="vla-adapter", name="VLA-Adapter", org="OpenHelix 团队", release_date="2025-09", params_b=0.5, arch_type="vlm_plus_action_expert",
      arch_notes="Prismatic 架构 + Qwen2.5-0.5B 语言主干，轻量策略头（Pro 版策略约 207MB）", license="MIT（代码仓库）；权重模型卡未标注", commercial_ok=None,
      weights_url="https://huggingface.co/VLA-Adapter/LIBERO-Spatial", code_url="https://github.com/OpenHelix-Team/VLA-Adapter", paper_url="https://arxiv.org/abs/2509.09372",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪", cross_embodiment="LIBERO / CALVIN 微调；ALOHA（Cobot Magic）真机部署", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("release_date,license,params_b,arch_notes,cross_embodiment,code_url", "https://github.com/OpenHelix-Team/VLA-Adapter", "README：论文 2025-09-11、代码 2025-09-22；MIT license；0.5B；Qwen2.5-0.5B；LIBERO / CALVIN；ALOHA / Cobot Magic")],
      verify_note="权重许可证未标注"),
]

by = {m["id"]: m for m in D["models"]}
for m in MODELS:
    if m["id"] in by: by[m["id"]].update(m)
    else: D["models"].append(m)

# SmolVLA：补参数与许可证核实状态
sm = by.get("smolvla")
if sm:
    sm.update(params_b=0.45, release_date="2025-06", license="权重模型卡未标注许可证（LeRobot 代码仓库 Apache-2.0）", commercial_ok=None, paper_url="https://arxiv.org/abs/2506.01844",
              weights_url="https://huggingface.co/lerobot/smolvla_base")
    sm.setdefault("evidence", []).append(ev("params_b,release_date,weights_url,license", HF + "lerobot/smolvla_base", "safetensors 450,046,176；createdAt 2025-06-01；模型卡无 license 字段", "hub"))
    sm["verify_note"] = "权重许可证未标注，待核实；参数 0.45B"

EMB = [
 dict(id="widowx-250s", name="WidowX 250 S", vendor="Trossen Robotics", form="single_arm", dof=6, end_effector="平行夹爪", sdk_url="https://www.trossenrobotics.com/", price_range_cny="待核实", data_formats=["BridgeData V2 / RLDS", "LeRobot"],
      evidence=[ev("form,dof", "https://github.com/octo-models/octo", "BridgeData V2 / Octo 评测本体（README）"), ev("form", "https://github.com/IPEC-PUBLIC/EO-1", "EO-1 README 列 WidowX 250 S 为评测本体")]),
 dict(id="google-robot", name="Google Robot（Everyday Robots）", vendor="Google / Everyday Robots", form="single_arm", dof=7, end_effector="平行夹爪", sdk_url=None, price_range_cny="不对外销售", data_formats=["RT-1 / fractal RLDS"],
      evidence=[ev("form", "https://github.com/SpatialVLA/SpatialVLA", "SpatialVLA README 评测本体：Google Robot / WidowX / Franka"), ev("form", "https://github.com/microsoft/CogACT", "CogACT 训练数据 fractal20220817_data（Google robot）")]),
 dict(id="aloha-2", name="ALOHA 2 / Cobot Magic（双臂）", vendor="Trossen Robotics / 松灵 AgileX", form="dual_arm", dof=12, end_effector="双平行夹爪", sdk_url="https://github.com/tonyzhaozh/aloha", price_range_cny="待核实", data_formats=["ALOHA HDF5", "LeRobot"],
      evidence=[ev("form", "https://github.com/thu-ml/RoboticsDiffusionTransformer", "RDT-1B 在 ALOHA 双臂上微调 6K+ episodes"), ev("form", "https://github.com/OpenHelix-Team/VLA-Adapter", "VLA-Adapter：ALOHA deployment support, verified on Cobot Magic")]),
 dict(id="galaxea-r1pro", name="Galaxea R1 Pro", vendor="星海图（Galaxea）", form="dual_arm_wheeled", dof=None, end_effector="待核实", sdk_url="待核实", price_range_cny="待核实", data_formats=["待核实"],
      evidence=[ev("form", "https://github.com/robbyant/lingbot-vla", "LingBot-VLA README 实测本体：Agibot G1 / AgileX / Galaxea R1Pro")]),
 dict(id="franka-panda", name="Franka Emika Panda", vendor="Franka Robotics", form="single_arm", dof=7, end_effector="Franka Hand 平行夹爪", sdk_url="https://frankaemika.github.io/docs/", price_range_cny="待核实", data_formats=["RLDS", "LeRobot"],
      evidence=[ev("form,dof", "https://github.com/IPEC-PUBLIC/EO-1", "EO-1 README 评测本体 Franka Panda"), ev("form", "https://github.com/PKU-EPIC/GraspVLA", "GraspVLA 基于 LeRobot Franka 数据集")]),
]
eb = {e["id"]: e for e in D["embodiments"]}
for e in EMB:
    if e["id"] in eb: eb[e["id"]].update(e)
    else: D["embodiments"].append(e)

D["_meta"]["generated"] = F
D["_meta"]["notes"] += " 2026-09-04：第二批 17 个模型（OpenVLA / Octo 更新；RDT-1B、CogACT、SpatialVLA、UniVLA、MolmoAct、RynnVLA-001、WALL-OSS、InternVLA-M1、GraspVLA、Being-H0、EO-1、X-VLA、LingBot-VLA 4B、NORA、VLA-Adapter 新增）与 5 个本体，全部按 GitHub README + Hugging Face 模型卡 API 核实并附 evidence；许可证只抄原文，代码与权重许可证不一致时 commercial_ok 置 null。"
io.open(P, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, indent=1))
print("模型 %d · 本体 %d · 硬件 %d" % (len(D["models"]), len(D["embodiments"]), len(D["hardware"])))
