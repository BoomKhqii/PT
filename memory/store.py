import sqlite3
import requests
import json

conn = sqlite3.connect('pt.db')
category = "general" # default category for the memory entry

conn.execute(""" 
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        content TEXT NOT NULL,
        fact_key TEXT NOT NULL,
        UNIQUE (category, fact_key)
    );
""")
columns = {row[1] for row in conn.execute("PRAGMA table_info(memory)")} # Get existing columns in the memory table

# Method to call to store memory in the database
def store_memory(data):
    # Parse the rawContent JSON string into a Python dictionary
    whatAction = data.get("action", "").lower()  # Check if the action is "insert"
    category = data.get("scope", "general")
    content = data.get("fact")
    fact_key = data["fact_key"] 
    #validity = data.get("valid_until", None)  # Optional validity field

    if not isinstance(content, str) or not content.strip():
        print("Empty or invalid content, skipping memory storage.")
        return False
    content = content.strip()

    conn = sqlite3.connect("pt.db")
    if whatAction == "upsert":
        try:
            conn.execute(
                """
                INSERT INTO memory (category, content, fact_key)
                VALUES (?, ?, ?)
                ON CONFLICT(category, fact_key)
                DO UPDATE SET content = excluded.content
                """,
                (category, content, fact_key),
            )
            conn.execute("""INSERT INTO memory_fts(memory_fts) VALUES ('rebuild');""")
            conn.commit()
            return True
        finally:
            conn.close()
    elif whatAction == "supersede":
        print("Replace an outdated fact while preserving its history | User changes their project priority")
        # Supersede the existing fact by updating its content and category
    else:
        print("	Wait for clarification before saving | Two facts appear contradictory")
        #pending contradictio of two facts, we will need to handle this case in the future
    print(f"Memory stored: {category} | {content} | {fact_key}")

conn.commit()
conn.close()