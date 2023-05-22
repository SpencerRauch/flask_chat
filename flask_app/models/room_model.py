from flask_app.config.mysqlconnect import connectToMySQL
from flask_app import DATABASE
from flask import flash
import re

class Room:
    def __init__(self,data):
        self.id = data['id']
        self.name = data['name']
        self.private = data['private']
        self.deleted = data['deleted']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.creator_id = data['creator_id']


    @classmethod
    def create(cls,data):
        query = """
            INSERT INTO rooms (name, creator_id)
            VALUES (%(name)s, %(creator_id)s);
        """
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def create_private(cls,data):
        query = """
            INSERT INTO rooms (name, creator_id, private)
            VALUES (%(name)s, %(creator_id)s, 1);
        """
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def get_public(cls):
        query = """
            SELECT * FROM rooms WHERE private = 0;
        """
        results = connectToMySQL(DATABASE).query_db(query)
        all_rooms = []
        for row in results:
            all_rooms.append(cls(row))
        return all_rooms
    
    @classmethod
    def get_by_id(cls,data):
        query = """
            SELECT * FROM rooms WHERE id = %(id)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            return cls(results[0])
        return False
    
    @classmethod
    def public_get_created_by_user_id(cls,data):
        query = """
            SELECT *, COUNT(users_join_rooms.user_id) as joined FROM rooms 
            JOIN users ON users.id = rooms.creator_id
            LEFT JOIN users_join_rooms ON rooms.id = users_join_rooms.room_id 
            WHERE users.id = %(id)s AND rooms.private = 0
            GROUP BY rooms.id;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        rooms = []
        if results:
            for row in results:
                room = cls(row)
                room.joined = row['joined']
                rooms.append(room)
        return rooms
    
    @classmethod
    def private_get_created_by_user_id(cls,data):
        query = """
            SELECT * FROM rooms 
            JOIN users ON users.id = rooms.creator_id
            WHERE users.id = %(id)s AND rooms.private = 1;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        rooms = []
        if results:
            for row in results:
                rooms.append(cls(row))
        return rooms
   
    @classmethod
    def get_by_name(cls,data):
        query = """
            SELECT * FROM rooms WHERE name = %(id)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            return cls(results[0])
        return False
    
    @classmethod
    def get_history_by_id(cls,data):
        data = {
            **data,
            'format': r"%m/%d/%Y, %r" 
        }
        query = """
            SELECT name, content, username, DATE_FORMAT(messages.created_at, %(format)s) as created_at FROM rooms 
            LEFT JOIN messages ON messages.room_id = rooms.id
            LEFT JOIN users ON messages.sender_id = users.id
            WHERE rooms.id = %(id)s;
        """
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results[0]['content'] == None:
            return [{'name':results[0]['name'],'content':'Start us off!','username':'nothing','created_at':'this time'}]
        return results

    @classmethod
    def leave_room(cls,data):
        query = """
            DELETE FROM users_join_rooms 
            WHERE room_id = %(room_id)s AND
            user_id = %(user_id)s;
        """
        return connectToMySQL(DATABASE).query_db(query,data)
    
    @classmethod
    def join_room(cls,data):
        query = """
            INSERT INTO users_join_rooms 
            (room_id, user_id)
            VALUES (%(room_id)s, %(user_id)s);
        """
        return connectToMySQL(DATABASE).query_db(query,data)