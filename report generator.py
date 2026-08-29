def get_scan_history():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    return cursor.execute("SELECT * FROM SCANS").fetchall()