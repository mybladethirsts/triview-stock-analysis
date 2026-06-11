#!/usr/bin/env python3
"""
Triview — 特征提取引擎

从基础财务数据、市场数据和行业标签中，提取三大视角所需的评分特征。
尊重隐私：所有数据通过本地 API 或用户提供，不外传。
"""

from typing import Dict, Optional
import re


def normalize_ticker(ticker: str, market: str) -> str:
    """标准化 ticker 为通用格式"""
    t = ticker.strip().upper()
    if market == "hk":
        if not t.endswith(".HK"):
            t = t.zfill(5) + ".HK"
    elif market == "a-share":
        if "." not in t:
            t = t.zfill(6)
            if t.startswith(("6", "9")):
                t += ".SS"
            elif t.startswith(("0", "3")):
                t += ".SZ"
            elif t.startswith(("8", "4")):
                t += ".BJ"
            else:
                t += ".SS"
    return t


def extract_market_from_ticker(ticker: str) -> str:
    """从 ticker 推断市场"""
    t = ticker.strip().upper()
    if t.endswith(".HK"):
        return "hk"
    if t.endswith((".SS", ".SZ", ".BJ", ".SH")):
        return "a-share"
    return "us"


def classify_industry_category(industry: str, sector: str, business_summary: str = "") -> str:
    """
    行业分类路由：将行业映射到评分分支类别
    
    返回: manufacturing / consumer / financial / healthcare / energy / platform / other
    """
    text = f"{industry} {sector} {business_summary}".lower()
    
    # 内联关键字映射（与 __init__.py 保持一致，避免循环导入）
    categories = {
        "manufacturing": ["semiconductor", "chip", "manufacturing", "industrial", "hardware",
                          "equipment", "machinery", "auto", "aerospace", "chemical",
                          "半导体", "芯片", "制造", "工业", "硬件", "设备", "机械",
                          "汽车", "航空", "化工", "材料"],
        "consumer": ["consumer", "retail", "brand", "beverage", "food", "apparel",
                     "household", "personal", "tobacco", "gaming",
                     "消费", "零售", "品牌", "饮料", "食品", "服装",
                     "家居", "个人护理", "烟草"],
        "financial": ["bank", "financial", "insurance", "broker", "asset management",
                      "investment", "fintech", "exchange",
                      "银行", "金融", "保险", "券商", "资产管理",
                      "投资", "交易所"],
        "healthcare": ["healthcare", "pharma", "biotech", "medical", "device",
                       "diagnostic", "hospital", "drug", "therapeutic", "clinical",
                       "医疗", "制药", "生物技术", "医疗器械", "诊断",
                       "医院", "药物", "临床"],
        "energy": ["energy", "oil", "gas", "mining", "utility", "renewable",
                   "solar", "wind", "nuclear",
                   "电力", "能源", "石油", "天然气", "矿业", "公用事业",
                   "可再生能源", "光伏", "风电", "核电"],
        "platform": ["software", "internet", "platform", "cloud", "saas", "social",
                     "e-commerce", "marketplace", "search", "advertising",
                     "软件", "互联网", "平台", "云", "社交", "电商",
                     "搜索", "广告"],
    }
    
    for category, keywords in categories.items():
        if any(kw in text for kw in keywords):
            return category
    
    return "other"


def classify_industry(industry: str, sector: str) -> Dict[str, bool]:
    """行业标签分类，用于 AI 供应链检测"""
    tags = {}
    text = f"{industry} {sector}".lower()
    
    ai_keywords = [
        "semiconductor", "chip", "ai", "optical", "fiber", "laser",
        "photonic", "quantum", "datacenter", "cloud", "network",
        "storage", "memory", "gpu", "cpu", "hpc", "connector",
        "packaging", "substrate", "wafer", "epitaxy", "crystal",
        "semiconductor equipment", "semiconductor materials",
        "半导体", "芯片", "光模块", "光通信", "光电子", "AI", "人工智能",
        "算力", "数据中心", "存储", "封装", "衬底", "外延",
    ]
    
    robot_keywords = [
        "robot", "automation", "servo", "motor", "reducer", "sensor",
        "actuator", "encoder", "机器人", "减速器", "伺服", "传感器",
        "灵巧手", "力矩",
    ]
    
    ev_keywords = [
        "electric vehicle", "ev", "battery", "lithium", "charging",
        "inverter", "power electronics", "新能源", "电动车",
        "锂电池", "固态电池", "充电桩",
    ]
    
    tags["in_ai_chain"] = any(kw in text for kw in ai_keywords)
    tags["in_robot_chain"] = any(kw in text for kw in robot_keywords)
    tags["in_ev_chain"] = any(kw in text for kw in ev_keywords)
    tags["is_tech"] = tags["in_ai_chain"] or tags["in_robot_chain"] or tags["in_ev_chain"]
    
    return tags


def estimate_evidence_grade(info: Dict, industry_tags: Dict) -> str:
    """根据可获取的数据源评估证据等级"""
    has_revenue = info.get("totalRevenue", 0) > 0
    has_cashflow = info.get("operatingCashFlow", 0) != 0
    has_guidance = bool(info.get("recommendationKey"))
    
    if has_revenue and has_cashflow:
        return "strong"
    elif has_revenue:
        return "medium"
    else:
        return "weak"


def estimate_supply_chain_tier(info: Dict, industry_tags: Dict) -> tuple:
    """估计供应链层级。取最上游命中的层"""
    desc = f"{info.get('industry', '')} {info.get('sector', '')} {info.get('longBusinessSummary', '')}"
    desc_lower = desc.lower()
    
    tiers = [
        ("材料耗材", ["material", "wafer", "substrate", "chemical", "gas", "ingot",
                       "材料", "衬底", "晶棒", "化学品", "气体", "耗材"]),
        ("制程/封装", ["foundry", "packaging", "assembly", "test", "osat", "coating",
                        "代工", "封装", "封测", "制程", "镀膜"]),
        ("设备/测试", ["equipment", "inspection", "metrology", "lithography", "etch",
                        "etching", "deposition", "设备", "检测", "量测", "光刻"]),
        ("芯片/器件", ["chip", "device", "module", "component", "sensor", "laser",
                        "led", "diode", "transceiver", "芯片", "器件", "模块", "传感器"]),
        ("基础设施", ["infrastructure", "data center", "network", "fiber", "cable",
                       "基础设施", "数据中心", "光纤", "线缆"]),
        ("模块/子系统", ["subsystem", "board", "pcie", "memory module",
                          "子系统", "板卡", "模组"]),
        ("系统集成", ["system", "integration", "oem", "整机", "系统", "集成"]),
        ("下游需求", ["application", "software", "platform", "service",
                       "应用", "软件", "平台", "服务"]),
    ]
    
    tier_weights = {
        "材料耗材": 1.00, "制程/封装": 0.92, "设备/测试": 0.85,
        "芯片/器件": 0.78, "基础设施": 0.70, "模块/子系统": 0.62,
        "系统集成": 0.50, "下游需求": 0.40,
    }
    
    for name, keywords in tiers:
        if any(kw in desc_lower for kw in keywords):
            return name, tier_weights.get(name, 0.50)
    
    return ("未分类", 0.50)


def extract_features(info: Dict, user_description: str = "") -> Dict:
    """从基础数据和用户描述中提取核心特征"""
    
    industry = info.get("industry", "") or ""
    sector = info.get("sector", "") or ""
    desc = info.get("longBusinessSummary", "") or user_description
    
    industry_tags = classify_industry(industry + " " + sector + " " + desc, sector)
    industry_category = classify_industry_category(industry, sector, desc)
    evidence = estimate_evidence_grade(info, industry_tags)
    tier_name, tier_weight = estimate_supply_chain_tier(info, industry_tags)
    
    market_cap = info.get("marketCap", 0)
    
    features = {
        # 基础
        "name": info.get("longName", ""),
        "market_cap": market_cap,
        "market_cap_yi": round(market_cap / 1e8, 2) if market_cap else 0,
        "is_smallcap": market_cap < 3e10 if market_cap else False,
        "industry": industry,
        "sector": sector,
        
        # 行业分类
        "industry_category": industry_category,
        "industry_tags": industry_tags,
        "in_ai_chain": industry_tags["in_ai_chain"],
        "in_robot_chain": industry_tags["in_robot_chain"],
        "in_ev_chain": industry_tags["in_ev_chain"],
        "is_tech": industry_tags["is_tech"],
        
        # 证据与供应链
        "evidence_grade": evidence,
        "supply_chain_tier": tier_name,
        "tier_weight": tier_weight,
        
        # 财务
        "gross_margin": info.get("grossMargins", 0),
        "operating_margin": info.get("operatingMargins", 0),
        "revenue": info.get("totalRevenue", 0),
        "revenue_growth": info.get("revenueGrowth", 0),
        "net_income": info.get("netIncomeToCommon", 0),
        "free_cashflow": info.get("freeCashflow", 0),
        "rd_spend": info.get("researchDevelopment", 0),
        "capex": info.get("capitalExpenditures", 0),
        "pe_ratio": info.get("trailingPE", 0),
        "forward_pe": info.get("forwardPE", 0),
        "ps_ratio": info.get("priceToSalesTrailing12Months", 0),
        "pb_ratio": info.get("priceToBook", 0),
        "dividend_yield": info.get("dividendYield", 0),
    }
    
    # 衍生指标
    if features["revenue"] and features["revenue"] > 0:
        features["rd_intensity"] = features["rd_spend"] / features["revenue"] if features["rd_spend"] else 0
        features["fcf_yield"] = features["free_cashflow"] / features["revenue"] if features["free_cashflow"] else 0
    else:
        features["rd_intensity"] = 0
        features["fcf_yield"] = 0
    
    return features
