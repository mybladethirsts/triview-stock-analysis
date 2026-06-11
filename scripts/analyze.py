#!/usr/bin/env python3
"""
Triview — 三视股票分析

用法:
  python3 scripts/analyze.py NVDA
  python3 scripts/analyze.py 300750 --market a-share
  python3 scripts/analyze.py 0700.HK --market hk
  python3 scripts/analyze.py NVDA --json      # JSON 格式输出
  python3 scripts/analyze.py NVDA --summary   # 仅摘要
  
依赖: pip install yfinance
"""

import argparse
import sys
import json

# 将 lib 目录加入路径
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.features import normalize_ticker, extract_market_from_ticker, extract_features
from lib.consensus import run_analysis
from lib.report import generate_report, format_summary


def parse_args():
    parser = argparse.ArgumentParser(
        description="Triview — 三视股票分析",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/analyze.py NVDA                          # 美股分析
  python3 scripts/analyze.py 300750 --market a-share       # A 股分析
  python3 scripts/analyze.py 0700.HK                       # 港股分析
  python3 scripts/analyze.py NVDA --json                   # JSON 输出
  python3 scripts/analyze.py NVDA --summary                # 简短摘要
  python3 scripts/analyze.py NVDA --macro 宽松初期         # 指定宏观象限
        """,
    )
    parser.add_argument("ticker", type=str, help="股票代码 (e.g., NVDA, 300750, 0700.HK)")
    parser.add_argument("--market", type=str, choices=["us", "hk", "a-share", "auto"],
                        default="auto", help="市场 (默认 auto: 自动识别)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--summary", action="store_true", help="仅输出简短摘要")
    parser.add_argument("--macro", type=str, default=None,
                        help="宏观象限 (宽松初期/宽松中期/过热期/紧缩初期/紧缩中期/衰退期)")
    parser.add_argument("--company", type=str, default="", help="公司名称/描述 (无数据时使用)")
    return parser.parse_args()


def fetch_data(ticker_norm: str, market: str) -> dict:
    """获取股票基础数据"""
    try:
        import yfinance as yf
        obj = yf.Ticker(ticker_norm)
        info = obj.info
        if not info or info.get("regularMarketPrice") is None:
            # 可能 ticker 格式不对，尝试去掉后缀
            if market == "hk":
                alt = ticker_norm.replace(".HK", "")
                obj = yf.Ticker(alt)
                info = obj.info
            elif market == "a-share":
                # A 股通过 yfinance 获取的数据有限
                pass
        return info if info else {}
    except ImportError:
        print("⚠️ 需要安装 yfinance: pip install yfinance", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"⚠️ 数据获取失败: {e}", file=sys.stderr)
        return {}


def main():
    args = parse_args()
    
    # ── 确定市场 ──
    market = args.market
    if market == "auto":
        market = extract_market_from_ticker(args.ticker)
    
    # ── 标准化 ticker ──
    ticker_norm = normalize_ticker(args.ticker, market)
    
    # ── 获取基础数据 ──
    info = fetch_data(ticker_norm, market)
    
    # ── 提取特征 ──
    features = extract_features(info, args.company)
    
    # ── 宏观状态 ──
    macro_state = None
    if args.macro:
        macro_state = {"quadrant": args.macro, "confidence": 0.7}
    
    # ── 运行分析 ──
    consensus = run_analysis(features, macro_state=macro_state)
    
    # ── 输出 ──
    if args.json:
        output = {
            "ticker": args.ticker,
            "market": market,
            "features": {k: v for k, v in features.items()
                         if isinstance(v, (str, int, float, bool))},
            "analysis": consensus.to_dict(),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    elif args.summary:
        print(format_summary(consensus, args.ticker))
    else:
        report = generate_report(consensus, features, ticker=args.ticker, market=market)
        print(report)


if __name__ == "__main__":
    main()
