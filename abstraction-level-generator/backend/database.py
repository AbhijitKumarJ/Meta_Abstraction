# backend/database.py

import sqlite3
from contextlib import contextmanager

DATABASE_NAME = 'abstraction_levels.db'

def create_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_question TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create RawRequestResponseLog table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RawRequestResponseLog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                level_number INTEGER,
                request_type TEXT,
                input_prompt TEXT,
                raw_response TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES Questions (id)
            )
        ''')
        
        # Create DetailedAbstractions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DetailedAbstractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                level_number INTEGER,
                ideal_representation TEXT,
                generated_question TEXT,
                score REAL,
                variables TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES Questions (id)
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

# Create tables when the module is imported
create_tables()
