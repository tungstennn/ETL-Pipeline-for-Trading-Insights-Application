import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Replace with your API key
# call API key from the environment variable
API_KEY = os.getenv('API_KEY')
BTC_symbol = "BTC/GBP"
ETH_symbol = "ETH/GBP"

interval = "30min"     # Hourly data


# Function to get crypto data
def get_crypto_data(symbol, interval):
    # API Endpoint
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={API_KEY}"

    # Fetch data
    response = requests.get(url)
    data = response.json()

    # Check for errors
    if "values" in data:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        print(symbol)
        print(df.head())
        print('--------------------------------------------------------------')
    else:
        print("Error:", data.get("message", "Unknown error"))
        print('--------------------------------------------------------------')


# Get data
get_crypto_data(BTC_symbol, interval)
get_crypto_data(ETH_symbol, interval)