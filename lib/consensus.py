#!/usr/bin/env python3
"""
Triview — 共识引擎

将三维独立评分按权重合成，生成最终 verdict。

权重: 标的质地(40%) + 宏观轮动(30%) + 技术趋势(30%)
"""
from lib.__init__ import Signal, ScoreDetail, Consensus
from lib.scorer import score_fundamentals, score_macro, score_technical
from typing import Dict, Optional


def run_analysis(features: Dict,
                 macro_state: Dict = None,
                 price_data: Dict = None,
                 user_input: Dict = None,
                 skip_self_review: bool = False) -> Consensus:
    """
    运行全部分析流程，返回 Consensus 结果
    
    Args:
        features: features.extract_features() 的输出
        macro_state: 可选，宏观象限描述 {quadrant, confidence}
        price_data: 可选，价格数据
        user_input: 可选，用户附加信息
        skip_self_review: 调试用，跳过自检
    """
    
    # ── 三维独立评分 ──
    fundamentals = score_fundamentals(features, user_input)
    macro = score_macro(features, macro_state)
    technical = score_technical(features, price_data)
    
    scores = {
        "business_quality": fundamentals,
        "macro_rotation": macro,
        "technical_trend": technical,
    }
    
    # ── 加权合成 ──
    weighted = (
        fundamentals.score * fundamentals.weight
        + macro.score * macro.weight
        + technical.score * technical.weight
    )
    
    # ── 信号判定 ──
    bull_count = sum(1 for s in [fundamentals, macro, technical] if s.signal == Signal.BULLISH)
    bear_count = sum(1 for s in [fundamentals, macro, technical] if s.signal == Signal.BEARISH)
    neutral_count = 3 - bull_count - bear_count
    
    if bull_count >= 2 and weighted >= 65:
        overall_signal = Signal.BULLISH
        if weighted >= 80:
            verdict = "★★★ 强烈看多 · 三视角共振，值得重仓"
        elif weighted >= 65:
            verdict = "★★ 看多 · 多数视角一致，考虑建仓"
        else:
            verdict = "★ 偏多 · 有利因素为主，观望建仓时机"
    elif bear_count >= 2 or weighted < 35:
        overall_signal = Signal.BEARISH
        verdict = "★ 看空 · 多数视角不利，回避"
    elif bear_count >= 1 and weighted < 50:
        overall_signal = Signal.BEARISH
        verdict = "【警告】做空或不参与 · 关键维度亮红灯"
    else:
        overall_signal = Signal.NEUTRAL
        verdict = "中性分歧 · 有争议需进一步验证，减仓或观望"
    
    consensus = Consensus(
        scores=scores,
        weighted_total=weighted,
        overall_signal=overall_signal,
        verdict=verdict,
    )
    
    # ── 自检门禁 ──
    if not skip_self_review:
        from lib.self_review import run_self_review
        review = run_self_review(features, consensus, user_input)
        consensus.self_review = review
    
    return consensus
