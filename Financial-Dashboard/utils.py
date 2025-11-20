import pandas as pd, os, io, numpy as np
import yfinance as yf
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(DATA_DIR, exist_ok=True)


# ===== DATA FETCH FUNCTIONS =====

def fetch_yf_symbol(symbol, period="1mo", interval="1d"):
    t = yf.Ticker(symbol)
    hist = t.history(period=period, interval=interval)
    if hist.empty:
        raise RuntimeError(f"No data for {symbol}")
    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    latest = hist["Close"].iloc[-1]
    pct = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
    return {
        "symbol": symbol,
        "latest": float(latest),
        "pct": round(float(pct), 2),
        "history": hist[["Close"]]
    }


def load_sample_csv(name="markets_sample.csv"):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return pd.read_csv(path)
    df = pd.DataFrame({
        "Market": ["Pakistan Stocks", "Gold", "USD/PKR", "BTC"],
        "Latest": [56340, 2120, 280, 68450],
        "Change%": [1.5, 0.8, -0.2, 2.3]
    })
    df.to_csv(path, index=False)
    return df


def top_movers_from_symbols(symbol_results, top_n=5):
    df = pd.DataFrame([
        {"Market": r.get("symbol"), "Latest": r.get("latest"), "Change%": r.get("pct")}
        for r in symbol_results
    ])
    gainers = df.sort_values("Change%", ascending=False).head(top_n)
    losers = df.sort_values("Change%", ascending=True).head(top_n)
    return gainers, losers


# ===== AI TREND SUMMARY =====
def trend_summary(hist, name="Asset", period_label="recent period"):
    if hist is None or hist.empty:
        return f"No historical data available for {name}."

    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    closes = hist["Close"]

    mean = closes.mean()
    latest = closes.iloc[-1]
    change = ((latest - closes.iloc[0]) / closes.iloc[0]) * 100
    vol = closes.pct_change().std() * 100

    if change > 5:
        mood = "upward momentum"
    elif change < -5:
        mood = "downward pressure"
    else:
        mood = "sideways consolidation"

    if vol > 3:
        vol_comment = "with high volatility"
    else:
        vol_comment = "in a stable range"

    return (
        f"{name} shows {mood} over the {period_label}, "
        f"changing by {change:.2f}% {vol_comment}. "
        f"Current average level: {mean:.2f}."
    )


# ===== PDF REPORT =====
def generate_pdf_report(summary_dict, filepath):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, summary_dict.get("title", "Market Report"))
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-2.7*cm, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y = height-3.8*cm
    for item in summary_dict.get("items", []):
        line = f"{item.get('name')}: {item.get('latest')} ({item.get('change')}%)"
        c.drawString(2*cm, y, line)
        y -= 0.7*cm
        if y < 2*cm:
            c.showPage()
            y = height-2*cm
    c.showPage()
    c.save()
    return filepath
