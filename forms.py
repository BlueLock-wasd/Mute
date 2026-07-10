from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

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
    genre = SelectField('Жанр', choices=[
        ('Rock', 'Рок'),
        ('Pop', 'Поп'),
        ('Electronic', 'Электроника'),
        ('Jazz', 'Джаз'),
        ('Hip-Hop', 'Хип-Хоп')
    ])
    audio_file = FileField('Файл (MP3 или WAV', validators=[FileRequired()])
    submit = SubmitField('Загрузить трек')