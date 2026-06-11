# Macro Indicators (宏观指标)

跨市场宏观指标参考，用于 TraderS 视角的宏观环境判断。

## 美国市场（US Stocks）

### 利率与货币政策
- **联邦基金利率（Fed Funds Rate）**：美联储政策利率
  - 数据来源：Fed [https://www.federalreserve.gov/](https://www.federalreserve.gov/)
  - 影响：利率上升 → 成长股估值承压，利率下降 → 流动性宽松
- **10 年期国债收益率（10Y Treasury Yield）**：
  - 数据来源：FRED [https://fred.stlouisfed.org/series/DGS10](https://fred.stlouisfed.org/series/DGS10)
  - 影响：收益率上升 → 股票相对吸引力下降，科技股承压
- **2 年期国债收益率（2Y Treasury Yield）**：
  - 数据来源：FRED [https://fred.stlouisfed.org/series/DGS2](https://fred.stlouisfed.org/series/DGS2)
  - 影响：短端利率反映美联储政策预期
- **收益率曲线（10Y-2Y Spread）**：
  - 倒挂（负值）= 衰退预期，陡峭化 = 复苏预期

### 流动性与风险偏好
- **VIX（恐慌指数）**：
  - 数据来源：CBOE [https://www.cboe.com/tradable_products/vix/](https://www.cboe.com/tradable_products/vix/)
  - <15 = 低波动，>25 = 高波动，>35 = 恐慌
- **高收益债券利差（High-Yield Spread）**：
  - 数据来源：FRED [https://fred.stlouisfed.org/series/BAMLH0A0HYM2](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)
  - 利差扩大 = 风险偏好下降，利差收窄 = 风险偏好上升
- **美元指数（DXY）**：
  - 数据来源：FRED [https://fred.stlouisfed.org/series/DTWEXBGS](https://fred.stlouisfed.org/series/DTWEXBGS)
  - 美元走强 → 新兴市场承压，美元走弱 → 风险资产受益

### 行业 Capex 与 AI 相关
- **超大规模云厂商 Capex（Hyperscaler Capex）**：
  - 公司：NVDA、MSFT、GOOGL、AMZN、META 财报中的 Capex 指引
  - 跟踪：[SemiconStocks](https://semiconstocks.com/) 的 Capex 追踪器
  - 影响：Capex 上调 → AI 供应链受益，Capex 下修 → AI 供应链承压
- **AI 服务器出货量**：
  - 数据来源：Dell'Oro、Gartner、IDC 报告
  - 影响：出货量超预期 → 算力供应链受益

### 消费者与企业信心
- **密歇根大学消费者信心指数**：
  - 数据来源：FRED [https://fred.stlouisfed.org/series/UMCSENT](https://fred.stlouisfed.org/series/UMCSENT)
- **ISM 制造业 PMI**：
  - 数据来源：ISM [https://www.instituteforsupplymanagement.org/](https://www.instituteforsupplymanagement.org/)
  - >50 = 扩张，<50 = 收缩

---

## 港股市场（HK Stocks）

### 中国宏观（影响港股的核心）
- **货币政策**：
  - **中期借贷便利（MLF）利率**：央行政策利率
    - 数据来源：中国人民银行 [http://www.pbc.gov.cn/](http://www.pbc.gov.cn/)
  - **贷款市场报价利率（LPR）**：
    - 数据来源：全国银行间同业拆借中心 [https://www.chinamoney.com.cn/](https://www.chinamoney.com.cn/)
- **货币供应**：
  - **M2 增速**：反映流动性宽松程度
    - 数据来源：中国人民银行 [http://www.pbc.gov.cn/](http://www.pbc.gov.cn/)
  - **社会融资规模（Social Financing）**：反映实体经济融资需求
    - 数据来源：中国人民银行
- **人民币汇率**：
  - **USD/CNY（在岸）**、**USD/CNH（离岸）**
    - 数据来源：中国外汇交易中心 [https://www.chinamoney.com.cn/](https://www.chinamoney.com.cn/)
  - 人民币贬值 → 南向资金流出，港股承压

### 南向资金（South-Bound Capital）
- **南向资金日度净流入**：
  - 数据来源：Wind、东方财富、同花顺
  - 影响：持续净流入 → 港股科技/消费受益，持续净流出 → 港股承压
- **南向资金持仓变化**：
  - 跟踪：Wind 南向资金持仓周报

### 香港本地指标
- **港币同业拆借利率（HIBOR）**：
  - 数据来源：香港银行公会 [https://www.hkab.org.hk/](https://www.hkab.org.hk/)
  - 影响：HIBOR 上升 → 港股流动性收紧
- **恒生指数（HSI）**：
  - 数据来源：恒生指数公司 [https://www.hsi.com.hk/](https://www.hsi.com.hk/)

---

## A 股市场（A-Shares）

### 货币政策与流动性
- **逆回购利率（7 天、14 天）**：
  - 数据来源：中国人民银行 [http://www.pbc.gov.cn/](http://www.pbc.gov.cn/)
- **MLF 利率**、**LPR**：
  - 同上
- **M2 增速**、**社会融资规模**：
  - 同上
- **北向资金（North-Bound Capital）**：
  - 数据来源：Wind、东方财富
  - 影响：持续净流入 → A 股核心资产受益

### 监管政策
- **证监会（CSRC）政策**：
  - 数据来源：中国证监会 [http://www.csrc.gov.cn/](http://www.csrc.gov.cn/)
  - 关键政策：IPO 节奏、再融资规则、减持规定、退市新规
- **国务院常务会议**：
  - 数据来源：中国政府网 [http://www.gov.cn/](http://www.gov.cn/)
  - 影响：产业政策、补贴政策、监管方向
- **央行货币政策执行报告**：
  - 数据来源：中国人民银行 [http://www.pbc.gov.cn/](http://www.pbc.gov.cn/)

### 经济数据
- **GDP 增速**：
  - 数据来源：国家统计局 [http://www.stats.gov.cn/](http://www.stats.gov.cn/)
- **PMI（制造业、非制造业）**：
  - 数据来源：国家统计局
  - >50 = 扩张，<50 = 收缩
- **CPI**、**PPI**：
  - 数据来源：国家统计局
  - CPI 上行 → 消费股受益，PPI 上行 → 周期股受益
- **固定资产投资**、**房地产开发投资**：
  - 数据来源：国家统计局

### 市场情绪
- **融资余额（Margin Balance）**：
  - 数据来源：东方财富、同花顺
  - 影响：融资余额快速上升 → 市场情绪过热，可能回调
- **股指期货升贴水**：
  - 数据来源：中金所 [http://www.cffex.com.cn/](http://www.cffex.com.cn/)
  - 贴水扩大 → 市场悲观，升水 → 市场乐观
- **雪球产品（Snowball）** 敲入/敲出：
  - 影响：集中敲入可能加剧下跌

---

## 宏观判断框架（TraderS 视角）

### 宏观环境分类
| 环境 | 特征 | 适合策略 |
|------|------|---------|
| **宽松初期** | 利率下行、流动性改善、估值修复 | 成长股、科技股、小盘股 |
| **宽松中期** | 需求复苏、企业盈利改善 | 周期股、消费股、价值股 |
| **过热期** | 通胀上行、利率见底、估值高企 | 防御股、现金、商品 |
| **紧缩初期** | 利率上行、流动性收紧、估值承压 | 减持成长股、增持价值股 |
| **紧缩中期** | 需求下滑、企业盈利恶化 | 防御、现金、债券 |
| **衰退期** | 利率快速下行、避险情绪升温 | 国债、黄金、防御股 |

### 宏观 → 行业轮动
- **利率下行** → 科技、消费、地产（高估值板块受益）
- **利率上行** → 银行、保险、周期（价值股受益）
- **人民币贬值** → 出口股受益、航空/造纸承压
- **人民币升值** → 航空、造纸受益、出口股承压
- **油价上涨** → 石油石化受益、交运承压
- **油价下跌** → 交运受益、石油石化承压

### 宏观 → 供应链瓶颈
- **流动性宽松 + AI Capex 扩张** → 供应链瓶颈逻辑最强（Serenity 框架最有效）
- **流动性收紧 + AI Capex 下修** → 供应链瓶颈逻辑减弱（即使有瓶颈，估值也会承压）
- **地缘政治紧张** → 供应链瓶颈逻辑分化（国产替代加速 vs. 全球供应链中断）

---

## 数据来源汇总

| 市场 | 数据类型 | 主要来源 |
|------|---------|---------|
| 美国 | 利率、收益率 | FRED, Fed, TreasuryDirect |
| 美国 | 波动率、风险偏好 | CBOE (VIX), FRED (High-Yield Spread) |
| 美国 | Capex、财报 | SEC EDGAR, 公司官网, SemiconStocks |
| 港股 | 中国宏观 | 中国人民银行, 国家统计局, 中国政府网 |
| 港股 | 南向资金 | Wind, 东方财富, 同花顺 |
| 港股 | 本地利率 | 香港银行公会 (HIBOR) |
| A 股 | 货币政策、流动性 | 中国人民银行 |
| A 股 | 监管政策 | 中国证监会, 中国政府网 |
| A 股 | 经济数据 | 国家统计局 |
| A 股 | 市场情绪 | 东方财富, 同花顺, 中金所 |

---

*基于 TraderS 缺德道人 (@Trader_S18) 的公开研究方法提炼，仅供学习研究使用。*
