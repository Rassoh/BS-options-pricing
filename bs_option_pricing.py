import math
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import yfinance as yf
## Hardcoding variables to test the function using Nvidias option data today
# S = 177.88
# K = 115
# T = 1/365
# r = 0.05
# sigma = 2.6


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def calculate_d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    numerator = math.log(S/K) +(r+sigma**2/2)*T 
    denominator = sigma*T**0.5
    return numerator/denominator

def calculate_d2(S: float, K: float, T:float, sigma: float, r:float) -> float:
    d1 = calculate_d1(S, K, T, r, sigma)
    return d1 - sigma*T**0.5

def black_scholes_price(
        S:float,
        K:float,
        T:float,
        r:float,
        sigma:float,
        option_type:str = "call"
) -> float:
    
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        raise ValueError("S, K, T, and sigma must be positive numbers.")
    
    d1 = calculate_d1(S,K,T,r,sigma)
    d2 = calculate_d2(S,K,T,r,sigma)
    if option_type.lower() == "call":
        price = S * normal_cdf(d1) - K * math.exp(-r*T) * normal_cdf(d2)
    elif option_type.lower() == "put":
        price = K * math.exp(-r*T) * normal_cdf(-d2) - S *normal_cdf(-d1)
    else: 
        raise ValueError("option_type must be 'call' or 'put'")
    
    return price 
    

ticker = "NVDA"
t =  yf.Ticker(ticker)
history = t.history(period="6mo", interval="1d")
S = float(history["Close"].dropna().iloc[-1])
expiries = t.options 
expiry = expiries[0]
options_chain = t.option_chain(expiry)
calls = options_chain.calls.copy()
puts = options_chain.puts.copy()

def prepare_option_data(
        df: pd.DataFrame, option_type: str, 
        S: float, expiry: str) -> pd.DataFrame:
    
    out = df.copy() 

    #Convert numeric columns first 
    numeric_cols =  ["strike", "lastPrice", "bid", "ask", "impliedVolatility",
                     "openInterest", "volume"]
    for col in numeric_cols:
        if col in out.columns: 
            out[col] = pd.to_numeric(out[col], errors="coerce") 
    # compute mid price 
    out["mid"] = (out["bid"] + out["ask"])/2 

    #fallback to last price if mid is not available
    out["mid"] = out["mid"].fillna(out["lastPrice"])

    #metadata
    out["option_type"] = option_type
    out["S"] = S
    out["expiry"] = expiry

    #time calculation/conversion
    valuation_dt = datetime.now(timezone.utc)
    expiry_dt = datetime.strptime(expiry, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    T = (expiry_dt - valuation_dt).total_seconds() / (365*24*3600)
    out["T"] = T

    return out

calls_clean= prepare_option_data(calls, "call", S, expiry)
puts_clean = prepare_option_data(puts, "put", S, expiry)

options_df = pd.concat([calls_clean, puts_clean], ignore_index=True)
# print(options_df.head())

r = 0.04
options_df["r"] = r

options_df["K"] = options_df["strike"]
options_df["sigma"] = options_df["impliedVolatility"]

cols = ["contractSymbol", "option_type", "S", "K", "T", "r", 
        "sigma", "bid", "ask", "mid", "volume", "openInterest"]
#Datframe filter
options_df = options_df[
    (options_df["K"] > 0) &
    (options_df["T"] > 0) &
    (options_df["sigma"] > 0) &
    (options_df["mid"] >0) &
    (options_df["volume"].fillna(0) > 0) &
    (options_df["openInterest"].fillna(0) > 0)
].copy() 

options_df["bs_price"] = options_df.apply(
    lambda row: black_scholes_price(
        S=row["S"],
        K=row["K"],
        T=row["T"],
        r=row["r"],
        sigma=row["sigma"],
        option_type=row["option_type"]
    ), axis=1
)

options_df["mispricing"] = options_df["mid"] - options_df["bs_price"]
options_df["abs_error"] = options_df["mispricing"].abs()

view_cols = [
    "contractSymbol", "option_type", "K", "mid", "bs_price",
    "mispricing", "sigma", "volume", "openInterest", "abs_error"
]

print(options_df[view_cols].sort_values("abs_error", ascending=False).head(20))