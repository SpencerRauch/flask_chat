from flask_app.config.mysqlconnect import connectToMySQL
from flask_app import DATABASE
from flask_app.models import room_model
from flask import flash
import re
ALPHA = re.compile(r"^[a-zA-Z]+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$") 

class User:
    def __init__(self,data) -> None:
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def create(cls,data):
        query = """
            INSERT INTO users (username, email, password)
            VALUES (%(username)s, %(email)s, %(password)s);
        """
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def get_by_id(cls,data):
        query = """
            SELECT * FROM users 
            LEFT JOIN users_join_rooms 
            ON users_join_rooms.user_id = users.id
            LEFT JOIN rooms
            ON users_join_rooms.room_id = rooms.id
            WHERE users.id = %(id)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            user = cls(results[0])
            user.joined_rooms = []
            for row in results:
                if row['rooms.id'] == None:
                    return user
                room_data = {
                    **row,
                    'id': row['rooms.id'],
                    'created_at': row['rooms.created_at'],
                    'updated_at': row['rooms.updated_at']
                }
                user.joined_rooms.append(room_model.Room(room_data))
            return user
        return False

    #This version doesn't instatiate, for use with our api calls
    @classmethod
    def get_by_id_dict(cls,data):
        query = """
            SELECT * FROM users 
            LEFT JOIN users_join_rooms 
            ON users_join_rooms.user_id = users.id
            WHERE id = %(id)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            user = {
                'username': results[0]['username'],
                'id': results[0]['id']
            }
            user['joined_room_ids'] = []
            for row in results:
                user['joined_room_ids'].append(row['room_id'])
            return user
        return False
    

    
    @classmethod
    def get_by_username(cls,data):
        query = """
            SELECT * FROM users WHERE username = %(username)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            return cls(results[0])
        return False
    
    @staticmethod
    def validator(data):
        print('data', data)
        is_valid = True
        if len(data['username']) < 1:
            is_valid = False
            flash('First name required','reg')
        elif len(data['username']) < 2:
            is_valid = False
            flash('First name must be 2 chars','reg')
        else:
            potential_user = User.get_by_username({'username': data['username']}) #this will either return a user or FALSE
            if potential_user:
                flash('username already exists in db', 'reg')
                is_valid = False
        if len(data['email']) < 1:
            is_valid = False
            flash('Email required','reg')
        elif not EMAIL_REGEX.match(data['email']):
            is_valid = False
            flash('Email must be valid format','reg')
        if len(data['password']) < 1:
            flash('pass req', 'reg')
            is_valid = False
        elif len(data['password']) < 8:
            flash('pass must be > 8 char', 'reg')
            is_valid = False
        elif data['password'] != data['confirm_pass']:
            flash('passwords must match', 'reg')
            is_valid = False
        return is_valid
    
