from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from config import Config

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Config.ROLE_USER, Config.ROLE_ADMIN), default=Config.ROLE_USER)
    avatar_url = db.Column(db.String(255), default=Config.DEFAULT_AVATAR)
    created_at = db.Column(db.DateTime, default=utc_now)
    tracks = db.relationship('Track', backref='author', lazy='dynamic', cascade='all, delete-orphan')


class Track(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    cover_path = db.Column(db.String(255), default=Config.DEFAULT_COVER)
    duration = db.Column(db.Integer, default=0)
    track_order = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=utc_now)
    plays = db.Column(db.Integer, default=0)
    source = db.Column(db.String(30), default=Config.SOURCE_MANUAL)
