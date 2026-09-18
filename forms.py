from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from config import Config

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=8, max=60)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class UploadTrackForm(FlaskForm):
    title = StringField('Название трека', validators=[DataRequired(), Length(max=100)])
    artist = StringField('Исполнитель', validators=[DataRequired(), Length(max=100)])
    genre = SelectField('Жанр', choices=Config.GENRES)
    audio_file = FileField('Файл (MP3 или WAV)', validators=[FileRequired()])
    cover_file = FileField('Обложка (PNG/JPG, опционально)')
    submit = SubmitField('Загрузить трек')