import math 
import numpy as np

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
    
