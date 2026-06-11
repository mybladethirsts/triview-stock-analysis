#!/usr/bin/env python3
"""
Triview — 报告生成器

将分析结果格式化为可读的报告文本。
"""

from lib.__init__ import Consensus, Signal
from typing import Dict


def generate_report(consensus: Consensus, features: Dict,
                    ticker: str = "", market: str = "") -> str:
    """生成完整分析报告"""
    
    lines = []
    name = features.get("name", ticker or "未知标的")
    ind = features.get("industry", "未分类")
    sec = features.get("sector", "")
    mc = features.get("market_cap_yi", 0)
    ic = features.get("industry_category", "other")
    
    # ── 头部 ──
    lines.append(f"{'='*60}")
    lines.append(f"  Triview 三视  |  {name}")
    lines.append(f"  Ticker: {ticker}  |  Market: {market or 'auto'}")
    lines.append(f"{'='*60}")
    lines.append("")
    
    # ── Verdict ──
    signal_char = {
        Signal.BULLISH: "🟢",
        Signal.NEUTRAL: "🟡",
        Signal.BEARISH: "🔴",
        Signal.SKIP: "⚪",
    }.get(consensus.overall_signal, "⚪")
    
    lines.append(f"【{signal_char} {consensus.overall_signal.value.upper()}】")
    lines.append(f"  综合评分: {consensus.weighted_total:.1f}/100")
    lines.append(f"  结论: {consensus.verdict}")
    lines.append("")
    
    # ── 基础信息 ──
    lines.append(f"📋 基本信息")
    lines.append(f"  Industry: {ind}  |  Sector: {sec}")
    lines.append(f"  市值: {mc:.0f}亿人民币等值")
    lines.append(f"  行业分类: {ic}")
    lines.append(f"  供应链层级: {features.get('supply_chain_tier', '—')}")
    lines.append(f"  证据等级: {features.get('evidence_grade', 'weak').upper()}")
    lines.append("")
    
    # ── 三维评分表 ──
    lines.append(f"📊 三维评分")
    lines.append(f"  {'维度':<20} {'得分':<8} {'信号':<10} {'权重':<8}")
    lines.append(f"  {'─'*20} {'─'*8} {'─'*10} {'─'*8}")
    
    for name_lbl, key in [
        ("🏛️ 标的质地", "business_quality"),
        ("🌊 宏观轮动", "macro_rotation"),
        ("📈 技术趋势", "technical_trend"),
    ]:
        sd = consensus.scores.get(key)
        if sd:
            sig = {Signal.BULLISH: "🟢看多", Signal.NEUTRAL: "🟡中性", Signal.BEARISH: "🔴看空", Signal.SKIP: "⚪跳过"}
            lines.append(f"  {name_lbl:<20} {sd.score:<8.1f} {sig.get(sd.signal,'?'):<10} {sd.weight:<8.0%}")
    lines.append(f"  {'─'*20} {'─'*8} {'─'*10} {'─'*8}")
    lines.append(f"  {'加权总分':<20} {consensus.weighted_total:<8.1f}  ")
    lines.append("")
    
    # ── 各视角详情 ──
    for name_lbl, key, desc in [
        ("🏛️ 标的质地", "business_quality", "护城河/商业模式/行业评分"),
        ("🌊 宏观轮动", "macro_rotation", "宏观象限与趋势匹配"),
        ("📈 技术趋势", "technical_trend", "量价关系与技术信号"),
    ]:
        sd = consensus.scores.get(key)
        if not sd:
            continue
        lines.append(f"── {name_lbl} — {desc} ──")
        pt = sd.penalty_total or 0
        rs = sd.raw_score or 0
        lines.append(f"  评分: {sd.score:.1f}/100 | 原始: {rs:.0f} | "
                     f"罚分: {pt:.0%}")
        lines.append(f"  关键因子:")
        for kf in sd.key_factors[:6]:
            lines.append(f"    · {kf}")
        lines.append("")
    
    # ── 自检结果 ──
    sr = consensus.self_review
    if sr:
        lines.append(f"🔍 自检门禁")
        lines.append(f"  状态: {sr.get('status', '?')}")
        lines.append(f"  摘要: {sr.get('summary', '?')}")
        if sr.get("warnings"):
            lines.append(f"  警告:")
            for w in sr["warnings"][:3]:
                lines.append(f"    ⚠️ {w}")
        lines.append("")
    
    # ── 风险提示 ──
    lines.append(f"⚠️ 风险提示")
    lines.append(f"  · 本分析基于公开数据和量化模型，不构成投资建议")
    lines.append(f"  · 过往表现不保证未来结果")
    lines.append(f"  · 请自行核实关键数据点")
    lines.append(f"")
    lines.append(f"{'='*60}")
    lines.append(f"  Triview 三视 — 三维量化评分 | 适配全行业")
    
    return "\n".join(lines)


def format_summary(consensus: Consensus, ticker: str = "") -> str:
    """生成简短摘要（适合消息推送）"""
    
    sig_char = {
        Signal.BULLISH: "🟢",
        Signal.NEUTRAL: "🟡",
        Signal.BEARISH: "🔴",
        Signal.SKIP: "⚪",
    }.get(consensus.overall_signal, "⚪")
    
    lines = [
        f"【{sig_char} {ticker or 'Stock'}】{consensus.verdict}",
        f"  总分: {consensus.weighted_total:.0f}/100",
    ]
    
    for key, name in [("business_quality", "质地"), ("macro_rotation", "宏观"), ("technical_trend", "技术")]:
        sd = consensus.scores.get(key)
        if sd:
            lines.append(f"  {name}: {sd.score:.0f} {sd.signal.value}")
    
    return "\n".join(lines)
