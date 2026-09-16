#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EconPaper Architect · 论文硬校验
--------------------------------
扫描论文稿，输出硬阻断项（不通过不放行）与软提示项（提示但不阻断）。

硬阻断三条（用户确认的验收红线）：
  H1 存在未标注的模拟数据
  H2 正文引用与参考文献表不一一对应
  H3 实证类论文未论证识别假设

用法:
  python check.py <论文.md> [--bib references.bib] [--lang zh|en]
退出码: 0 = 无硬阻断；1 = 存在硬阻断（必须修复后才可进入下一阶段）
"""
import os
import re
import sys
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SIM_WORDS = ["模拟数据", "模拟生成", "虚构数据", "示例结果", "占位数据", "simulated data", "synthetic data",
             "placeholder data", "mock data"]
SIM_TAG = "[SIM]"
AI_LIT_TAG = "⚠️AI推荐·须核验"
TODO_TAGS = ["示例结果，需用户替换", "简化框架，建议用户扩展", "需用户核实"]

IDENT_WORDS = ["识别假设", "识别策略", "平行趋势", "排他性", "外生性", "连续性", "不可操纵", "共同支撑",
               "条件独立", "SUTVA", "随机化", "identification assumption", "parallel trends",
               "exclusion restriction", "unconfoundedness", "exogeneity"]
EMPIRICAL_WORDS = ["双重差分", "DID", "工具变量", "IV", "断点回归", "RDD", "倾向得分", "PSM", "合成控制", "SCM",
                   "面板固定效应", "固定效应", "回归结果", "regression", "2SLS", "事件研究", "标准误",
                   "系数", "显著性"]
AI_TONE = ["综上所述", "值得注意的是", "不难看出", "显而易见", "众所周知", "在当今社会", "随着...的发展",
           "具有重要的意义", "it is worth noting", "in conclusion", "delve into", "tapestry"]
NORMATIVE = ["应该大幅", "必须立即", "毫无疑问是最好的", "显然优于"]

CITE_PATTERNS = [
    re.compile(r"\\cite[a-zA-Z]*\{([^}]+)\}"),          # \citep{key1,key2}
    re.compile(r"\[@([A-Za-z0-9_\-:]+)"),                # pandoc [@key]
    re.compile(r"\\bibitem\{([^}]+)\}", re.S),           # \bibitem{key}（归入参考文献侧）
]
REF_HEAD = re.compile(r"^#{1,3}\s*(参考文献|References|Bibliography)\s*$", re.M | re.I)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def split_body_and_refs(text):
    m = REF_HEAD.search(text)
    if not m:
        return text, ""
    return text[:m.start()], text[m.start():]


def collect_citations(body):
    keys = set()
    for pat in CITE_PATTERNS[:2]:
        for m in pat.finditer(body):
            for k in m.group(1).split(","):
                k = k.strip()
                if k:
                    keys.add(k)
    # 中文著者-年份式引用（如：张三（2020））只做计数，不做键匹配
    cn_year = re.findall(r"[一-龥A-Za-z]+\s*[（(]\s*(19|20)\d{2}\s*[）)]", body)
    return keys, len(cn_year)


def collect_ref_keys(refs_text, bib_path):
    keys = set()
    for m in CITE_PATTERNS[2].finditer(refs_text):
        keys.add(m.group(1).strip())
    for m in re.finditer(r"@\w+\{([^,]+),", refs_text):
        keys.add(m.group(1).strip())
    if bib_path and os.path.exists(bib_path):
        keys |= set(m.group(1).strip() for m in re.finditer(r"@\w+\{([^,]+),", read(bib_path)))
    return keys


def main():
    ap = argparse.ArgumentParser(description="EconPaper Architect 论文硬校验")
    ap.add_argument("file")
    ap.add_argument("--bib", default=None, help="BibTeX 路径（默认取同目录 references.bib）")
    ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    a = ap.parse_args()

    if not os.path.exists(a.file):
        print(f"✘ 文件不存在：{a.file}")
        return 1
    text = read(a.file)
    body, refs = split_body_and_refs(text)
    bib = a.bib or os.path.join(os.path.dirname(os.path.abspath(a.file)), "references.bib")

    hard, soft = [], []

    # ---------------- H1 模拟数据标注 ----------------
    lines = text.split("\n")
    for i, ln in enumerate(lines, 1):
        for w in SIM_WORDS:
            if w in ln and SIM_TAG not in ln:
                # 允许前 3 行内出现 [SIM] 声明
                ctx = "\n".join(lines[max(0, i - 4):i])
                if SIM_TAG not in ctx:
                    hard.append(f"H1 第{i}行出现「{w}」但缺少 [SIM] 标记：{ln.strip()[:60]}")
                break
    if SIM_TAG in text and "模拟数据" not in text and "simulated" not in text.lower():
        soft.append("存在 [SIM] 标记，但未给出模拟数据说明文字，建议补一句“本节数据为模拟数据，仅供格式演示”。")

    # ---------------- H2 引用一致性 ----------------
    cites, cn_year_n = collect_citations(body)
    ref_keys = collect_ref_keys(refs, bib)
    if cites or ref_keys:
        missing = sorted(cites - ref_keys)
        unused = sorted(ref_keys - cites)
        if missing:
            hard.append(f"H2 正文引用了但参考文献表中缺失（{len(missing)} 项）：{', '.join(missing[:10])}"
                        + (" ..." if len(missing) > 10 else ""))
        if unused:
            soft.append(f"参考文献表中存在正文未引用的条目（{len(unused)} 项）：{', '.join(unused[:10])}")
    else:
        soft.append("未检出可机检的引用键（\\cite{} 或 [@key]）。若为 GB/T 7714 著者-年份制，"
                    f"正文检出 {cn_year_n} 处著者-年份引用，请人工核对与文末列表一一对应。")

    # ---------------- H3 识别假设论证 ----------------
    is_empirical = any(w in text for w in EMPIRICAL_WORDS)
    if is_empirical:
        if not any(w in text for w in IDENT_WORDS):
            hard.append("H3 判定为实证类论文，但全文未检出识别假设论证（平行趋势/排他性/外生性/连续性等）。"
                        "识别策略论证是审稿人最关注的部分，必须补充。")
    else:
        soft.append("未检出实证方法关键词，按理论/综述类处理，跳过 H3。")

    # ---------------- 软提示 ----------------
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    if title_m:
        t = title_m.group(1).strip()
        n = len(re.sub(r"\s", "", t))
        if a.lang == "zh" and n > 25:
            soft.append(f"标题 {n} 字（中文建议 ≤25 字）：{t}")
        if a.lang == "en" and len(t.split()) > 15:
            soft.append(f"标题 {len(t.split())} 词（英文建议 ≤15 词）：{t}")
    else:
        soft.append("未检出一级标题。")

    if "关键词" not in text and "Keywords" not in text:
        soft.append("缺少关键词。")

    abs_m = re.search(r"(摘要|Abstract)[^\n]*\n+(.{20,2000}?)\n", text)
    if abs_m:
        ab = abs_m.group(2)
        n = len(re.sub(r"\s", "", ab))
        if a.lang == "zh" and not (200 <= n <= 300):
            soft.append(f"摘要约 {n} 字（中文建议 200–300 字）。")
    else:
        soft.append("未检出摘要。")

    if "$" not in text and "\\begin{equation" not in text:
        soft.append("未检出公式（行内 $...$ 或 equation 环境）。")
    if "\\toprule" not in text and not re.search(r"^\|.*\|", text, re.M):
        soft.append("未检出三线表（booktabs \\toprule）或 Markdown 表格。")
    figs = re.findall(r"!\[([^\]]*)\]\(([^)]*)\)", text)
    if not figs:
        soft.append("未检出图片占位符，实证论文建议至少含事件研究图/系数图。")
    else:
        for alt, _ in figs:
            if not alt or len(alt) < 3:
                soft.append(f"图片占位符缺少规范标题：![] 建议写成 ![图X：标题](placeholder)")
                break
    if not re.search(r"[0-9]+\.?[0-9]*\s*(%|个百分点|个单位|个标准差)", text) and is_empirical:
        soft.append("结果部分未检出具量级的数字陈述（如“X 每增加 1 个标准差，Y 增加 0.15 个单位”）。")
    if is_empirical and "局限" not in text and "limitation" not in text.lower():
        soft.append("未检出研究局限陈述。")
    if is_empirical and "政策" not in text and "policy" not in text.lower():
        soft.append("未检出政策含义段落。")
    for w in AI_TONE:
        if w in text:
            soft.append(f"疑似 AI 腔/套话：「{w}」，建议删除或改写。")
            break
    for w in NORMATIVE:
        if w in text:
            soft.append(f"疑似规范性判断：「{w}」，AER 式风格要求避免 normative language。")
            break
    if AI_LIT_TAG in text:
        soft.append("存在 ⚠️AI推荐·须核验 的文献，终稿前必须逐条核验并转正，否则不得进入参考文献表。")
    for t in TODO_TAGS:
        if t in text:
            soft.append(f"存在待替换标记：「{t}」，终稿前须处理。")
    if "\\label{eq:" in text and not re.search(r"\\ref\{eq:|\\eqref\{eq:", text):
        soft.append("存在公式标签但正文未引用（\\eqref）。")

    # ---------------- 输出 ----------------
    print("=" * 68)
    print(f"EconPaper Architect · 论文校验报告  |  {os.path.basename(a.file)}")
    print("=" * 68)
    print(f"\n▍硬阻断项（{len(hard)}）—— 不通过不得进入下一阶段")
    if hard:
        for h in hard:
            print(f"  ✘ {h}")
    else:
        print("  ✔ 无。三条红线全部通过。")
    print(f"\n▍软提示项（{len(soft)}）—— 提示但不阻断")
    if soft:
        for s in soft:
            print(f"  · {s}")
    else:
        print("  ✔ 无。")
    print("\n" + "=" * 68)
    print("处理优先级（手册 §7.2）：内容错误 > 逻辑错误 > 结构问题 > 格式问题 > 语言问题")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
