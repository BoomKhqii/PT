import sqlite3
import requests
import json

conn = sqlite3.connect('pt.db')
category = "general" # default category for the memory entry

conn.execute(""" 

    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        content TEXT NOT NULL
    )
""")

# Method to call to store memory in the database
def store_memory(category, content):
    conn = sqlite3.connect('pt.db')

    try:
        conn.execute("""
            INSERT INTO memory (category, content) VALUES (?, ?)
        """, (category, content)
        )
        conn.commit()
    finally:
        conn.close()

# hardcoded memory --only temporary
#conn.execute("""
#
#    insert into memory (category, content) values ('general', 'You once tried running MetaTrader 5 on a Raspberry Pi 5 with 16 GB RAM, using Wine on Debian Linux, rather than a conventional Windows PC.')
 
#""")


conn.commit()
conn.close()