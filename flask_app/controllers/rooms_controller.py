from flask_app import app, socketio
from flask import render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from flask_app.models.user_model import User
from flask_app.models.room_model import Room
from flask_app.models.message_model import Message


# API ROUTES
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

#Display Dashboard
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

#Create new room
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
    
#Delete a room
@app.route('/rooms/<int:id>/delete', methods=['POST'])
def delete_room(id):
    if 'user_id' not in session:
        return redirect('/')
    room = Room.get_by_id({'id':id})
    if room.creator_id != session['user_id']:
        session.clear()
        flash('Logged out for being a jerk', reg)
        return redirect('/')
    Room.delete_room({'id':id})
    return redirect('/my_rooms')