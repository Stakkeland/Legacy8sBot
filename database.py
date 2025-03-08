import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Database schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    mp INTEGER,
    mp_wins INTEGER,
    mp_losses INTEGER,
    sr INTEGER,
    rank TEXT NOT NULL CHECK(rank IN ('Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Overlord')),
    location TEXT NOT NULL CHECK(location IN ('west', 'central', 'east', 'eu', 'china', 'australia', 'south america', 'africa'))
)
''')
conn.commit()