import json
import sqlite3
from config import DATABASE_FILE
def create_database():
    con = sqlite3.connect(DATABASE_FILE)
    c=con.cursor()
    c.execute(''' CREATE TABLE  IF NOT EXISTS scans(
     
    scan_id TEXT PRIMARY KEY,
    submitted_url TEXT NOT NULL,
    final_url TEXT,
    status TEXT NOT NULL,
    risk_index INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    report_json TEXT
    )''')
    con.commit()
    con.close()

    #Users database
    usr=sqlite3.connect('users.db')
    cc=usr.cursor()
    cc.execute('''CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    name TEXT,
    password TEXT )''')
    usr.commit()
    usr.close()

def save_scan(report):
    con=sqlite3.connect(DATABASE_FILE)
    c=con.cursor()
    c.execute('''
    INSERT INTO scans (scan_id, submitted_url, final_url, status, 
    risk_index, risk_level, model_dump_json) 
    VALUES('{}','{}','{}','{}',{},'{}','{}')'''.format(report.scan_id,
    report.submitted_url,
    report.final_url,
    report.status,
    report.risk_index,
    report.risk_level,
    report.model_dump_json()))
    con.commit()
    con.close()

def get_scan_history():
    con=sqlite3.connect(DATABASE_FILE)
    c=con.cursor()
    rows = c.execute('''SELECT * FROM scans ORDER BY created_at DESC''').fetchall()

    con.close()
    return rows


def fetch_pending_scan():
    streamlit_to_scanner_create()
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT USERNAME, TARGET_URL
            FROM TO_SCANS
            WHERE STATUS = 'pending'
            LIMIT 1
            """
        )

        return cursor.fetchone()
def mark_scan_processing(
    username: str,
    scan_id: str,
) -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            UPDATE TO_SCANS
            SET SCAN_ID = ?,
                STATUS = 'processing'
            WHERE USERNAME = ?
              AND STATUS = 'pending'
            """,
            (scan_id, username),
        )
def streamlit_to_scanner_create():
    con=sqlite3.connect(DATABASE_FILE)
    c=con.cursor()
    query=("""CREATE TABLE IF NOT EXISTS TO_SCANS (
        USERNAME TEXT NOT NULL,
        TARGET_URL TEXT NOT NULL,
        SCAN_ID TEXT,
        STATUS TEXT DEFAULT 'pending',
        OUTPUT_FOLDER TEXT,
        ERROR_MESSAGE TEXT)""")
    c.execute(query)
    con.commit()
    con.close()


def streamlit_to_scanner_save(username,target_url):
    con=sqlite3.connect(DATABASE_FILE)
    c=con.cursor()
    query=("""INSERT INTO TO_SCANS (USERNAME,TARGET_URL) VALUES (?,?)""")
    c.execute(query,(username,target_url))
    con.commit()
    con.close()


def mark_scan_completed(
    scan_id: str,
    output_folder: str,
) -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            UPDATE TO_SCANS
            SET OUTPUT_FOLDER = ?,
                STATUS = 'completed'
            WHERE SCAN_ID = ?
            """,
            (output_folder, scan_id),
        )

def mark_scan_failed(
    scan_id: str,
    error_message: str,
) -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            UPDATE TO_SCANS
            SET STATUS = 'failed',
                ERROR_MESSAGE = ?
            WHERE SCAN_ID = ?
            """,
            (error_message, scan_id),
        )
