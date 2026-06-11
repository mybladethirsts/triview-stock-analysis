# Self-Review Gate System (机械级自查门)

> 从 UZI-Skill (wbh604) 的机械级自检引擎移植。确保分析报告在质量不足时被阻止生成，
> 而不是让用户看到有问题的结果。

## 为什么需要

仅有 SKILL.md 里"软要求"级别的 gate 是不够的。实际分析中常见问题：

- **行业映射错误**: "工业金属"被误映射到"农副食品加工"（BUG#R10 类）
- **数据维度缺失**: 某些 fetcher 从未运行或静默崩溃
- **占位符残留**: synthesis 里遗留"[脚本占位]"、"[TODO]"、"[未实现]"
- **评分异常**: panel 平均分为 0 或超过 100
- **港股特殊问题**: kline 数据为空、financials 完全缺失
- **概念编造**: 提及"苹果/特斯拉供应链"但 main_business 无相关业务

## 检查清单

### 1. Data Integrity Checks (数据完整性)

| # | Check | Severity | 描述 | 触发条件 |
|---|-------|----------|------|---------|
| 1 | 行业映射正确性 | critical | 行业被误映射到高碰撞类别 | "工业金属"→"农副食品加工"等已知碰撞对 |
| 2 | 维度完备性 | critical | 应跑的分析维度必须都存在 | profile-aware：lite 只检查启用的维度 |
| 3 | 维度空数据 | critical/warning | 维度 key 存在但 data 完全为空 | 区分 timeout(crash) vs 真空 |
| 4 | 港股K线数据 | critical | 港股 kline_count 不能为 0 | 市场=H 且 count=0 |
| 5 | 港股财报数据 | critical/warning | 港股 financials 不能为空 | 市场=H 且 roe_history 缺失 |
| 6 | 数据覆盖率 | critical/warning | coverage_pct >= 60% 才出报告 | lite/CLI 模式降为 warning |

### 2. Content Quality Checks (内容质量)

| # | Check | Severity | 描述 | 触发条件 |
|---|-------|----------|------|---------|
| 7 | 占位符检测 | critical | synthesis 含占位符 | "[脚本占位]"、"[TODO]"、"占位符"、"PLACEHOLDER" |
| 8 | 估值合理性 | warning | DCF 内在价值不为 0/None | intrinsic_value_per_share=0 |
| 9 | 行业数据覆盖 | warning | 行业景气度需 WebSearch 补齐 | needs_web_search=True 且 agent 未补 |
| 10 | 材料数据 | warning | 金属类股票需有原材料数据 | 行业含"有色金属"类但 materials 为空 |

### 3. Consistency Checks (一致性)

| # | Check | Severity | 描述 | 触发条件 |
|---|-------|----------|------|---------|
| 11 | 多空辩论完整性 | critical/warning | debate.bull 和 bear 不能都为空 | 未选出 bullish/bearish 代表 |
| 12 | 评委打分异常 | critical | panel 分数确实异常 | 平均分=0 或 >100 |
| 13 | 评委skip率过高 | warning | >50% 评委 skip | 可能不在其能力圈或出 bug |
| 14 | 一致性公式 | warning | 使用最新混合公式 | consensus_formula 版本陈旧 |
| 15 | 事实核查 | warning | 提到的供应链关联需有证据 | "苹果供应链"但 main_business 无相关业务 |

### 4. Report Validation (报告验证)

| # | Check | Severity | 描述 | 触发条件 |
|---|-------|----------|------|---------|
| 16 | agent_analysis 完整性 | critical/warning | agent_reviewed=true | 文件不存在或未标记已审查 |
| 17 | dim_commentary 覆盖率 | warning | 至少覆盖 15/22 维 | 覆盖维数 < 15 |

## 执行流程

```
          ┌─────────────────────┐
          │  raw_data/synthesis  │
          │  + panel/agent_analysis  │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │  Run all 17 checks  │
          └──────────┬──────────┘
                     ▼
          ┌─────────────────────┐
          │  critical_count?    │
          │  ┌─── 0: ✅ Pass    │
          │  └─── >0: ❌ Block  │
          └─────────────────────┘
```

## 降级策略

- **lite 模式** (快速分析): critical 降级为 warning，允许出报告但标注
- **CLI 直跑模式** (无 agent 介入): critical 降级为 warning
- **CI/batch 环境**: 同上

## 可能的假阳性处理

- **港股特有检查**: 仅当 `market == "H"` 时才触发
- **金属材料检查**: 仅当行业含"有色金属"类关键词
- **profile-aware**: 只检查当前 profile 启用的维度（lite 模式只跑 7 维不报 missing）

## 示例：_review_issues.json 输出

```json
{
  "ticker": "300308",
  "market": "A",
  "reviewed_at": "2026-06-10T12:00:00",
  "critical_count": 1,
  "warning_count": 2,
  "info_count": 0,
  "passed": false,
  "issues": [
    {
      "severity": "critical",
      "category": "data",
      "dim": "7_industry",
      "issue": "BUG#R10 class regression: 申万行业 '工业金属' 被误映射到证监会 '农副食品加工'",
      "evidence": "industry='工业金属', matched='农副食品加工'",
      "suggested_fix": "检查 lib/industry_mapping 映射表"
    }
  ]
}
```

*移植自 UZI-Skill (github.com/wbh604/UZI-Skill) 的 self_review.py 自查引擎。*
