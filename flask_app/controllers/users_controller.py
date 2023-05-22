from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_bcrypt import Bcrypt
from flask_app.models.user_model import User

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/users/register', methods=['POST'])
def reg_user():
    print(request.form)
    if not User.validator(request.form):
        return redirect('/')
    
    #hash our password
    hashed_pass = bcrypt.generate_password_hash(request.form['password'])

    data = {
        **request.form,
        'password': hashed_pass,
        'confirm_pass': hashed_pass #technically just here to make Spencer feel better
    }
    logged_user_id = User.create(data)
    session['user_id'] = logged_user_id
    return redirect('/dashboard')

@app.route('/users/login', methods=['POST'])
def log_user():
    data = {
        'username': request.form['username']
    }
    potential_user = User.get_by_username(data)
    if not potential_user:
        flash('Invalid credentials', 'log')
        print('user not found')
        return redirect('/')
    
    if not bcrypt.check_password_hash(potential_user.password, request.form['password']):
        flash('Invalid credentials', 'log')
        print('invlid pss')
        return redirect('/')
    session['user_id'] = potential_user.id
    return redirect('/dashboard')


@app.route('/my_rooms')
def my_rooms():
    if 'user_id' not in session:
        return redirect('/')
    logged_user = User.get_by_id({'id':session['user_id']})
    return render_template('my_rooms.html', logged_user=logged_user)

@app.route('/users/logout')
def logout():
    del session['user_id']
    return redirect('/')

@app.route('/api/users/get_logged_user')
def get_logged_user():
    if 'user_id' not in session:
        return redirect('/')
    return User.get_by_id_dict({'id': session['user_id']})
