import sqlite3

DB_FILE = "database.db"
SCHEMA_FILE = "schema.sql"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("DB initialized:", DB_FILE)

if __name__ == "__main__":
    init_db()