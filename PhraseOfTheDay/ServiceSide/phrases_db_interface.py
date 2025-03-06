import sqlite3

from phrase import Phrase

class db_interface:
    
    def __init__(self):
        conn = sqlite3.connect('phrases.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT UNIQUE NOT NULL,
                description TEXT,
                example TEXT,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_used TIMESTAMP
            )
        ''')
        conn.close()

    def insert_phrase(self, phrase, description, example, date_used=None):
        if (self.phrase_exists(phrase)):
            return False
        conn = sqlite3.connect('phrases.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO phrases (phrase, description, example, date_used)
            VALUES (?, ?, ?, ?)
        ''', (phrase, description, example, date_used))
        conn.commit()
        conn.close()

    def phrase_exists(self, phrase):
        conn = sqlite3.connect('phrases.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM phrases WHERE phrase = ?', (phrase,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_phrase_for_date(self, date):
        conn = sqlite3.connect('phrases.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM phrases WHERE date_used = ?', (date,))
        result = cursor.fetchone()
        conn.close()
        if not result == None:
            _, phrase, description, example, _, date_used = result
            phrase = Phrase(phrase, description, example)
            phrase.set_date(date_used)
            return phrase
        return None 

    def get_used_phrases_string(self):
        conn = sqlite3.connect('phrases.db')
        cursor = conn.cursor()
        cursor.execute('SELECT phrase FROM phrases')
        rows = cursor.fetchall()
        conn.close()
        phrases = [row[0] for row in rows]
        return ', '.join(phrases)