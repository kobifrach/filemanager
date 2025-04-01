# database.py
import pyodbc

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
