import os
import json
import traceback
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ================== CONFIG ==================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(" OPENAI_API_KEY not found in .env")
    raise SystemExit(0)

db_url = os.getenv("DB_URL")  
engine = None
if db_url:
    engine = create_engine(db_url)

client = OpenAI()

# ================== DATA LOADERS ==================


def load_file_dataframe(path: str) -> pd.DataFrame:
    """Load a DataFrame from CSV or Excel, based on file extension."""
    path = path.strip()
    if not path:
        raise ValueError("Empty file path")

    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    elif lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type. Use .csv, .xlsx or .xls")


def load_mysql_dataframe(table_name: str = "employees") -> pd.DataFrame:
    """Load data from MySQL using SQLAlchemy engine."""
    if engine is None:
        raise RuntimeError("DB_URL is not set in .env")

    print(f"📥 Loading data from MySQL (table '{table_name}')...")
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    return df


def build_context(df: pd.DataFrame, max_rows: int = 20):
    """Build a small context (columns + sample rows) to send to the model."""
    return {
        "columns": list(df.columns),
        "rows": df.head(max_rows).to_dict(orient="records"),
    }


# ================== OPENAI LOGIC ==================


def ask_ai_and_execute(question: str, df: pd.DataFrame, context: dict):
    """
    Ask the model a question about the data.
    If it returns Python code (```python ... ```), execute it on df.
    Otherwise, return the natural language answer.
    """

    system_prompt = (
        "You are a data analyst. "
        "Your job is to answer questions about a tabular dataset (pandas DataFrame) "
        "AND generate Python pandas code when needed.\n\n"
        "Rules:\n"
        "1. If the user's question requires data manipulation, return ONLY Python code, nothing else.\n"
        "2. The code must operate on the dataframe named df.\n"
        "3. Do NOT use print(). Return the dataframe or value as the last expression.\n"
        "4. If no code is needed, answer normally in plain English.\n"
        "5. Your response format must be either natural language, or python code.\n"
        "6. When filtering rows, ALWAYS return full rows (all columns), not a single column.\n"
        "7. If you compute a single number (mean, min, max, range, etc.) return just that number."
        "   - Pure natural language answer\n"
        "   - Pure Python code inside triple backticks ```python ... ```"
    )

    user_prompt = (
        f"Columns: {context['columns']}\n\n"
        f"Sample rows (JSON):\n"
        f"{json.dumps(context['rows'], ensure_ascii=False, indent=2)}\n\n"
        f"User question:\n{question}"
    )

    # --- API call ---
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as e:
        return f"API error: {e}"

    # --- Read response text ---
    try:
        raw = response.output[0].content[0].text.strip()
    except Exception as e:
        return f"Error reading AI response: {e}"

    # --- If AI returned python code ---
    if raw.startswith("```python"):
        code = raw.replace("```python", "").replace("```", "").strip()

        try:
            lines = [line for line in code.splitlines() if line.strip()]
            local_env = {"df": df}

            if len(lines) == 1:
                result = eval(lines[0], {}, local_env)
            else:
                body = "\n".join(lines[:-1])
                last_expr = lines[-1]
                exec(body, {}, local_env)
                result = eval(last_expr, {}, local_env)

            return result

        except Exception as e:
            return f"Execution error: {e}\nCode was:\n{code}"

    
    return raw


# ================== MAIN ==================


def main():
    print("\n AI Data Assistant (CSV/Excel + MySQL) is ready! ")
    print("You can analyze either CSV/Excel files or a MySQL table.\n")

    print("Choose data source:")
    print("1) CSV / Excel file")
    print("2) MySQL table 'employees'")
    choice = input("Enter 1 or 2 (default 1): ").strip()
    if choice == "":
        choice = "1"

    df = None

    if choice == "1":
        file_path = input("Enter path to CSV or Excel file (default: data.csv): ").strip()
        if not file_path:
            file_path = "data.csv"

        try:
            df = load_file_dataframe(file_path)
        except Exception as e:
            print(" Error loading file:", e)
            return

        print(" File loaded successfully!")
    elif choice == "2":
        try:
            df = load_mysql_dataframe("employees")
        except Exception as e:
            print(" Error loading from MySQL:", e)
            return

        print(" MySQL data loaded successfully!")
    else:
        print("Invalid choice.")
        return

    print("Columns:", list(df.columns))
    context = build_context(df)

    while True:
        try:
            q = input("\nAsk a question about the data (or type 'exit' to quit): ")
        except EOFError:
            break

        if q.lower() == "exit":
            break
        if not q.strip():
            continue

        try:
            answer = ask_ai_and_execute(q, df, context)

            # ---- normalize pandas / numpy outputs for JSON printing ----
            if isinstance(answer, pd.DataFrame):
                answer = answer.to_dict(orient="records")
            elif isinstance(answer, pd.Series):
                answer = answer.to_dict()
            elif isinstance(answer, np.generic):
                answer = answer.item()

            # if it's already a string (natural language) – just print
            if isinstance(answer, str):
                print("\n Result:\n", answer, "\n")
            else:
                print("\n Result:\n", json.dumps(answer, indent=2, ensure_ascii=False), "\n")

        except Exception as e:
            print("Unexpected error while handling the question:")
            print(e)
            print("Full traceback:")
            traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Top-level error:", e)
        print("Full traceback:")
        traceback.print_exc()
