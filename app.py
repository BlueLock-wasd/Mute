from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from config import Config
from models import db, User, Track
from forms import LoginForm, RegisterForm, UploadTrackForm

app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)


login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    # Берем последние 6 треков из базы
    tracks = Track.query.order_by(Track.uploaded_at.desc()).limit(10).all()
    return render_template('index.html', tracks=tracks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        flash('Неверное имя или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Теперь войдите', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/music')
def music_library():
    tracks = Track.query.order_by(Track.uploaded_at.desc()).all()
    return render_template('music.html', tracks=tracks)


@app.route('/profile/<username>')
def profile(username):
    # Ищем пользователя по имени. Если нет — 404 ошибка
    user = User.query.filter_by(username=username).first_or_404()

    # Получаем все треки этого пользователя
    tracks = Track.query.filter_by(user_id=user.id).order_by(Track.uploaded_at.desc()).all()

    return render_template('profile.html', user=user, tracks=tracks)


@app.route('/library/<username>')
def user_library(username):
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id).order_by(Track.uploaded_at.desc()).all()
    return render_template('user_library.html', user=user, tracks=tracks)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_track():
    form = UploadTrackForm()

    if form.validate_on_submit():
        file = form.audio_file.data

        # Проверка на существование
        if file and (file.filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav'}):
            # Генерируем безопасное имя для файла
            filename = secure_filename(file.filename)

            upload_folder = os.path.join(app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)

            file.save(os.path.join(upload_folder, filename))

            new_track = Track(
                title=form.title.data,
                artist=form.artist.data,
                genre=form.genre.data,
                file_path='uploads/' + filename,
                author=current_user
            )
            db.session.add(new_track)
            db.session.commit()

            flash('Трек успешно загружен!', 'success')
            return redirect(url_for('music_library'))
        else:
            flash('Пожалуйста, загрузите файт в формате MP3 или Wav', 'danger')

    return render_template('upload.html', form=form)


@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('settings'))

    file = request.files['avatar']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('settings'))

    # Разрешаем только картинки
    if file and (file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        upload_folder = os.path.join(app.root_path, 'static/uploads/avatar')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        current_user.avatar_url = filename
        db.session.commit()
        flash('Аватар обновлён!', 'success')
    else:
        flash('Недопустимый формат файла (только PNG, JPG, GIF)', 'danger')

    return redirect(url_for('settings'))

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory('static/uploads', filename)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)