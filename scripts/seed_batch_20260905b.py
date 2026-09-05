# -*- coding: utf-8 -*-
"""2026-09-05 第四批：RDT2-VQ、InternVLA-A1.5、VLA-0、MiniVLA、Genie Envisioner（GE-Act）。来源：GitHub README + Hugging Face 模型卡 API。"""
import io, json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_v0.json")
D = json.load(io.open(P, encoding="utf-8"))
F = "2026-09-05"
def ev(field, url, note, st="official"): return {"field": field, "url": url, "source_type": st, "fetched": F, "note": note}
HF = "https://huggingface.co/api/models/"

MODELS = [
 dict(id="rdt2-vq", name="RDT2-VQ", org="清华大学 TSAIL（thu-ml）", release_date="2025-09", params_b=8.29, arch_type="monolithic_autoregressive",
      arch_notes="Qwen2.5-VL-7B-Instruct 改造的自回归 VLA，Residual VQ 动作分词器；另有 flow-matching 版 RDT2-FM；以 UMI 手持夹爪采的人类操作数据预训练，零样本跨本体", license="Apache-2.0（代码与模型卡）", commercial_ok=True,
      weights_url="https://huggingface.co/robotics-diffusion-transformer/RDT2-VQ", code_url="https://github.com/thu-ml/RDT2", paper_url="https://arxiv.org/abs/2602.03310",
      modalities_in=["rgb", "language"], action_space="24 步 × 20 维相对动作块（双臂末端）", cross_embodiment="10,000+ 小时、100+ 室内场景的 UMI 人类操作数据；双臂 UR5e / 双臂 Franka FR3 零样本", pretrain_hours=10000,
      target_embodiments=["dual_arm"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,pretrain_hours,code_url", "https://github.com/thu-ml/RDT2", "README：2025-09 模型、2026-02 论文；Apache-2.0；Qwen2.5-VL-7B-Instruct；Residual VQ；10,000+ hours；Bimanual UR5e / FR3 / UMI gripper"),
        ev("params_b,weights_url,license", HF + "robotics-diffusion-transformer/RDT2-VQ", "safetensors 8,292,166,656；license: apache-2.0；createdAt 2025-09-22", "hub")],
      verify_note=None),
 dict(id="internvla-a1.5", name="InternVLA-A1.5", org="上海人工智能实验室 InternRobotics", release_date="2026-07", params_b=2.69, arch_type="vlm_plus_action_expert",
      arch_notes="Qwen3.5-2B 原生 VLM + 轻量统一动作专家；base / RoboTwin / LIBERO / DOMINO 四个权重", license="CC BY-NC-SA 4.0（代码仓库与模型卡一致）", commercial_ok=False,
      weights_url="https://huggingface.co/InternRobotics/InternVLA-A1.5-base", code_url="https://github.com/InternRobotics/InternVLA-A1", paper_url="https://arxiv.org/abs/2607.04988",
      modalities_in=["rgb", "language", "state"], action_space="关节 / 末端（动作专家）", cross_embodiment="InternData-A1 + LeRobot v2.1 数据；RoboTwin 2.0 / LIBERO / SimplerEnv / DOMINO", pretrain_hours=None,
      target_embodiments=["single_arm", "dual_arm"], evidence=[
        ev("license,arch_notes,cross_embodiment,code_url", "https://github.com/InternRobotics/InternVLA-A1", "README：CC BY-NC-SA 4.0；Qwen3.5-2B backbone + lightweight unified action expert；InternData-A1；RoboTwin 2.0 / LIBERO / SimplerEnv / DOMINO"),
        ev("params_b,weights_url,license,release_date", HF + "InternRobotics/InternVLA-A1.5-base", "safetensors 2,685,264,547；license: cc-by-nc-sa-4.0；createdAt 2026-07-04；base Qwen/Qwen3.5-2B", "hub")],
      verify_note="非商用许可证"),
 dict(id="vla-0", name="VLA-0", org="NVIDIA Research", release_date="2025-10", params_b=3.0, arch_type="monolithic_autoregressive",
      arch_notes="不改架构、把动作直接当文本让 Qwen2.5-VL-3B-Instruct 输出；无大规模机器人预训练", license="CC BY-NC 4.0（代码与权重）；底座受 Qwen Research License 约束", commercial_ok=False,
      weights_url="https://huggingface.co/ankgoyal/vla0-libero", code_url="https://github.com/NVlabs/vla0", paper_url="https://arxiv.org/abs/2510.13054",
      modalities_in=["rgb", "language"], action_space="末端位姿增量 + 夹爪（文本形式输出）", cross_embodiment="LIBERO 仿真；SO-100 真机", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("license,arch_notes,cross_embodiment,code_url", "https://github.com/NVlabs/vla0", "README：CC BY-NC 4.0 license；base model subject to Qwen Research License；Qwen2.5-VL-3B-Instruct；LIBERO；SO-100 robot"),
        ev("weights_url", HF + "ankgoyal/vla0-libero", "模型卡 lastModified 2025-11-18；无 license 字段与参数计数", "hub")],
      verify_note="参数量按底座 3B；权重卡无 license 字段，以代码库声明为准"),
 dict(id="minivla", name="MiniVLA", org="Stanford ILIAD", release_date="2024-12", params_b=0.5, arch_type="monolithic_autoregressive",
      arch_notes="OpenVLA 缩小版：Prismatic 架构 + Qwen2.5-0.5B 语言主干 + DINOSigLIP 视觉，256 个额外动作 token", license="代码 MIT；README 注明预训练权重可能继承底座（Llama Community License）限制", commercial_ok=None,
      weights_url="https://huggingface.co/collections/Stanford-ILIAD/minivla-675a2a9aca369ff3a6c04e33", code_url="https://github.com/Stanford-ILIAD/openvla-mini", paper_url="https://arxiv.org/abs/2406.09246",
      modalities_in=["rgb", "language"], action_space="7-DoF 末端位姿增量 + 夹爪（离散 token）", cross_embodiment="Open X-Embodiment 混合；LIBERO 四套任务；WidowX / BridgeData V2", pretrain_hours=None,
      target_embodiments=["single_arm"], evidence=[
        ev("release_date,params_b,license,arch_notes,cross_embodiment,code_url,weights_url", "https://github.com/Stanford-ILIAD/openvla-mini", "README：2024-12-09 Added MiniVLA configs with Qwen2.5 0.5B backbone；All code is made available under the MIT License；pretrained models may inherit restrictions from the underlying base models（Llama Community License）；LIBERO / WidowX")],
      verify_note="权重许可证按 README 声明存疑，置待核实"),
 dict(id="genie-envisioner", name="Genie Envisioner（GE-Act）", org="智元机器人（AgiBot）", release_date="2025-08", params_b=None, arch_type="villa",
      arch_notes="视频世界模型 GE-Base（LTX-Video 系）+ 动作模型 GE-Act + 仿真器 GE-Sim（Cosmos2）；以 AgiBotWorld 数据训练", license="代码分两块：LTX/Cosmos/pipeline/openpi_client 部分 Apache-2.0，其余代码与数据 CC BY-NC-SA 4.0；权重模型卡未标注", commercial_ok=None,
      weights_url="https://huggingface.co/agibot-world/Genie-Envisioner", code_url="https://github.com/AgibotTech/Genie-Envisioner", paper_url="https://arxiv.org/abs/2508.05635",
      modalities_in=["rgb", "language"], action_space="关节（GE-Act，基于视频潜空间）", cross_embodiment="AgiBotWorld 数据集（README 未量化小时）", pretrain_hours=None,
      target_embodiments=["dual_arm_wheeled"], evidence=[
        ev("release_date,license,arch_notes,cross_embodiment,code_url", "https://github.com/AgibotTech/Genie-Envisioner", "README：论文 2025-08-08、代码 08-13、权重 08-14；Apache-2.0（部分目录）+ CC BY-NC-SA 4.0（其余代码与数据）；LTX-Video / Cosmos2；AgiBotWorld"),
        ev("weights_url", HF + "agibot-world/Genie-Envisioner", "模型卡 Genie-Envisioner-v1.0：GE_base_fast_v0.1 / ge_base_slow_v0.1 safetensors；无 license 字段；createdAt 2025-08-13", "hub")],
      verify_note="世界模型 + 动作模型组合，权重许可证未标注；参数量未标注"),
]
by = {m["id"]: m for m in D["models"]}
for m in MODELS:
    if m["id"] in by: by[m["id"]].update(m)
    else: D["models"].append(m)
D["_meta"]["notes"] += " 2026-09-05（第四批）：RDT2-VQ、InternVLA-A1.5、VLA-0、MiniVLA、Genie Envisioner。"
io.open(P, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, indent=1))
print("模型 %d · 本体 %d" % (len(D["models"]), len(D["embodiments"])))
