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

conn.execute("PRAGMA foreign_keys = ON;")

conn.execute(""" 
    CREATE TABLE IF NOT EXISTS memory_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        fact_key TEXT NOT NULL,
        current_version_id INTEGER,

        UNIQUE (category, fact_key),

        FOREIGN KEY (id, current_version_id)
            REFERENCES memory_versions (fact_id, id)
    );
""")

conn.execute(""" 
    CREATE TABLE IF NOT EXISTS memory_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fact_id INTEGER NOT NULL,
        version_number INTEGER NOT NULL,
        content TEXT NOT NULL CHECK (length(trim(content)) > 0),

        recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        valid_from TEXT,
        valid_until TEXT,
        source TEXT NOT NULL,

        UNIQUE (fact_id, version_number),
        UNIQUE (fact_id, id),

        FOREIGN KEY (fact_id)
            REFERENCES memory_facts (id),

        CHECK (
            valid_from IS NULL
            OR valid_until IS NULL
            OR valid_until > valid_from
        )
    );
""")

columns = {row[1] for row in conn.execute("PRAGMA table_info(memory)")} # Get existing columns in the memory table

# memory_Facts has id, category, fact_key, current_version_id
#memory_versions has id, fact_id, version_number, content, recorded_at, valid_from, valid_until, source
# Method to call to store memory in the database
def store_memory(data):
    # Parse the rawContent JSON string into a Python dictionary
    category = data.get("category", "general")
    fact_key = data.get("fact_key")
    content = data.get("content")
    source = data.get("source", "user_stated")
    valid_from = data.get("valid_from", None)
    valid_until = data.get("valid_until", None)
    
    if not isinstance(content, str) or not content.strip():
        print("Empty or invalid content, skipping memory storage.")
        return False
    content = content.strip()

    conn = sqlite3.connect("pt.db")
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")

            # Create the logical fact if it does not exist.
            conn.execute(
                """
                INSERT INTO memory_facts (category, fact_key)
                VALUES (?, ?)
                ON CONFLICT(category, fact_key) DO NOTHING
                """,
                (category, fact_key),
            )

            fact_id, current_version_id = conn.execute(
                """
                SELECT id, current_version_id
                FROM memory_facts
                WHERE category = ? AND fact_key = ?
                """,
                (category, fact_key),
            ).fetchone()

            # Skip an unchanged version.
            current = conn.execute(
                """
                SELECT content, valid_from, valid_until
                FROM memory_versions
                WHERE id = ? AND fact_id = ?
                """,
                (current_version_id, fact_id),
            ).fetchone()

            if current == (content, valid_from, valid_until):
                return False

            version_number = conn.execute(
                """
                SELECT COALESCE(MAX(version_number), 0) + 1
                FROM memory_versions
                WHERE fact_id = ?
                """,
                (fact_id,),
            ).fetchone()[0]

            cursor = conn.execute(
                """
                INSERT INTO memory_versions (
                    fact_id, version_number, content,
                    valid_from, valid_until, source
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    fact_id, version_number, content,
                    valid_from, valid_until, source,
                ),
            )

            conn.execute(
                """
                UPDATE memory_facts
                SET current_version_id = ?
                WHERE id = ?
                """,
                (cursor.lastrowid, fact_id),
            )

        return True
    finally:
        conn.close()

conn.commit()
conn.close()