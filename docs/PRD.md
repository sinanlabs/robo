# 具身模型中立层(代号 VLA罗盘 / 英文名待定)——可开发 PRD v1.0

> 日期:2026-08-31 | 负责人:Eric | 开发主体:AI(Claude Code)+ 技术合伙人(第1阶段起)
> 范围:第0阶段(公开索引+测量CLI)完整规格;第1阶段(统一SDK)接口级规格;第2阶段(托管推理)概要规格
> 阅读约定:P0=第0阶段必须;P1=第1阶段;P2=第2阶段。每个功能附验收标准(AC)。

---

## 0. 最新态势(2026-08,本PRD的事实基础)

- **开源VLA正在从"单本体"走向"跨本体"**:蚂蚁灵波 LingBot-VLA 2.0(2026-07-08开源)用6万小时真实数据预训练,覆盖17家厂商、20种机器人构型(乐聚、智元、宇树、松灵、星海图、银河通用、Franka、傅立叶等);英伟达 GR00T N1.7(3B,开放且**商业许可**,Action Cascade双系统);智元 GO-1(开源,LeRobot格式);π0/π0.5(开放权重);SmolVLA(轻量);OpenVLA、X-VLA(学术)。星海图宣布8月WRC开源首个具身基础模型、9月CoRL开放数据集,并推出 Galaxea Data Hub(百万小时国产数据开放商用)。
- **分层架构成为行业共识**:逐际动力 COSA 0.5(2026-07-15)明确三层:System 2 认知层约1Hz(语言模型,场景理解/推理/任务调度)、System 1 技能层约50Hz(VLA是被调用的技能之一)、System 0 运控层1000Hz。**→ 云端可承载的是System 2(约1Hz)与离线评测/微调;本产品只做这一层。**
- **工具链标准在形成但不成熟**:LeRobot Dataset v3.0(Hub原生流式、少量大文件)成为数据事实标准;LeRobot 异步推理(RobotClient↔PolicyServer)已发布,但社区报告"迁移旧模型与新训模型在异步推理下表现差异大"等问题 → 统一、稳健的客户端层存在真实需求。
- **巨头占位**:华为云 CloudRobo(2026-06公测,全流程平台,昇腾亲和)、腾讯 Tairos(模块化开放平台)。二者均非跨云跨芯片中立、均无商业运营级公开测量与按次自助调用。
- **需求侧**:2026Q1具身融资约200亿元;智源指出创业公司普遍"通用开源大模型+运动控制" → 几百家公司是开源模型的消费者。

---

## 1. 产品定义

**一句话:**面向机器人开发者的中立"模型选择与调用层":在一分钟内回答"该用哪个大脑、在哪跑、花多少钱",在一行代码内用上它。

**目标(第0-1阶段):**
1. 建立中文区最完整、可审计的开源VLA索引与成本/延迟数据层;
2. 让开发者通过统一SDK在不同VLA之间"改一个参数就切换";
3. 用众包测量形成数据飞轮,并成为第2阶段托管推理与公开榜的基础。

**非目标(明确不做):**
- 不做30-50Hz实时控制回路的云端托管;
- 不做机器人本体销售/租赁;
- 不做训练框架(复用LeRobot等);
- 第0-1阶段不做付费认证、不做具名负面榜单。

**中立宪法(产品内置,不可配置):**排名与推荐不含商业变量;所有测量方法与原始数据可下载;自托管与第三方端点同等展示;含商业关系的位置显著标注。

---

## 2. 用户与核心用例

| 角色 | 典型画像 | 核心用例 | 成功标准 |
|---|---|---|---|
| U1 机器人初创算法工程师 | 30人公司,有自研本体,需通用操作能力 | "我们的双臂轮式机器人该用哪个开源VLA?在4090上延迟多少?"→ 索引筛选+对比 → SDK一键试 | 2周部署比较缩短到1天 |
| U2 实验室研究生 | 用SO-101/松灵机械臂做课题 | 找到支持自己本体的模型与基线分数;复现;上传自己的延迟测量 | 找到并跑通<1小时 |
| U3 集成商/RaaS技术负责人 | 车队含宇树+普渡+机械臂 | 评估多模型在多本体上的可用性与成本 | 能出对比报告 |
| U4 模型厂商DevRel | 刚开源一个VLA | 让开发者发现并正确使用 | 被索引、被SDK适配、被测量 |
| U5 投资人/分析师(P2) | 看行情 | 模型/端点变化订阅 | 订阅数据 |

---

## 3. 功能需求

### M1 模型索引(Model Registry)— P0
**描述:**开源/开放VLA的结构化目录,中英双语。

**字段(必填*)**
- 基本:名称*、组织*、发布日*、版本*、参数量*、架构类型(单系统/双系统/三层中的层级)、许可证*(SPDX+商用可否*)、权重链接*、代码链接*、论文链接
- 能力:输入模态(RGB/深度/语言/状态)、动作空间类型(关节/末端位姿/底盘)、动作块长度、支持的控制频率范围、是否支持跨本体、预训练数据规模(小时)
- 适配本体:关联 M2
- 基准:关联 M3(论文/复现分数)
- 部署:推荐硬件、最低显存、已知部署路径(LeRobot/VLAgents/官方脚本)、部署难度(1-5,含依据)
- 证据:每个字段的来源URL、抓取时间、快照哈希(复用算力罗盘证据链)

**页面**
- 列表页:筛选(本体、许可证、商用可否、显存、模态、跨本体)、排序(发布日、参数量、社区热度、延迟)
- 详情页:字段+证据链+适配矩阵+延迟/成本+教程链接+更新历史
- 对比页:最多4个模型并排

**AC**
- 首批≥10个模型,字段完整率≥90%,每条字段可点开看来源;
- 任一数字两步内回溯到原始快照;
- 中英切换无缺项。

### M2 本体与适配矩阵(Embodiment & Compatibility)— P0
**描述:**机器人本体目录及"模型×本体"适配状态。

**字段:**本体名称*、厂商*、形态(人形/双臂/单臂/轮式/四足)、自由度、末端类型、官方SDK/ROS接口、价格区间(公开价)、数据格式支持(LeRobot v3等)。
**适配状态枚举:**`官方声明支持` / `社区复现成功(附链接)` / `理论可微调` / `不支持` / `未知`;每条附证据。
**页面:**矩阵视图(模型为行、本体为列),单元格颜色=状态,点开看证据。
**AC:**首批≥6个本体(宇树G1/H1、智元、松灵机械臂、SO-101、Franka、傅立叶任选),矩阵≥60格有状态与证据。

### M3 基准与延迟/成本层(Benchmarks, Latency & Cost)— P0
**基准:**收录 LIBERO、SimplerEnv、VLABench、RoboBench 等的公开分数;字段:基准名、任务集、分数、来源(论文/官方/复现)、日期。
**延迟(核心差异化):**
- 测量单元:`模型版本 × 硬件 × 精度(fp16/int8等) × 批大小=1 × 输入分辨率 × 动作块长度`;
- 指标:单步推理延迟 p50/p95(ms)、首动作延迟、吞吐(动作块/秒)、显存峰值(GB)、功耗(可选);
- 来源:文献值(标注)、维护者实测、**众包CLI上传(M4)**,三类分色展示;
- 成本:`每千次推理成本 = 延迟 × 该硬件小时单价(来自算力罗盘API)/3600 × 1000`;硬件单价每日刷新。
**页面:**模型详情页的"延迟与成本"卡;硬件维度页("4090上所有模型的延迟排名")。
**AC:**≥10模型×3硬件(4090、A100/A800、Jetson Thor或Orin)有至少一类延迟数据;成本列每日更新;每个数字可见样本量与来源类型。

### M4 众包测量CLI(`vlabench` 工作名)— P0
**描述:**开源Python CLI,一条命令在本地显卡测某模型推理延迟,生成可复现报告并可选上传。

**命令**
```
vlabench list                      # 列出可测模型与所需权重
vlabench run --model gr00t-n1.7 --steps 200 --precision fp16
vlabench report --last            # 本地JSON/Markdown报告
vlabench upload --last            # 上传到索引(匿名或署名)
vlabench hw                       # 采集硬件指纹
```
**输出Schema(JSON)**
```json
{
 "schema_version":"0.1",
 "model":{"id":"gr00t-n1.7","weights_sha256":"...","precision":"fp16"},
 "hardware":{"gpu":"RTX 4090","vram_gb":24,"driver":"...","cuda":"...","cpu":"...","os":"..."},
 "config":{"batch":1,"image_res":"224x224","action_chunk":16,"warmup_steps":20,"steps":200},
 "metrics":{"latency_ms_p50":..,"latency_ms_p95":..,"throughput_chunks_s":..,"vram_peak_gb":..},
 "env_fingerprint":"...","timestamp":"...","client_version":"0.1.0"
}
```
**规则:**只上传指标与硬件指纹,不上传图像/数据/密钥;同一指纹同配置24h内去重;异常值(偏离中位数>3σ)进待审队列;贡献者榜(署名者)。
**AC:**支持首批≥5个模型;在4090上一次完整运行<15分钟;上传成功率≥95%;≥50条有效上传(阶段0验收)。

### M5 教程与部署指南(Docs)— P0
- 结构:`在<硬件>上运行<模型>`模板化教程;每篇含:环境、权重获取、依赖、运行命令、常见错误、实测延迟(用M4)、成本估算;
- 双语;版本化;评论/纠错入口;
- AC:首季≥6篇;每篇含可复现命令与M4报告链接。

### M6 统一SDK(`vla-router` 工作名)— P1
**目标:**一套Python接口调用任意VLA策略服务器或本地模型。
**核心API(草案)**
```python
from vlarouter import Policy, Observation

policy = Policy.connect(
    model="lingbot-vla-2.0",          # 或 "gr00t-n1.7" / "go-1" / "pi0.5"
    backend="lerobot-async",          # lerobot-async | vlagents | rosa | local | http
    endpoint="http://host:port",      # 远程时
    embodiment="unitree-g1",          # 触发本体适配配置
)
obs = Observation(images={"front": img, "wrist": img2}, state=joint_state, instruction="pick up the cup")
actions = policy.act(obs)             # 返回标准动作块(np.ndarray + 元数据)
policy.metrics()                      # 延迟/吞吐,自动可选上报到索引
```
**标准Schema:**Observation(图像字典、状态向量、指令、时间戳、本体ID);Action(动作块矩阵、动作空间描述、频率、置信度可选)。
**后端适配器:**lerobot-async(RobotClient协议)、vlagents、rosa、local(直接加载权重)、http(OpenAI风格JSON,便于第2阶段托管)。
**特性:**模型热切换;超时/重试;版本锁;与索引联动的`recommend(task, embodiment, budget)`。
**AC:**≥3后端、≥5模型可用;示例仓库在SO-101与一个仿真环境跑通;PyPI发布;文档完整;周安装≥100(阶段1验收)。

### M7 托管推理(概要)— P2
- 托管2-3个许可清晰的开源VLA(System 2/评测/微调用途),OpenAI风格HTTP端点+SDK http后端;
- 计费:按请求/按GPU时;预付余额;
- 公开指标:每端点可用率、TTFT、吞吐(对齐OpenRouter口径);
- 微调任务:上传LeRobot v3数据集→任务队列→返回权重与评测报告。

### M8 公开性能榜 — P2
- 维度:模型×端点×地域×时间窗;样本量与置信区间必显;措辞宪法(只陈述测量)。

### M9 账号、订阅、告警 — P1/P2
- 邮箱/GitHub登录;关注模型/本体的更新提醒;RSS/Webhook(飞书、钉钉);P2付费订阅。

---

## 4. 数据模型(实体与关键字段)

- `Model(id, name, org, release_date, params, arch_type, license, commercial_ok, weights_url, code_url, paper_url, modalities, action_space, cross_embodiment, pretrain_hours, status)`
- `ModelVersion(model_id, version, weights_sha256, release_date, changelog_url)`
- `Embodiment(id, name, vendor, form, dof, end_effector, sdk_url, price_range, data_formats)`
- `Compatibility(model_version_id, embodiment_id, status, evidence_id)`
- `Hardware(id, name, vram_gb, type, price_source_id)` ← 价格来自算力罗盘 `hardware_price_daily(hardware_id, date, price_cny_per_hour, source_id)`
- `Benchmark(id, name, task_suite, url)`;`BenchmarkResult(model_version_id, benchmark_id, score, source_type, evidence_id, date)`
- `LatencyMeasurement(id, model_version_id, hardware_id, precision, config_json, p50, p95, throughput, vram_peak, source_type[literature|maintainer|crowd], contributor_id, fingerprint, created_at, review_status)`
- `Source(id, url, type, terms_status)`;`Snapshot(id, source_id, fetched_at, sha256, storage_key)`;`Evidence(id, snapshot_id, field_path, note)`
- `Tutorial(id, model_version_id, hardware_id, locale, body_md, measurement_id, version)`
- `Endpoint(id, provider_id, model_version_id, region, url, pricing_json, status)`(P2);`Provider(id, name, type[self|third_party], neutrality_disclosure)`
- `User/Contributor(id, handle, github_id, email_hash, reputation)`;`Submission(id, type, payload, status, reviewer_id)`
- `Correction(id, entity, field, old, new, reason, actor, created_at)`

---

## 5. 测量方法论(规范摘要,完整版另文)

1. 预热≥20步后计时;每次≥200步;报告p50/p95;
2. 固定输入分辨率与动作块长度,记录到config;
3. 硬件指纹含GPU型号、驱动、CUDA、CPU、内存、OS、电源模式;
4. 同一(模型版本×硬件×精度×配置)至少3个独立贡献者或维护者复测后标记"已验证";
5. 展示规则:样本量<3显示"初步";偏离中位数>3σ隔离待审;
6. 成本口径:按算力罗盘该硬件当日按需小时价,注明来源与日期;
7. 任何公开结论只陈述测量值与条件,不作模型优劣的定性断言(优劣由用户按任务判断)。

---

## 6. 系统架构

```
数据采集(模型发布/论文/仓库/HF Hub) → 来源适配器 → 快照(R2/OSS, 哈希)
      → 标准化 → 数据库(Postgres 或 D1) → API(Hono/Workers) → 站点(Astro, 静态+岛)
众包CLI(Python, PyPI) → 上传API(签名+限频) → 待审队列 → 入库 → 榜/卡片
算力罗盘价格API ─────────────────────────────→ 成本计算
SDK(Python, PyPI) ↔ 策略服务器后端 ↔ (P2)托管推理集群 → 指标管道 → 公开榜
```
- 与算力罗盘共用:站点框架、证据链服务、价格数据、账号系统;
- 部署:海外Cloudflare为主(免备案、快),国内可达性用RUM监测;CLI/SDK发布到PyPI+GitHub(+国内镜像);
- 安全:CLI不采集任何图像/数据;上传需一次性签名令牌;密钥不落盘;
- 许可合规:每个模型的License字段驱动"可托管/不可托管"标记(P2)。

---

## 7. 非功能需求

- 性能:索引页首屏<2s(国内RUM p75<3.5s);API p95<300ms;
- 可审计:所有公开数字可回溯;修正留痕;
- 国际化:zh-CN / en 同步;
- 可维护性:新增一个模型条目≤30分钟;新增一个CLI模型适配≤半天;
- 可用性:索引月可用率≥99.5%;
- 隐私:不强制注册;邮箱哈希存储;贡献者可匿名。

---

## 8. 里程碑与验收(第0阶段12周)

| 周 | 交付 | AC |
|---|---|---|
| 1-2 | 数据模型+证据链复用;首批10模型/6本体录入;索引v0.1上线 | 字段完整率≥90%,证据可回溯 |
| 3-4 | 延迟/成本层(文献+维护者实测,3硬件);对比页 | ≥10模型×3硬件有数据 |
| 5-6 | CLI v0.1(5模型)+上传+贡献者榜 | 4090一次运行<15分钟 |
| 7-8 | 教程×3;英文版;RSS/关注 | 教程含可复现命令 |
| 9-10 | 适配矩阵扩展;CLI模型扩到8;教程×3 | 矩阵≥60格 |
| 11-12 | 阶段验收 | 月访问≥2000、复访≥20%、众包≥50条、外部引用≥5、技术候选≥3 |

第1阶段(SDK)以M6规格启动,前置条件:技术合伙人到位。

---

## 9. 风险与开放问题

- LeRobot异步推理不稳定 → SDK需自带回退与一致性测试;
- 模型许可差异(部分禁商用) → 索引明确标注;托管仅选许可清晰者;
- 众包数据作弊/噪声 → 指纹+去重+待审+多源验证;
- 华为/腾讯平台推出类似索引 → 坚持中立+跨云+可审计,做速度;
- 开放问题:英文名与域名;是否独立域名或作为算力罗盘子栏目(建议先子栏目,阶段1独立)。

---

## 附录A:首批模型清单(建议)
GR00T N1.7(NVIDIA)、LingBot-VLA 2.0(蚂蚁灵波)、GO-1(智元)、π0 / π0.5(Physical Intelligence)、SmolVLA(HF)、OpenVLA、X-VLA、Octo、(星海图WRC开源模型,发布后补入)、(COSA相关开放组件如有)。

## 附录B:首批本体清单(建议)
宇树 G1/H1、智元 精灵G1/远征、松灵机械臂(Piper等)、SO-101、Franka、傅立叶 GR系列。

## 附录C:主要来源
- LingBot-VLA 2.0开源:qbitai.com/2026/07/445668.html
- GR00T N1.7:huggingface.co/blog/nvidia/gr00t-n1-7
- 逐际动力COSA 0.5三层架构:(2026-07-15发布报道)
- 星海图WRC开源计划与Galaxea Data Hub:qbitai.com/2026/06/436223.html;aimaoxian.com/artr/dPYq8qgm82.html
- LeRobot Dataset v3 / 异步推理:huggingface.co/blog/lerobot-datasets-v3;huggingface.co/docs/lerobot/en/async;github.com/huggingface/lerobot/issues/2980
- 华为云CloudRobo:cls.cn/detail/2391562;腾讯Tairos:tairos.tencent.com
- VLABench:github.com/OpenMOSS/VLABench
