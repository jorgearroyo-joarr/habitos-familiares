
import sqlite3
import os

db_path = "x:\\Data\\mega\\familia.arroyo.rivera@outlook.com\\Family\\habitos-familiares\\habitosfam.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE profiles SET balance = 0.0 WHERE balance IS NULL")
    print(f"Updated balance for {cursor.rowcount} rows")
    cursor.execute("UPDATE profiles SET unlocked_themes = '[\"default\"]' WHERE unlocked_themes IS NULL")
    print(f"Updated unlocked_themes for {cursor.rowcount} rows")
    cursor.execute("UPDATE profiles SET unlocked_avatars = '[]' WHERE unlocked_avatars IS NULL")
    print(f"Updated unlocked_avatars for {cursor.rowcount} rows")
    conn.commit()
    conn.close()
    print("Database patch completed successfully.")
else:
    print(f"Database not found: {db_path}")
