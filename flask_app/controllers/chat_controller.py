from flask_app import app, socketio
from flask import render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from flask_app.models.user_model import User
from flask_socketio import emit, join_room, leave_room, send

GLOBAL_CHAT = [
    {'username':'System', 'content':'Welcome', 'created_at': 'placeholder date time'}
]

@socketio.on('connect')
def test_connect(auth):
    print('printed',auth)
    emit('chat_history', {'data': GLOBAL_CHAT})


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('new_message')
def new_message(data):
    GLOBAL_CHAT.append(data);
    print(GLOBAL_CHAT)
    socketio.emit('message_added', data)
