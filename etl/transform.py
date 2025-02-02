import pandas as pd


def combine_dataframes(dfs):
    if not dfs:
        return None

    combined_df = dfs[0]  # Start with first dataframe
    for df in dfs[1:]:
        combined_df = pd.concat(dfs, ignore_index=True)

    return combined_df
