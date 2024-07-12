from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from flask import request, jsonify
from datetime import datetime
import re


def delete_html_tags(text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

db = SQLAlchemy()
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=True)
    first_name = db.Column(db.String(), unique=False, nullable= True)
    last_name = db.Column(db.String(), unique=False, nullable= True)
    username = db.Column(db.String(), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean(), unique=False, nullable=True)


    def __repr__(self):
        return f'<User {self.email}>'
        
    def serialize(self):
        return {'id': self.id,
                'email': self.email,
                'is_active': self.is_active,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
                'is_admin': self.is_admin}


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=False, nullable=False)
    game_name = db.Column(db.String(), unique=False, nullable=True)
    body = db.Column(db.String(), unique=False, nullable=False)
    date = db.Column(db.Date(), unique=False, nullable=True)
    image_url = db.Column(db.String(), unique=False, nullable=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    game_to = db.relationship('Games', foreign_keys=[game_id])

    def __repr__(self):
        return f'<Post {self.title}>'

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'game_name': self.game_name,
            'body': self.body,
            'date': self.date,
            'image_url': self.image_url,
            'game_id': self.game_id
        }

@event.listens_for(Posts, 'before_insert')
def before_insert(mapper, connection, target):
    if target.game_id:
        game = Games.query.get(target.game_id)
        if game:
            target.game_name = game.name

@event.listens_for(Posts, 'before_update')
def before_update(mapper, connection, target):
    if target.game_id:
        game = Games.query.get(target.game_id)
        if game:
            target.game_name = game.name


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_to = db.relationship('Users', foreign_keys=[user_id])
    def __repr__(self):
        return f'<Like {self.id}>'
        
    def serialize(self):
        return {'id': self.id,
                'user_id': self.user_id}


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    background_image = db.Column(db.String(), unique=False, nullable=True) 
    description = db.Column(db.String(), unique=False, nullable=False)
    released_at = db.Column(db.String(), unique=False, nullable=True)
    metacritic = db.Column(db.Integer(), unique=False, nullable=True)


    def __repr__(self):
        return f'<Game {self.name}>'
    
    def clean_description(self):
        return delete_html_tags(self.description)
        
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'background_image': self.background_image, 
                'description': self.clean_description(),
                'metacritic': self.metacritic,
                'released_at': self.released_at}
