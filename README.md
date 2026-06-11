# 三视股票分析（Triview Stock Analysis）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![GitHub](https://img.shields.io/badge/GitHub-mybladethirsts-181717?logo=github)](https://github.com/mybladethirsts)

**三维独立评分 · 行业自适应 · 加权共识 · A股/港股/美股**

Triview（三视）从三个完全独立的视角分析同一只股票，不偏科于任何行业。第一维（标的质地）会根据行业自动路由到最合适的评分分支——制造业走供应链卡位，消费走品牌护城河，金融走网络+监管壁垒，医疗走管线+专利，平台走网络效应，能源走资源禀赋。

---

## 为什么是"三维"？

- **好的基本面 ≠ 可以买。** 宏观逆风下再好的公司也会跌。
- **宏观顺风 ≠ 马上进场。** 技术面告诉你的是入场时机。
- **技术走好 ≠ 基本面支持。** 没基本面支撑的趋势只是噪音。

**Triview 三视强迫你从三个角度回答同一个问题：这票现在能不能碰？**

---

## 三维框架

| 视角 | 权重 | 核心问题 | 行业自适应 |
|:----:|:----:|----------|:----------:|
| 🏛️ **标的质地** | 40% | 这是一个好生意吗？ | ✅ 全行业自动路由 |
| 🌊 **宏观轮动** | 30% | 现在的风往哪吹？ | ✅ |
| 📈 **技术趋势** | 30% | 图形和数据告诉你什么？ | ✅ |

### 标的质地 — 行业自适应评分

| 分支 | 适用行业 | 评分模型 |
|:----|:--------|:---------|
| 🏭 **供应链卡位** | 制造业/科技/硬件 | 六步量化法：链命中→壁垒→证据→弹性→财务→拐点 |
| 🏪 **品牌护城河** | 消费/品牌/零售 | 品牌力量→规模渠道→增长复购→财务→防御 |
| 🏦 **网络+监管壁垒** | 金融/保险 | 网络规模→盈利→增长→资本充足→股息 |
| 🧬 **管线+专利壁垒** | 医疗/生物 | R&D强度→毛利率→管线成长→财务稳定→规模背书 |
| 🌐 **网络效应+数据** | 平台/互联网 | 网络效应→盈利模式→增长动能→现金流→护城河 |
| 🪨 **资源禀赋** | 能源/大宗商品 | 储备规模→成本曲线→现金流→低资本密集→股息 |
| 📊 **通用评分** | 兜底/未知行业 | 盈利质量→增长→规模→现金流→防御性 |

---

## 安装

### 方法 1: OpenClaw
```bash
openclaw skill install sanhu-stock-analysis
```

### 方法 2: 手动
```bash
cp -r sanhu-stock-analysis ~/.qclaw/skills/
```

---

## 快速使用

```bash
# 分析 NVDA
python3 ~/.qclaw/skills/sanhu-stock-analysis/scripts/analyze.py NVDA

# A 股茅台
python3 scripts/analyze.py 600519.SS --market a-share

# 港股腾讯
python3 scripts/analyze.py 0700.HK

# JSON 格式
python3 scripts/analyze.py NVDA --json

# 指定宏观象限
python3 scripts/analyze.py NVDA --macro "宽松中期"
```

### 依赖
```bash
pip install yfinance
```

---

## 共识信号

| 条件 | 信号 | 意义 |
|:----|:----:|:----|
| 两维看多 + 总分 ≥ 80 | 🟢 强烈看多 | 三维共振，值得重仓 |
| 两维看多 + 总分 ≥ 65 | 🟢 看多 | 多数视角一致，考虑建仓 |
| 中性分歧 | 🟡 中性 | 有争议需验证，减仓或观望 |
| 两维看空 | 🔴 看空 | 多数视角不利，回避 |
| 关键维度 < 30 | 🔴 警告 | 不做多 |

---

## 自检门禁

每次输出前自动运行 16 项检查：
- **数据完整性**(4项)：公司名、行业、市值、基本面
- **内容质量**(4项)：证据等级、链判定、因子支撑、信号明确度
- **一致性**(4项)：三维方向是否矛盾、行业路由合理性
- **安全**(4项)：免责声明、流动性、政策风险、数据时效

---

## 方法论来源

本技能吸收了以下开源项目的设计理念：

- **UZI-Skill (github.com/wbh604)** — 独立评委→加权共识的架构理念；机械自检门禁的设计思路
- **Serenity / TraderS** — 供应链卡位分析方法论；宏观六象限分类法
- **multi-market-stock-analysis** — 本技能前身，三视角综合框架和参考文档

所有代码为**自主实现**，无直接代码复制。

---

## 文件结构

```
sanhu-stock-analysis/
├── SKILL.md              # 技能定义
├── README.md             # 本文
├── references/
│   ├── bottleneck_methodology.md  # 供应链卡位六步法
│   ├── moat_analysis.md           # 护城河类型分析
│   ├── macro_indicators.md        # 宏观指标手册
│   ├── technical_playbook.md      # 技术执行手册
│   ├── cross_market_comparison.md # 跨市场对比
│   ├── market_specific_risks.md   # 市场风险
│   └── self_review_gate.md        # 自检门禁
├── scripts/analyze.py   # 主入口
├── scripts/fetch_*.py   # 数据获取脚本
└── lib/
    ├── __init__.py       # 核心类型 & 常量
    ├── features.py       # 特征提取
    ├── scorer.py         # 三维评分引擎
    ├── consensus.py      # 共识合成
    ├── self_review.py    # 自检门禁
    └── report.py         # 报告生成
```

---

## 免责声明

⚠️ **非投资建议。** 本技能仅用于研究和教育目的。所有投资决策均附带风险。

⚠️ **始终自行核实关键数据点。** 评分基于公开财务数据和行业标签推断。

⚠️ **模型局限性：** 无法预测黑天鹅事件、突发政策变化、或情绪驱动的短期波动。

---

**📦 GitHub**: [github.com/mybladethirsts/triview-stock-analysis](https://github.com/mybladethirsts/triview-stock-analysis)
