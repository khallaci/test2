"""Safe version demonstrating parameterized queries / prepared statements."""
import sqlite3

def search_safe(q: str):
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    # SAFE: use parameterized queries to avoid injection risks
    cur.execute("SELECT id, name FROM users WHERE name LIKE ?", ('%' + q + '%',))
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    print(search_safe('alice'))
