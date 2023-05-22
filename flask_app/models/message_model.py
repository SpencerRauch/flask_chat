from flask_app.config.mysqlconnect import connectToMySQL
from flask_app import DATABASE
from flask import flash

class Message:
    def __init__(self,data):
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sender_id = data['sender_id']
        self.room_id = data['room_id']

    
    @classmethod
    def create(cls,data):
        query = """
            INSERT INTO messages (content, sender_id, room_id)
            VALUES (%(content)s, %(sender_id)s, %(room_id)s);
        """
        return connectToMySQL(DATABASE).query_db(query, data)

