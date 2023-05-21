from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'PLACEHOLDER KEY DO NOT USE IN PRODUCTION'
socketio = SocketIO(app)
DATABASE = 'flask_chat'