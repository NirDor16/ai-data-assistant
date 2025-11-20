import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    print(" DB_URL not found in .env")
    raise SystemExit(1)

engine = create_engine(DB_URL)


def main():
    excel_path = "test.xlsx"  

    print(f" Loading data from {excel_path} ...")
    
    df = pd.read_excel(excel_path)

    df = df[["name", "age", "department", "salary", "years_experience", "city"]]

    print(" Data loaded:")
    print(df.head())

    df.to_sql("employees", engine, if_exists="replace", index=False)

    print(" Table 'employees' created/updated in MySQL!")
    print("   Rows:", len(df))


if __name__ == "__main__":
    main()
