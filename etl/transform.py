import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["title"])
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df
