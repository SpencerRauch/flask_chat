from flask_app import app, socketio
from flask import render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from flask_app.models.user_model import User
from flask_app.models.room_model import Room
from flask_app.models.message_model import Message
from flask_socketio import emit, join_room, leave_room, send

#  This was just used for testing early on
GLOBAL_CHAT = [
    {'username':'System', 'content':'Welcome', 'created_at': 'placeholder date time'}
]

@socketio.on('connect')
def test_connect(auth):
    print('printed',auth)
    emit('chat_history', {'data': GLOBAL_CHAT})


@socketio.on('join')
def on_join(data):
    print('join called')
    username = data['username']
    room = data['room']
    join_room(str(room))
    socketio.emit('user_join',(username,room),to=str(room))

@socketio.on('leave')
def on_leave(data):
    print('leave called for', data)
    username = data['username']
    room = data['room']
    leave_room(room)
    socketio.emit('user_leave',(username,room),to=str(room))

@socketio.on('new_message')
def new_message(data, currentRoom):
    # GLOBAL_CHAT.append(data);
    # print(GLOBAL_CHAT)
    print(f'new message called for room {currentRoom}')
    Message.create({
        'content': data['content'],
        'sender_id': session['user_id'],
        'room_id': currentRoom})
    
    socketio.emit('message_added', (data, currentRoom),to=str(currentRoom))


        