import time
from typing import Optional
from fastapi import FastAPI  # type: ignore[import-not-found]
from fastapi.responses import JSONResponse, FileResponse  # type: ignore[import-not-found]
from fastapi.staticfiles import StaticFiles  # type: ignore[import-not-found]
from pathlib import Path

from ..greeks_engine.option_chain import fetch_nifty_option_chain, OptionChainSnapshot

app = FastAPI(title="MyQuantDesk – NIFTY Options Greeks")

latest_snapshot: Optional[OptionChainSnapshot] = None
last_fetch_time: float = 0
fetch_interval = 5  # seconds

def fetch_latest_snapshot() -> OptionChainSnapshot:
    global latest_snapshot, last_fetch_time
    now = time.time()
    if latest_snapshot is None or (now - last_fetch_time) >= fetch_interval:
        latest_snapshot = fetch_nifty_option_chain(strikecount=1)
        last_fetch_time = now
    return latest_snapshot

def snapshot_to_dict(snapshot: OptionChainSnapshot) -> dict:
    return {
        "underlying": snapshot.underlying,
        "timestamp": snapshot.timestamp,
        "spot_ltp": snapshot.spot_ltp,
        "options": [
            {
                "symbol": opt.symbol,
                "strike_price": opt.strike_price,
                "option_type": opt.option_type,
                "ltp": opt.ltp,
                "bid": opt.bid,
                "ask": opt.ask,
                "oi": opt.oi,
                "volume": opt.volume,
                "delta": opt.delta,
                "gamma": opt.gamma,
                "theta": opt.theta,
                "vega": opt.vega,
                "iv": opt.iv,
            }
            for opt in snapshot.options
        ],
    }

@app.get("/health")
async def health():
    age = time.time() - last_fetch_time if last_fetch_time else None
    return {
        "status": "ok",
        "last_fetch_age_sec": age,
        "has_snapshot": latest_snapshot is not None,
    }

@app.get("/snapshot")
async def get_snapshot():
    snapshot = fetch_latest_snapshot()
    return snapshot_to_dict(snapshot)

# Serve static frontend files
PROJECT_ROOT = Path(__file__).resolve().parents[2]
frontend_dir = PROJECT_ROOT / "src" / "frontend"

frontend_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "frontend/index.html not found"},
        )
    return FileResponse(str(index_path))

@app.get("/options")
async def options_page():
    options_path = frontend_dir / "options.html"
    if not options_path.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "frontend/options.html not found"},
        )
    return FileResponse(str(options_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
