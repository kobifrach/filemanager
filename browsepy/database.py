# database.py
import pyodbc
from datetime import datetime
from flask import current_app

#פה מתחברים לDB

def get_db_connection():
    server = 'DESKTOP-C0CP90K\\MSSQLSERVER01'
    database = 'ManageDB'
    # username = 'your_username'
    # password = 'your_password'
    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                        f'SERVER={server};'
                        f'DATABASE={database};'
                        f'Trusted_Connection=yes;')

        return conn
    except pyodbc.Error as e:
            current_app.logger.error(f"Error connecting to database: {e}")
            raise Exception("שגיאה בחיבור למסד הנתונים")

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
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        
        # רישום ההיסטוריה
        log_action(query, performer)
        
        current_app.logger.info(f"Query executed successfully: {query}")
    except pyodbc.Error as e:
        current_app.logger.error(f"Error executing query: {e}")
        raise Exception("שגיאה בהרצת השאילתה")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()