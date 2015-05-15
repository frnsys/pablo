import os
import sqlite3
import hashlib

pablo_dir = os.path.expanduser('~/.pablo')
if not os.path.exists(pablo_dir):
    os.makedirs(pablo_dir)
db_file = os.path.join(pablo_dir, 'songs.db')

conn = sqlite3.connect(db_file)
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