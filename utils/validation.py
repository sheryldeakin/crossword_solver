import pandas as pd

def validate_clue_df(df):
    required = ["number", "start_col", "start_row", "end_col", "end_row", "clue"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    if df[["start_col", "start_row", "end_col", "end_row"]].isnull().any().any():
        raise ValueError("Coordinate columns contain null values.")
