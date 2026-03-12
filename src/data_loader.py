from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pandas as pd
import yfinance as yf
import numpy as np

def time_to_expiry_years(expiry: str) -> float:
    ny_tz = ZoneInfo("America/New_York")
    utc_tz = ZoneInfo("UTC")

    # Treat expiry as 4:00 PM New York time
    expiry_dt_ny = datetime.strptime(expiry, "%Y-%m-%d").replace(
        hour=16,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=ny_tz
    )

    now_utc = datetime.now(utc_tz)
    expiry_dt_utc = expiry_dt_ny.astimezone(utc_tz)

    T = (expiry_dt_utc - now_utc).total_seconds() / (365.0 * 24 * 3600)
    return T

def get_spot_price(ticker: str, period: str = "6mo") -> float:
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval="1d")
    return float(hist["Close"].dropna().iloc[-1])

def get_expiries(ticker: str):
    t = yf.Ticker(ticker)
    return t.options

def get_option_chain(ticker: str, expiry: str):
    t = yf.Ticker(ticker)
    chain = t.option_chain(expiry)
    return chain.calls.copy(), chain.puts.copy()

def prepare_option_table(df: pd.DataFrame, option_type: str, S: float, expiry: str) -> pd.DataFrame:
    out = df.copy()

    numeric_cols = ["strike", "lastPrice", "bid", "ask", "impliedVolatility", "openInterest", "volume"]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["mid"] = (out["bid"] + out["ask"]) / 2
    out["mid"] = out["mid"].where(out["mid"].notna(), out["lastPrice"])

    T = time_to_expiry_years(expiry)

    out["option_type"] = option_type
    out["S"] = S
    out["expiry"] = expiry
    out["T"] = T

    return out

def build_options_dataframe(ticker: str, expiry: str) -> pd.DataFrame:
    S = get_spot_price(ticker)
    calls, puts = get_option_chain(ticker, expiry)

    calls_clean = prepare_option_table(calls, "call", S, expiry)
    puts_clean = prepare_option_table(puts, "put", S, expiry)

    options_df = pd.concat([calls_clean, puts_clean], ignore_index=True)
    return options_df

def get_underlying_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval=interval)
    return hist.copy()

def compute_log_returns(close_prices: pd.Series) -> pd.Series:
    return np.log(close_prices / close_prices.shift(1))

def compute_rolling_hist_vol(close_prices: pd.Series, window: int = 30, trading_days: int = 252) -> pd.Series:
    log_returns = compute_log_returns(close_prices)
    rolling_std = log_returns.rolling(window=window).std()
    hist_vol = rolling_std * np.sqrt(trading_days)
    return hist_vol


