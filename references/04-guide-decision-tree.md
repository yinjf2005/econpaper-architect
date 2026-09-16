# 指引 §3.6 六层决策逻辑 + §3.7 理论来源检索

> 保真摘录自《经济论文撰写指引》§3.6、§3.7。这是 D-2~D-7 决策卡的裁决依据。

### 3.6 方法选择的决策逻辑（与3.0逐项对应版）


#### 决策层 1：研究目标是什么？


| 研究目标 | 适配模型 | 不适配模型 | 原因 | 替代 |
|---|---|---|---|---|
| 因果效应（X→Y） | RCT、自然实验、DID、IV、RDD、PSM、SCM | 纯理论模型、DSGE | 不直接识别因果 | 先做识别策略 |
| 结构参数/反事实 | BLP、动态离散选择、CGE、DSGE、机制设计 | 简约式 DID/IV | 无法估计弹性、福利、均衡 | 结构模型 |
| 动态路径 | VAR/SVAR/BVAR、局部投影、DSGE | 横截面 PSM | 无时间维度 | 时间序列/面板 |
| 异质性处理效应 | 因果森林、元学习器、DML | 传统 TWFE DID | 只给平均效应 | CS/SA + 因果森林 |
| 复杂系统涌现 | ABM、系统动力学 | 代表性主体 DSGE | 无法捕捉异质互动 | ABM |
| 制度设计 | 机制设计、博弈论 | 简约式回归 | 无激励相容 | 机制设计 |


#### 决策层 2：识别来源是什么？


| 识别来源 | 适配模型 | 不适配模型 | 原因 | 替代 |
|---|---|---|---|---|
| 随机化 | RCT | DID、IV、PSM | 随机化更干净 | RCT 不可行时再用 |
| 外生政策冲击 | DID、自然实验、事件研究 | PSM | 不可观测混杂 | DID+PSM 可辅助 |
| 阈值 | RDD | DID | 无断点 | IV、RDD |
| 工具变量 | IV | PSM | 内生性未解决 | 有效工具时用 IV |
| 可观测选择 | PSM、DR、DML | 传统 OLS | 选择偏误 | 加 DID/IV |
| 单一/少数处理单位 | SCM、合成 DID | 传统 DID | 平行趋势不可信 | SCM/合成 DID |
| 均衡条件 | 结构模型 | 简约式 | 无均衡约束 | BLP/DSGE/CGE |


#### 决策层 3：数据条件是什么？


| 数据条件 | 适配模型 | 不适配模型 | 原因 | 替代 |
|---|---|---|---|---|
| 高维协变量 | DML、因果森林 | 传统 OLS | 过拟合/正则化偏差 | DML |
| 面板数据 | 固定效应、DID、动态离散选择 | 横截面 PSM | 忽略个体异质性 | 固定效应/DID |
| 时间序列 | VAR、DSGE、局部投影 | 横截面 RCT | 无时间动态 | VAR/DSGE |
| 聚合市场份额 | BLP | 微观离散选择 | 无个体数据 | BLP |
| SAM/IO 表 | CGE | 简约式 | 无部门关联 | CGE |
| 单一处理单位 | SCM、合成 DID | 传统 DID | 无对照组 | SCM |


#### 决策层 4：推断目标是什么？


| 推断目标 | 适配模型 | 不适配模型 | 原因 | 替代 |
|---|---|---|---|---|
| ATE/ATT | RCT、DID、IV、RDD、PSM、SCM | 因果森林 | 平均效应即可 | 传统识别 |
| CATE | 因果森林、元学习器、DML | 传统 TWFE | 只给平均 | 因果森林 |
| 结构参数 | BLP、动态离散选择、DSGE、CGE | DID/IV | 无结构解释 | 结构模型 |
| 脉冲响应 | VAR/SVAR/BVAR、DSGE | 横截面 | 无动态 | VAR/DSGE |
| 福利变化 | BLP、CGE、DSGE、机制设计 | 简约式 | 无福利基础 | 结构模型 |
| 涌现现象 | ABM、系统动力学 | 代表性主体 | 无法涌现 | ABM |


#### 决策层 5：关键假设是否成立？不适配时如何替代？


| 关键假设 | 适配模型 | 不成立时的不适配模型 | 替代方案 |
|---|---|---|---|
| SUTVA | RCT | 有溢出效应的 RCT | 饱和设计、聚类随机、ABM |
| 平行趋势 | 传统 DID | 交错异质下的 TWFE | CS、SA、DCDH、BJS、合成 DID |
| 排他性 | IV | 排他性不成立时的 IV | RDD、DID、结构模型 |
| 连续性/不可操纵 | RDD | 可操纵断点 | 甜甜圈 RDD、IV、DID |
| CIA | PSM、DR | 不可观测混杂下的 PSM | IV、DID、RDD、DML |
| 无干扰 | SCM | donor 受共同冲击 | 合成 DID、贝叶斯 SCM |
| 均衡 | 结构模型 | 非均衡/危机 | ABM、简约式 |
| 理性预期 | DSGE | 危机、异质性 | ABM、金融摩擦 DSGE |


#### 决策层 6：稳健性与交叉验证


| 主模型 | 必须报告的稳健性 | 不适配的替代 |
|---|---|---|
| 传统 TWFE DID | Bacon 分解、平行趋势、CS/SA | 交错异质时改用 CS/SA/DCDH/BJS |
| IV | 弱工具检验、AR、有效 F、过度识别 | 弱工具时改用 LIML/AR |
| RDD | McCrary、带宽敏感性、协变量平衡 | 操纵时改用甜甜圈 RDD |
| PSM | 平衡性、共同支撑、多种匹配 | 不可观测混杂时改用 IV/DID |
| SCM | placebo test、RMSPE、donor 稳健性 | donor 受冲击时改用合成 DID |
| DSGE | 先验敏感性、MCMC 收敛、脉冲响应 | 危机时改用 ABM/金融摩擦 DSGE |
| VAR | 滞后阶数、识别约束、bootstrap | 结构解释弱时改用 SVAR/DSGE |
| ABM | 随机种子、参数扫描、历史矩 | 验证难时改用 DSGE/博弈论 |

小结：3.0与3.6的对应关系。3.0 与 3.6 的对应关系从“平面清单+线性流程”升级为“六层决策树 × 五大家族模型 × 适配/不适配/替代矩阵”。核心对应关系是：3.0 的每一类模型，都在 3.6 中有明确的进入条件和退出条件；3.6 的每一步决策，都能回指 3.0 的具体模型，并点名不适配模型及替代方案。适配与不适配不再隐含，而是显式列出。因此，模型选择部分具备了可检索、可决策、可辩护的实操指引性。

### 3.7 理论来源检索指引

以下按方法论家族列出最值得优先检索的综述性文献，便于研究者快速进入某一方法的文献脉络：
因果推断综述：
陈强（2025），《计量经济学中的因果推断：过去、现在与未来》，《中山大学学报（社会科学版）》，第1期，第43-64页。系统梳理了从随机实验到分位数控制法的完整谱系，文献更新至2024年前沿。
Angrist & Pischke (2009), Mostly Harmless Econometrics；Angrist & Pischke (2015), Mastering ‘Metrics。
DID前沿：
Goodman-Bacon (2021), Journal of Econometrics；Callaway & Sant‘Anna (2021), Journal of Econometrics；Sun & Abraham (2021), Journal of Econometrics；De Chaisemartin & D’Haultfœuille (2020), AER；Borusyak, Jaravel & Spiess (2024), Review of Economic Studies。
刘冲、沙学康、张妍，《交错双重差分：处理效应异质性与估计方法选择》，《数量经济技术经济研究》。
SCM前沿：
Abadie (2021), Journal of Economic Literature；王云浩、胡哲、王继豪、高巍（2026），《合成控制法的研究进展：理论、应用与前瞻》，《计量经济学报》，第6卷第2期。
Arkhangelsky et al. (2021), “Synthetic Difference-in-Differences,” AER。
IV前沿：
Andrews, Stock & Sun (2019), Annual Review of Economics；Stock & Yogo (2005)。
RDD前沿：
Imbens & Lemieux (2008), Journal of Econometrics；黄炜、向科谚、袁洛琪（2025），《数量经济技术经济研究》。
结构化模型：
BLP (1995), Econometrica；Rust (1987), Econometrica；Aguirregabira & Mira (2010), Journal of Econometrics；李凯、孟一鸣、郭晓玲（2020），《产经评论》。
宏观模型：
Smets & Wouters (2003), JEEA；Trescher & Tessmann (2025), “DSGE Models: Practical Methodological Note and Recent Trends”。
机器学习与因果推断：
Chernozhukov et al. (2018), Econometrics Journal；Wager & Athey (2018), JASA；Künzel et al. (2019), PNAS；解海天（2025），《双重机器学习的理论与应用》，《数量经济技术经济研究》。
