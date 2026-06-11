#!/usr/bin/env python3
"""
Triview — 三维评分引擎

三大视角的独立评分逻辑：
  1. 标的质地 (Business Quality) — 按行业分类路由评分分支
  2. 宏观轮动 (Macro Rotation) — 宏观象限匹配
  3. 技术趋势 (Technical Trend) — 量价技术信号

每维输出 0-100 分 + 信号 + 推理过程。
"""

from lib.__init__ import (
    Signal, ScoreDetail, EVIDENCE_LADDER, PENALTY_FACTORS, SUPPLY_CHAIN_TIERS,
    MACRO_QUADRANTS, MARKET_DAY_TYPES, MOAT_TYPES, INDUSTRY_CATEGORIES,
)
from typing import Dict, Optional, List, Tuple
import math


# ═══════════════════════════════════════════════════════════
# 视角 1：标的质地 (Business Quality) — 40% 权重
# ═══════════════════════════════════════════════════════════

def score_fundamentals(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """
    标的质地评分：根据行业分类路由到不同评分分支
    
    路由逻辑：
      - manufacturing → 供应链卡位分析（原六步法）
      - consumer     → 品牌护城河分析
      - financial    → 网络+监管壁垒分析
      - healthcare   → 管线+专利分析
      - energy       → 资源禀赋+成本分析
      - platform     → 网络效应+数据壁垒
      - other        → 通用财务质量评分
    """
    category = features.get("industry_category", "other")
    chain_hit = features.get("in_ai_chain", False) or features.get("in_robot_chain", False) or features.get("in_ev_chain", False)
    
    # 即使是消费/金融等行业，如果有供应链概念也走卡位
    if category in ("manufacturing", "energy") or (chain_hit and category != "platform"):
        return _score_bottleneck(features, user_input)
    elif category == "consumer":
        return _score_consumer_moat(features, user_input)
    elif category == "financial":
        return _score_financial_moat(features, user_input)
    elif category == "healthcare":
        return _score_healthcare_moat(features, user_input)
    elif category == "platform":
        return _score_platform_moat(features, user_input)
    elif category == "energy":
        return _score_energy_moat(features, user_input)
    else:
        return _score_generic_quality(features, user_input)


# ─── 分支 1a: 供应链卡位 (原六步法) ───

def _score_bottleneck(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """
    供应链卡位评分：六步法量化实现（适用于制造/科技/供应链）
    """
    key_factors = []
    penalties = 0.0
    penalty_notes = []
    
    # ─── 1. 链命中 (0-20) ───
    chain_score = 0
    chain_hit = features.get("in_ai_chain", False) or features.get("in_robot_chain", False)
    if chain_hit:
        chain_score = 20
        key_factors.append("在 AI/机器人供应链上")
        if features.get("in_ai_chain"):
            key_factors.append(f"AI 链: {features.get('industry', '未知')}")
        if features.get("in_robot_chain"):
            key_factors.append("具身智能/机器人链")
    elif features.get("in_ev_chain"):
        chain_score = 12
        key_factors.append("在 EV 供应链上(非核心 AI，权重降档)")
    elif features.get("is_tech"):
        chain_score = 8
        key_factors.append("有科技属性但非核心链")
    else:
        chain_score = 0
        key_factors.append("不在科技/AI 供应链上 — 建议切换到通用质地分析")
    
    # ─── 2. 不可替代性 (0-25) ───
    irreplaceable = 0
    gm = features.get("gross_margin", 0) or 0
    rd = features.get("rd_intensity", 0) or 0
    pe = features.get("pe_ratio", 0) or 0
    
    if gm > 0.50:
        irreplaceable += 10
        key_factors.append(f"高毛利率 ({gm*100:.0f}%) — 强定价权")
    elif gm > 0.30:
        irreplaceable += 6
    else:
        irreplaceable += 2
    
    if rd > 0.15:
        irreplaceable += 8
        key_factors.append(f"高研发强度 ({rd*100:.0f}%) — 技术壁垒")
    elif rd > 0.08:
        irreplaceable += 5
    else:
        irreplaceable += 1
    
    if pe > 30:
        irreplaceable += 4
    elif pe > 15:
        irreplaceable += 3
    else:
        irreplaceable += 1
    
    tier_weight = features.get("tier_weight", 0.50)
    if tier_weight >= 0.85:
        irreplaceable += 3
        key_factors.append(f"供应链上游 ({features.get('supply_chain_tier', '未知')})")
    
    # ─── 3. 证据阶梯 (0-15) ───
    evidence = features.get("evidence_grade", "weak")
    evidence_mult = EVIDENCE_LADDER[evidence]["multiplier"]
    evidence_score_map = {"strong": 15, "medium": 10, "weak": 5}
    evidence_score = evidence_score_map.get(evidence, 5)
    key_factors.append(f"证据等级: {evidence} (系数×{evidence_mult})")
    
    # ─── 4. 弹性 (0-15) ───
    mc_yi = features.get("market_cap_yi", 0)
    elastic_score = 0
    if features.get("is_smallcap") and chain_hit:
        elastic_score = 15
        key_factors.append(f"小市值高弹性 ({mc_yi:.0f}亿)")
    elif mc_yi < 500:
        elastic_score = 10
    elif mc_yi < 1000:
        elastic_score = 5
    else:
        elastic_score = 3
    
    # ─── 5. 财务健康 (0-15) ───
    finance_score = 0
    rg = features.get("revenue_growth", 0) or 0
    fcf = features.get("free_cashflow", 0) or 0
    
    if rg > 0.20:
        finance_score += 8
    elif rg > 0.10:
        finance_score += 5
    elif rg > 0:
        finance_score += 3
    
    if fcf > 0:
        finance_score += 4
        key_factors.append("正向自由现金流")
    if features.get("revenue", 0) > 0:
        finance_score += 3
    
    # ─── 6. 催化剂 (0-10) ───
    catalyst_score = 0
    if features.get("in_ai_chain") and rg > 0.30:
        catalyst_score += 5
        key_factors.append("AI 链上高增长 — 需求拐点")
    if features.get("in_robot_chain") and rg > 0.15:
        catalyst_score += 3
    if chain_hit:
        catalyst_score += 2
    
    raw_score = chain_score + irreplaceable + evidence_score + elastic_score + finance_score + catalyst_score
    raw_score = raw_score * tier_weight
    
    # ─── 罚分 ───
    if chain_hit and evidence == "weak":
        penalties += 0.20
        penalty_notes.append("热赛道+无硬证据 → 拉高出货嫌疑 (-20%)")
    if mc_yi < 30:
        penalties += 0.15
        penalty_notes.append(f"市值仅{mc_yi:.0f}亿 → 微盘流动性风险 (-15%)")
    
    penalties = min(penalties, 0.60)
    final_score = raw_score * (1 - penalties)
    final_score = max(0, min(100, final_score))
    
    if final_score >= 70 and chain_hit:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"供应链卡位: 链={chain_score}/20, 壁垒={irreplaceable}/25, "
    rationale += f"证据={evidence_score}/15, 弹性={elastic_score}/15, "
    rationale += f"财务={finance_score}/15, 拐点={catalyst_score}/10 | "
    rationale += f"原始={raw_score:.0f} → 罚分{penalties:.0%} → 最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=evidence,
        key_factors=key_factors + penalty_notes,
        rationale=rationale,
        penalty_total=penalties,
        raw_score=raw_score,
    )


# ─── 分支 1b: 消费品牌护城河 ───

def _score_consumer_moat(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """消费/品牌类：品牌护城河 + 定价权 + 渠道壁垒"""
    key_factors = []
    penalties = 0.0
    penalty_notes = []
    
    # ─── 品牌力量 (0-25) ───
    gm = features.get("gross_margin", 0) or 0
    brand_score = 0
    if gm > 0.60:
        brand_score = 22
        key_factors.append(f"超高毛利率 ({gm*100:.0f}%) — 强品牌溢价")
    elif gm > 0.40:
        brand_score = 16
        key_factors.append(f"高毛利率 ({gm*100:.0f}%) — 有品牌力")
    elif gm > 0.25:
        brand_score = 10
    else:
        brand_score = 5
        key_factors.append("低毛利率 — 品牌力弱或成本结构差")
    
    # ─── 规模+渠道 (0-20) ───
    mc_yi = features.get("market_cap_yi", 0)
    scale_score = 0
    if mc_yi > 1000:
        scale_score = 18
        key_factors.append(f"大市值 ({mc_yi:.0f}亿) — 规模效应优势")
    elif mc_yi > 200:
        scale_score = 12
    else:
        scale_score = 6
        key_factors.append("市值较小，规模效应待观察")
    
    # ─── 增长+复购 (0-20) ───
    rg = features.get("revenue_growth", 0) or 0
    growth_score = 0
    if rg > 0.15:
        growth_score = 18
        key_factors.append(f"收入增长 {rg*100:.0f}% — 健康扩张")
    elif rg > 0.05:
        growth_score = 12
    elif rg > 0:
        growth_score = 6
    else:
        growth_score = 3
        key_factors.append("收入收缩 — 需关注")
    
    # ─── 财务健壮性 (0-20) ───
    fcf = features.get("free_cashflow", 0) or 0
    fcf_yield = features.get("fcf_yield", 0) or 0
    finance_score = 0
    if fcf > 0 and fcf_yield > 0.10:
        finance_score = 18
        key_factors.append(f"强自由现金流转化 (FCF/收入={fcf_yield*100:.0f}%)")
    elif fcf > 0:
        finance_score = 12
    else:
        finance_score = 4
        key_factors.append("自由现金流为负")
    
    # ─── 股息+防御性 (0-15) ───
    div = features.get("dividend_yield", 0) or 0
    defensive_score = 0
    if 0.01 < div < 0.04:
        defensive_score = 13
        key_factors.append(f"合理股息 ({div*100:.1f}%) — 防御性")
    elif div >= 0.04:
        defensive_score = 10
    else:
        defensive_score = 5
    
    raw_score = brand_score + scale_score + growth_score + finance_score + defensive_score
    raw_score = max(0, min(100, raw_score))
    
    # ─── 罚分 ───
    if rg < 0:
        penalties += 0.10
        penalty_notes.append("营收下滑 — 品牌老化风险 (-10%)")
    if mc_yi < 30:
        penalties += 0.15
        penalty_notes.append("微盘消费股 — 流动性风险 (-15%)")
    
    penalties = min(penalties, 0.60)
    final_score = raw_score * (1 - penalties)
    
    if final_score >= 70:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"消费品牌: 品牌={brand_score}/25, 规模={scale_score}/20, "
    rationale += f"增长={growth_score}/20, 财务={finance_score}/20, 防御={defensive_score}/15 | "
    rationale += f"原始={raw_score:.0f} → 罚分{penalties:.0%} → 最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=features.get("evidence_grade", "weak"),
        key_factors=key_factors + penalty_notes,
        rationale=rationale,
        penalty_total=penalties,
        raw_score=raw_score,
    )


# ─── 分支 1c: 金融监管壁垒 ───

def _score_financial_moat(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """金融/保险类：网络效应 + 息差管理 + 监管护城河"""
    key_factors = []
    
    mc_yi = features.get("market_cap_yi", 0)
    rg = features.get("revenue_growth", 0) or 0
    gm = features.get("gross_margin", 0) or 0
    om = features.get("operating_margin", 0) or 0
    fcf = features.get("free_cashflow", 0) or 0
    
    # ─── 网络+规模 (0-30) ───
    network_score = 0
    if mc_yi > 5000:
        network_score = 28
        key_factors.append(f"超大金融体 ({mc_yi:.0f}亿) — 网络规模壁垒")
    elif mc_yi > 1000:
        network_score = 20
    elif mc_yi > 200:
        network_score = 12
    else:
        network_score = 6
    
    # ─── 盈利能力 (0-25) ───
    profit_score = 0
    if om > 0.35:
        profit_score = 23
        key_factors.append(f"强运营利润率 ({om*100:.0f}%)")
    elif om > 0.20:
        profit_score = 16
    elif om > 0.10:
        profit_score = 10
    else:
        profit_score = 5
    
    # ─── 增长 (0-20) ───
    growth_score = 0
    if rg > 0.12:
        growth_score = 18
        key_factors.append(f"健康增长 ({rg*100:.0f}%)")
    elif rg > 0.05:
        growth_score = 12
    elif rg > 0:
        growth_score = 7
    else:
        growth_score = 3
    
    # ─── 资本充足 (0-15) ───
    cap_score = 0
    if fcf > 0 and mc_yi > 1000:
        cap_score = 14
        key_factors.append("正向自由现金流 — 资本充足")
    elif fcf > 0:
        cap_score = 10
    else:
        cap_score = 4
    
    # ─── 股息回报 (0-10) ───
    div = features.get("dividend_yield", 0) or 0
    div_score = 0
    if 0.02 < div < 0.05:
        div_score = 9
        key_factors.append(f"合理股息 ({div*100:.1f}%)")
    elif div >= 0.05:
        div_score = 7
    else:
        div_score = 3
    
    raw_score = network_score + profit_score + growth_score + cap_score + div_score
    final_score = max(0, min(100, raw_score))
    
    if final_score >= 70:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"金融质地: 网络={network_score}/30, 盈利={profit_score}/25, "
    rationale += f"增长={growth_score}/20, 资本={cap_score}/15, 股息={div_score}/10 | "
    rationale += f"最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=features.get("evidence_grade", "medium"),
        key_factors=key_factors,
        rationale=rationale,
    )


# ─── 分支 1d: 医疗管线护城河 ───

def _score_healthcare_moat(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """医疗/生物类：管线价值 + 专利护城河 + FDA 壁垒"""
    key_factors = []
    
    rg = features.get("revenue_growth", 0) or 0
    gm = features.get("gross_margin", 0) or 0
    rd = features.get("rd_intensity", 0) or 0
    mc_yi = features.get("market_cap_yi", 0)
    fcf = features.get("free_cashflow", 0) or 0
    
    # ─── 专利+研发壁垒 (0-30) ───
    patent_score = 0
    if rd > 0.20:
        patent_score = 28
        key_factors.append(f"极高研发强度 ({rd*100:.0f}%) — 强管线/专利壁垒")
    elif rd > 0.12:
        patent_score = 20
    elif rd > 0.06:
        patent_score = 12
    else:
        patent_score = 5
    
    # ─── 毛利率=定价权 (0-25) ───
    margin_score = 0
    if gm > 0.70:
        margin_score = 23
        key_factors.append(f"超高毛利率 ({gm*100:.0f}%) — 创新药定价权")
    elif gm > 0.50:
        margin_score = 16
    elif gm > 0.30:
        margin_score = 10
    else:
        margin_score = 5
    
    # ─── 管线成长 (0-20) ───
    pipeline_score = 0
    if rg > 0.20:
        pipeline_score = 18
        key_factors.append(f"高增长 ({rg*100:.0f}%) — 管线释放期")
    elif rg > 0.08:
        pipeline_score = 12
    elif rg > 0:
        pipeline_score = 7
    else:
        pipeline_score = 3
    
    # ─── 财务稳定性 (0-15) ───
    stable_score = 0
    if fcf > 0:
        stable_score = 13
        key_factors.append("正向自由现金流 — 成熟药企")
        if mc_yi > 1000:
            stable_score += 2
    else:
        stable_score = 5
        key_factors.append("FCF 为负 — 研发投入阶段，关注现金消耗")
    
    # ─── 市值背书 (0-10) ───
    size_score = 0
    if mc_yi > 5000:
        size_score = 9
    elif mc_yi > 500:
        size_score = 6
    else:
        size_score = 3
        key_factors.append("小市值生物科技 — 高风险高回报")
    
    raw_score = patent_score + margin_score + pipeline_score + stable_score + size_score
    final_score = max(0, min(100, raw_score))
    
    if final_score >= 70:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"医疗质地: 研发={patent_score}/30, 毛利={margin_score}/25, "
    rationale += f"增长={pipeline_score}/20, 财务={stable_score}/15, 规模={size_score}/10 | "
    rationale += f"最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=features.get("evidence_grade", "medium"),
        key_factors=key_factors,
        rationale=rationale,
    )


# ─── 分支 1e: 平台网络效应 ───

def _score_platform_moat(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """平台/互联网类：双边网络效应 + 数据壁垒 + 切换成本"""
    key_factors = []
    
    rg = features.get("revenue_growth", 0) or 0
    gm = features.get("gross_margin", 0) or 0
    mc_yi = features.get("market_cap_yi", 0)
    fcf = features.get("free_cashflow", 0) or 0
    
    # ─── 网络效应强度 (0-30) ───
    network_score = 0
    if mc_yi > 10000:
        network_score = 28
        key_factors.append(f"超级平台 ({mc_yi:.0f}亿) — 强大网络效应")
    elif mc_yi > 1000:
        network_score = 20
        key_factors.append(f"大型平台 ({mc_yi:.0f}亿) — 网络效应显著")
    elif mc_yi > 100:
        network_score = 12
    else:
        network_score = 6
        key_factors.append("规模较小 — 网络效应待验证")
    
    # ─── 盈利模式 (0-25) ───
    model_score = 0
    if gm > 0.70:
        model_score = 23
        key_factors.append(f"高毛利率 ({gm*100:.0f}%) — 轻资产/高利润模型")
    elif gm > 0.50:
        model_score = 16
    else:
        model_score = 8
    
    # ─── 增长动能 (0-20) ───
    growth_score = 0
    if rg > 0.25:
        growth_score = 18
        key_factors.append(f"高速增长 ({rg*100:.0f}%)")
    elif rg > 0.12:
        growth_score = 12
    elif rg > 0:
        growth_score = 7
    else:
        growth_score = 3
    
    # ─── 现金流质量 (0-15) ───
    cash_score = 0
    if fcf > 0 and gm > 0.60:
        cash_score = 14
        key_factors.append("强 FCF + 高毛利 — 优秀商业模式")
    elif fcf > 0:
        cash_score = 9
    else:
        cash_score = 4
    
    # ─── 护城河宽度 (0-10) ───
    moat_score = 0
    if mc_yi > 5000 and gm > 0.60:
        moat_score = 9
        key_factors.append("大平台+高毛利 — 宽护城河")
    elif mc_yi > 500:
        moat_score = 6
    else:
        moat_score = 3
    
    raw_score = network_score + model_score + growth_score + cash_score + moat_score
    final_score = max(0, min(100, raw_score))
    
    if final_score >= 70:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"平台质地: 网络={network_score}/30, 模式={model_score}/25, "
    rationale += f"增长={growth_score}/20, 现金={cash_score}/15, 护城河={moat_score}/10 | "
    rationale += f"最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=features.get("evidence_grade", "medium"),
        key_factors=key_factors,
        rationale=rationale,
    )


# ─── 分支 1f: 能源资源禀赋 ───
# (energy 类此时已路由到 _score_bottleneck，这是备用逻辑)

def _score_energy_moat(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """能源/资源类：资源禀赋 + 成本曲线位置"""
    return _score_generic_quality(features, user_input)


# ─── 分支 1g: 通用质地评分（兜底）───

def _score_generic_quality(features: Dict, user_input: Dict = None) -> ScoreDetail:
    """通用质地评分：当无法确定行业分类时的兜底逻辑"""
    key_factors = []
    
    rg = features.get("revenue_growth", 0) or 0
    gm = features.get("gross_margin", 0) or 0
    fcf = features.get("free_cashflow", 0) or 0
    mc_yi = features.get("market_cap_yi", 0)
    om = features.get("operating_margin", 0) or 0
    
    # 综合看盈利质量 (0-30)
    profit_score = 0
    if gm > 0.50 and om > 0.15:
        profit_score = 28
        key_factors.append(f"双高毛利 ({gm*100:.0f}%) + 运营利润率 ({om*100:.0f}%)")
    elif gm > 0.30:
        profit_score = 18
    else:
        profit_score = 8
    
    # 增长 (0-25)
    growth_score = 0
    if rg > 0.15:
        growth_score = 22
        key_factors.append(f"增长强劲 ({rg*100:.0f}%)")
    elif rg > 0.05:
        growth_score = 14
    elif rg > 0:
        growth_score = 8
    else:
        growth_score = 4
    
    # 规模 (0-20)
    scale_score = 0
    if mc_yi > 1000:
        scale_score = 18
    elif mc_yi > 100:
        scale_score = 12
    else:
        scale_score = 6
    
    # 现金流 (0-15)
    cash_score = 0
    if fcf > 0:
        cash_score = 13
        key_factors.append("正向自由现金流")
    else:
        cash_score = 5
    
    # 防御性 (0-10)
    def_score = 0
    div = features.get("dividend_yield", 0) or 0
    if div > 0.01:
        def_score = 8
    else:
        def_score = 3
    
    raw_score = profit_score + growth_score + scale_score + cash_score + def_score
    final_score = max(0, min(100, raw_score))
    
    if final_score >= 70:
        signal = Signal.BULLISH
    elif final_score >= 45:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"通用质地: 盈利={profit_score}/30, 增长={growth_score}/25, "
    rationale += f"规模={scale_score}/20, 现金={cash_score}/15, 防御={def_score}/10 | "
    rationale += f"最终{final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="business_quality",
        score=final_score,
        signal=signal,
        weight=0.40,
        evidence_grade=features.get("evidence_grade", "weak"),
        key_factors=key_factors,
        rationale=rationale,
    )


# ═══════════════════════════════════════════════════════════
# 视角 2：宏观轮动 (Macro Rotation) — 30% 权重
# ═══════════════════════════════════════════════════════════

def score_macro(features: Dict, macro_state: Dict = None) -> ScoreDetail:
    """
    宏观周期匹配评分
    
    评分逻辑 (0-100)：
      - 周期匹配 (0-35)：行业与当前宏观象限是否同向
      - 行业趋势 (0-30)：收入增长 + 利润率趋势
      - 资金流向 (0-20)：代理指标
      - 政策方向 (0-15)：产业政策支持度
    """
    key_factors = []
    
    if macro_state is None:
        macro_state = {"quadrant": "宽松中期", "confidence": 0.6}
    
    quadrant = macro_state.get("quadrant", "宽松中期")
    quadrant_info = MACRO_QUADRANTS.get(quadrant, {})
    
    # ─── 1. 周期匹配 (0-35) ───
    cycle_score = 0
    sector = (features.get("sector", "") or "").lower()
    industry = (features.get("industry", "") or "").lower()
    
    growth_favored = ["technology", "semiconductor", "communication", "consumer cyclical",
                      "科技", "半导体", "通信", "消费"]
    value_favored = ["financial", "insurance", "energy", "industrial",
                     "金融", "保险", "能源", "工业"]
    defensive_favored = ["utilities", "consumer defensive", "healthcare",
                         "公用事业", "必选消费", "医疗"]
    
    if quadrant in ["宽松初期", "宽松中期"]:
        if any(s in sector or s in industry for s in growth_favored):
            cycle_score = 30
            key_factors.append(f"成长股适配{quadrant} · 顺风")
        elif any(s in sector or s in industry for s in value_favored):
            cycle_score = 20
            key_factors.append(f"价值股在{quadrant}表现中性")
        else:
            cycle_score = 15
    elif quadrant in ["紧缩初期", "紧缩中期"]:
        if any(s in sector or s in industry for s in value_favored):
            cycle_score = 30
            key_factors.append(f"价值股适配{quadrant} · 逆风中的避风港")
        elif any(s in sector or s in industry for s in growth_favored):
            cycle_score = 10
            key_factors.append(f"成长股在{quadrant}承压")
        else:
            cycle_score = 20
        if any(s in sector or s in industry for s in defensive_favored):
            cycle_score += 5
            key_factors.append("防御板块额外加分")
    elif quadrant in ["过热期", "衰退期"]:
        if any(s in sector or s in industry for s in defensive_favored):
            cycle_score = 30
            key_factors.append(f"防御股适配{quadrant}")
        else:
            cycle_score = 10
            key_factors.append(f"非防御板块在{quadrant}受压")
    else:
        cycle_score = 20
    
    cycle_score = cycle_score * (0.5 + macro_state.get("confidence", 0.6) * 0.5)
    
    # ─── 2. 行业趋势 (0-30) ───
    trend_score = 0
    rg = features.get("revenue_growth", 0) or 0
    gm = features.get("gross_margin", 0) or 0
    
    if rg > 0.20 and gm > 0.40:
        trend_score = 28
        key_factors.append("行业高增长+高毛利 — 健康趋势")
    elif rg > 0.15:
        trend_score = 20
    elif rg > 0:
        trend_score = 12
    else:
        trend_score = 5
        key_factors.append("收入收缩 — 行业逆风")
    
    # ─── 3. 资金流向(代理) (0-20) ───
    flow_score = 0
    pe = features.get("pe_ratio", 0) or 0
    if pe > 0 and pe < 50:
        flow_score += 10
    if rg > 0.15:
        flow_score += 8
    else:
        flow_score += 3
    
    # ─── 4. 政策方向 (0-15) ───
    policy_score = 0
    if features.get("in_ai_chain"):
        policy_score += 8
        key_factors.append("AI 获全球政策支持")
    if features.get("in_ev_chain"):
        policy_score += 5
    if features.get("in_robot_chain"):
        policy_score += 5
    # 医疗政策
    if features.get("industry_category") == "healthcare":
        policy_score += 4
        key_factors.append("医疗健康政策驱动")
    
    final_score = cycle_score + trend_score + flow_score + policy_score
    final_score = max(0, min(100, final_score))
    
    if final_score >= 65:
        signal = Signal.BULLISH
    elif final_score >= 40:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"宏观轮动: 周期={cycle_score:.0f}/35, 趋势={trend_score}/30, "
    rationale += f"资金={flow_score}/20, 政策={policy_score}/15 | "
    rationale += f"总计 {final_score:.0f}/100, 象限={quadrant}"
    
    return ScoreDetail(
        dimension="macro_rotation",
        score=final_score,
        signal=signal,
        weight=0.30,
        evidence_grade="medium",
        key_factors=key_factors,
        rationale=rationale,
    )


# ═══════════════════════════════════════════════════════════
# 视角 3：技术趋势 (Technical Trend) — 30% 权重
# ═══════════════════════════════════════════════════════════

def score_technical(features: Dict, price_data: Dict = None) -> ScoreDetail:
    """
    技术趋势评分
    
    评分逻辑 (0-100)：
      - 趋势方向 (0-30)：MA 多头排列/价格趋势
      - 动量信号 (0-25)：RSI/MACD 位置
      - 量价配合 (0-20)：上涨放量/背离检测
      - 波动性 (0-15)：ATR 与入场时机
      - 乖离率 (0-10)：距均线远近
    """
    key_factors = []
    
    has_price = price_data is not None and len(price_data) > 0
    rg = features.get("revenue_growth", 0) or 0
    
    if has_price:
        trend_score = _calc_trend_score(price_data, key_factors)
        momentum_score = _calc_momentum_score(price_data, key_factors)
        volume_score = _calc_volume_score(price_data, key_factors)
        vol_score = _calc_volatility_score(price_data, key_factors)
        deviation_score = _calc_deviation_score(price_data, key_factors)
    else:
        trend_score = 12
        momentum_score = 10
        volume_score = 8
        vol_score = 8
        deviation_score = 5
        key_factors.append("无实时价格数据，使用财务代理评分（保守估计）")
        if rg > 0.20:
            trend_score += 5
            key_factors.append("高增长基本面支撑趋势判断")
    
    final_score = trend_score + momentum_score + volume_score + vol_score + deviation_score
    final_score = max(0, min(100, final_score))
    
    if final_score >= 65:
        signal = Signal.BULLISH
    elif final_score >= 40:
        signal = Signal.NEUTRAL
    else:
        signal = Signal.BEARISH
    
    rationale = f"技术趋势: 方向={trend_score}/30, 动量={momentum_score}/25, "
    rationale += f"量价={volume_score}/20, 波动={vol_score}/15, 乖离={deviation_score}/10 | "
    rationale += f"总计 {final_score:.0f}/100"
    
    return ScoreDetail(
        dimension="technical_trend",
        score=final_score,
        signal=signal,
        weight=0.30,
        evidence_grade="medium",
        key_factors=key_factors,
        rationale=rationale,
    )


# ─── 技术评分辅助函数 ───

def _calc_trend_score(price_data: Dict, key_factors: List[str]) -> int:
    changes = price_data.get("price_changes", [])
    if not changes:
        return 12
    
    ma20 = price_data.get("ma20", 0)
    close = price_data.get("close", 0)
    ma50 = price_data.get("ma50", 0)
    ma200 = price_data.get("ma200", 0)
    
    bull_aligned = (ma20 > ma50 > ma200) if (ma20 and ma50 and ma200) else False
    if bull_aligned:
        key_factors.append(f"MA 多头排列 (m20>{ma50:.2f}>{ma200:.2f})")
        return 28
    elif ma20 > ma50:
        key_factors.append("短期均线向上")
        return 20
    elif ma20 > 0:
        key_factors.append("均线方向中性")
        return 12
    else:
        return 10

def _calc_momentum_score(price_data: Dict, key_factors: List[str]) -> int:
    rsi = price_data.get("rsi_14", 50)
    if rsi > 70:
        key_factors.append(f"RSI={rsi:.0f} — 超买")
        return 8
    elif rsi > 55:
        key_factors.append(f"RSI={rsi:.0f} — 多头健康")
        return 22
    elif rsi > 40:
        key_factors.append(f"RSI={rsi:.0f} — 中性")
        return 14
    elif rsi > 25:
        key_factors.append(f"RSI={rsi:.0f} — 超卖")
        return 10
    else:
        key_factors.append(f"RSI={rsi:.0f} — 深度超卖")
        return 6

def _calc_volume_score(price_data: Dict, key_factors: List[str]) -> int:
    vol_trend = price_data.get("volume_trend", "neutral")
    vol_ratio = price_data.get("volume_ratio", 1.0)
    if vol_trend == "rising" and vol_ratio > 1.5:
        key_factors.append(f"量能放大 {vol_ratio:.1f}×")
        return 20
    elif vol_trend == "rising":
        return 15
    elif vol_trend == "declining":
        key_factors.append("量能萎缩")
        return 8
    else:
        return 10

def _calc_volatility_score(price_data: Dict, key_factors: List[str]) -> int:
    atr_pct = price_data.get("atr_pct", 0)
    if atr_pct == 0:
        return 8
    elif atr_pct < 0.02:
        key_factors.append(f"低波动 (ATR={atr_pct:.1%})")
        return 15
    elif atr_pct < 0.04:
        key_factors.append(f"中波动 (ATR={atr_pct:.1%})")
        return 10
    else:
        key_factors.append(f"高波动 (ATR={atr_pct:.1%})")
        return 5

def _calc_deviation_score(price_data: Dict, key_factors: List[str]) -> int:
    deviation = price_data.get("ma20_deviation", 0)
    if deviation == 0:
        return 5
    dev_abs = abs(deviation)
    if dev_abs < 5:
        return 10
    elif dev_abs < 10:
        return 7
    elif dev_abs < 20:
        key_factors.append(f"乖离 {deviation:.1f}%")
        return 4
    else:
        key_factors.append(f"大乖离 {deviation:.1f}%")
        return 2
