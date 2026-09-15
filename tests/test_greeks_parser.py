import pytest
from src.greeks_engine.parser import parse_fyers_option_greeks, OptionGreeks


def test_parse_complete_greeks():
    raw = {
        "symbol": "NSE:NIFTY26OCT24500CE",
        "strike": 24500,
        "option_type": "CE",
        "expiry": "2026-10-29",
        "ltp": 210.5,
        "iv": 0.132,
        "delta": 0.52,
        "gamma": 0.0041,
        "theta": -8.3,
        "vega": 12.1,
        "rho": 3.4,
        "oi": 54321,
        "volume": 12345,
    }

    g = parse_fyers_option_greeks(raw)

    assert g.symbol == "NSE:NIFTY26OCT24500CE"
    assert g.strike == 24500
    assert g.option_type == "CE"
    assert g.expiry == "2026-10-29"
    assert g.ltp == 210.5
    assert g.iv == 0.132
    assert g.delta == 0.52
    assert g.gamma == 0.0041
    assert g.theta == -8.3
    assert g.vega == 12.1
    assert g.rho == 3.4


def test_missing_greeks_defaults_to_none():
    raw = {
        "symbol": "NSE:NIFTY26OCT24000PE",
        "strike": 24000,
        "option_type": "PE",
        "expiry": "2026-10-29",
        "ltp": 90.0,
    }

    g = parse_fyers_option_greeks(raw)

    assert g.iv is None
    assert g.delta is None
    assert g.gamma is None
    assert g.ltp == 90.0
    assert g.option_type == "PE"
