# -*- coding: utf-8 -*-
"""2026-09-05 本体核实：按厂商官网 / 官方文档补自由度、末端、负载、价格、SDK，全部带 evidence。价格只抄官网标价；没标价写“官网未标价”。"""
import io, json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "seed_v0.json")
D = json.load(io.open(P, encoding="utf-8"))
F = "2026-09-05"
def ev(field, url, note, st="official"): return {"field": field, "url": url, "source_type": st, "fetched": F, "note": note}

B = {
 "unitree-g1": dict(dof=23, end_effector="标准版无手；G1 EDU 可选 Dex3-1 三指力控手（7 DoF）+ 2 腕部自由度", sdk_url="https://github.com/unitreerobotics", price_range_cny="官网标价 US$13.5K（G1 标准版，不含税运）；EDU 版询价",
     data_formats=["unitree_sdk2（DDS）", "LeRobot 社区数据集"], evidence=[ev("dof,end_effector,price_range_cny,sdk_url", "https://www.unitree.com/g1", "官网：G1 23 DOF；G1 EDU 23–43；Dex3-1 三指力控手；US $13.5K；Resource Center github.com/unitreerobotics")]),
 "unitree-h1": dict(dof=18, end_effector="可选；H1-2 可选 Dex5-1 等双手", sdk_url="https://github.com/unitreerobotics", price_range_cny="官网未标价",
     data_formats=["unitree_sdk2（DDS）"], evidence=[ev("dof,end_effector,sdk_url", "https://www.unitree.com/h1", "官网：H1 18 DOF（腿 5×2 + 臂 4×2）；H1-2 27 DOF（腿 6×2 + 臂 7×2）；H1-2 可选 Dex5-1")]),
 "agibot-genie-g1": dict(dof=20, end_effector="6 自由度灵巧手，可换二指夹爪", sdk_url="https://www.agibot.com.cn/products/G1", price_range_cny="官网未标价",
     data_formats=["AgiBot World（LeRobot 格式发布）"], evidence=[ev("dof,end_effector,sdk_url", "https://www.agibot.com.cn/products/G1", "官网：20 个自主自由度（不含末端）；单臂 6 DoF；6 自由度灵巧手可替换二指夹爪；单手 3kg；开放 GDK；Agibotworld 百万条数据")]),
 "agilex-piper": dict(dof=6, end_effector="平行夹爪（可选）", sdk_url="https://global.agilex.ai/products/piper", price_range_cny="官网标价 US$1,999",
     data_formats=["Python API / ROS1 / ROS2", "LeRobot 社区数据集"], evidence=[ev("dof,price_range_cny,sdk_url", "https://global.agilex.ai/products/piper", "官网：6 dof；1.5kg payload；626 mm reach；$1,999.00；Python API，ROS1/ROS2")]),
 "so-101": dict(dof=6, end_effector="平行夹爪（3D 打印）", sdk_url="https://github.com/TheRobotStudio/SO-ARM100", price_range_cny="BOM 约 US$122（从动臂）/ US$230（主从双臂），自行打印装配",
     data_formats=["LeRobotDataset"], evidence=[ev("dof,price_range_cny,sdk_url", "https://github.com/TheRobotStudio/SO-ARM100", "README：The RobotStudio 与 Hugging Face 合作；Apache-2.0；follower $121.94 / 双臂 $229.88；6× STS3215"),
     ev("data_formats", "https://huggingface.co/docs/lerobot/so101", "LeRobot 官方文档 SO-101 装配与标定")]),
 "franka-fr3": dict(dof=7, end_effector="Franka Hand 平行夹爪", sdk_url="https://frankarobotics.github.io/docs/", price_range_cny="官网未标价",
     data_formats=["libfranka / FCI（1 kHz）", "ROS 2", "DROID（RLDS）"], evidence=[ev("dof,end_effector,sdk_url,data_formats", "https://franka.de/products/franka-research-3", "官网：7 Degrees of freedom；Payload 3 kg；855 mm；libfranka open source C++；FCI 1 kHz；ROS 2")]),
 "franka-panda": dict(dof=7, end_effector="Franka Hand 平行夹爪", sdk_url="https://frankarobotics.github.io/docs/", price_range_cny="已停产，由 FR3 接替；官网未标价",
     data_formats=["libfranka / FCI", "RLDS", "LeRobot"], evidence=[ev("dof,end_effector,sdk_url", "https://franka.de/products/franka-research-3", "Franka Research 3 页面（Panda 后继型号，同 7 DoF / Franka Hand / libfranka）")]),
 "fourier-gr": dict(name="Fourier GR-2", dof=53, end_effector="12 自由度灵巧手，含 6 个阵列触觉传感器", sdk_url="https://www.fftai.com/", price_range_cny="仅企业/机构销售，官网未标价",
     data_formats=["NVIDIA Isaac Lab", "ROS", "MuJoCo"], evidence=[ev("dof,end_effector,data_formats", "https://www.therobotreport.com/fourier-launches-gr-2-humanoid-software-platform/", "The Robot Report：GR-2 175 cm / 63 kg，53 DoF，12-DoF hands with 6 array-type tactile sensors；兼容 Isaac Lab / ROS / MuJoCo", "news")]),
 "widowx-250s": dict(dof=6, end_effector="X-Series 可换指夹爪", sdk_url="https://www.trossenrobotics.com/widowx-250", price_range_cny="已停产，官网未标价",
     data_formats=["Interbotix ROS/ROS 2", "BridgeData V2（RLDS）", "LeRobot"], evidence=[ev("dof,end_effector,sdk_url", "https://www.trossenrobotics.com/widowx-250", "官网：6 DOF；250g payload；650mm reach；Interbotix Python/ROS；THIS PRODUCT HAS BEEN DISCONTINUED")]),
 "galaxea-r1pro": dict(dof=26, end_effector="力控平行夹爪", sdk_url="https://docs.galaxea-dynamics.com/", price_range_cny="官网未标价",
     data_formats=["Galaxea Open-World Dataset", "ROS（GitHub userguide-galaxea）"], evidence=[ev("dof,end_effector,sdk_url", "https://galaxea-dynamics.com/pages/r1-pro-product-specification", "官网规格：Total 26 DoF；Per-arm 7；Torso 4；Chassis 6；Force-controlled parallel gripper；3.5 kg rated / 5 kg max @500mm；docs.galaxea-dynamics.com")]),
}
eb = {e["id"]: e for e in D["embodiments"]}
n = 0
for k, v in B.items():
    if k in eb:
        old_ev = eb[k].get("evidence", [])
        eb[k].update({kk: vv for kk, vv in v.items() if kk != "evidence"})
        eb[k]["evidence"] = old_ev + v["evidence"]; n += 1
D["_meta"]["notes"] += " 2026-09-05：10 个本体按厂商官网核实自由度/末端/负载/价格/SDK。"
io.open(P, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, indent=1))
print("本体已核实 %d / %d" % (n, len(D["embodiments"])))
