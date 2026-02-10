from etl.extract import extract_csv
from etl.transform import clean_data
from etl.load import load_to_postgres

def run():
    df = extract_csv("data/raw/data.csv")
    df = clean_data(df)
    load_to_postgres(df)

if __name__ == "__main__":
    run()
