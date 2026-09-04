from email.mime import image

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

from sqlalchemy.engine import default

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin'), default='user')
    avatar_url = db.Column(db.String(255), default='avatar/default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с треками (один ко многим)
    tracks = db.relationship('Track', backref='author', lazy='dynamic', cascade='all, delete-orphan')


class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    cover_path = db.Column(db.String(255), default='images/covers_default/default_1.jpg')
    duration = db.Column(db.Integer, default=0)
    track_order = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    plays = db.Column(db.Integer, default=0)
