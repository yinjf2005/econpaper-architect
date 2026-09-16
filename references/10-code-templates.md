# 计量代码模板（Stata 为主 + Python 补充）

> 生成实证节时按主模型取用。所有代码为**模板**，变量名须替换为用户实际数据；**不得臆造运行结果**——结果表必须由用户跑完回填，或经授权后标注 `[SIM]`。
> 模型适配与不适配条件见 `04-guide-decision-tree.md`；稳健性清单由 `scripts/decide.py` 输出。

## 0. 通用前置

```stata
* ---------- 0.1 环境 ----------
clear all
set more off
set linesize 200
global path "D:/project"
global data "$path/data"
global out  "$path/out"
cap mkdir "$out"

use "$data/panel.dta", clear

* ---------- 0.2 面板设定 ----------
xtset id year
* 强平衡面板检查
xtpattern, gen(pat)
tab pat

* ---------- 0.3 描述性统计（输出三线表） ----------
ssc install fsum, replace     // 或 logout / esttab / asdoc
fsum y x1 x2 ctrl1 ctrl2, stats(mean sd min max n) ///
    title("表1 描述性统计") saving("$out/tab1_desc.rtf") replace

* ---------- 0.4 相关系数 ----------
pwcorr_a y x1 x2, star1(0.01) star5(0.05) star10(0.1)
```

结果表统一用 `esttab` 导出（配合 `booktabs` 风格）：

```stata
ssc install estout, replace
esttab m1 m2 m3 using "$out/tab2_main.rtf", replace b(%6.3f) se(%6.3f) ///
    star(* 0.1 ** 0.05 *** 0.01) stats(N r2_a, labels("样本量" "调整R²")) ///
    title("表2 基准回归结果") addnotes("括号内为聚类到个体层面的稳健标准误；*** p<0.01, ** p<0.05, * p<0.1")
```

---

## 1. Tier1 · 交叠 DID（处理时点交错 + 异质效应）

> **首选现代估计量，禁止直接报 TWFE 点估计了事。** 依据指引 §3.6 决策层 5：平行趋势在交错异质下失效，改用 CS/SA/DCDH/BJS。

```stata
* ---------- 1.1 Callaway & Sant'Anna (CS) ----------
ssc install csdid, replace
ssc install drdid, replace

csdid y ctrl1 ctrl2, ivar(id) time(year) gvar(first_treat) ///
      method(dripw) agg(simple) wboot rseed(1234)
estat all
estat event, window(-5 5) estore(cs_ev)
csdid_plot, title("事件研究图：CS 估计量") ///
      ytitle("ATT") xtitle("相对处理期的期数") ///
      name(csdid_event, replace)
graph export "$out/fig_event_cs.png", replace width(1600)

* ---------- 1.2 Sun & Abraham (SA) ----------
ssc install eventstudyinteract, replace
eventstudyinteract y rel_time_* abs_time_*, ///
      cohort(first_treat) control_cohort(never_treat) ///
      absorb(id year) vce(cluster id)

* ---------- 1.3 Bacon 分解（诊断 TWFE 偏误来源） ----------
ssc install bacondecomp, replace
bacondecomp y D, ddetail
* 若"坏对照（已处理组作对照）"权重高，必须改报 CS/SA

* ---------- 1.4 Borusyak-Jaravel-Spiess 插补估计 ----------
ssc install did_imputation, replace
did_imputation y id year first_treat, allhorizons pretrend(5) ///
      cluster(id) autosample

* ---------- 1.5 平行趋势检验（预处理期联合检验） ----------
* 事件研究图中预处理期系数应联合不显著；报告 F 检验 p 值
```

**必报稳健性**：CS / SA / BJS 三估计量对照、Bacon 分解、预处理期联合检验、预期效应检验（提前 1–2 期设哑变量）、安慰剂（随机提前处理时点 500 次）。

---

## 2. Tier1 · 传统 TWFE DID（处理时点统一时可用）

```stata
gen post = (year >= 2015)
gen treat = (province_group == 1)
gen D = treat * post

reghdfe y D ctrl1 ctrl2, absorb(id year) vce(cluster id)
est store m1
* 逐步加入控制变量
reghdfe y D ctrl1 ctrl2 ctrl3, absorb(id year) vce(cluster id)
est store m2

* 平行趋势（仅当时点统一且无异质效应时才有意义）
```

**坑**：处理时点交错 + 异质效应时 TWFE 会产生"坏对照"偏误（Goodman-Bacon 2021）。遇此情形回到 §1。

---

## 3. Tier1 · 事件研究法

```stata
* 生成相对期数哑变量
gen rel = year - first_treat
replace rel = -1000 if missing(first_treat)      // 从未处理组
forvalues k = 6(-1)1 { gen pre`k' = (rel == -`k') }
gen d0 = (rel == 0)
forvalues k = 1/6 { gen post`k' = (rel == `k') }
replace pre6 = 0 if rel < -6                      // 端点归并
replace post6 = 0 if rel > 6 & !missing(rel)

reghdfe y pre6 pre5 pre4 pre3 pre2 d0 post1-post5 post6 ctrl1 ctrl2, ///
        absorb(id year) vce(cluster id) nocons   // 以 pre1 为基期

coefplot, baselevels keep(pre* d0 post*) vertical ///
        yline(0, lp(dash) lc(gs8)) xline(6, lp(dash) lc(gs8)) ///
        ciopts(recast(rcap)) title("动态效应") xtitle("相对处理期")
graph export "$out/fig_event.png", replace width(1600)
```

---

## 4. Tier1 · 工具变量（IV / 2SLS）

```stata
ssc install ivreg2, replace
ssc install ranktest, replace
ssc install ivreghdfe, replace

* ---------- 4.1 基准 2SLS ----------
ivreghdfe y ctrl1 ctrl2 (x = z1 z2), absorb(id year) cluster(id) first
est store iv1

* ---------- 4.2 必报诊断 ----------
* 弱工具：Kleibergen-Paap rk Wald F 应 > 10（Stock-Yogo 临界值）
* 过度识别：Hansen J / Sargan 检验 p > 0.1
* 欠识别：Kleibergen-Paap rk LM

ivreg2 y ctrl1 ctrl2 (x = z1 z2), cluster(id) first
estat firststage, all
estat overid
estat endogenous          // 若拒绝，说明确实需要 IV

* ---------- 4.3 弱工具稳健推断 ----------
ivreg2 y ctrl1 ctrl2 (x = z1 z2), cluster(id) liml      // LIML
* 或 AR 置信集
```

**坑**：排他性约束只能靠文字论证，检验无法证明。必须专设段落讨论工具的外生性，并做"排除约束的证伪检验"（如把工具放入对前定变量的回归）。

---

## 5. Tier1 · 断点回归（RDD）

```stata
ssc install rdrobust, replace
ssc install rddensity, replace
ssc install rdplot, replace

* ---------- 5.1 带宽选择 ----------
rdbwselect y runvar, c(0) p(1) bwselect(mserd)

* ---------- 5.2 局部线性估计 ----------
rdrobust y runvar, c(0) p(1) bwselect(mserd) vce(cluster id)
* 输出：Conventional / Bias-corrected / Robust 三行，主结果报 Robust

* ---------- 5.3 图形 ----------
rdplot y runvar, c(0) p(1) graph_options(title("断点回归图"))
graph export "$out/fig_rd.png", replace width(1600)

* ---------- 5.4 必报诊断 ----------
rddensity runvar, c(0)        // McCrary 密度检验，p>0.1 说明无操纵
* 带宽敏感性：0.5×、1×、2× 带宽
* 协变量连续性：把前定协变量作为结果变量跑 rdrobust，应不显著
* 甜甜圈 RDD：剔除断点附近 5% 样本重跑
```

---

## 6. Tier1 · 倾向得分匹配（PSM）

```stata
ssc install psmatch2, replace

* ---------- 6.1 估计倾向得分 ----------
pscore treat ctrl1 ctrl2 ctrl3, pscore(ps) blockid(blk) detail
* 或 logit treat ctrl1 ctrl2 ctrl3 ; predict ps, pr

* ---------- 6.2 匹配 ----------
psmatch2 treat ctrl1 ctrl2, outcome(y) neighbor(4) caliper(0.05) ///
        common ate ties logit

* ---------- 6.3 必报诊断 ----------
pstest ctrl1 ctrl2 ctrl3, both graph      // 平衡性：标准化偏差 <10%
* 共同支撑：psgraph 或查看 ps 分布重叠区
* 多种算法对照：近邻(1/4)、卡尺、核匹配、半径匹配

* ---------- 6.4 双稳健（DR） ----------
ssc install drdid, replace   // 或 teffects
teffects psmatch (y) (treat ctrl1 ctrl2, logit), atet vce(robust)
```

**坑**：PSM 只解决可观测混杂。存在不可观测混杂时改 IV/DID/RDD/DML（指引 §3.6 决策层 5）。

---

## 7. Tier1 · 合成控制法（SCM）

```stata
ssc install synth, replace
ssc install synth_runner, replace   // 便于做 placebo 与 RMSPE 比

tsset id year
synth y x1 x2 x3 y(2010) y(2012) y(2014), ///
      trunit(5) trperiod(2015) ///
      xperiod(2010(1)2014) figure ///
      nested allopt
graph export "$out/fig_scm.png", replace width(1600)

* ---------- 7.1 placebo in-space（对 donor 逐一同理合成） ----------
synth_runner y x1 x2 x3, trunit(5) trperiod(2015) ///
      gen_vars(scm_dif) placebo

* ---------- 7.2 必报诊断 ----------
* 预处理期拟合：RMSPE 应尽量小，且远小于 placebo 的 RMSPE
* placebo test：处理单位的效应应位于 placebo 分布尾部
* leave-one-out：逐一剔除 donor 重跑
* donor 受共同冲击时改用合成 DID（sdid）
ssc install sdid, replace
sdid y id year treat, vce(placebo) seed(1234)
```

---

## 8. Tier1 · 面板固定效应

```stata
ssc install reghdfe, replace
ssc install ftools, replace

reghdfe y x ctrl1 ctrl2, absorb(id year) vce(cluster id)
* 多维固定效应（如 行业×年份）
reghdfe y x ctrl1 ctrl2, absorb(id year#industry) vce(cluster id)

* 动态面板（滞后因变量，GMM）
xtabond2 y L.y x ctrl1 ctrl2 i.year, gmm(L.y, lag(2 4)) iv(i.year) ///
        robust two
estat abond          // AR(2) 应不显著
estat sargan         // 过度识别应不显著
```

---

## 9. Tier2 · 双重机器学习（DML）与因果森林

```python
# ---------- 9.1 DML（Python / econml） ----------
from econml.dml import CausalForestDML, LinearDML
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import numpy as np, pandas as pd

df = pd.read_stata("panel.dta")
Y = df["y"].values
T = df["x"].values
X = df[[c for c in df.columns if c.startswith("ctrl")]].values
W = pd.get_dummies(df[["id", "year"]], drop_first=True).values  # 固定效应

est = LinearDML(
    model_y=GradientBoostingRegressor(random_state=0),
    model_t=GradientBoostingRegressor(random_state=0),
    discrete_treatment=False, cv=5, random_state=0)
est.fit(Y, T, X=X, W=W)
theta = est.ate(X)
ci = est.ate_interval(X, alpha=0.05)
print(f"ATE = {theta:.4f}, 95% CI = [{ci[0]:.4f}, {ci[1]:.4f}]")

# ---------- 9.2 因果森林（CATE） ----------
from econml.dml import CausalForestDML
cf = CausalForestDML(
    model_y=RandomForestRegressor(random_state=0),
    model_t=RandomForestRegressor(random_state=0),
    n_estimators=2000, min_samples_leaf=25,
    max_depth=None, honest=True, cv=5, random_state=0)
cf.fit(Y, T, X=X, W=W)
cate = cf.const_marginal_effect(X)

import matplotlib.pyplot as plt
plt.figure(figsize=(8, 4))
plt.hist(cate, bins=40, color="#4C72B0", edgecolor="white")
plt.xlabel("CATE"); plt.ylabel("频数")
plt.title("异质性处理效应分布")
plt.tight_layout(); plt.savefig("figures/fig_cate.png", dpi=200)

# 变量重要性
imp = cf.feature_importances(max_depth=4)
```

**必报**：交叉拟合折数敏感性（cv=3/5/10）、不同学习器对照（Lasso / RF / GBDT）、正交性检验、样本分割稳定性。

---

## 10. 通用图形规范（Matplotlib）

```python
import matplotlib.pyplot as plt
plt.rcParams.update({
    "font.sans-serif": ["SimHei", "Microsoft YaHei", "Arial Unicode MS"],  # 中文
    "axes.unicode_minus": False,
    "figure.dpi": 200, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10,
})

# 事件研究图
def event_plot(betas, ci_lo, ci_hi, periods, title="动态效应"):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.errorbar(periods, betas,
                yerr=[np.array(betas) - np.array(ci_lo), np.array(ci_hi) - np.array(betas)],
                fmt="o", color="#C44E52", ecolor="#C44E52", elinewidth=1.2, capsize=3, ms=4)
    ax.axhline(0, color="grey", ls="--", lw=1)
    ax.axvline(-0.5, color="grey", ls=":", lw=1)
    ax.set_xlabel("相对处理期的期数"); ax.set_ylabel("估计系数")
    ax.set_title(title)
    fig.tight_layout(); fig.savefig("figures/fig_event.png")
```

图片占位符统一写作 `![图X：标题](figures/fig_xxx.png)`，并在图注中注明数据来源与样本区间。
