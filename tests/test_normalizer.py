import pytest
from src.data_ingestion.normalizer import normalize_fyers_tick, NormalizedTick


def test_normalize_future_tick():
    raw = {
        "symbol": "NSE:NIFTY26OCTFUT",
        "ts": 1726403400123,
        "ltp": 24510.35,
        "bid": 24509.0,
        "ask": 24511.0,
        "bid_qty": 100,
        "ask_qty": 150,
        "oi": 123456,
        "volume": 987654,
    }
    tick = normalize_fyers_tick(raw)

    assert tick.symbol == "NSE:NIFTY26OCTFUT"
    assert tick.ts == 1726403400123
    assert tick.ltp == 24510.35
    assert tick.is_option is False
    assert tick.underlying is None
    assert tick.bid == 24509.0
    assert tick.ask == 24511.0


def test_normalize_option_tick():
    raw = {
        "symbol": "NSE:NIFTY26OCT24500CE",
        "ts": 1726403400456,
        "ltp": 210.5,
        "bid": 209.0,
        "ask": 212.0,
        "bid_qty": 50,
        "ask_qty": 75,
        "oi": 54321,
        "volume": 12345,
    }
    tick = normalize_fyers_tick(raw)

    assert tick.is_option is True
    assert tick.underlying == "NIFTY"
    assert tick.ltp == 210.5


def test_missing_fields_defaults():
    raw = {
        "symbol": "NSE:NIFTY26OCTFUT",
        "ts": 1726403400789,
        "ltp": 24500.0,
    }
    tick = normalize_fyers_tick(raw)

    assert tick.bid is None
    assert tick.ask is None
    assert tick.oi is None
    assert tick.volume is None


def test_invalid_ltp_raises():
    raw = {
        "symbol": "NSE:NIFTY26OCTFUT",
        "ts": 1726403400999,
        "ltp": -10,
    }

    with pytest.raises(ValueError, match="Invalid LTP"):
        normalize_fyers_tick(raw)
