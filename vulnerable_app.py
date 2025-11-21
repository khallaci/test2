"""Simple illustrative script showing unsafe SQL usage.
This is intentionally vulnerable **only** to demonstrate detection of unsafe patterns.
DO NOT run this against production or remote systems. Use only local test databases.
"""
import sqlite3
from flask import Flask, request

app = Flask(__name__)

# Example: unsafe string interpolation to build SQL queries
@app.route('/search')
def search():
    q = request.args.get('q', '')  # user-supplied input
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    # VULNERABLE: building SQL by concatenating user input into the query string
    sql = "SELECT id, name FROM users WHERE name LIKE '%" + q + "%'"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return {"results": rows}

if __name__ == '__main__':
    # Note: this is for local testing only. The Flask app uses a local sqlite file.
    app.run(debug=True)
