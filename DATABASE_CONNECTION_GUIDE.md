# Database Connection Guide

## Why this change was made

Previously, every database function repeated the same steps:

1. Connect to MySQL.
2. Create a cursor.
3. Run the query.
4. Save the changes.
5. Close the cursor.
6. Close the connection.

Repeating these steps makes the code longer and harder to update. If the database settings change, every function would need to be changed.

The repeated code is now kept in one place inside `backend/src/database_call.py`.

## Step 1: Keep database settings in one place

The database settings are stored in `DB_CONFIG`:

```python
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3307")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "nse_sme_announcements"),
}
```

The program reads these values from environment variables. This keeps the password out of the Python files.

Before running the program in PowerShell, set the password:

```powershell
$env:DB_PASSWORD = "your-password"
```

You can also change the other settings when needed:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3307"
$env:DB_USER = "root"
$env:DB_NAME = "nse_sme_announcements"
```

These PowerShell values last only for the current terminal window.

## Step 2: Open and close the database automatically

The `database_cursor` helper handles the repeated work:

```python
@contextmanager
def database_cursor(commit=False):
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        if commit:
            connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
```

This helper:

1. Opens the database connection.
2. Creates the cursor used to run SQL.
3. Saves changes when `commit=True` is used.
4. Cancels unfinished changes if an error happens.
5. Always closes the cursor and connection.

## Step 3: Read data

For a `SELECT` query, use `database_cursor()`:

```python
def get_existed_stock_names():
    query = "SELECT id, symbol FROM stocks_list"

    with database_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
```

There is no need to manually open or close the connection.

## Step 4: Insert or change data

For `INSERT`, `UPDATE`, or `DELETE`, use `commit=True`:

```python
def add_stock(symbol, stock_name):
    query = """
        INSERT INTO stocks_list (symbol, stock_name)
        VALUES (%s, %s)
    """

    with database_cursor(commit=True) as cursor:
        cursor.execute(query, (symbol, stock_name))
```

`commit=True` tells the helper to save the changes after the query succeeds.

## Step 5: Insert many rows

Use `executemany` when inserting several rows:

```python
def add_many_stocks(stocks):
    query = """
        INSERT INTO stocks_list (symbol, stock_name)
        VALUES (%s, %s)
    """

    with database_cursor(commit=True) as cursor:
        cursor.executemany(query, stocks)
```

Example data:

```python
stocks = [
    ("ABC", "ABC Limited"),
    ("XYZ", "XYZ Limited"),
]

add_many_stocks(stocks)
```

## Adding new functions later

When adding a new database function:

1. Write the SQL query.
2. Open `database_cursor()` with `with`.
3. Run the query using `cursor.execute()` or `cursor.executemany()`.
4. Use `commit=True` only when the query changes data.

You do not need to write the connection details or closing code again.

## Files that were changed

- `backend/src/database_call.py`: Holds the database settings and shared connection helper.
- `backend/src/main.py`: Uses the shared helper when inserting announcement data.

## Git note

The `.gitignore` file currently contains `backend`. This means Git ignores the entire backend folder, including the changed Python files.

Remove that line if the backend source code should be saved in Git. Add smaller ignore rules for private or generated files instead, such as:

```gitignore
backend/venv/
backend/src/__pycache__/
*.pyc
```

Never save a real database password in Git.
