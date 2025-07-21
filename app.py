from flask import Flask,redirect,render_template,request
from flask_sock import Sock
clients = []

app = Flask(__name__)
sock = Sock(app)
connected_clients = set()
@app.route("/")
def index():
    return render_template("index.html")


@sock.route('/dash')
def dash(ws):
    clients.append(ws)
    try:
        while True:
            data = ws.receive()
            for client in clients:
                if client != ws:
                    client.send(data)
    except:
        clients.remove(ws)


if __name__ == "__main__":
    app.run(debug=True)


