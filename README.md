# AI Data Assistant Project

A Python‑based data analytics assistant that loads employee data from Excel or MySQL, analyzes it using Pandas and NumPy, and answers natural‑language questions using an AI model.

## Features
- Load data from CSV/Excel or MySQL  
- Clean and standardize employee datasets  
- Query data using natural language  
- Compute statistics (averages, salary ranges, comparisons)  
- Virtual environment isolation with `venv`  
- Technologies: Python, Pandas, NumPy, SQLAlchemy, MySQL, OpenAI API  

## Project Structure
- `csv_ai_assistant.py` — main AI assistant script  
- `init_mysql.py` — loads Excel data into MySQL  
- `employees.xlsx` — sample dataset  
- `.venv/` — project virtual environment  
- `requirements.txt` — all dependencies  

## How to Run
### 1. Create virtual environment
```
python -m venv .venv
```

### 2. Activate it
```
.\.venv\Scriptsctivate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Load Excel data into MySQL
```
python init_mysql.py
```

### 5. Run the assistant
```
python csv_ai_assistant.py
```

## Technologies Used
- **Python 3**
- **Pandas** — data analysis  
- **NumPy** — mathematical operations  
- **SQLAlchemy + MySQL** — database backend  
- **OpenAI LLM** — natural‑language question answering  

