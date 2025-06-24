import os
import datetime
import requests
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objs as go
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


st.set_page_config("Real-Time Finance Dashboard", layout="centered")
st.title("Financial Data Analysis Dashboard (Live)")

symbols = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSft)": "MSft",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Google (GOOG)": "GOOG",
    "Meta (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Nvidia (NVDA)": "NVDA",
    "AMD (AMD)": "AMD",
    "Intel (INTC)": "INTC",
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Gold (XAUUSD)": "XAUUSD=X",
    "US Dollar (USD)": "USD=X",
}


selected_symbol_name = st.selectbox("Select an asset", list(symbols.keys()))
Select_symbol = symbols[selected_symbol_name]

start_date = st.date_input("From date :", datetime.date(2022, 1, 1))
end_date = st.date_input("To date :", datetime.date.today())
delta_days = (end_date - start_date).days

interval_option = st.selectbox(
    "Select interval (resolution of data):",
    ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"],
    index=9,
)

minute_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]
if interval_option in minute_intervals and delta_days > 7:
    st.warning(
        f"⚠️ interval '{interval_option}'It may not return any data for more than 7 days."
    )


if st.button("Load data"):
    try:
        data = yf.download(
            Select_symbol, start=start_date, end=end_date, interval=interval_option
        )

        if data.empty:
            st.warning(
                "⚠️ No data found. Try a different symbol, shorter date range, or different interval."
            )

        else:
            data.index = pd.to_datetime(data.index)
            st.session_state.data = data
            st.success(
                f"✅Data loaded successfully for {selected_symbol_name} from {start_date} to {end_date}."
            )

    except Exception as e:
        st.error(f"❌ Error downloading data: {e}")

if "data" not in st.session_state:
    st.session_state["data"] = None
data = st.session_state.data

if data is not None:
    st.write("📊 Data preview:")
    st.dataframe(data.tail())

    if all(col in data.columns for col in ["Open", "High", "Low", "Close"]):
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=data.index,
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                )
            ]
        )
        fig.update_layout(
            title=f"Candlestick Chart {selected_symbol_name}",
            xaxis_title="Time",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Candlestick data is incomplete or unavailable.")

    data["Benefit"] = data["Close"].pct_change()
    data["Tolerance"] = (data["High"] - data["Low"]) / data["Low"]

    st.subheader("📈 Benefit")
    fig_benefit = go.Figure()
    fig_benefit.add_trace(
        go.Scatter(
            x=data.index, y=data["Benefit"], name="Benefit", line=dict(color="green")
        )
    )
    fig_benefit.update_layout(xaxis_title="time", yaxis_title="Benefit")
    st.plotly_chart(fig_benefit, use_container_width=True)

    st.subheader("📉 Tolerance")
    fig_tolerance = go.Figure()
    fig_tolerance.add_trace(
        go.Scatter(
            x=data.index, y=data["Tolerance"], name="Tolerance", line=dict(color="red")
        )
    )
    fig_tolerance.update_layout(xaxis_title="time", yaxis_title="Tolerance")
    st.plotly_chart(fig_tolerance, use_container_width=True)

    def get_news(query, date, api_key):
        url = f"https://newsapi.org/v2/everything?q={query}&from={date}&to={date}&sortBy=popularity&language=en&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            return []

    news_date = st.date_input("Date of news review :", datetime.date.today())
    formatted_date = news_date.strftime("%Y-%m-%d")

    symbol_names_for_news = {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "AMZN": "Amazon",
        "TSLA": "Tesla",
        "GOOG": "Google",
        "META": "Meta",
        "NFLX": "Netflix",
        "NVDA": "Nvidia",
        "AMD": "AMD",
        "INTC": "Intel",
        "BTC-USD": "Bitcoin",
        "XAUUSD=X": "Gold",
        "USD=X": "US Dollar",
    }

    api_key = NEWS_API_KEY

    if st.button("Show news"):
        st.info(
            f"Looking for news '{symbol_names_for_news[Select_symbol]}' in history {formatted_date} ..."
        )
        query_keyword = symbol_names_for_news.get(Select_symbol, Select_symbol)

        news_list = get_news(query_keyword, formatted_date, api_key)
        if news_list:
            for article in news_list[:5]:
                st.markdown(
                    f"""
                    <span style='font-size:14px'><strong>{article['title']}</strong></span>  
                    <span style='font-size:12px'>{article['description'] or '...'}</span>  
                    <a href="{article['url']}" target="_blank" style="font-size:12px">📰 مطالعه کامل</a>
                    <hr style='margin-top:4px;margin-bottom:8px;border:0.5px solid gray'>
                    """,
                    unsafe_allow_html=True,
                )

        else:
            st.warning("No news found.")
