# 外部 Skill 集成映射与降级细则

> 对应手册第八部分（Skill 1–Skill 10）。策略：**自包含优先 + 机会主义外挂**——内核能力全部内置，外部 skill 有则优先调用，缺失即降级，绝不因外部依赖缺失而中断流程。
> 匹配依据：本机已安装 skill 实际盘点（2026-09-17）；SkillHub 远程检索对 latex / bibliography / stata / econometrics / literature review 等查询均返回同一组低分结果（score<0.05），判定**远程无可用候选**，故外部依赖只在已装 skill 中选取。

## 一、必须参与（手册 §8.1）

| 手册编号 | 需求 | 本机实现 | 外部外挂（有则用） | 降级方案 |
|---|---|---|---|---|
| Skill 1 | 结构化对话管理 | `scripts/state.py`（S0–S9 + D-1~D-10 + 决策日志 + 跳步校验） | — | 脚本即实现，无外部依赖 |
| Skill 2 | 决策树/规则引擎 | `scripts/decide.py`（六层决策 + 模型画像 + 稳健性清单） | — | 条件不足时返回"需补充信息"，不臆断 |
| Skill 3 | 文档生成 | SKILL.md §五生成规则 + `assets/paper_template.md` | `academic-paper`（成稿流水线）、`office-doc-suite`（docx） | 直接输出 Markdown+LaTeX |
| Skill 4 | 公式渲染 | 内置 LaTeX 规范（SKILL.md §二-9） | — | 语法自检：检查 `$` 配对、`\begin/\end` 配对、非法命令 |

## 二、建议参与（手册 §8.2）

| 手册编号 | 需求 | 外部外挂 | 降级方案 |
|---|---|---|---|
| Skill 5 | 数据可视化 | `huashu-design`、`frontend-design`（交互式图表） | `references/10-code-templates.md` §10 的 Matplotlib 规范 + `figures/` 目录 |
| Skill 6 | 文献检索/引用管理 | `systematic-literature-review`（多文献综述，输出 BibTeX）、`defuddle`（抓取文献页正文）、ima 知识库（`ima-skill`，用户自建文献库） | 按 SKILL.md §二-6 三档制推荐并标 `⚠️AI推荐·须核验`；不得直接进参考文献表 |
| Skill 7 | 表格生成 | `excel-generation` / `excel-handler`（若需 Excel 侧表） | 三线表模板（手册 §6.2）+ `esttab` 输出 |

## 三、可选参与（手册 §8.3）

| 手册编号 | 需求 | 外部外挂 | 降级方案 |
|---|---|---|---|
| Skill 8 | 代码生成/执行 | **无**（本机无任何 Stata/R 计量 skill） | `references/10-code-templates.md` 取模板；生成代码 + 运行说明，**严禁臆造运行结果** |
| Skill 9 | 排版美化 | `office-doc-suite`（docx）、`tencent-docx/doc-typeset`（**含 academic-paper 排版模板与主题**）、`pdf` | `assets/paper.tex` LaTeX 模板 + 提示用户自行编译 |
| Skill 10 | 多轮迭代管理 | — | `state.json` 的 log/notes 字段记录版本与修改；`scripts/check.py` 每次迭代重跑 |

## 四、边界声明（防误触发）

| 场景 | 走哪个 skill |
|---|---|
| 期刊向经济学学术论文：识别策略、模型选择、逻辑方式、计量代码 | **本 skill** |
| 行业 / 市场 / 投资 / 政策研报 | `research-report-standard` |
| 已有稿件只需润色、降重、引文一致性校验、格式转换 | `academic-paper` |
| 单篇文献的评审意见 | `academic-paper-review` |
| 系统性文献综述（跨多篇论文） | `systematic-literature-review` |
| 人文类论文（历史/哲学/文学） | `humanities-writing-companion` |

## 五、调用纪律

1. 每次调用外部 skill 前先确认其存在；不存在则**静默走降级列**，不向用户抱怨缺失。
2. 外挂产出的文献、数据、结果，同样受 SKILL.md §二-6（文献三档制）与 §二-7（模拟数据授权）约束。
3. 外部 skill 的输出若与本 skill 的决策卡冲突，以**用户确认过的决策卡**为准。
4. 安装任何新 skill 前，须按全局规则执行安全扫描（`skill-security-scan`），P0 强警告 + 同意才装。
