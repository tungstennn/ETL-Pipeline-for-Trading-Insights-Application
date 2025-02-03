import streamlit as st
import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.extract import get_data_from_db
import psycopg2
from dotenv import load_dotenv
import streamlit_option_menu
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

load_dotenv()

with st.sidebar:
    selected = option_menu(
        menu_title="Dashboard",
        options=["Market Overview", "Crypto Trends", "Tech Stocks", "Market Insights", "Real-Time Data"],
        icons=["house", "bar-chart-line", "cpu", "pie-chart", "activity"],
        menu_icon="cast",
        default_index=0,
    )

stocks_df = get_data_from_db("SELECT * FROM abdirahmans_market_data where volume is not null;")
crypto_df = get_data_from_db("SELECT * FROM abdirahmans_market_data where volume is null;")
combined_df = get_data_from_db("SELECT * FROM abdirahmans_market_data;")
# Ensure datetime column is in datetime format
combined_df['datetime'] = pd.to_datetime(combined_df['datetime'])

if selected == "Market Overview":

    # -------------------- KPIs --------------------

    # 1. Total Market Cap (using the sum of 'close' prices as a proxy)
    # total_market_cap = combined_df.groupby('symbol')['close'].last().sum()

    # 2. % Gain Over the Last 30 Days
    combined_df['date'] = pd.to_datetime(combined_df['datetime']).dt.date
    latest_prices = combined_df.groupby('symbol')['close'].last()
    initial_prices = combined_df.groupby('symbol')['close'].first()

    performance = ((latest_prices - initial_prices) / initial_prices) * 100
    best_performer = performance.idxmax()
    best_performance_value = performance.max()

    # st.metric("🚀 Best Performer", f"{best_performer}", f"+{best_performance_value:.2f}%")


    # 2. Average Daily Volume
    combined_df['date'] = combined_df['datetime'].dt.date
    average_daily_volume = combined_df.groupby('date')['volume'].sum().mean()

    # 3. Top Gainer (based on % change from open to close)
    combined_df['price_change_pct'] = ((combined_df['close'] - combined_df['open']) / combined_df['open']) * 100
    top_gainer_row = combined_df.loc[combined_df['price_change_pct'].idxmax()]
    top_gainer = top_gainer_row['symbol']
    top_gainer_change = top_gainer_row['price_change_pct']

    # --------------------- Display KPIs ---------------------
    st.title("📊 Market Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("🚀 Best Performer", f"{best_performer}", f"+{best_performance_value:.2f}%")
    col2.metric("Avg Daily Volume", f"${average_daily_volume/1e6:.2f}M")
    col3.metric("Top Gainer", f"{top_gainer}", f"+{top_gainer_change:.2f}%")

    # -------------------- Market Trends Line Chart --------------------
    st.subheader("📊 Market Trends Overview")

    col1, col2 = st.columns(2)

    # Tech Stocks Trend
    with col1:
        st.write("💻 Tech Stocks")
        tech_trend = stocks_df.pivot_table(index='datetime', columns='symbol', values='close').fillna(method='ffill')
        st.line_chart(tech_trend)

    # Crypto Trend
    with col2:
        st.write("₿ Crypto Trends")
        crypto_trend = crypto_df.pivot_table(index='datetime', columns='symbol', values='close').fillna(method='ffill')
        st.line_chart(crypto_trend)

    # Pivot data for line chart
    trend_data = combined_df.pivot_table(index='datetime', columns='symbol', values='close').fillna(method='ffill')

    st.subheader("📈 Market Performance (Normalized)")

    # Calculate percentage change
    normalized_trend = trend_data.pct_change().cumsum() * 100  # Cumulative percentage change

    st.line_chart(normalized_trend)
    
elif selected == "Crypto Trends":
    # Assuming crypto_df is already defined and updated
    crypto_symbols = crypto_df['symbol'].unique()

    # Latest Data for Each Crypto
    latest_data = crypto_df.groupby('symbol').last().reset_index()

    st.subheader("📊 Crypto Key Metrics")

    # Display Metrics for Each Crypto
    for symbol in crypto_symbols:
        crypto = latest_data[latest_data['symbol'] == symbol].iloc[0]
        price_change = ((crypto['close'] - crypto['open']) / crypto['open']) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric(f"{symbol} Price", f"${crypto['close']:.2f}", f"{price_change:.2f}%")
        #col2.metric("24H Volume", f"{crypto['volume'] / 1e6:.2f}M")
        col3.metric("24H High/Low", f"${crypto['high']:.2f} / ${crypto['low']:.2f}")
        
    st.subheader("📈 Price Trends Over Time")

    # Line Chart for Closing Prices
    price_trend = crypto_df.pivot_table(index='datetime', columns='symbol', values='close').fillna(method='ffill')
    st.line_chart(price_trend)

    # st.subheader("⚡ Volatility Analysis")

    # # Volatility Calculation
    # volatility = crypto_df.groupby('symbol')['close'].rolling(window=7).std().reset_index()
    # volatility_pivot = volatility.pivot(index='datetime', columns='symbol', values='close')

    # st.line_chart(volatility_pivot)

    # st.subheader("🔗 Correlation Between Cryptos")

    # # Correlation Matrix
    # corr_matrix = price_trend.corr()

    # # Heatmap
    # fig, ax = plt.subplots()
    # sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    # st.pyplot(fig)
    
    