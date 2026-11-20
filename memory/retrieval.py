import ollama
import numpy as np
import sqlite3
import requests
import json

EMBEDDING_MODEL = 'qwen3-embedding:0.6b'
conn = sqlite3.connect('pt.db')

# Create the FTS5 virtual table for memory content if it doesn't exist
conn.execute(""" 
    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5 (
        content,
        content ='memory',
        content_rowid ='id'
    )
""")

conn.execute("""INSERT INTO memory_fts(memory_fts) VALUES ('rebuild');""")

# Create the embedded_memories table if it doesn't exist
conn.execute("""
     CREATE TABLE IF NOT EXISTS embedded_memories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        embedding BLOB
    )
""")

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

def intoEmbedding(text: str) -> bytes:
        response = ollama.embed(EMBEDDING_MODEL, input=text) # converting text into vectors

        # vec stores each number as a float32
        vec = np.array(response["embeddings"][0], dtype = np.float32) 

        return vec.tobytes() # converting vector into bytes aka unstructured data to store into the blob

# Extract all existing memory content from the database
# memories has id and content
with sqlite3.connect("pt.db") as db:
    memories = db.execute(
        "SELECT id, content FROM memory ORDER BY id"
    ).fetchall()

for t_id, t_content in memories:
    if not t_content or not t_content.strip():
        continue

    # converting text into vectors
    vector_blob = intoEmbedding(t_content)
    conn.execute("""
    INSERT INTO embedded_memories (id, content, embedding)
    VALUES (?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        content = excluded.content,
        embedding = excluded.embedding
    """, (t_id, t_content, vector_blob))

conn.commit()
conn.close()