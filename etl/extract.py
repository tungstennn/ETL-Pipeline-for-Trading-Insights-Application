import requests
import pandas as pd
import os
from dotenv import load_dotenv
import psycopg2
from textblob import TextBlob

# Load variables from .env file
load_dotenv()

#interval = "1h"     # Hourly data

# Function to get data
def get_12_data(symbol, interval):
    API_KEY = os.getenv('API_KEY')
    # API Endpoint
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={API_KEY}"

    # Fetch data
    response = requests.get(url)
    data = response.json()

    # Check for errors
    if "values" in data:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["symbol"] = symbol
        # Hardcoded Filter to Exclude GBP Crypto
        df = df[~df['symbol'].str.contains('/GBP')]
        return df
    else:
        return "Error:", data.get("message", "Unknown error")

def get_data_from_db(query):
    conn = psycopg2.connect(
        host=os.getenv("DB_host"),
        database=os.getenv("DB_name"),
        user=os.getenv("DB_username"),
        password=os.getenv("DB_password"),
        port=os.getenv("DB_port")  # Default is usually 5432
    )
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to fetch news
def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={os.getenv('news_api_key')}"
    response = requests.get(url)
    data = response.json()
    return data['articles']
