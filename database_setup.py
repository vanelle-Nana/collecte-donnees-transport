import sqlite3

def init_db():
    conn = sqlite3.connect('transport.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trajets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compagnie TEXT,
            depart TEXT,
            arrivee TEXT,
            prix REAL,
            date_voyage TEXT,
            date_collecte DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Succès : Dossier tout neuf et base de données prête !")

if __name__ == "__main__":
    init_db()