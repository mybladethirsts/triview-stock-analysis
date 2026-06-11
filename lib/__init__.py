#!/usr/bin/env python3
"""
Triview — 三视股票分析核心框架

三维独立评估体系：
  1. 标的质地 (Business Quality) — 护城河/商业模式/定价权（按行业分支评估）
  2. 宏观轮动 (Macro Rotation) — 宏观象限匹配与资金流向
  3. 技术趋势 (Technical Trend) — 量价关系与趋势信号

每一维独立生成评分(0-100)、信号(bullish/neutral/bearish)和论证，
最后由共识引擎按权重(40/30/30)合成最终 verdict。

适用于所有行业：制造业/科技走供应链卡位分析，消费走品牌护城河，
金融看网络效应和监管壁垒，医疗看管线价值，平台看双边网络效应。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json


class Signal(Enum):
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    SKIP = "skip"


@dataclass
class ScoreDetail:
    """单项评分的完整记录"""
    dimension: str
    score: float              # 0-100
    signal: Signal
    weight: float             # 全局权重
    evidence_grade: str       # strong / medium / weak
    key_factors: List[str]    # 关键判断因子
    rationale: str            # 推理过程
    penalty_total: float = 0.0  # 罚分累计
    raw_score: float = 0.0   # 罚分前的原始分

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "score": round(self.score, 1),
            "signal": self.signal.value,
            "weight": self.weight,
            "evidence_grade": self.evidence_grade,
            "key_factors": self.key_factors,
            "rationale": self.rationale,
            "penalty_total": round(self.penalty_total, 2),
            "raw_score": round(self.raw_score, 1),
        }


@dataclass
class Consensus:
    """三维共识结果"""
    scores: Dict[str, ScoreDetail]
    weighted_total: float
    overall_signal: Signal
    verdict: str
    self_review: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "perspectives": {k: v.to_dict() for k, v in self.scores.items()},
            "weighted_total": round(self.weighted_total, 1),
            "overall_signal": self.overall_signal.value,
            "verdict": self.verdict,
            "self_review": self.self_review,
        }


# ─── 行业分类 ──────────────────────────────────────────
# 用于将第一维（标的质地）路由到不同的评分分支
INDUSTRY_CATEGORIES = {
    "manufacturing": {  # 制造/科技/硬件 —— 供应链卡位分析
        "keywords": ["semiconductor", "chip", "manufacturing", "industrial", "hardware",
                      "equipment", "machinery", "auto", "aerospace", "chemical",
                      "半导体", "芯片", "制造", "工业", "硬件", "设备", "机械",
                      "汽车", "航空", "化工", "材料"],
        "description": "制造业/科技硬件，走供应链卡位分析",
    },
    "consumer": {  # 消费/品牌 —— 品牌护城河分析
        "keywords": ["consumer", "retail", "brand", "beverage", "food", "apparel",
                      "household", "personal", "tobacco", "gaming",
                      "消费", "零售", "品牌", "饮料", "食品", "服装",
                      "家居", "个人护理", "烟草"],
        "description": "消费/品牌，走品牌护城河分析",
    },
    "financial": {  # 金融/保险 —— 网络+监管壁垒
        "keywords": ["bank", "financial", "insurance", "broker", "asset management",
                      "investment", "fintech", "exchange",
                      "银行", "金融", "保险", "券商", "资产管理",
                      "投资", "交易所"],
        "description": "金融/保险，走网络+监管壁垒分析",
    },
    "healthcare": {  # 医疗/生物 —— 管线+专利分析
        "keywords": ["healthcare", "pharma", "biotech", "medical", "device",
                      "diagnostic", "hospital", "drug", "therapeutic", "clinical",
                      "医疗", "制药", "生物技术", "医疗器械", "诊断",
                      "医院", "药物", "临床"],
        "description": "医疗/生物，走管线+专利护城河分析",
    },
    "energy": {  # 能源/大宗 —— 资源+成本分析
        "keywords": ["energy", "oil", "gas", "mining", "utility", "renewable",
                      "solar", "wind", "nuclear", "电力", "能源", "石油",
                      "天然气", "矿业", "公用事业", "可再生能源", "光伏", "风电"],
        "description": "能源/大宗，走资源禀赋+成本曲线分析",
    },
    "platform": {  # 平台/互联网 —— 网络效应+数据壁垒
        "keywords": ["software", "internet", "platform", "cloud", "saas", "social",
                      "e-commerce", "marketplace", "search", "advertising",
                      "软件", "互联网", "平台", "云", "社交", "电商",
                      "搜索", "广告", "SaaS"],
        "description": "平台/互联网，走网络效应+数据壁垒分析",
    },
}

DIMENSION_KEYS = {
    "business_quality": "business_quality",
    "macro_rotation": "macro_rotation",
    "technical_trend": "technical_trend",
}

DIMENSION_NICKNAMES = {
    "business_quality": "标的质地",
    "macro_rotation": "宏观轮动",
    "technical_trend": "技术趋势",
}

# ─── 证据阶梯 ──────────────────────────────────────────
EVIDENCE_LADDER = {
    "strong": {
        "multiplier": 1.0,
        "sources": ["财报/季报", "交易所公告", "客户定点/长协订单", "FDA/监管批准",
                     "专利授权", "量产交付公告", "官方产能指引", "IPO/增发招股书"],
        "description": "有可靠来源可验证的硬证据",
    },
    "medium": {
        "multiplier": 0.85,
        "sources": ["卖方研报(有可见假设)", "权威财经媒体一手报道", "行业协会数据",
                     "管理层公开表态(earnings call)", "工商/海关数据"],
        "description": "有合理推断但非第一手确认",
    },
    "weak": {
        "multiplier": 0.70,
        "sources": ["社交媒体/论坛", "自媒体", "不具名渠道", "截图/传言",
                     "仅情绪面推断"],
        "description": "仅有叙事，无硬证据支撑",
    },
}


# ─── 护城河类型 ─────────────────────────────────────────
MOAT_TYPES = {
    "品牌护城河": "消费者愿意为品牌支付溢价，复购率高，难替代",
    "网络效应": "用户越多价值越大，形成自然垄断",
    "规模效应": "成本随规模下降，对手难以追赶",
    "切换成本": "用户离开成本高，锁定效应强",
    "IP/专利壁垒": "技术受法律保护，竞争对手无法复制",
    "监管/牌照壁垒": "行业准入受限，现有玩家享有保护",
    "数据壁垒": "数据积累改进产品，形成反馈飞轮",
    "资源禀赋": "拥有稀缺自然资源或地理位置优势",
}

# ─── 八类罚分因子 ──────────────────────────────────────
PENALTY_FACTORS = {
    "炒作无订单": {"trigger": "高热度+零硬证据", "max_penalty": 0.20},
    "微盘流动性": {"trigger": "市值<30亿(出不来货)", "max_penalty": 0.15},
    "会计/杀猪盘": {"trigger": "财务可疑/异常关联交易/revenue quality差", "max_penalty": 0.20},
    "治理风险": {"trigger": "实控人质押比例高/频繁减持", "max_penalty": 0.15},
    "周期陷阱": {"trigger": "纯周期行业(非真成长瓶颈)", "max_penalty": 0.15},
    "替代风险": {"trigger": "技术路线竞争/新材料方案", "max_penalty": 0.15},
    "地缘风险": {"trigger": "出口管制/制裁且无替代叙事", "max_penalty": 0.10},
    "稀释风险": {"trigger": "近期大规模定增/增发/解禁", "max_penalty": 0.15},
}


# ─── 供应链八层分层 ────────────────────────────────────
SUPPLY_CHAIN_TIERS = [
    ("材料耗材", 1.00),
    ("制程/封装", 0.92),
    ("设备/测试", 0.85),
    ("芯片/器件", 0.78),
    ("基础设施", 0.70),
    ("模块/子系统", 0.62),
    ("系统集成", 0.50),
    ("下游需求", 0.40),
]


# ─── 宏观象限 ──────────────────────────────────────────
MACRO_QUADRANTS = {
    "宽松初期": {"特征": "利率下行、流动性改善", "适配": "成长股/科技股/小盘股"},
    "宽松中期": {"特征": "需求复苏、盈利改善", "适配": "周期/消费/价值"},
    "过热期": {"特征": "通胀上行、估值高企", "适配": "防御/商品/现金"},
    "紧缩初期": {"特征": "利率上行、流动性收紧", "适配": "减持成长/增持价值"},
    "紧缩中期": {"特征": "需求下滑、盈利恶化", "适配": "防御/现金/债券"},
    "衰退期": {"特征": "利率快速下行、避险", "适配": "国债/黄金/防御"},
}


# ─── 技术市场日分类 ────────────────────────────────────
MARKET_DAY_TYPES = {
    "趋势日": "价格单向运动，跟随趋势持仓",
    "区间日": "价格区间震荡，低买高卖",
    "事件日": "催化剂落地(财报/FOMC/CPI)，等 30min 再动",
    "破线日": "关键支撑/阻力突破，跟随方向",
    "转换日": "市场等新催化剂，空仓观望",
}
