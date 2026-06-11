# Triview — 三视股票分析

<p align="center">
  <b>三维独立评分 · 行业自适应 · 加权共识 · A股/港股/美股</b>
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue.svg">
</p>

---

**EN — Triview** is a multi-perspective equity research tool for A-share, HK, and US markets. It analyzes every stock from **three independent lenses** — Business Quality, Macro Rotation, and Technical Trend — then weights them into a single consensus verdict.

What sets Triview apart: the Business Quality lens is **industry-adaptive**. It automatically routes each stock to the right scoring model:
- **Manufacturing/Tech** → Supply chain bottleneck analysis (6-step quantification: signals → financials → verification → valuation → confirmation → alpha score)
- **Consumer/Brand** → Brand moat + pricing power + distribution
- **Financial/Insurance** → Network effects + regulatory moat
- **Healthcare/Biotech** → Pipeline value + patent barriers
- **Platform/Internet** → Network effects + data moat
- **Energy/Commodity** → Resource endowment + cost curve position
- **Everything else** → Generic quality scoring (fallback)

Every analysis passes through a **16-item mechanical self-review gate** before being released — no verdict leaves the engine with a critical hole.

**Built for:** individual investors who want structure without dogma, verification without vendor lock-in, and a framework they can internalize and use at any time.

---

**CN — Triview 三视** 是一套面向个人投资者的多视角股票分析工具，覆盖 A 股、港股、美股三大市场。

核心逻辑：每只股票从 **三个完全独立的视角** 来评估，再按权重合成结论。

第一维「标的质地」是 **行业自适应的**——系统识别行业后自动路由到最合适的评分分支：
- 制造业/科技 → 供应链卡位分析（六步量化）
- 消费/品牌 → 品牌护城河评估
- 金融/保险 → 网络+监管壁垒评分
- 医疗/生物 → 管线+专利价值评估
- 平台/互联网 → 网络效应+数据壁垒分析
- 能源/大宗 → 资源禀赋+成本曲线定位
- 其他行业 → 通用质量评分（兜底）

每一份分析结果必须通过 **16 项机械级自检门禁** 才能输出——不允许带着漏洞的结论出门。

**适合谁用：** 需要分析框架但不迷信单一方法论的个人投资者；想看第三方视角作为参考的研究者。

---

## Quick Start

```bash
pip install yfinance
git clone https://github.com/mybladethirsts/triview-stock-analysis.git
cd triview-stock-analysis

python3 scripts/analyze.py NVDA           # US stocks
python3 scripts/analyze.py 600519.SS --market a-share  # A-share
python3 scripts/analyze.py 0700.HK        # HK stocks
python3 scripts/analyze.py NVDA --json    # machine-readable
```

## File Structure

```
triview-stock-analysis/
├── SKILL.md                # Agent skill definition
├── README.md               # Full user manual
├── docs/introduction.md    # Design philosophy
├── references/             # Methodology deep-dives
│   ├── bottleneck_methodology.md
│   ├── moat_analysis.md
│   ├── macro_indicators.md
│   ├── technical_playbook.md
│   ├── cross_market_comparison.md
│   ├── market_specific_risks.md
│   └── self_review_gate.md
├── scripts/
│   ├── analyze.py          # Main entry point
│   ├── fetch_us_data.py
│   ├── fetch_hk_data.py
│   └── fetch_ashare_data.py
└── lib/                    # Core engine (self-implemented)
    ├── __init__.py         # Types & constants
    ├── features.py         # Feature extraction
    ├── scorer.py           # Three-lens scoring engine
    ├── consensus.py        # Weighted consensus
    ├── self_review.py      # Self-review gate
    └── report.py           # Report formatter
```

## Credits

Inspired by the architecture and methodology of:
- **UZI-Skill** (github.com/wbh604) — independent-jury consensus and mechanical self-review design
- **Serenity / TraderS** — supply chain bottleneck analysis and macro cycle classification frameworks
- **multi-market-stock-analysis** — predecessor project, three-perspective stock analysis foundation

All code is **self-implemented**. No direct code copy from any upstream project.

---

## License

MIT
