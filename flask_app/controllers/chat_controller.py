from flask_app import app, socketio
from flask import render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from flask_app.models.user_model import User
from flask_app.models.room_model import Room
from flask_app.models.message_model import Message
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


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    logged_user = User.get_by_id(data)
    public_rooms = Room.get_public()
    return render_template('dashboard.html', logged_user=logged_user, public_rooms=public_rooms)

@app.route('/api/rooms/<int:id>/history')
def get_room_history(id):
    data = {
        'id': id
    }
    return Room.get_history_by_id(data)

@app.route('/api/rooms/<int:id>/leave')
def remove_room(id):
    data = {
        'room_id': id,
        'user_id': session['user_id']
    }
    Room.leave_room(data)
    return {'message':'success'}

@app.route('/api/rooms/<int:id>/join')
def join_new_room(id):
    data = {
        'room_id': id,
        'user_id': session['user_id']
    }
    Room.join_room(data)
    roomname = Room.get_by_id({'id':id}).name
    return {'message':'success', 'roomname': roomname}

@app.route('/rooms/create', methods=['POST'])
def create_room():
    if 'user_id' not in session:
        return redirect('/')
    data ={
        'creator_id': session['user_id'],
        'name': request.form['name']
    }
    if 'private' in request.form:
        new_room = Room.create_private(data)
    else:
        new_room = Room.create(data)
    Room.join_room({
        'room_id': new_room,
        'user_id': session['user_id']     
    })
    return redirect('/my_rooms')
    