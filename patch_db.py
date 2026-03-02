import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "ailover.db")

print(f"Veritabani yolu: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("ALTER TABLE users ADD COLUMN custom_persona_active BOOLEAN DEFAULT 0")
    cursor.execute("ALTER TABLE users ADD COLUMN custom_persona_name VARCHAR")
    cursor.execute("ALTER TABLE users ADD COLUMN custom_persona_prompt TEXT")
    
    conn.commit()
    print("Kolonlar basariyla eklendi.")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Kolonlar zaten var.")
    else:
        print(f"Hata: {e}")
except Exception as e:
    print(f"Beklenmeyen hata: {e}")
finally:
    if conn:
        conn.close()
