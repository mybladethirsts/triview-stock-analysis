#!/usr/bin/env python3
"""
Fetch A-share stock data for multi-market-stock-analysis skill.

Usage:
    python3 fetch_ashare_data.py --ticker 300750 --days 252

Note:
    Ticker format:
    - Shanghai (沪市): 6XXXXX -> 6XXXXX.SS (e.g., 600519.SS for 贵州茅台)
    - Shenzhen (深市): 0XXXXX or 3XXXXX -> XXXXX.SZ (e.g., 000001.SZ for 平安银行, 300750.SZ for 宁德时代)
    - STAR Market (科创板): 68XXXX -> 688XXX.SS (e.g., 688981.SS for 中芯国际)
    - Beijing Stock Exchange (北交所): 8XXXXX or 4XXXXX -> XXXXX.BJ (e.g., 835185.BJ for 贝特瑞)

    Dependencies: pip install yfinance pandas
"""

import argparse
import sys
import json
from datetime import datetime, timedelta

def parse_args():
    parser = argparse.ArgumentParser(description="Fetch A-share stock data")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker (e.g., 300750 for 宁德时代, 600519 for 贵州茅台)")
    parser.add_argument("--days", type=int, default=252, help="Number of trading days to fetch (default: 252)")
    return parser.parse_args()

def normalize_ticker(ticker):
    """Normalize A-share ticker to yfinance format."""
    ticker = ticker.strip()
    
    # If already has suffix, return as-is
    if '.' in ticker:
        return ticker.upper()
    
    # Add suffix based on ticker prefix
    ticker = ticker.zfill(6)  # Pad to 6 digits
    
    if ticker.startswith('6'):  # Shanghai
        return f"{ticker}.SS"
    elif ticker.startswith(('0', '3')):  # Shenzhen (main board + ChiNext)
        return f"{ticker}.SZ"
    elif ticker.startswith('8') or ticker.startswith('4'):  # Beijing Stock Exchange
        return f"{ticker}.BJ"
    else:
        # Default to Shanghai
        return f"{ticker}.SS"

def fetch_ashare_data(ticker, days=252):
    """
    Fetch A-share stock data using yfinance.
    Returns dict with price, volume, fundamentals.
    """
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print(json.dumps({"status": "error", "message": "Missing dependency: pip install yfinance pandas"}))
        sys.exit(1)
    
    # Normalize ticker
    ticker_norm = normalize_ticker(ticker)
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days*2)  # approximate, will filter later
    
    # Fetch data
    try:
        ticker_obj = yf.Ticker(ticker_norm)
        df = ticker_obj.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        
        if df.empty:
            return {"status": "error", "message": f"No data found for ticker {ticker} (normalized to {ticker_norm})"}
        
        # Limit to last N days
        df = df.tail(days)
        
        # Calculate ATR
        df['tr1'] = df['High'] - df['Low']
        df['tr2'] = abs(df['High'] - df['Close'].shift(1))
        df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # Get latest data
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else None
        
        result = {
            "status": "ok",
            "ticker": ticker,
            "ticker_normalized": ticker_norm,
            "currency": "CNY",
            "days_fetched": len(df),
            "latest": {
                "date": df.index[-1].strftime("%Y-%m-%d"),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "close": float(latest['Close']),
                "volume": int(latest['Volume']),
                "atr": float(latest['atr']) if not pd.isna(latest['atr']) else None,
            },
            "prev_close": float(prev['Close']) if prev is not None else None,
            "change_pct": float((latest['Close'] - prev['Close']) / prev['Close'] * 100) if prev is not None else None,
            "avg_volume_20d": float(df['Volume'].tail(20).mean()),
            "volatility_20d": float(df['Close'].pct_change().tail(20).std() * (252**0.5) * 100),  # Annualized
        }
        
        # Fetch fundamentals
        try:
            info = ticker_obj.info
            result["fundamentals"] = {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                "pb_ratio": info.get("priceToBook"),
                "revenue_growth": info.get("revenueGrowth"),
                "gross_margin": info.get("grossMargins"),
                "operating_margin": info.get("operatingMargins"),
                "profit_margin": info.get("profitMargins"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
            }
        except Exception as e:
            result["fundamentals"] = {"error": str(e)}
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    args = parse_args()
    result = fetch_ashare_data(args.ticker, args.days)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
