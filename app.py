from flask import Flask,redirect,render_template,request
from flask_sock import Sock

import sqlite3
from urllib.parse import parse_qs

# Setup DB
def init_db():
    with sqlite3.connect("chat.db") as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

init_db()


clients = []

app = Flask(__name__)
sock = Sock(app)
connected_clients = set()
@app.route("/")
def index():
    return render_template("index.html")


@sock.route('/dash')
def dash(ws):
    query = ws.environ.get('QUERY_STRING', '')
    params = parse_qs(query)
    username = params.get('username', ['anon'])[0]
    clients.append(ws)
    with sqlite3.connect("chat.db") as con:
            for row in con.execute("SELECT message, timestamp FROM messages WHERE username = ?", (username,)):
                ws.send(f"[{row[1]}] {username}: {row[0]}")
    
    try:
        while True:
            data = ws.receive()
            with sqlite3.connect("chat.db") as con:
                con.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, data))
            for client in clients:
                if client != ws:
                    client.send(f"{username}: {data}")
    except:
        clients.remove(ws)


if __name__ == "__main__":
    app.run(debug=True)


