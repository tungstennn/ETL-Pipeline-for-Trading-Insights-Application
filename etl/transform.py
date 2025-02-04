import pandas as pd
from textblob import TextBlob



def combine_dataframes(dfs):
    if not dfs:
        return None

    combined_df = dfs[0]  # Start with first dataframe
    for df in dfs[1:]:
        combined_df = pd.concat(dfs, ignore_index=True)

    return combined_df

# Function for Sentiment Analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity  # Range: -1 (negative) to 1 (positive)
