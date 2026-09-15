from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class NormalizedTick:
    symbol: str
    ts: int  # ms since epoch
    ltp: float
    bid: Optional[float]
    ask: Optional[float]
    bid_qty: Optional[int]
    ask_qty: Optional[int]
    oi: Optional[int]
    volume: Optional[int]
    is_option: bool
    underlying: Optional[str]


def normalize_fyers_tick(raw: dict) -> NormalizedTick:
    symbol: str = raw["symbol"]
    ts: int = raw.get("ts", int(time.time() * 1000))
    ltp: float = float(raw["ltp"])

    if ltp <= 0:
        raise ValueError("Invalid LTP")

    bid = raw.get("bid")
    ask = raw.get("ask")
    bid_qty = raw.get("bid_qty")
    ask_qty = raw.get("ask_qty")
    oi = raw.get("oi")
    volume = raw.get("volume")

    is_option = (
        "OPT" in symbol.upper()
        or "CE" in symbol.upper()
        or "PE" in symbol.upper()
    )
    underlying: Optional[str] = None

    if is_option:
        if "NIFTY" in symbol.upper():
            underlying = "NIFTY"
        elif "BANKNIFTY" in symbol.upper() or "BNF" in symbol.upper():
            underlying = "BANKNIFTY"

    return NormalizedTick(
        symbol=symbol,
        ts=ts,
        ltp=ltp,
        bid=bid,
        ask=ask,
        bid_qty=bid_qty,
        ask_qty=ask_qty,
        oi=oi,
        volume=volume,
        is_option=is_option,
        underlying=underlying,
    )
