import streamlit as st
import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.extract import get_data_from_db
from etl.extract import fetch_news
from etl.transform import analyze_sentiment
import psycopg2
from dotenv import load_dotenv
import streamlit_option_menu
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from textblob import TextBlob


load_dotenv()

with st.sidebar:
    selected = option_menu(
        menu_title="Dashboard",
        options=["Market Overview", "Crypto Trends", "Tech Stocks", "Market Insights"],
        icons=["house", "bar-chart-line", "cpu", "pie-chart"],
        menu_icon="cast",
        default_index=0,
    )

stocks_df = get_data_from_db("SELECT datetime, open, high, low, close, volume, symbol FROM abdirahmans_market_data WHERE (volume is not null) AND (symbol NOT LIKE '%/GBP') ORDER BY datetime;")
crypto_df = get_data_from_db("SELECT datetime, open, high, low, close, volume, symbol FROM abdirahmans_market_data where (volume is null) AND (symbol NOT LIKE '%/GBP') ORDER BY datetime;")
combined_df = get_data_from_db("SELECT datetime, open, high, low, close, volume, symbol FROM abdirahmans_market_data WHERE (symbol NOT LIKE '%/GBP') ORDER BY datetime;")
# Ensure datetime column is in datetime format
stocks_df['datetime'] = pd.to_datetime(stocks_df['datetime'])
crypto_df['datetime'] = pd.to_datetime(crypto_df['datetime'])
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
        crypto = latest_data[latest_data['symbol'] == symbol].iloc[-1]
        price_change = ((crypto['close'] - crypto['open']) / crypto['open']) * 100

        col1, col3 = st.columns(2)
        col1.metric(f"{symbol} Price", f"${crypto['close']:.2f}", f"{price_change:.2f}%")
        #col2.metric("24H Volume", f"{crypto['volume'] / 1e6:.2f}M")
        col3.metric("24H High/Low", f"${crypto['high']:.2f} / ${crypto['low']:.2f}")
        
    st.subheader("📈 Price Trends Over Time")

    # Line Chart for Closing Prices
    price_trend = crypto_df.pivot_table(index='datetime', columns='symbol', values='close').fillna(method='ffill')
    st.line_chart(price_trend)

    #s t.subheader("⚡ Volatility Analysis")

    # st.subheader("🔗 Correlation Between Cryptos")

    # # Correlation Matrix
    # corr_matrix = price_trend.corr()

    # # Heatmap
    # fig, ax = plt.subplots()
    # sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=ax)
    # st.pyplot(fig)
    
    st.subheader("📊 Moving Averages Analysis")

    # User selection for crypto asset
    selected_crypto = st.selectbox("Select Cryptocurrency", crypto_df['symbol'].unique())

    # Filter data for selected crypto
    crypto_data = crypto_df[crypto_df['symbol'] == selected_crypto]

    # Ensure datetime is in datetime format
    crypto_data['datetime'] = pd.to_datetime(crypto_data['datetime'])

    # Sort by datetime to ensure correct rolling calculations
    crypto_data = crypto_data.sort_values('datetime')

    # Calculate Moving Averages
    crypto_data['7-Day SMA'] = crypto_data['close'].rolling(window=7).mean()
    crypto_data['30-Day SMA'] = crypto_data['close'].rolling(window=30).mean()
    #crypto_data['EMA (20)'] = crypto_data['close'].ewm(span=20, adjust=False).mean()

    # Plotting
    st.line_chart(crypto_data.set_index('datetime')[['close', '7-Day SMA', '30-Day SMA']])
        
elif selected == "Tech Stocks":
    st.title("💻 Tech Stocks Analysis")

    # Dropdown to select a specific tech stock
    selected_stock = st.selectbox("Select Tech Stock", stocks_df['symbol'].unique())

    # Filter data for the selected stock
    stock_data = stocks_df[stocks_df['symbol'] == selected_stock]

    # Ensure datetime is in datetime format
    stock_data['datetime'] = pd.to_datetime(stock_data['datetime'])
    stock_data = stock_data.sort_values('datetime')
    
    # 1. Key Metrics (KPIs)
    latest_data = stock_data.iloc[-1]
    price_change = ((latest_data['close'] - stock_data.iloc[-2]['close']) / stock_data.iloc[-2]['close']) * 100

    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"{selected_stock} Price", f"${latest_data['close']:.2f}", f"{price_change:.2f}%")
    col2.metric("24H Volume", f"{latest_data['volume'] / 1e6:.2f}M")
    col3.metric("All-Time High", f"${stock_data['close'].max():.2f}")
    
    
    # 3. Moving Averages
    st.subheader("📉 Moving Averages (7 & 30 Day)")

    stock_data['7-Day SMA'] = stock_data['close'].rolling(window=7).mean()
    stock_data['30-Day SMA'] = stock_data['close'].rolling(window=30).mean()

    st.line_chart(stock_data.set_index('datetime')[['close', '7-Day SMA', '30-Day SMA']])
    
    # 2. Price Trend Analysis
    st.subheader("📊 Price Trend Over Time")
    st.line_chart(stock_data.set_index('datetime')['close'])

    # 4. Performance Comparison of All Tech Stocks
    st.subheader("📊 Stock Performance Comparison")

    # Calculate % change over the last 30 days for all stocks
    performance = stocks_df.groupby('symbol').apply(
        lambda x: ((x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0]) * 100
    ).reset_index(name='30-Day Change (%)')

    st.bar_chart(performance.set_index('symbol')['30-Day Change (%)'])
    
elif selected == "Market Insights":
    st.title("Market Insights")
    
    st.subheader("📰 Market Sentiment Analysis")

    # User Input for Query
    query = st.selectbox("Select a Stock/Crypto Symbol:", combined_df['symbol'].unique())
    #query = st.text_input("Enter a Stock/Crypto Symbol (e.g., BTC, AAPL, ETH):", "BTC")

    # Fetch News
    if st.button("Get Market Sentiment"):
        articles = fetch_news(query)

        if articles:
            # Process news articles
            sentiments = []
            for article in articles:
                #sentiment_score = analyze_sentiment(article['title'] + " " + article['description'])
                sentiment_score = analyze_sentiment((article.get('title') or '') + " " + (article.get('description') or ''))
                sentiments.append({
                    'title': article['title'],
                    'description': article['description'],
                    'sentiment_score': sentiment_score
                })

            # Convert to DataFrame
            df = pd.DataFrame(sentiments)

            # Calculate Overall Sentiment
            overall_sentiment = df['sentiment_score'].mean()

            # Display Sentiment Result
            sentiment_label = "Bullish 📈" if overall_sentiment > 0 else "Bearish 📉" if overall_sentiment < 0 else "Neutral ⚖️"
            st.metric(label="Market Sentiment", value=sentiment_label, delta=f"{overall_sentiment * 100:.2f}%")

            # Show News Headlines
            st.subheader("🗞️ Recent Headlines")
            for i, row in df.iterrows():
                st.write(f"**{row['title']}**")
                st.write(row['description'])
                st.write(f"Sentiment Score: {row['sentiment_score']:.2f}")
                st.write("---")
        else:
            st.warning("No news articles found for this query.")           # Hire Train Deploy