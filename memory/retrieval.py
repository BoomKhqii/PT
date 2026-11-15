import sqlite3
import requests
import json

conn = sqlite3.connect('pt.db')

conn.execute(""" 
    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5 (
        content,
        content ='memory',
        content_rowid ='id'
    )
""")

conn.execute("""INSERT INTO memory_fts(memory_fts) VALUES ('rebuild');""")

def retrieve_memory(conn, search_query):
    return conn.execute(
        """
        SELECT m.id, m.category, m.content
        FROM memory_fts
        JOIN memory AS m ON m.id = memory_fts.rowid
        WHERE memory_fts MATCH ?
        ORDER BY rank
        LIMIT 5
        """,
        (search_query,),
    ).fetchall()

conn.commit()
conn.close()