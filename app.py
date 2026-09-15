from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from mutagen import File as MutagenFile
import os


from config import Config
from models import db, User, Track
from forms import LoginForm, RegisterForm, UploadTrackForm
import random

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

ALLOWED_AUDIO = {'mp3', 'wav'}
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif'}

MOSCOW_TZ = timezone(timedelta(hours=Config.TIMEZONE_OFFSET))

def get_random_default_cover():
    default_folder = os.path.join(app.root_path, 'static/images/covers_default')
    default_covers = [f for f in os.listdir(default_folder)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if default_covers:
        return f'images/covers_default/{random.choice(default_covers)}'
    else:
        return 'images/covers_default/default_1.jpg'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_filter('format_duration')
def format_duration(seconds):
    if not seconds:
        return '0:00'
    m = seconds // 60
    s = seconds % 60
    return f'{m}:{s:02d}'


@app.route('/')
def index():
    tracks = Track.query.order_by(Track.uploaded_at.desc()).limit(Config.HOME_TRACKS_LIMIT).all()
    user_tracks = []
    if current_user.is_authenticated:
        user_tracks = Track.query.filter_by(user_id=current_user.id).order_by(Track.uploaded_at.desc()).all()
    return render_template('index.html', tracks=tracks, user_tracks=user_tracks)    


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
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id).order_by(Track.uploaded_at.desc()).all()

    return render_template('profile.html', user=user, tracks=tracks)


@app.route('/library/<username>')
def user_library(username):
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id).order_by(Track.track_order.asc(), Track.uploaded_at.desc()).all()
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
        audio_file = form.audio_file.data
        cover_file = form.cover_file.data

        if audio_file and audio_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO:
            filename = secure_filename(audio_file.filename)
            timestamp = datetime.now(MOSCOW_TZ).strftime('%Y%m%d_%H%M%S')
            filename = f'{timestamp}_{filename}'

            upload_folder = os.path.join(app.root_path, Config.UPLOAD_FOLDER)
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            audio_file.save(file_path)

            try:
                audio = MutagenFile(file_path)
                duration_seconds = int(audio.info.length) if audio and hasattr(audio.info, 'length') else 0
            except Exception as e:
                print(f"⚠️ Не удалось прочитать длительность: {e}")
                duration_seconds = 0
        else:
            flash('Пожалуйста, загрузите файл в формате MP3 или WAV', 'danger')
            return render_template('upload.html', form=form)

        cover_path = None
        if cover_file and cover_file.filename != '':
            ext = cover_file.filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_IMAGES:
                cover_timestamp = datetime.now(MOSCOW_TZ).strftime('%Y%m%d_%H%M%S')
                cover_filename = secure_filename(f"cover_{current_user.id}_{cover_timestamp}.{ext}")

                cover_folder = os.path.join(app.root_path, Config.COVERS_DOWNLOAD_FOLDER)
                os.makedirs(cover_folder, exist_ok=True)
                cover_file.save(os.path.join(cover_folder, cover_filename))

                cover_path = f'images/covers_download/{cover_filename}'
            else:
                flash('Обложка должна быть в формате PNG, JPG или GIF (использована случайная)', 'warning')
                cover_path = get_random_default_cover()
        else:
            cover_path = get_random_default_cover()

        new_track = Track(
            title=form.title.data,
            artist=form.artist.data,
            genre=form.genre.data,
            file_path=f'uploads/{filename}',
            cover_path=cover_path,
            duration=duration_seconds,
            author=current_user,
            source='manual'
        )
        db.session.add(new_track)
        db.session.commit()

        flash('Трек успешно загружен!', 'success')
        return redirect(url_for('music_library'))

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

    if file and (file.filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES):
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


@app.route('/api/reorder_tracks', methods=['POST'])
@login_required
def reorder_tracks():
    data = request.json
    track_ids = data.get('track_ids', [])

    for index, track_id in enumerate(track_ids):
        track = Track.query.get(track_id)
        if track and track.user_id == current_user.id:
            track.track_order = index

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/delete_track/<int:track_id>', methods=['DELETE'])
@login_required
def delete_track(track_id):
    track = Track.query.get_or_404(track_id)

    if track.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'У вас нет прав для удаления этого трека'}), 403

    try:
        file_path = os.path.join(app.root_path, 'static', track.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

    db.session.delete(track)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Трек успешно удалён'})


# ===== МОЯ СТАТИСТИКА =====
@app.route('/stats/<username>')
def user_stats(username):
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id).all()

    # Общая статистика
    total_tracks = len(tracks)
    total_duration = sum(t.duration or 0 for t in tracks)
    total_plays = sum(t.plays or 0 for t in tracks)

    # Топ-жанры
    genre_counts = {}
    for t in tracks:
        genre_counts[t.genre] = genre_counts.get(t.genre, 0) + 1
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:Config.TOP_LIMIT]
    top_tracks = sorted(tracks, key=lambda t: t.plays or 0, reverse=True)[:Config.TOP_LIMIT]

    hours = total_duration // 3600
    minutes = (total_duration % 3600) // 60

    return render_template('user_stats.html',
                           user=user,
                           total_tracks=total_tracks,
                           total_plays=total_plays,
                           hours=hours,
                           minutes=minutes,
                           top_genres=top_genres,
                           top_tracks=top_tracks)


# ===== ТРЕКИ, ДОБАВЛЕННЫЕ ВРУЧНУЮ =====
@app.route('/tracks-manual/<username>')
def user_tracks_manual(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Показываем треки, у которых нет поля source или source == 'manual'
    tracks = Track.query.filter_by(user_id=user.id).filter(
        (Track.source == 'manual') | (Track.source == None)
    ).order_by(Track.uploaded_at.desc()).all()
    return render_template('user_tracks_manual.html', user=user, tracks=tracks)


# ===== ТРЕКИ, ДОБАВЛЕННЫЕ ИЗ JSON =====
@app.route('/tracks-json/<username>')
def user_tracks_json(username):
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id, source='json').order_by(Track.uploaded_at.desc()).all()
    return render_template('user_tracks_json.html', user=user, tracks=tracks)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли', 'danger')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
