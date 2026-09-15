from dataclasses import dataclass
from typing import Optional


@dataclass
class OptionGreeks:
    symbol: str
    strike: int
    option_type: str  # "CE" or "PE"
    expiry: str
    ltp: float
    iv: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    vega: Optional[float]
    rho: Optional[float]
    oi: Optional[int]
    volume: Optional[int]


def parse_fyers_option_greeks(raw: dict) -> OptionGreeks:
    return OptionGreeks(
        symbol=raw["symbol"],
        strike=int(raw["strike"]),
        option_type=raw["option_type"],
        expiry=raw["expiry"],
        ltp=float(raw["ltp"]),
        iv=raw.get("iv"),
        delta=raw.get("delta"),
        gamma=raw.get("gamma"),
        theta=raw.get("theta"),
        vega=raw.get("vega"),
        rho=raw.get("rho"),
        oi=raw.get("oi"),
        volume=raw.get("volume"),
    )
