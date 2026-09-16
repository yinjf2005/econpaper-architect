# 指引 §3.1–§3.5 模型详解（因果识别 / 结构模型 / 时间序列与面板 / ML 因果 / 仿真）

> 保真摘录自《经济论文撰写指引》§3.1–§3.5。仅在需要模型细节时加载。

### 3.1 因果识别策略（Causal Identification Strategies）

这一板块的方法均以反事实推断为逻辑内核，目标是回答“X是否导致了Y”。各方法在“如何构造反事实”这一根本问题上采取不同策略。

#### 3.1.1 随机实验与自然实验

随机实验（RCT）
核心用途： 通过随机分配处理状态，直接消除选择偏误，获得无偏的因果效应估计。这是因果推断的“黄金标准”。
适用条件： 研究者有能力对处理分配进行随机化（实验室实验、田野实验、调查实验）；样本量足以保证随机化后的组间平衡；处理无溢出效应（SUTVA）。
不适用情形： 涉及宏观政策、历史事件等不可操控的处理；处理效应存在一般均衡反馈（如大规模就业培训可能改变市场工资）。
细化场景： 发展经济学中的扶贫项目评估（如随机发放现金转移）、劳动经济学中的求职援助实验、行为经济学中的助推干预（nudge）实验。
关键理论来源： Duflo, Glennerster & Kremer (2007), “Using Randomization in Development Economics Research: A Toolkit”; Banerjee & Duflo (2009), “The Experimental Approach to Development Economics”。
实操注意： 需预注册（pre-registration）以防范p-hacking；需报告 attrition（样本流失）及其处理方式；需讨论外部效度（external validity）的边界。
自然实验（Natural Experiment）
核心用途： 利用外生冲击（政策变动、自然灾害、制度断裂）近似随机地分配处理，识别因果效应。
适用条件： 存在一个与研究问题相关的、外生的制度或环境变化；该变化对处理组和对照组的影响机制清晰可辨。
细化场景： 德国统一对东德经济的影响、中国国企改革对生产率的影响、疫情冲击对劳动力供给的影响。Angrist & Krueger (1991) 利用越战征兵抽签研究教育回报是自然实验设计的经典范例。
关键理论来源： Angrist & Krueger (2001), “Instrumental Variables and the Search for Identification”; Rosenzweig & Wolpin (2000), “Natural ‘Natural Experiments’ in Economics”。
实操注意： 自然实验的“外生性”往往需要论证而非假定；需排除同期其他冲击的干扰；处理组与对照组的可比性需要证据支持。

#### 3.1.2 双重差分（DID）家族

传统双重差分（Two-Way Fixed Effects DID）
核心用途： 利用政策实施前后、处理组与对照组的双重差异，识别处理效应。
适用条件： 处理组与对照组在政策前满足平行趋势假定（parallel trends）；处理时点统一或近似统一；无预期效应（anticipation effect）或预期效应可建模。
不适用情形： 处理时点交错且处理效应异质时，传统TWFE估计量会产生负权重偏误（negative weighting bias），这是近年DID文献的核心警示。
细化场景： 最低工资政策对就业的影响、环境规制对企业排放的影响、自贸区设立对贸易流量的影响。
关键理论来源： Ashenfelter & Card (1985); Card & Krueger (1994); Goodman-Bacon (2021), “Difference-in-Differences with Variation in Treatment Timing” ——提出Bacon分解，是诊断TWFE偏误的必备工具。
实操注意： 必须进行平行趋势检验（事件研究图）；当处理时点交错时，必须使用Bacon分解诊断负权重比例，负权重接近1说明估计较稳健，接近0则表明结果不可靠。
交叠DID的异质性稳健估计（Heterogeneity-Robust Staggered DID）
这是近五年DID领域最活跃的方法论前沿。当处理时点交错（staggered adoption）且处理效应随时间或组别变化时，传统TWFE的组别-时期平均处理效应估计不再无偏。当前主流的三类估计量：
Callaway & Sant‘Anna (2021) 估计量（csdid） ：先估计每个“组别-时期”的处理效应，再按需要聚合为总体ATT或事件研究动态效应。适用条件： 需要“从未处理组”或“尚未处理组”作为干净对照。关键来源： Callaway & Sant’Anna (2021), “Difference-in-Differences with Multiple Time Periods,” Journal of Econometrics。
Sun & Abraham (2021) 估计量（eventstudyinteract） ：通过“交互加权”纠正事件研究估计中的污染问题，适用于需要绘制事件研究图的情形。关键来源： Sun & Abraham (2021), “Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects,” Journal of Econometrics。
De Chaisemartin & D‘Haultfœuille (2020) 估计量（did_multiplegt） ：允许处理效应随组别和时间变化，同时处理“处理退出”情形（非吸收性处理）。关键来源： De Chaisemartin & D’Haultfœuille (2020), “Two-Way Fixed Effects Estimators with Heterogeneous Treatment Effects,” AER。
Borusyak, Jaravel & Spiess (2024) 的插补估计量：以“插补”形式实现有效估计，允许不受限制的处理效应异质性。关键来源： Borusyak, Jaravel & Spiess (2024), “Revisiting Event-Study Designs: Robust and Efficient Estimation,” Review of Economic Studies。
实操注意： 选择估计量的核心判断标准：若希望估计总体ATT，CS或BJS均可作为主估计；若希望绘制事件研究图，应使用SA、CS动态聚合或BJS动态估计，不要直接使用传统TWFE的leads and lags。Bacon分解中的异质性处理稳健性指标越接近1越稳健，越接近0则表明结果越不稳健。
合成DID（Synthetic DID）
核心用途： 将合成控制法的权重构建思路与DID框架结合，为每个处理单位构建“合成对照”，削弱对平行趋势假定的依赖。
适用条件： 处理单位数量较少、处理时点交错、传统平行趋势难以满足。
细化场景： 少数省份实施某项政策、少数城市试点某项改革。
关键理论来源： Arkhangelsky et al. (2021), “Synthetic Difference-in-Differences,” AER。
实操注意： 合成DID对“不处理单位池”的质量敏感；需要检验合成对照的预处理拟合优度；placebo test是必要的稳健性检验。

#### 3.1.3 工具变量（IV）

核心用途： 当核心解释变量存在内生性（遗漏变量、反向因果、测量误差）时，利用工具变量的外生变异识别因果效应。
适用条件（两个不可检验的核心假定）：
相关性（relevance）： 工具变量与内生解释变量显著相关。经验规则：第一阶段F统计量 > 10（Staiger & Stock, 1997）。但现代标准更严格，需报告Kleibergen-Paap rk Wald F（异方差/聚类稳健），并参考Montiel Olea & Pflueger (2013) 的有效F临界值。
排他性（exclusion）： 工具变量仅通过内生解释变量影响结果变量。这一假定不可直接检验，需理论论证和间接证据（如过度识别检验、placebo检验）。
不适用情形： 找不到满足排他性约束的工具；工具与遗漏变量直接相关；工具仅通过其他未观测渠道影响结果。
细化场景： 教育回报估计中利用义务教育法改革或距离学校的距离作为教育的工具；制度质量对经济增长的影响中利用殖民者死亡率或法律起源作为制度的工具（Acemoglu, Johnson & Robinson, 2001）；贸易开放对增长的影响中利用地理特征作为贸易的工具。
关键理论来源： Angrist, Imbens & Rubin (1996), “Identification of Causal Effects Using Instrumental Variables”; Stock & Yogo (2005), “Testing for Weak Instruments in Linear IV Regression”; Andrews, Stock & Sun (2019), “Weak Instruments in Instrumental Variables Regression,” Annual Review of Economics。
实操注意： 弱工具下的推断需使用弱工具稳健方法（Anderson-Rubin检验、有效F检验）；恰好识别时AR检验对弱工具完全稳健；过度识别检验（Sargan/Hansen J）在弱工具下失效，不可依赖。

#### 3.1.4 断点回归（RDD）

核心用途： 当处理分配基于一个连续变量是否超过某个阈值时，利用阈值附近的局部随机性识别因果效应。
适用条件： 存在一个连续配置变量（running variable）和一个明确的断点；个体无法精确操纵配置变量（或操纵可被检验和排除）；断点附近处理组与对照组在可观测和不可观测特征上连续。
两种设计框架：
精确断点（Sharp RDD）： 断点一侧全部接受处理，另一侧全部不接受。如高考分数线决定是否录取。
模糊断点（Fuzzy RDD）： 断点处处理概率发生不连续跳跃但非从0到1。此时断点作为工具变量使用。
细化场景： 班级规模对学生成绩的影响（利用最大班额规定）、贫困线附近的扶贫政策效果、选举中的“险胜”与“惨败”对后续政策的影响（Lee, 2008）。
关键理论来源： Hahn, Todd & van der Klaauw (2001), “Identification and Estimation of Treatment Effects with a Regression-Discontinuity Design”; Imbens & Lemieux (2008), “Regression Discontinuity Designs: A Guide to Practice,” Journal of Econometrics；黄炜、向科谚、袁洛琪（2025），《断点回归设计的实证指南：操作规范、应用误区与实践拓展》，《数量经济技术经济研究》。
实操注意： 最优带宽选择（IK/CCT方法）是关键；需报告多个带宽下的结果；McCrary密度检验用于检验配置变量在断点处是否存在操纵；协变量平衡检验是必要的；断点回归图的绘制是论文的标准配置。特殊情形还包括多重配置变量、多重断点和拐点回归设计。

#### 3.1.5 匹配与加权方法

倾向得分匹配（PSM）
核心用途： 在可观测变量层面平衡处理组与对照组，构造“统计上的双胞胎”来估计处理效应。
适用条件： 条件独立假定（CIA）——控制可观测变量后，处理分配与潜在结果独立。这意味着所有影响处理分配和结果的混杂变量都已被观测并纳入模型。
不适用情形： 存在不可观测的混杂因素（这是PSM最致命的局限，也是审稿人最常攻击的点）；样本量不足以在倾向得分上实现良好匹配。
细化场景： 项目评估中处理组与对照组在年龄、教育、收入等可观测特征上差异较大时；与DID结合使用（PSM-DID）以同时控制可观测和不可观测异质性。
关键理论来源： Rosenbaum & Rubin (1983), “The Central Role of the Propensity Score in Observational Studies for Causal Effects”; Heckman, Ichimura & Todd (1997), “Matching as an Econometric Evaluation Estimator”。
实操注意： 匹配后需报告平衡性检验（标准化偏差 < 10%）；共同支撑域（common support）的讨论不可省略；PSM的结果对匹配算法（最近邻、核匹配、半径匹配）敏感，需报告多种算法的稳健性。
双稳健估计（Doubly Robust Estimation）
核心用途： 同时建模处理方程和结果方程，只要其中一个模型正确指定，估计量就一致。
适用条件： 有丰富的协变量信息；两个模型（处理模型和结果模型）中至少一个正确指定。
细化场景： 当研究者对结果方程的函数形式不确定时，双稳健方法提供了额外的保护。与机器学习结合后（如DML），在高维协变量场景中尤为有力。
关键理论来源： Robins, Rotnitzky & Zhao (1994); Chernozhukov et al. (2018), “Double/Debiased Machine Learning for Treatment and Structural Parameters,” Econometrics Journal。

#### 3.1.6 合成控制法（SCM）及其扩展

核心用途： 当处理单位只有一个或少数几个（如一个国家、一个省份）时，通过对多个未处理单位赋予最优权重，构建“合成对照”来估计处理效应。
适用条件： 处理单位数量少（单个或少量）；有足够数量的未处理单位（donor pool）可供加权；处理前的拟合期足够长以估计权重；处理单位的结果趋势可以被donor pool的加权平均合理逼近。
核心优势： 小规模数据适用性强、反事实透明度高、结果可解释性佳，且允许个体异质性和不可观测的时变混杂因素存在。当数据存在自相关时，DID不再适用，研究者常转向SCM。
不适用情形： donor pool中的单位受到与处理单位相同的冲击（interference）；处理前拟合期太短；处理单位的结果值位于donor pool结果集的边界之外（此时标准SCM权重约束可能次优，需使用正则化SCM）。
细化场景： 加州控烟法案对烟草消费的影响（Abadie et al., 2010，SCM的经典应用）；德国统一对西德经济的影响（Abadie et al., 2015）；中国某省份实施碳交易试点对碳排放的影响。
关键理论来源： Abadie & Gardeazabal (2003), “The Economic Costs of Conflict: A Case Study of the Basque Country”; Abadie, Diamond & Hainmueller (2010), “Synthetic Control Methods for Comparative Case Studies,” JASA；Abadie (2021), “Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects,” Journal of Economic Literature。
前沿扩展：
正则化SCM（RSCM）： 放松权重非负且和为1的约束，在边界情形下优于标准SCM。
贝叶斯SCM： 引入马蹄先验（horseshoe prior）处理多个处理单位和交错处理时点。
合成DID： 见3.1.2节。
与深度学习结合： 通过非线性激活函数扩展SCM的拟合能力。
实操注意： 必须进行placebo test（安慰剂检验）——对每个donor单位假装其为处理单位，比较处理效应的分布；需报告预处理拟合的RMSPE（均方根预测误差）；donor pool的选择需有理论依据，排除受处理溢出影响的单位。

### 3.2 结构化模型与估计（Structural Models and Estimation）

结构化模型的核心特征是：明确建模经济主体的最优化行为和市场的均衡条件，估计出“结构参数”（偏好参数、技术参数），从而进行反事实分析和福利评估。与简约式（reduced-form）方法的根本区别在于：结构化模型允许研究者回答“如果政策变成X会怎样”的反事实问题。

#### 3.2.1 离散选择需求模型与BLP

核心用途： 在差异化产品市场中估计需求函数和成本函数，进而进行并购模拟、福利分析和产业政策评估。BLP模型基于供需关系估计需求和成本参数，估计得到的结构参数更加贴近现实，能够进行均衡及福利分析，合理地评估产业政策。
适用条件： 有产品层面的市场份额数据（aggregate shares）；存在产品特征数据（价格、质量、广告等）；需要工具变量处理价格内生性（通常使用成本转移工具，如竞争对手的产品特征）。
不适用情形： 产品数量过多导致随机系数维度爆炸；市场份额数据不可得或质量差；消费者偏好高度非参数化，随机系数Logit的分布假设难以成立。
细化场景： 汽车市场需求估计与并购模拟（BLP, 1995的经典应用）；电信运营商定价策略评估；航空业竞争与合并的福利分析；中国新购汽车市场的需求估计与并购模拟。
关键理论来源： Berry (1994), “Estimating Discrete-Choice Models of Product Differentiation,” RAND Journal of Economics——提出BLP的估计框架；Berry, Levinsohn & Pakes (1995), “Automobile Prices in Market Equilibrium,” Econometrica——BLP模型的奠基性论文；Nevo (2001), “Measuring Market Power in the Ready-to-Eat Cereal Industry,” Econometrica；李凯、孟一鸣、郭晓玲（2020），《BLP模型发展及其在产业组织应用综述》，《产经评论》。
实操注意： BLP估计的计算量较大（需要收缩映射 inversion）；工具变量的有效性需要论证（成本转移工具是否满足排他性）；需要报告估计后的需求弹性矩阵和加价（markup）估计；反事实模拟的结果对随机系数分布假设敏感。

#### 3.2.2 动态离散选择模型（Dynamic Discrete Choice）

核心用途： 建模个体在跨期环境下的离散选择行为（是否更换引擎、是否进入市场、是否退出），估计结构参数并模拟反事实政策。
适用条件： 个体的决策具有动态性（当前决策影响未来状态和收益）；有面板数据追踪个体决策和状态变量的历史；需要处理“不可观测状态变量”和“未来预期”的建模问题。
不适用情形： 决策本质上是静态的（无跨期联系）；数据不足以识别贴现因子或状态转移概率。
细化场景： Rust (1987) 的巴士引擎更换模型（Harold Zurcher的引擎更换决策）是该模型的经典范例；企业进入退出的动态博弈（如航空业的市场进入）；劳动力市场中的退休决策；医疗保险中的计划选择。
关键理论来源： Rust (1987), “Optimal Replacement of GMC Bus Engines: An Empirical Model of Harold Zurcher,” Econometrica——动态离散选择模型的奠基性工作；Hotz & Miller (1993), “Conditional Choice Probabilities and the Estimation of Dynamic Models,” Review of Economic Studies；Aguirregabiria & Mira (2010), “Dynamic Discrete Choice Structural Models: A Survey,” Journal of Econometrics。
实操注意： 逆向归纳的计算复杂度随状态空间维度指数增长（维度诅咒）；CCP（条件选择概率）两步法可降低计算负担；贴现因子的识别通常依赖于数据中的动态模式，需谨慎论证；连续时间版本的识别和估计需引入随机过程假设。

#### 3.2.3 一般均衡与CGE模型

核心用途： 分析政策冲击（税收、贸易、环境规制）对整个经济系统的全局效应，包括对价格、产出、要素配置和福利的影响。
适用条件： 需要构建包含多个部门、多个要素和多个主体的经济系统；有社会核算矩阵（SAM）或投入产出表作为校准基础；参数校准需有文献依据或计量估计支撑。
细化场景： 碳税改革的经济影响评估；贸易自由化对收入和分配的影响；税收改革对劳动供给和储蓄的效应。中国CGE模型常被用于评估“双碳”目标下的政策路径。
关键理论来源： Shoven & Whalley (1984), “Applied General-Equilibrium Models of Taxation and International Trade”; Kehoe & Kehoe (1994), “A Primer on Static Applied General Equilibrium Models”; Dixon & Jorgenson (2013), Handbook of Computable General Equilibrium Modeling。
实操注意： CES生产函数的替代弹性参数是CGE模型中最敏感的校准参数，需有可靠的计量估计或文献依据（贝叶斯估计方法可用于CES生产函数的参数估计）；模型的福利结论对 closure rule（宏观闭合规则）的选择敏感。

#### 3.2.4 DSGE模型

核心用途： 宏观政策分析（货币政策、财政政策、宏观审慎政策）的标准工具。DSGE模型通过构建包含家庭、企业、政府等经济主体的动态随机一般均衡框架，其核心逻辑是求解各主体的最优化问题并配合市场出清条件形成均衡动态系统，借助脉冲响应图（IRF）呈现经济变量间的动态关系。
适用条件： 需要宏观时间序列数据（产出、通胀、利率、就业等）；模型参数可通过校准或贝叶斯估计赋值；研究问题涉及政策规则的变化或结构性冲击的传导。
不适用情形： 模型对经济危机的建模能力有限（这是DSGE的主要批评之一）；代表性主体假设和理性预期假设在特定情境下过于严格；参数估计面临识别困难。
细化场景： 货币政策规则（Taylor规则）对通胀和产出的影响；财政刺激政策的乘数效应；负利率政策的传导机制；新冠疫情冲击的宏观效应模拟。
关键理论来源： Smets & Wouters (2003), “An Estimated Dynamic Stochastic General Equilibrium Model of the Euro Area,” Journal of the European Economic Association——DSGE估计的基准模型；Christiano, Eichenbaum & Evans (2005), “Nominal Rigidities and the Dynamic Effects of a Shock to Monetary Policy,” Journal of Political Economy；Gertler & Karadi (2011), “A Model of Unconventional Monetary Policy,” Journal of Monetary Economics；Trescher & Tessmann (2025), “DSGE Models: Practical Methodological Note and Recent Trends”。
实操注意： DSGE模型的优势在于利用均衡条件进行估计，消除了指定排除性约束的需要；但需要对参数校准进行敏感性分析；模型的脉冲响应图是论文的核心呈现形式；贝叶斯估计中的先验分布选择会显著影响后验结果，需进行先验敏感性检验。

#### 3.2.5 博弈论与机制设计模型

博弈论模型
核心用途： 分析经济主体之间的策略互动与均衡选择。适用于寡头竞争、拍卖、谈判、平台竞争等场景。
细化场景： 平台双边市场中的定价策略（如电商平台的商家与消费者）；拍卖机制中的投标行为（如频谱拍卖）；企业合谋与反垄断分析；银行挤兑中的协调博弈。
关键理论来源： Fudenberg & Tirole (1991), Game Theory; Tirole (1988), The Theory of Industrial Organization；Athey & Bagwell (2008), “Collusion and Price Rigidity,” Review of Economic Studies。
机制设计模型
核心用途： 从合意的目标出发，反向设计最优的制度安排（契约、拍卖规则、监管机制）。机制设计是“博弈论的反向工程”——先定义合意的结果，再设计游戏规则以实现该结果。
适用条件： 有明确的委托人-代理人结构；代理人的信息是私人信息；存在信息不对称或道德风险。
细化场景： 最优所得税设计（Mirrlees, 1971）；拍卖设计（Myerson, 1981）；监管中的激励规制（Laffont & Tirole, 1993）；碳排放权交易机制设计。
关键理论来源： Myerson (1981), “Optimal Auction Design,” Mathematics of Operations Research；Laffont & Tirole (1993), A Theory of Incentives in Procurement and Regulation；Bolton & Dewatripont (2005), Contract Theory。
实操注意： 机制设计论文的理论贡献通常在于：刻画最优机制的特征、证明其存在性、讨论其与次优机制的效率差距。实证检验机制设计理论较为困难，通常以实验室实验或现场实验作为补充。

### 3.3 时间序列与面板模型


#### 3.3.1 向量自回归（VAR/SVAR/BVAR）

核心用途： 分析多个宏观时间序列变量之间的动态互动关系，识别结构性冲击（如货币政策冲击、财政冲击）的传导效应。
适用条件： 有足够长的时间序列数据；变量间的动态关系可以通过线性系统合理逼近；需要施加识别假设（递归排序、符号约束、长期约束）来分离结构性冲击。
细化场景： 货币政策冲击对产出和通胀的动态效应（Christiano, Eichenbaum & Evans, 1999）；油价冲击对宏观经济的影响；财政政策的乘数效应。
关键理论来源： Sims (1980), “Macroeconomics and Reality,” Econometrica；Christiano, Eichenbaum & Evans (1999), “Monetary Policy Shocks: What Have We Learned and to What End?,” Handbook of Macroeconomics；Uhlig (2005), “What Are the Effects of Monetary Policy on Output?,” Journal of Monetary Economics。
实操注意： 变量排序对递归识别至关重要，需有理论依据；滞后阶数选择（AIC/BIC/HQ）需报告；脉冲响应图的置信区间需使用bootstrap方法；符号约束识别（Uhlig, 2005）在近年被广泛采用，但需注意“识别不足”问题。

#### 3.3.2 面板数据模型

核心用途： 利用面板数据的个体和时间双重维度，控制不可观测的个体异质性，估计变量间的关系。
模型选择流程：
混合OLS vs 固定效应： F检验。
固定效应 vs 随机效应： Hausman检验。Hausman检验通过时，应选用固定效应模型；否则选用随机效应模型。经验规则：当不能把观测个体当作从一个大总体中随机抽样的结果时，使用固定效应模型。
细化场景： 省级面板数据中政策变量对经济增长的影响；企业面板数据中治理结构对绩效的影响；跨国面板数据中制度质量对发展的影响。
关键理论来源： Wooldridge (2010), Econometric Analysis of Cross Section and Panel Data；Baltagi (2021), Econometric Analysis of Panel Data。
实操注意： 固定效应模型无法估计不随时间变化的变量（如性别、地理位置）的系数；随机效应模型的CIA假定在多数应用场景中过于严格；聚类稳健标准误（clustered standard errors）在面板数据中是标配。

### 3.4 机器学习与因果推断的交叉方法


#### 3.4.1 双重机器学习（DML）

核心用途： 在高维协变量场景中估计因果效应，同时避免过拟合和正则化偏差。传统线性回归难以捕捉经济数据中的高维特征与非线性关系，DML允许在灵活控制高维复杂协变量的同时获得对因果效应的稳健估计和推断。
适用条件： 协变量维度高（接近或超过样本量）；协变量与处理变量、结果变量之间的关系非线性或复杂；有可信的识别策略（如部分线性模型、交互模型）。
不适用情形： 识别策略本身不可信（DML不能替代识别策略，只能改进估计）；样本量太小，交叉拟合（cross-fitting）的样本分割不稳定。
细化场景： 劳动经济学中教育/职业培训对收入的影响，控制个人技能、就业地区、家庭负担等高维变量；公司金融中绿色金融政策对全要素碳生产率的影响；政策评估中大量控制变量的场景。
关键理论来源： Chernozhukov et al. (2018), “Double/Debiased Machine Learning for Treatment and Structural Parameters,” Econometrics Journal——DML的奠基性论文；解海天（2025），《双重机器学习的理论与应用——从“黑箱”到“工具箱”的实践指南》，《数量经济技术经济研究》。
实操注意： 核心机制是正交化（orthogonalization）和交叉拟合（cross-fitting），用以消除正则化偏差；需报告不同机器学习方法（Lasso、随机森林、梯度提升）的稳健性；DML的置信区间在大样本下有效，小样本下需谨慎；DML已从横截面数据扩展到面板数据。

#### 3.4.2 因果森林（Causal Forests）

核心用途： 估计条件平均处理效应（CATE） ——理解处理效应在不同个体/群体间的异质性。当不是所有人都能被处理、需要优先排序时（如有限预算下的优惠券发放），CATE估计尤为有用。
适用条件： 有丰富的个体层面协变量；样本量足够大（CATE的估计目标是函数而非有限维向量，估计难度远高于平均处理效应）；处理分配近似随机或在条件独立假定下可识别。
细化场景： 个性化推荐中的优惠券发放策略；精准医疗中的治疗方案选择；教育干预中不同学生群体的差异化效应。
关键理论来源： Wager & Athey (2018), “Estimation and Inference of Heterogeneous Treatment Effects using Random Forests,” JASA；Athey, Tibshirani & Wager (2019), “Generalized Random Forests,” Annals of Statistics；Chen & Jing (2025), “Recent Advances in Causal Machine Learning and Dynamic Policy Learning”。
实操注意： 因果森林通过“局部中心化”（local centering）消除混杂偏差；GRF框架提供了渐近正态性和置信区间；高维协变量场景下需配合DML使用。

#### 3.4.3 元学习器（Meta-Learners）

核心用途： 通过组合多个机器学习模型来估计CATE，是一组灵活的“框架”而非单一算法。
主要类型： S-learner（单一模型，将处理变量作为特征）、T-learner（处理组和对照组分别建模）、X-learner（在处理组和对照组样本量不平衡时优于T-learner）、DR-learner（结合双稳健估计）、R-learner（残差化方法）。
适用条件： 有合适的机器学习模型（随机森林、梯度提升、神经网络）作为基学习器；样本量充足。
细化场景： 当研究者不确定处理效应是否异质时，元学习器提供了“探索性”的异质性发现工具。但探索性发现的结果需通过样本外验证或预注册的确认性分析来验证。
关键理论来源： Künzel et al. (2019), “Metalearners for Estimating Heterogeneous Treatment Effects using Machine Learning,” PNAS；Nie & Wager (2021), “Quasi-Oracle Estimation of Heterogeneous Treatment Effects,” Biometrika。

### 3.5 仿真与计算模型


#### 3.5.1 基于主体的仿真（ABM）

核心用途： 建模异质性主体之间的互动如何产生宏观层面的涌现现象（emergent phenomena），如金融危机中的传染效应、房价泡沫的形成与破裂、技术扩散的S型曲线。
适用条件： 系统具有复杂的异质性互动；传统代表性主体模型无法捕捉涌现现象；有足够的微观行为参数数据或合理的校准依据。
不适用情形： 可以通过解析模型得到清晰结论的场景（ABM的“黑箱”特征使其结论难以一般化）；微观行为参数的校准缺乏依据。
细化场景： 银行间市场的系统性风险传染；房地产市场的泡沫与崩盘；碳排放交易中的企业策略互动；流行病的经济影响模拟。
关键理论来源： Tesfatsion & Judd (2006), Handbook of Computational Economics, Vol. 2: Agent-Based Computational Economics；LeBaron & Tesfatsion (2008), “Modeling Macroeconomies as Open-Ended Dynamic Systems of Interacting Agents,” AER P&P。
实操注意： ABM论文需要报告稳健性检验——不同随机种子下的结果稳定性；模型的“验证”是难点，需通过历史数据或典型事实来评估模型的合理性；敏感性分析（参数扫描）是标配。

#### 3.5.2 系统动力学

核心用途： 建模经济系统中的反馈回路和时滞效应，适用于政策延迟效应和长期动态分析。
适用条件： 系统中存在明确的反馈结构（正反馈/负反馈）；政策效应具有显著的时间延迟；适合中长期动态分析而非短期预测。
细化场景： 能源-经济-环境的耦合系统建模；人口老龄化对养老金系统的压力；公共卫生政策的长期经济影响。
关键理论来源： Forrester (1961), Industrial Dynamics；Sterman (2000), Business Dynamics: Systems Thinking and Modeling for a Complex World。

#### 3.5.3 数值校准与贝叶斯估计

核心用途： 为结构化模型（DSGE、CGE、动态离散选择）的参数赋值，并进行模型评估和政策模拟。
主要方法：
校准（Calibration）： 基于文献或长期数据均值设定参数值，适用于参数难以通过计量方法识别的情形。
贝叶斯估计： 将先验信息与数据结合，通过MCMC（如Metropolis-Hastings算法）获得参数的后验分布。
矩匹配（Moment Matching）： 选择参数使模型模拟的矩（方差、自相关等）与数据中的矩尽可能接近。
关键理论来源： Smets & Wouters (2003); An & Schorfheide (2007), “Bayesian Analysis of DSGE Models,” Econometric Reviews；Fernández-Villaverde (2010), “The Econometrics of DSGE Models,” SERIEs。
实操注意： 贝叶斯估计中的先验选择需进行敏感性分析；MCMC的收敛诊断（Gelman-Rubin统计量、trace plot）是必要的；校准的参数需进行敏感性分析以评估结论的稳健性。
