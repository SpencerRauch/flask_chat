from flask_app import app, socketio
from flask_app.controllers import users_controller, chat_controller, rooms_controller

# notice we use the socketio instance to run our app
if __name__=='__main__':
    socketio.run(app,debug=True)
