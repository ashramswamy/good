import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime

# Streamlit Config
st.set_page_config(page_title="📊 Enhanced Stock Market Dashboard", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("📊 Dashboard Controls")

# Description
st.sidebar.markdown("""
Welcome to your *Stock Dashboard*!  
Track *Opening, Closing, Volume, and **% Change* of top companies in real time.
""")

# Stock selection
symbols = st.sidebar.multiselect(
    "📌 Select Stocks to View",
    ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "IBM", "INTC"],
    default=["AAPL", "MSFT"]
)

# Date selection
start_date = st.sidebar.date_input("🗓 Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("📅 End Date", datetime.date.today())

# Explanation of terms
with st.sidebar.expander("ℹ What do these mean?"):
    st.markdown("""
    - *Open*: Price at market open  
    - *Close*: Price at market close  
    - *Volume*: Number of shares traded  
    - *% Change*: Daily percent movement  
    """)

# Theme toggle
dark_mode = st.sidebar.checkbox("🌗 Enable Dark Theme")

# Main Heading
st.title("📈Real-Time Stock Market Dashboard")
st.markdown("View real-time stock prices with interactive *Opening/Closing price trends, **volume*, and more!")

# Download Refresh Button (Optional)
refresh = st.sidebar.button("🔄 Refresh Data")

# Data load block
if symbols:
    all_data = yf.download(symbols, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)
    st.success("✅ Data successfully loaded!")

    # ---- Raw Data Preview ----
    st.subheader("📋 Raw Data Preview")
    with st.expander("Click to view raw data"):
        preview_data = pd.concat([all_data[sym].assign(Symbol=sym) for sym in symbols])
        st.dataframe(preview_data.head(20), use_container_width=True)

    # CSV Download
    csv_data = preview_data.to_csv(index=True).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name='stock_data.csv',
        mime='text/csv'
    )

    # ---- Opening Price Chart ----
    st.subheader("🚀 Opening Stock Price Trend")
    fig_open = go.Figure()
    for sym in symbols:
        fig_open.add_trace(go.Scatter(
            x=all_data[sym].index,
            y=all_data[sym]["Open"],
            mode='lines',
            name=sym
        ))
    fig_open.update_layout(title="Opening Price Over Time", xaxis_title="Date", yaxis_title="Opening Price (USD)")
    st.plotly_chart(fig_open, use_container_width=True)

    # ---- Closing Price Chart ----
    st.subheader("📉 Closing Stock Price Trend")
    fig_close = go.Figure()
    for sym in symbols:
        fig_close.add_trace(go.Scatter(
            x=all_data[sym].index,
            y=all_data[sym]["Close"],
            mode='lines+markers',
            name=sym
        ))
    fig_close.update_layout(title="Closing Price Over Time", xaxis_title="Date", yaxis_title="Closing Price (USD)")
    st.plotly_chart(fig_close, use_container_width=True)

    # ---- Volume Trend ----
    st.subheader("📊 Daily Volume Traded")
    fig_vol = go.Figure()
    for sym in symbols:
        fig_vol.add_trace(go.Scatter(
            x=all_data[sym].index,
            y=all_data[sym]["Volume"],
            mode='lines',
            stackgroup='one',
            name=sym
        ))
    fig_vol.update_layout(title="Volume Traded Over Time", xaxis_title="Date", yaxis_title="Volume")
    st.plotly_chart(fig_vol, use_container_width=True)

    # ---- Percentage Change ----
    st.subheader("📈 Daily % Change in Closing Price")
    fig_pct = go.Figure()
    for sym in symbols:
        pct_change = all_data[sym]["Close"].pct_change() * 100
        fig_pct.add_trace(go.Scatter(
            x=all_data[sym].index,
            y=pct_change,
            mode='lines',
            name=sym
        ))
    fig_pct.update_layout(title="Daily Percentage Change", xaxis_title="Date", yaxis_title="Change (%)")
    st.plotly_chart(fig_pct, use_container_width=True)

    # ---- Latest Snapshot Table ----
    st.subheader("🔍 Latest Market Snapshot")
    latest_data = {
        "Symbol": [],
        "Latest Price": [],
        "Opening Price": [],
        "High": [],
        "Low": [],
        "Volume": [],
    }

    for sym in symbols:
        latest_row = all_data[sym].iloc[-1]
        latest_data["Symbol"].append(sym)
        latest_data["Latest Price"].append(round(latest_row["Close"], 2))
        latest_data["Opening Price"].append(round(latest_row["Open"], 2))
        latest_data["High"].append(round(latest_row["High"], 2))
        latest_data["Low"].append(round(latest_row["Low"], 2))
        latest_data["Volume"].append(int(latest_row["Volume"]))

    df_latest = pd.DataFrame(latest_data)
    st.table(df_latest)

else:
    st.warning("👈 Please select at least one stock symbol to view data.")
