import requests
import pandas as pd
import os
from dotenv import load_dotenv
import psycopg2

# Load variables from .env file
load_dotenv()

# Replace with your API key
# call API key from the environment variable
API_KEY = os.getenv('API_KEY')
BTC_symbol = "BTC/GBP"
ETH_symbol = "ETH/GBP"

interval = "1h"     # Hourly data


# Function to get data
def get_12_data(symbol, interval):
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