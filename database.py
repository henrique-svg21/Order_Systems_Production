#creation and settings for SQLite database
import sqlite3

#constant with name of the database created on postgree
#the file will be created during first time execution
db_order = 'orders.db'

def get_connection():
    '''
    Creates and returns an connection with database SQLite
    
    Property row_factory allows rows access though order['product'] instead of order[1]
    
    returns:
        sqlite3.Connection: connection object with database 
    '''
    
    conn = sqlite3.connect(db_order)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    '''
    Inicializes database creating table 'orders' in case it does not exists. Safe for calling multiple times
    '''
    
    conn = get_connection()
    
    #Cursor() allows execution of SQL commands
    cursor = conn.cursor()
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS orders (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        status TEXT DEFAULT 'Pendent',
                        created_at TEXT DEFAULT (datetime(NOW(), 'localtime')) 
                    );  
                   ''')
    
    #commit() SAVES changes in .db file
    conn.commit()
    print("Database successfully inicialized!")
    
    