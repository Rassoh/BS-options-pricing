import math

## Hardcoding variables to test the function using Nvidias option data today
S = 177.88
K = 115
T = 1/365
r = 0.05
sigma = 2.6



## 


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
    d1 = calculate_d1(S,K,T,r,sigma)
    d2 = calculate_d2(S,K,T,r,sigma)
    if option_type.lower() == "call":
        price = S * normal_cdf(d1) - K * math.exp(-r*T) * normal_cdf(d2)
    elif option_type.lower() == "put":
        price = K * math.exp(-r*T) * normal_cdf(-d2) - S *normal_cdf(-d1)
    else: 
        raise ValueError("option_type must be 'call' or 'put'")
    
    return price 
    
call_price = black_scholes_price(S, K, T, r, sigma, "call")
put_price = black_scholes_price(S, K, T, r, sigma, "put")

print("Call Price:", round(call_price, 4))
print("Put Price:", round(put_price, 4))
