import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from utils import fetch_yf_symbol, load_sample_csv, trend_summary

# ===== Page Setup =====
st.set_page_config(
    page_title="Global Financial Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== Custom Styling =====
st.markdown("""
    <style>
    body { background-color: #f6f9fc; }
    .stApp {
        background: linear-gradient(to bottom right, #ffffff, #e9f5ff);
        color: #012a4a;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-header { font-size: 30px; color: #012a4a; font-weight: 700; }
    .section-header {
        color: #01497c; font-size: 20px; font-weight: 600;
        border-left: 4px solid #00b4d8; padding-left: 10px;
    }
    .metric-box {
        background: #ffffff; border-radius: 12px; padding: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08); text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ===== Header =====
st.markdown("<div class='main-header'>Global Financial Intelligence Dashboard</div>", unsafe_allow_html=True)
st.write("**Interactive Exploration • AI-Powered Insights • Clean Corporate Design**")

# ===== Sidebar Filters =====
st.sidebar.header("Filters & Quick Tools")

period_label = st.sidebar.selectbox(
    "Select Period", 
    ["1 week", "1 month", "3 months", "6 months", "1 year"], 
    index=1
)

symbols_dict = {
    "Pakistan Stocks": "^KSE",
    "Gold": "GC=F",
    "USD/PKR": "PKR=X",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD"
}

symbols = st.sidebar.multiselect("Select Assets", list(symbols_dict.keys()), default=["Pakistan Stocks", "Gold", "BTC"])
selected_symbols = [symbols_dict[s] for s in symbols]

# Currency Converter
amount = st.sidebar.number_input("Currency Converter: Amount", 100.0)
from_cur = st.sidebar.selectbox("From", ["USD", "PKR"])
to_cur = st.sidebar.selectbox("To", ["PKR", "USD"])

if from_cur == "USD" and to_cur == "PKR":
    converted = amount * 280
elif from_cur == "PKR" and to_cur == "USD":
    converted = amount / 280
else:
    converted = amount

st.sidebar.info(f"Converted: {converted:,.2f} {to_cur}")

# ===== Data Fetch =====
period_map = {
    "1 week": "7d",
    "1 month": "1mo",
    "3 months": "3mo",
    "6 months": "6mo",
    "1 year": "1y"
}
yf_period = period_map.get(period_label, "1mo")

results = []
for sym in selected_symbols:
    try:
        res = fetch_yf_symbol(sym, period=yf_period)
        results.append(res)
    except Exception:
        pass

if not results:
    st.warning("Could not fetch live data. Showing sample dataset.")
    df = load_sample_csv()
else:
    name_map = {v:k for k,v in symbols_dict.items()}
    df = pd.DataFrame([
        {
            "Market": name_map[r["symbol"]],
            "Latest": f"{r['latest']:,.2f}",
            "Change%": f"{r['pct']:+.2f}%"
        }
        for r in results
    ])

# ===== Market Overview =====
st.markdown("<div class='section-header'>Market Overview</div>", unsafe_allow_html=True)
cols = st.columns(len(df))
for i, row in df.iterrows():
    with cols[i]:
        color = "green" if float(row['Change%'].replace('%','')) > 0 else "red"
        st.markdown(f"""
        <div class='metric-box'>
        <b>{row['Market']}</b><br>
        <span style='font-size:24px;color:#01497c;'>{row['Latest']}</span><br>
        Change: <span style='color:{color};'>{row['Change%']}</span>
        </div>
        """, unsafe_allow_html=True)

# ===== Comparative Trends =====
st.markdown("<div class='section-header'>Comparative Price Trends</div>", unsafe_allow_html=True)
if results:
    trend_data = []
    for r in results:
        temp = r["history"].copy()
        temp["Asset"] = name_map.get(r["symbol"], r["symbol"])
        trend_data.append(temp)
    all_trends = pd.concat(trend_data)
    all_trends.reset_index(inplace=True)
    chart = alt.Chart(all_trends).mark_line(point=True).encode(
        x='Date:T', y='Close:Q', color='Asset:N'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)

# ===== Correlation Heatmap =====
st.markdown("<div class='section-header'>Correlation Heatmap</div>", unsafe_allow_html=True)
if results:
    pivot = all_trends.pivot(index='Date', columns='Asset', values='Close').corr()
    st.dataframe(pivot.style.background_gradient(cmap='Blues', axis=None).format("{:.2f}"))

# ===== AI Trend Summaries =====
st.markdown("<div class='section-header'>AI Trend Summaries</div>", unsafe_allow_html=True)
for r in results:
    friendly_name = name_map.get(r["symbol"], r["symbol"])
    st.info(trend_summary(r["history"], name=friendly_name, period_label=period_label))

# ===== Footer =====
st.markdown("---")
st.caption(f"Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | © Zainab276 2025 — Built for Insight & Decision Excellence")
