
from pathlib import Path

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="JARVIS Trading Dashboard")

app.mount(
    "/static",
    StaticFiles(directory=ROOT / "frontend"),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
def home():
    return (
        ROOT / "frontend" / "index.html"
    ).read_text(encoding="utf-8")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "JARVIS"}


@app.get("/api/market/quotes")
def quotes(
    symbols: str = "^NSEI,^NSEBANK,RELIANCE.NS,TCS.NS,INFY.NS"
):
    result = []

    for symbol in [
        s.strip() for s in symbols.split(",") if s.strip()
    ][:30]:
        try:
            info = yf.Ticker(symbol).fast_info

            price = info.get("last_price")
            previous = info.get("previous_close")

            change = None

            if price is not None and previous:
                change = (price - previous) / previous * 100

            result.append({
                "symbol": symbol,
                "price": price,
                "previous_close": previous,
                "change_pct": change
            })

        except Exception as error:
            result.append({
                "symbol": symbol,
                "error": str(error)
            })

    return {
        "quotes": result,
        "source": "Yahoo Finance"
    }


@app.get("/api/market/history")
def history(
    symbol: str = "^NSEI",
    period: str = "1mo",
    interval: str = "1d"
):
    allowed_periods = {
        "1d", "5d", "1mo", "3mo",
        "6mo", "1y", "2y", "5y"
    }

    allowed_intervals = {
        "5m", "15m", "30m", "60m",
        "1d", "1wk", "1mo"
    }

    if period not in allowed_periods:
        raise HTTPException(400, "Invalid period")

    if interval not in allowed_intervals:
        raise HTTPException(400, "Invalid interval")

    try:
        df = yf.Ticker(symbol).history(
            period=period,
            interval=interval,
            auto_adjust=True
        )

        if df.empty:
            return {"symbol": symbol, "data": []}

        df = df.reset_index()
        data = []

        for _, row in df.iterrows():
            data.append({
                "time": row.iloc[0].isoformat(),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })

        return {"symbol": symbol, "data": data}

    except Exception as error:
        raise HTTPException(
            502,
            f"Market data unavailable: {error}"
        )


@app.get("/api/signals")
def signals(
    symbols: str = "RELIANCE.NS,TCS.NS,INFY.NS"
):
    output = []

    for symbol in [
        s.strip() for s in symbols.split(",") if s.strip()
    ][:30]:
        try:
            df = yf.Ticker(symbol).history(
                period="6mo",
                interval="1d"
            )

            if len(df) < 50:
                output.append({
                    "symbol": symbol,
                    "signal": "INSUFFICIENT DATA"
                })
                continue

            close = df["Close"]

            sma20 = close.rolling(20).mean().iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1]

            delta = close.diff()

            gain = delta.clip(lower=0).rolling(14).mean()
            loss = -delta.clip(upper=0).rolling(14).mean()

            rs = (
                gain.iloc[-1] / loss.iloc[-1]
                if loss.iloc[-1] else 100
            )

            rsi = 100 - (100 / (1 + rs))

            if sma20 > sma50 and rsi < 70:
                signal = "BULLISH"
            elif sma20 < sma50 and rsi > 30:
                signal = "BEARISH"
            else:
                signal = "NEUTRAL"

            output.append({
                "symbol": symbol,
                "signal": signal,
                "price": round(float(close.iloc[-1]), 2),
                "sma20": round(float(sma20), 2),
                "sma50": round(float(sma50), 2),
                "rsi14": round(float(rsi), 1)
            })

        except Exception as error:
            output.append({
                "symbol": symbol,
                "error": str(error)
            })

    return {
        "signals": output,
        "note": "Research indicators only. Not investment advice."
    }
  
