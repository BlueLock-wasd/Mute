import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET', 3))
    UPLOAD_FOLDER = 'static/uploads'
    AVATAR_FOLDER = 'static/uploads/avatar'
    COVERS_DEFAULT_FOLDER = 'static/images/covers_default'
    COVERS_DOWNLOAD_FOLDER = 'static/images/covers_download'
    HOME_TRACKS_LIMIT = 10
    TOP_LIMIT = 5
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@mute.ru')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')