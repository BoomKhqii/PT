import sqlite3

conn = sqlite3.connect('pt.db')

conn.execute(""" 

    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        content TEXT NOT NULL,

""")


# hardcoded memory --only temporary
conn.execute("""

    insert into memory (category, content) values ('general', 'You once tried running MetaTrader 5 on a Raspberry Pi 5 with 16 GB RAM, using Wine on Debian Linux, rather than a conventional Windows PC.')
 
""")

conn.commit()
conn.close()