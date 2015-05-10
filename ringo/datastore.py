import sqlite3
import hashlib


conn = sqlite3.connect('songs.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS songs (hash text, bpm real, key text, scale text)')

def save(filename, bpm, key):
    hash = _hash(filename)
    c.execute('INSERT INTO songs VALUES (?, ?, ?, ?)', (hash, bpm, key.key, key.scale))
    conn.commit()


def load(filename):
    hash = _hash(filename)
    return c.execute('SELECT bpm, key, scale FROM songs WHERE (hash = ?)', (hash,)).fetchone()


def _hash(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()