from config import Database_file
import sqlite3
def get_scan_history():
    conn = sqlite3.connect(Database_file)
    cursor = conn.cursor()
    return cursor.execute("SELECT * FROM SCANS").fetchall()