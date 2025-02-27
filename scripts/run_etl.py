import requests
import pandas as pd
import os
from dotenv import load_dotenv
from etl.extract import get_12_data
from etl.transform import combine_dataframes
from etl.load import save_to_db

# Load variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')

interval = "30min"     # Hourly data

# Get data
tech_stocks = ['AAPL', 'GOOGL', 'AMZN', 'META']
crypto = ['BTC/USD', 'ETH/USD', 'SOL/USD']

all_assets = tech_stocks + crypto

dataframes = []

# Extract

for asset in all_assets:
    df = get_12_data(asset, interval)
    if df is not None:
        dataframes.append(df)

# Transform

final_df = combine_dataframes(dataframes)

# Load

save_to_db(final_df, "abdirahmans_market_data")


# Save to CSV file
# final_df.to_csv("data/12data.csv", index=False)