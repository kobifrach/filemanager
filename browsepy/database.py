# database.py
import pyodbc
from datetime import datetime

#פה מתחברים לDB

def get_db_connection():
    server = 'DESKTOP-C0CP90K\\MSSQLSERVER01'
    database = 'ManageDB'
    # username = 'your_username'
    # password = 'your_password'

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                      f'SERVER={server};'
                      f'DATABASE={database};'
                      f'Trusted_Connection=yes;')

    return conn
def log_action(action, performer):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO history (date, action, performer) VALUES (?, ?, ?)", 
                   (datetime.now(), action, performer))
    conn.commit()
    cursor.close()
    conn.close()

# דוגמה לשימוש במידלוור
def execute_db_operation(query, params, performer):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(query, params)
    conn.commit()
    
    # רישום ההיסטוריה (אם יש צורך)
    log_action(query, performer)
    
    cursor.close()
    conn.close()
