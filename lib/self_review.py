#!/usr/bin/env python3
"""
Triview — 机械级自检门禁

在每次输出前自动运行，确保分析质量。
分为三级：
  - critical: 不通过则报告无效
  - warning: 提示用户注意潜在问题
  - info: 提示信息

检查维度（16 项）：
  数据完整性 (4项) / 内容质量 (4项) / 一致性 (4项) / 安全 (4项)
"""

from typing import Dict, List, Optional
from lib.__init__ import Signal, Consensus


def run_self_review(features: Dict,
                    consensus: Consensus,
                    user_input: Dict = None) -> Dict:
    """运行全部自检，返回检查结果"""
    
    checks = []
    pass_count = 0
    fail_count = 0
    warn_count = 0
    
    # ═══════════════════════════════════════════
    # 第1类：数据完整性检查 (4项)
    # ═══════════════════════════════════════════
    
    # 1.1 公司名称
    has_name = bool(features.get("name"))
    checks.append({
        "id": "D01",
        "type": "critical" if not has_name else "pass",
        "check": "公司名称",
        "detail": "✅ 已识别" if has_name else "❌ 未识别标的名称 — 报告无法定位公司",
    })
    if has_name:
        pass_count += 1
    else:
        fail_count += 1
    
    # 1.2 行业信息
    has_industry = bool(features.get("industry"))
    checks.append({
        "id": "D02",
        "type": "warning" if not has_industry else "pass",
        "check": "行业分类",
        "detail": "✅ 行业已归类" if has_industry else "⚠️ 行业未分类 — 卡位猎手视角可能不准",
    })
    if has_industry:
        pass_count += 1
    else:
        warn_count += 1
    
    # 1.3 市值
    has_mc = features.get("market_cap_yi", 0) > 0
    checks.append({
        "id": "D03",
        "type": "warning" if not has_mc else "pass",
        "check": "市值数据",
        "detail": f"✅ 市值 {features.get('market_cap_yi', 0):.0f} 亿" if has_mc else "⚠️ 市值未获取 — 小盘弹性评分缺席",
    })
    if has_mc:
        pass_count += 1
    else:
        warn_count += 1
    
    # 1.4 基本面覆盖
    has_fundamentals = features.get("revenue", 0) > 0
    checks.append({
        "id": "D04",
        "type": "warning" if not has_fundamentals else "pass",
        "check": "基本面数据",
        "detail": "✅ 含收入/利润率数据" if has_fundamentals else "⚠️ 无基本面数据 — 评分仅靠行业标签推断",
    })
    if has_fundamentals:
        pass_count += 1
    else:
        warn_count += 1
    
    # ═══════════════════════════════════════════
    # 第2类：内容质量检查 (4项)
    # ═══════════════════════════════════════════
    
    # 2.1 证据等级 > weak
    ev = features.get("evidence_grade", "weak")
    ev_ok = ev != "weak"
    checks.append({
        "id": "Q01",
        "type": "warning" if not ev_ok else "pass",
        "check": "证据等级",
        "detail": f"✅ 证据等级={ev}" if ev_ok else "⚠️ 仅有弱证据 — 叙事风险高，需自行验证",
    })
    if ev_ok:
        pass_count += 1
    else:
        warn_count += 1
    
    # 2.2 AI 链判定
    in_chain = features.get("in_ai_chain", False) or features.get("is_tech", False)
    checks.append({
        "id": "Q02",
        "type": "info",
        "check": "供应链关联",
        "detail": f"📌 {'在 AI/科技供应链上' if in_chain else '非科技板块 — 卡位猎手得分天然偏低'}",
    })
    pass_count += 1  # info 不算失败
    
    # 2.3 是否有足够因子支撑评分
    has_factors = len(consensus.scores.get("bottleneck_hunter", {}).key_factors if hasattr(consensus.scores.get("bottleneck_hunter", {}), "key_factors") else []) > 2
    checks.append({
        "id": "Q03",
        "type": "info",
        "check": "评分解析度",
        "detail": "✅ 多因子支撑" if has_factors else "📌 因子较少 — 结论可能不够精细",
    })
    pass_count += 1
    
    # 2.4 信号足够确定
    strong_signal = consensus.overall_signal not in [Signal.NEUTRAL, Signal.SKIP]
    checks.append({
        "id": "Q04",
        "type": "info",
        "check": "信号明确度",
        "detail": "✅ 方向明确" if strong_signal else "📌 信号中性 — 建议用户自行增补信息再判断",
    })
    pass_count += 1
    
    # ═══════════════════════════════════════════
    # 第3类：一致性检查 (4项)
    # ═══════════════════════════════════════════
    
    # 3.1 卡位猎手 & 宏观 是否矛盾
    bottleneck_signal = consensus.scores.get("bottleneck_hunter", {}).signal if hasattr(consensus.scores.get("bottleneck_hunter", {}), "signal") else Signal.NEUTRAL
    macro_signal = consensus.scores.get("macro_rotation", {}).signal if hasattr(consensus.scores.get("macro_rotation", {}), "signal") else Signal.NEUTRAL
    if bottleneck_signal not in [Signal.NEUTRAL, Signal.SKIP] and macro_signal not in [Signal.NEUTRAL, Signal.SKIP]:
        aligned = bottleneck_signal == macro_signal
        checks.append({
            "id": "C01",
            "type": "warning" if not aligned else "pass",
            "check": "视角一致性(卡位 vs 宏观)",
            "detail": "✅ 两视角方向一致" if aligned else "⚠️ 卡位看多但宏观看空 — 冲突需分析优先级",
        })
        if aligned:
            pass_count += 1
        else:
            warn_count += 1
    else:
        checks.append({
            "id": "C01",
            "type": "info",
            "check": "视角一致性(卡位 vs 宏观)",
            "detail": "📌 至少一视角方向中性 — 一致性无需检查",
        })
        pass_count += 1
    
    # 3.2 技术信号验证
    tech_signal = consensus.scores.get("technical_trend", {}).signal if hasattr(consensus.scores.get("technical_trend", {}), "signal") else Signal.NEUTRAL
    checks.append({
        "id": "C02",
        "type": "info",
        "check": "技术验证",
        "detail": f"📌 技术信号：{tech_signal.value} — 用于验证/反验证基本面判断",
    })
    pass_count += 1
    
    # 3.3 小盘+强卡位检查 (无弹性有限)
    mc_yi = features.get("market_cap_yi", 0)
    is_smallcap = features.get("is_smallcap", False)
    if is_smallcap and bottleneck_signal == Signal.BULLISH:
        checks.append({
            "id": "C03",
            "type": "warning",
            "check": "小盘卡位溢价",
            "detail": f"⚠️ 小市值({mc_yi:.0f}亿)+强卡位 — 弹性大但波动大，需严格止损",
        })
        warn_count += 1
    else:
        checks.append({
            "id": "C03",
            "type": "pass",
            "check": "小盘卡位溢价",
            "detail": "✅ 非小盘强卡位组合 — 波动可控",
        })
        pass_count += 1
    
    # 3.4 多空对比
    total_bull = sum(1 for s in consensus.scores.values() if (hasattr(s, 'signal') and s.signal == Signal.BULLISH))
    total_bear = sum(1 for s in consensus.scores.values() if (hasattr(s, 'signal') and s.signal == Signal.BEARISH))
    checks.append({
        "id": "C04",
        "type": "info",
        "check": f"多空力量 (多头{total_bull} vs 空头{total_bear})",
        "detail": f"📌 {total_bull}维看多 · {total_bear}维看空 · {3-total_bull-total_bear}维中性",
    })
    pass_count += 1
    
    # ═══════════════════════════════════════════
    # 第4类：安全检查 (4项)
    # ═══════════════════════════════════════════
    
    # 4.1 高波动警告
    checks.append({
        "id": "S01",
        "type": "info",
        "check": "免责声明",
        "detail": "📌 本工具仅供研究参考，不构成投资建议，投资有风险",
    })
    pass_count += 1
    
    # 4.2 流动性检查
    if is_smallcap:
        checks.append({
            "id": "S02",
            "type": "warning",
            "check": "流动性",
            "detail": f"⚠️ {mc_yi:.0f}亿市值 — 微/小盘股存在流动性风险，注意买卖价差",
        })
        warn_count += 1
    else:
        checks.append({
            "id": "S02",
            "type": "pass",
            "check": "流动性",
            "detail": "✅ 市值充沛，流动性风险低",
        })
        pass_count += 1
    
    # 4.3 政策风险
    policy_notes = []
    if features.get("in_ev_chain"):
        policy_notes.append("EV 板块受补贴政策波动影响大")
    checks.append({
        "id": "S03",
        "type": "info",
        "check": "政策敏感性",
        "detail": f"📌 {'/'.join(policy_notes) if policy_notes else '无明显政策风险'}",
    })
    pass_count += 1
    
    # 4.4 数据新鲜度
    checks.append({
        "id": "S04",
        "type": "info",
        "check": "数据时效",
        "detail": "📌 评分基于最近可用财务数据 · 重大事件后需复查",
    })
    pass_count += 1
    
    # ── 报告有效性 ──
    report_valid = fail_count == 0
    
    result = {
        "valid": report_valid,
        "status": "✅ 通过" if report_valid else "❌ 未通过",
        "summary": f"{pass_count} 通过 / {warn_count} 警告 / {fail_count} 失败",
        "checks": checks,
        "warnings": [c["detail"] for c in checks if c["type"] == "warning"],
        "failures": [c["detail"] for c in checks if c["type"] == "critical"],
    }
    
    return result
