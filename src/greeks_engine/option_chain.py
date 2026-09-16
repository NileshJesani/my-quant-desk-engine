import os
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

client_id = os.getenv("FYERS_APP_ID")
access_token = os.getenv("FYERS_ACCESS_TOKEN")

if not client_id or not access_token:
    raise RuntimeError(
        "FYERS_APP_ID and FYERS_ACCESS_TOKEN must be set in the project .env file."
    )

fyers = fyersModel.FyersModel(
    client_id=client_id,
    is_async=False,
    token=access_token,
    log_path="",
)


@dataclass
class OptionContract:
    symbol: str
    strike_price: int
    option_type: str  # "CE" or "PE"
    ltp: float
    bid: Optional[float]
    ask: Optional[float]
    oi: Optional[int]
    volume: Optional[int]
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    vega: Optional[float]
    iv: Optional[float]


@dataclass
class OptionChainSnapshot:
    underlying: str
    timestamp: int  # seconds since epoch
    spot_ltp: Optional[float]
    options: List[OptionContract]


def fetch_nifty_option_chain(strikecount: int = 1) -> OptionChainSnapshot:
    """
    Fetch NIFTY option chain with Greeks from Fyers.
    The Fyers symbol for the NIFTY 50 index is "NSE:NIFTY50-INDEX".
    """
    underlying_symbol = "NSE:NIFTY50-INDEX"

    data = {
        "symbol": underlying_symbol,
        "strikecount": strikecount,
        "timestamp": "",
        "greeks": "1",
    }
    resp = fyers.optionchain(data=data)

    if resp.get("s") != "ok" or resp.get("code") != 200:
        raise RuntimeError(f"Option chain fetch failed: {resp}")

    raw_data = resp["data"]
    raw_chain: List[dict] = raw_data.get("optionsChain", [])

    spot_ltp: Optional[float] = None
    options: List[OptionContract] = []

    for item in raw_chain:
        opt_type = item.get("option_type", "")
        if not opt_type:
            # Underlying
            spot_ltp = item.get("ltp")
            continue

        greeks = item.get("greeks") or {}
        contract = OptionContract(
            symbol=item["symbol"],
            strike_price=int(item["strike_price"]),
            option_type=opt_type,
            ltp=float(item["ltp"]),
            bid=item.get("bid"),
            ask=item.get("ask"),
            oi=item.get("oi"),
            volume=item.get("volume"),
            delta=greeks.get("delta"),
            gamma=greeks.get("gamma"),
            theta=greeks.get("theta"),
            vega=greeks.get("vega"),
            iv=greeks.get("iv"),
        )
        options.append(contract)

    return OptionChainSnapshot(
        underlying=underlying_symbol,
        timestamp=int(time.time()),
        spot_ltp=spot_ltp,
        options=options,
    )


if __name__ == "__main__":
    snapshot = fetch_nifty_option_chain(strikecount=1)
    print("Underlying:", snapshot.underlying)
    print("Spot LTP:", snapshot.spot_ltp)
    print("Number of option contracts:", len(snapshot.options))
    for opt in snapshot.options[:10]:
        print(
            opt.symbol,
            opt.strike_price,
            opt.option_type,
            "LTP:",
            opt.ltp,
            "IV:",
            opt.iv,
            "delta:",
            opt.delta,
        )
