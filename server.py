from flask_app import app, socketio
from flask_app.controllers import users


if __name__=='__main__':
    socketio.run(app,debug=True)
