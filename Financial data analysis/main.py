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

refresh_on = st.sidebar.checkbox("Enable automatic refresh",value=True)
if refresh_on:
    st_autorefresh(interval=1*1000,key="live_refresh")
st.title("Live market analysis")

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
    "US Dollar (USD)": "USD=X"
}

st.set_page_config("Real-Time Finance Dashboard", layout="wide")
st.title("Financial Data Analysis Dashboard (Live)")

# Choose icon
selected_symbol_name = st.selectbox("Select an asset", list(symbols.keys()))
Select_symbol = symbols[selected_symbol_name]

# Define time frame
start_date = st.date_input("From date :", datetime.date(2022, 1, 1))
end_date = st.date_input("To date :", datetime.date.today())

# Manual update button
if st.button("Loading data"):
    data = yf.download(
        Select_symbol,
        start=start_date,
        end=end_date,
        period="1d",
        interval="1m")
    st.success("Data loaded successfully.")
    # Drawing a candlestick chart
    fig = go.Figure(
        data=[go.candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"]
        )])
    fig.update_layout(tittle=f"Candle chart{selected_symbol_name}",
                      xaxis_title="hystory",
                      yaxis_title="Price",
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Benefit and tolerance calculation
    data["Benefit"] = data["Close"].pct_change()
    data["Tolerance"] = (data["High"] - data["Low"])/data["Low"]
    st.line_chart(data[["Benefit", "Tolerance"]])

    fig_bt = go.Figure()

    # add Benefit
    fig_bt.add_trace(go.Scatter(
        x = data.index,
        y = data["Benefit"],
        name = "Benefit",
        line = dict(color = "green")
    ))
    # add Tolerance
    fig_bt.add_trace(go.Scatter(
        x = data.index,
        y = data["Tolerance"],
        name = "Tolerance",
        line = dict(color = "red"),
        yaxis="y2"
    ))

    fig_bt.update_layout(
        title = "Benefit , Tolerance",
        xaxis_titlr = "History",
        yaxis_titlr = "Benefit",
        yaxis2 = dict(
            title = "Tolerance",
            overlaying = "y",
            side = "right"
        ),
        legend = dict(x = 0,
                      y = 1.1 ,
                      orientation = "h"),
        margin = dict(l = 40,
                      r = 40,
                      t = 40,
                      b = 40))
    st.plotly_chart(fig_bt,use_container_width=True)

    def get_news(query, date, api_key):
        url = f"https://newsapi.org/v2/everything?q={query}&from={date}&to={date}&sortBy=popularity&language=en&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            return []
    news_date = st.date_input("Date of news review :",datetime.date.today())
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
        "USD=X": "US Dollar"
    }

    api_key = NEWS_API_KEY

    if st.button("Show news"):
        st.info(f"Looking for news '{symbol_names_for_news[Select_symbol]}' in history {formatted_date} ...")
        query_keyword = symbol_names_for_news.get(Select_symbol,Select_symbol)

        news_list = get_news(query_keyword,formatted_date, api_key)
        if news_list:
            for article in news_list[:5]:
                st.markdown(f"""
                                {article['title']}  
                                {article['description'] or '...'}  
                                [Complete study]({article['url']})
                                ---
                            """)
        else:
            st.warning("No news found.")




