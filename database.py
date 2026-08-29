import json
import sqlite3
from config import Database_file

def create_database():
    con = sqlite3.connect(Database_file)
    c = con.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS SCANS (
        USERNAME TEXT NOT NULL,
        SCAN_ID TEXT PRIMARY KEY,
        TARGET_URL TEXT NOT NULL,
        FINAL_URL TEXT,
        STATUS TEXT NOT NULL,
        RISK_INDEX INT,
        RISK_LEVEL TEXT,
        CREATED_AT TEXT DEFAULT CURRENT_TIMESTAMP,
        REPORT_JSON TEXT
    )''')
    con.commit()
    con.close()

def save_scan(report):
    con = sqlite3.connect(Database_file)
    c = con.cursor()
    query = ("""
    INSERT INTO SCANS (
        USERNAME, SCAN_ID, TARGET_URL, FINAL_URL, STATUS,
        RISK_INDEX, RISK_LEVEL, CREATED_AT, REPORT_JSON
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)
   
    c.execute(query, (
        report.username,
        report.scan_id,
        report.target_url,
        report.final_url,
        report.status,
        report.risk_index,
        report.risk_level,
        report.created_at,
        json.dumps(report.report_json)
    ))
    con.commit()
    con.close()

def get_scan_history():
    con = sqlite3.connect(Database_file)
    c = con.cursor()
    name = input('enter the username....')
    c.execute("SELECT * FROM SCANS WHERE USERNAME = ?", (name,))
    rows = c.fetchall()
    con.close()
    return rows

def get_history():
    n = input('enter user name....')
    connection = sqlite3.connect(Database_file)
    cursor = connection.cursor()
    cursor.execute(''' 
        SELECT scan_id, final_url, risk_index, created_at 
        FROM scans WHERE username = ?
    ''', (n,))
    a = cursor.fetchall()
    connection.close()
    return a

def streamlit_to_scanner_create():
    con = sqlite3.connect(Database_file)
    c = con.cursor()
    query = ("""CREATE TABLE IF NOT EXISTS TO_SCANS (
        USERNAME TEXT NOT NULL,
        TARGET_URL TEXT NOT NULL
    )""")
    c.execute(query)
    con.commit()
    con.close()

def streamlit_to_scanner_save(username, target_url):
    con = sqlite3.connect(Database_file)
    c = con.cursor()
    query = ("""INSERT INTO TO_SCANS (USERNAME, TARGET_URL) VALUES (?, ?)""")
    c.execute(query, (username, target_url))
    con.commit()
    con.close()