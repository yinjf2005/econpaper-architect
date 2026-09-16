#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EconPaper Architect · 决策引擎
--------------------------------
按《经济论文撰写指引》§3.6 六层决策树 + §4.3/§4.4 逻辑适配矩阵，
把研究条件翻译为：模型推荐 / 不适配模型 / 替代方案 / 依据节号 / 逻辑方式 / 稳健性清单 / 代码入口。

用法:
  python decide.py --goal 因果效应 --identification 外生政策冲击 --data 面板数据 --target ATE --assumption 平行趋势
  python decide.py --goal 异质性处理效应 --data 高维协变量 --target CATE
  python decide.py --list                 # 列出所有合法取值

说明: 本脚本只做规则裁决并给出"推荐项"，最终选择权在用户（手册 §三 C 类决策）。
"""
import sys
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 规则表

# 决策层 1：研究目标 → 模型家族（指引 §3.6 决策层 1）
L1 = {
    "因果效应": dict(
        fit="RCT / 自然实验 / DID / IV / RDD / PSM / SCM",
        unfit="纯理论模型、DSGE",
        why="不直接识别因果",
        alt="先做识别策略，再谈估计",
        family="因果识别家族",
    ),
    "结构参数": dict(
        fit="BLP / 动态离散选择 / CGE / DSGE / 机制设计",
        unfit="简约式 DID / IV",
        why="无法估计弹性、福利与一般均衡效应",
        alt="结构模型",
        family="结构模型家族",
    ),
    "反事实": dict(
        fit="BLP / 动态离散选择 / CGE / DSGE / 机制设计",
        unfit="简约式 DID / IV",
        why="反事实需要结构不变参数",
        alt="结构模型",
        family="结构模型家族",
    ),
    "动态路径": dict(
        fit="VAR / SVAR / BVAR / 局部投影 / DSGE",
        unfit="横截面 PSM",
        why="无时间维度",
        alt="时间序列 / 面板方法",
        family="时间序列与面板家族",
    ),
    "异质性处理效应": dict(
        fit="因果森林 / 元学习器 / DML",
        unfit="传统 TWFE DID",
        why="只给平均效应",
        alt="CS/SA 交叠 DID 稳健估计 + 因果森林",
        family="机器学习与因果推断交叉家族",
    ),
    "复杂系统涌现": dict(
        fit="ABM / 系统动力学",
        unfit="代表性主体 DSGE",
        why="无法捕捉异质性互动与涌现",
        alt="ABM",
        family="仿真与计算家族",
    ),
    "制度设计": dict(
        fit="机制设计 / 博弈论",
        unfit="简约式回归",
        why="无激励相容约束",
        alt="机制设计",
        family="结构模型家族（机制设计）",
    ),
}

# 决策层 2：识别来源 → 具体模型（指引 §3.6 决策层 2）
L2 = {
    "随机化": dict(fit="RCT", unfit="DID / IV / PSM", why="随机化更干净", alt="RCT 不可行时再用 DID/IV"),
    "外生政策冲击": dict(fit="DID / 自然实验 / 事件研究", unfit="PSM", why="不可观测混杂",
                   alt="DID + PSM 辅助；交错处理用 CS/SA/DCDH/BJS"),
    "阈值": dict(fit="RDD", unfit="DID", why="无断点", alt="IV、RDD（模糊断点用 Fuzzy RDD）"),
    "工具变量": dict(fit="IV / 2SLS", unfit="PSM", why="内生性未解决", alt="有效工具时用 IV，弱工具改 LIML/AR"),
    "可观测选择": dict(fit="PSM / DR / DML", unfit="传统 OLS", why="选择偏误", alt="叠加 DID / IV"),
    "单一处理单位": dict(fit="SCM / 合成 DID", unfit="传统 DID", why="平行趋势不可信",
                    alt="SCM / 合成 DID / 贝叶斯 SCM"),
    "均衡条件": dict(fit="结构模型（BLP / DSGE / CGE）", unfit="简约式", why="无均衡约束", alt="BLP / DSGE / CGE"),
}

# 决策层 3：数据条件 → 模型修正（指引 §3.6 决策层 3）
L3 = {
    "高维协变量": dict(fit="DML / 因果森林", unfit="传统 OLS", why="过拟合与正则化偏差", alt="DML"),
    "面板数据": dict(fit="固定效应 / DID / 动态离散选择", unfit="横截面 PSM", why="忽略个体异质性",
                   alt="固定效应 / 交叠 DID"),
    "时间序列": dict(fit="VAR / DSGE / 局部投影", unfit="横截面 RCT", why="无时间动态", alt="VAR / 局部投影"),
    "聚合市场份额": dict(fit="BLP", unfit="微观离散选择", why="无个体层面数据", alt="BLP"),
    "SAM/IO表": dict(fit="CGE", unfit="简约式", why="无部门关联", alt="CGE"),
    "单一处理单位数据": dict(fit="SCM / 合成 DID", unfit="传统 DID", why="无对照组", alt="SCM / 合成 DID"),
    "实验数据": dict(fit="RCT / 饱和设计 / 聚类随机", unfit="观测性匹配", why="可直接随机化", alt="RCT"),
    "网络数据": dict(fit="网络计量 / ABM", unfit="独立同分布假设下的 OLS", why="存在干扰与溢出", alt="网络 RCT / ABM"),
}

# 决策层 4：推断目标 → 模型确认（指引 §3.6 决策层 4）
L4 = {
    "ATE": dict(fit="RCT / DID / IV / RDD / PSM / SCM", unfit="因果森林", why="平均效应即可", alt="传统识别策略"),
    "ATT": dict(fit="RCT / DID / IV / RDD / PSM / SCM", unfit="因果森林", why="平均处理效应即可", alt="传统识别策略"),
    "CATE": dict(fit="因果森林 / 元学习器 / DML", unfit="传统 TWFE", why="只给平均效应", alt="因果森林 / DML"),
    "结构参数目标": dict(fit="BLP / 动态离散选择 / DSGE / CGE", unfit="DID / IV", why="无结构解释", alt="结构模型"),
    "脉冲响应": dict(fit="VAR / SVAR / BVAR / DSGE / 局部投影", unfit="横截面方法", why="无动态", alt="VAR / 局部投影"),
    "福利变化": dict(fit="BLP / CGE / DSGE / 机制设计", unfit="简约式", why="无福利基础", alt="结构模型"),
    "涌现现象": dict(fit="ABM / 系统动力学", unfit="代表性主体模型", why="无法涌现", alt="ABM"),
}

# 决策层 5：关键假设检验（指引 §3.6 决策层 5）
L5 = {
    "SUTVA": dict(fit="RCT", unfit="有溢出效应的 RCT", alt="饱和设计 / 聚类随机 / ABM"),
    "平行趋势": dict(fit="传统 DID", unfit="交错异质下的 TWFE", alt="CS / SA / DCDH / BJS / 合成 DID"),
    "排他性": dict(fit="IV", unfit="排他性不成立时的 IV", alt="RDD / DID / 结构模型"),
    "连续性": dict(fit="RDD", unfit="可操纵断点的 RDD", alt="甜甜圈 RDD / IV / DID"),
    "CIA": dict(fit="PSM / DR", unfit="不可观测混杂下的 PSM", alt="IV / DID / RDD / DML"),
    "无干扰": dict(fit="SCM", unfit="donor 受共同冲击的 SCM", alt="合成 DID / 贝叶斯 SCM"),
    "均衡": dict(fit="结构模型", unfit="非均衡 / 危机情形", alt="ABM / 简约式"),
    "理性预期": dict(fit="DSGE", unfit="危机与强异质性情形", alt="ABM / 含金融摩擦的 DSGE"),
}

# 决策层 6：主模型 → 必须报告的稳健性（指引 §3.6 决策层 6）
L6 = {
    "传统TWFE DID": ["Bacon 分解", "平行趋势检验", "CS/SA 稳健估计", "预期效应检验", "安慰剂检验"],
    "交叠DID": ["CS (Callaway & Sant'Anna)", "SA (Sun & Abraham)", "Bacon 分解", "BJS 插补估计", "事件研究图"],
    "IV": ["弱工具检验（有效 F）", "AR 置信集", "过度识别检验", "第一阶段图形", "排除约束讨论"],
    "RDD": ["McCrary 密度检验", "带宽敏感性", "协变量平衡", "甜甜圈 RDD", "伪断点检验"],
    "PSM": ["平衡性检验", "共同支撑", "多种匹配算法对比", "敏感性分析", "必要时改 IV/DID"],
    "SCM": ["placebo test（in-time / in-space）", "RMSPE 比", "donor 稳健性", "leave-one-out", "改用合成 DID"],
    "事件研究": ["预期效应检验", "动态效应图", "异质性稳健估计量", "对照组污染检验"],
    "面板固定效应": ["聚类层级稳健性", "滞后项设定", "工具变量法对照", "随机效应对照"],
    "DSGE": ["先验敏感性", "MCMC 收敛诊断", "脉冲响应稳健性", "边缘数据密度比较", "危机时改 ABM"],
    "VAR": ["滞后阶数选择", "识别约束稳健性", "bootstrap 置信区间", "SVAR 对照"],
    "ABM": ["随机种子敏感性", "参数扫描", "历史矩匹配", "与解析模型对照"],
    "BLP": ["工具变量有效性", "份额与价格内生性", "嵌套结构对照", "弹性合理性"],
    "DML": ["交叉拟合折数敏感性", "不同机器学习器对照", "正交性检验", "样本分割稳定性"],
    "因果森林": ["honest splitting", "变量重要性稳定性", "与 DML 结果对照", "子样本稳定性"],
}

# 模型画像：逻辑方式 / 样态 / 诊断 / 代码 / 图表（指引 §4.3 + 手册 §六 6.3）
PROFILE = {
    "交叠DID": dict(logic="归纳", form="树", aux="网", chain="数据→异质性划分→子样本效应→分支比较→交叉验证→总体结论",
                stata="csdid / eventstudyinteract / reghdfe", py="linearmodels + 自写事件研究",
                fig="事件研究图 + Bacon 分解图"),
    "传统TWFE DID": dict(logic="归纳", form="链", aux="—", chain="数据→平行趋势→双重差分→ATT→稳健性",
                    stata="reghdfe / xtreg", py="linearmodels", fig="平行趋势图 + 事件研究图"),
    "IV": dict(logic="归纳", form="链", aux="网", chain="相关性→排他性→2SLS→稳健性",
               stata="ivreg2 / ivreghdfe", py="linearmodels.IV2SLS", fig="第一阶段散点 + 折线图"),
    "RDD": dict(logic="归纳", form="链", aux="树", chain="断点两侧局部比较→带宽选择→局部效应→稳健性",
                stata="rdrobust / rddensity", py="rdrobust 移植 / 局部线性回归", fig="断点回归图 + McCrary 密度图"),
    "PSM": dict(logic="归纳", form="链", aux="网", chain="匹配→平衡→效应估计→多种算法交叉",
                stata="psmatch2 / teffects psmatch", py="sklearn + causalinference", fig="倾向得分分布图 + 协变量平衡图"),
    "SCM": dict(logic="溯因", form="链+树", aux="网", chain="现象→候选合成对照→排除竞争解释→最佳解释",
                stata="synth / allsynth", py="SyntheticControlMethods", fig="合成控制图 + placebo 图"),
    "事件研究": dict(logic="归纳", form="链+树", aux="网", chain="事件前后动态效应→异质性分支→交叉验证",
                 stata="eventstudyinteract / reghdfe + 交互项", py="linearmodels", fig="事件研究动态效应图"),
    "面板固定效应": dict(logic="归纳", form="链", aux="—", chain="个体异质性控制→估计→稳健性",
                   stata="reghdfe / xtreg fe", py="linearmodels.PanelOLS", fig="时间趋势图"),
    "BLP": dict(logic="演绎", form="树", aux="网、场", chain="假设→随机系数Logit→需求弹性→均衡价格→反事实",
                stata="—（多用 MATLAB/R）", py="pyblp", fig="需求弹性热力图"),
    "DSGE": dict(logic="演绎", form="环+树", aux="螺旋、场", chain="假设→动态模型→欧拉方程→稳态与转移动态→脉冲响应",
                 stata="—（Dynare/MATLAB）", py="dolo / Dynare", fig="脉冲响应图"),
    "CGE": dict(logic="演绎", form="树+环", aux="网、场", chain="假设→SAM校准→部门均衡→政策冲击→福利",
                stata="—（GAMS/GEMPACK）", py="—", fig="部门影响条形图"),
    "ABM": dict(logic="溯因+演绎", form="环", aux="网、螺旋、场", chain="现象→反馈机制→涌现→校准-模拟-验证→参数扫描",
                stata="—", py="mesa / NetLogo", fig="涌现现象图 + 参数扫描图"),
    "DML": dict(logic="归纳", form="链", aux="网", chain="正交化→交叉拟合→因果效应→多学习器对照",
                stata="—", py="econml / DoubleML", fig="系数对比图"),
    "因果森林": dict(logic="归纳", form="树", aux="场", chain="数据→递归划分→CATE→效应场",
                 stata="—", py="econml.CausalForestDML", fig="CATE 分布图 + 变量重要性图"),
    "VAR": dict(logic="归纳+演绎", form="环", aux="网、场", chain="数据→动态关系→反馈识别→脉冲响应→结构解释",
                stata="var / svar / varbasic", py="statsmodels.tsa.VAR", fig="脉冲响应图"),
    "RCT": dict(logic="归纳", form="链", aux="—", chain="随机化→效应估计→异质性→稳健性",
                stata="reg / randomize", py="statsmodels", fig="组间均值对比图"),
}

# 由条件组合推断最终模型的优先级规则
FALLBACK_MODEL = {
    "因果识别家族": "交叠DID",
    "结构模型家族": "结构模型（按目标选 BLP/DSGE/CGE）",
    "结构模型家族（机制设计）": "机制设计",
    "时间序列与面板家族": "VAR / 局部投影",
    "机器学习与因果推断交叉家族": "DML / 因果森林",
    "仿真与计算家族": "ABM",
}

ASSUMPTION_FIX = {
    "平行趋势": "交叠DID",
    "SUTVA": "RCT（改饱和设计或聚类随机）",
    "排他性": "RDD / 结构模型",
    "连续性": "甜甜圈RDD",
    "CIA": "DML / IV",
    "无干扰": "合成DID",
    "均衡": "ABM",
    "理性预期": "含金融摩擦的 DSGE",
}


def norm(table, value, label):
    if value in table:
        return value
    for k in table:
        if value and (value in k or k in value):
            return k
    return None


def emit(title, rows):
    print(f"\n【{title}】")
    if not rows:
        print("  （未提供该项条件，已跳过）")
        return
    for k, v in rows:
        print(f"  · {k}: {v}")


def main():
    ap = argparse.ArgumentParser(description="EconPaper Architect 决策引擎")
    ap.add_argument("--goal", help="研究目标：" + " / ".join(L1))
    ap.add_argument("--identification", help="识别来源：" + " / ".join(L2))
    ap.add_argument("--data", help="数据条件：" + " / ".join(L3))
    ap.add_argument("--target", help="推断目标：" + " / ".join(L4))
    ap.add_argument("--assumption", help="关键假设：" + " / ".join(L5))
    ap.add_argument("--model", help="（可选）指定主模型以直接取稳健性清单与画像")
    ap.add_argument("--list", action="store_true", help="列出所有合法取值")
    a = ap.parse_args()

    if a.list:
        print("研究目标(L1):", " / ".join(L1))
        print("识别来源(L2):", " / ".join(L2))
        print("数据条件(L3):", " / ".join(L3))
        print("推断目标(L4):", " / ".join(L4))
        print("关键假设(L5):", " / ".join(L5))
        print("主模型(L6):", " / ".join(L6))
        return 0

    if not any([a.goal, a.identification, a.data, a.target, a.assumption, a.model]):
        ap.error("至少提供一个条件，或用 --list 查看合法取值")

    print("=" * 68)
    print("EconPaper Architect · 决策引擎裁决结果（推荐项，须用户确认）")
    print("=" * 68)

    family = None
    g = norm(L1, a.goal, "goal") if a.goal else None
    if g:
        r = L1[g]
        family = r["family"]
        emit(f"决策层1 研究目标 → 模型家族（依据指引 §3.6 决策层1，输入：{a.goal}）",
             [("适配", r["fit"]), ("不适配", r["unfit"]), ("原因", r["why"]), ("替代", r["alt"]),
              ("→ 模型家族", r["family"])])
    else:
        print("\n【决策层1】未提供研究目标，模型家族待定。")

    if a.identification:
        k = norm(L2, a.identification, "id")
        if k:
            r = L2[k]
            emit(f"决策层2 识别来源 → 具体模型（依据 §3.6 决策层2，输入：{a.identification}）",
                 [("适配", r["fit"]), ("不适配", r["unfit"]), ("原因", r["why"]), ("替代", r["alt"])])

    if a.data:
        k = norm(L3, a.data, "data")
        if k:
            r = L3[k]
            emit(f"决策层3 数据条件 → 模型修正（依据 §3.6 决策层3，输入：{a.data}）",
                 [("适配", r["fit"]), ("不适配", r["unfit"]), ("原因", r["why"]), ("替代", r["alt"])])

    if a.target:
        k = norm(L4, a.target, "target")
        if k:
            r = L4[k]
            emit(f"决策层4 推断目标 → 模型确认（依据 §3.6 决策层4，输入：{a.target}）",
                 [("适配", r["fit"]), ("不适配", r["unfit"]), ("原因", r["why"]), ("替代", r["alt"])])

    if a.assumption:
        k = norm(L5, a.assumption, "assumption")
        if k:
            r = L5[k]
            emit(f"决策层5 关键假设检验（依据 §3.6 决策层5，输入：{a.assumption}）",
                 [("成立时", r["fit"]), ("不成立时不适配", r["unfit"]), ("替代方案", r["alt"])])

    # 综合推荐主模型
    model = a.model
    if not model and a.assumption and norm(L5, a.assumption, "a"):
        model = ASSUMPTION_FIX.get(norm(L5, a.assumption, "a"))
    if not model and a.identification:
        k = norm(L2, a.identification, "id")
        mapping = {"外生政策冲击": "交叠DID", "随机化": "RCT", "阈值": "RDD", "工具变量": "IV",
                   "可观测选择": "PSM", "单一/少数处理单位": "SCM", "均衡条件": "BLP/DSGE/CGE"}
        model = mapping.get(k)
    if not model and family:
        model = FALLBACK_MODEL.get(family)

    if model:
        key = None
        for k in PROFILE:
            if k in model or model in k:
                key = k
                break
        print("\n" + "=" * 68)
        print(f"◆ 综合推荐主模型：{model}")
        if key:
            p = PROFILE[key]
            print(f"  · 逻辑方式：{p['logic']} + {p['form']}（辅助样态：{p['aux']}）  —— 依据指引 §4.3")
            print(f"  · 章节叙事链：{p['chain']}  —— 依据指引 §4.5.2")
            print(f"  · Stata 入口：{p['stata']}")
            print(f"  · Python 入口：{p['py']}")
            print(f"  · 推荐图表：{p['fig']}  —— 依据手册 §6.3")
        rob = L6.get(key) if key else None
        if rob:
            print("  · 必须报告的稳健性（依据 §3.6 决策层6）：")
            for i, x in enumerate(rob, 1):
                print(f"      {i}. {x}")
        if a.assumption and norm(L5, a.assumption, "a"):
            print(f"  · ⚠ 关键假设「{a.assumption}」若不成立，替代方案：{L5[norm(L5, a.assumption, 'a')]['alt']}")

    print("\n" + "=" * 68)
    print("依据格式：依据指引 §3.6 决策层X / §4.3，因[上述条件]，选择[综合推荐主模型]，替代方案见各层『替代』。")
    print("本结果为推荐项，按手册 §三 属 C 类决策，须用户确认后方可写入决策汇总卡。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
