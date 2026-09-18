from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta
from mutagen import File as MutagenFile
import os
import random
from sqlalchemy import or_

from config import Config
from models import db, User, Track
from forms import LoginForm, RegisterForm, UploadTrackForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

MOSCOW_TZ = timezone(timedelta(hours=Config.TIMEZONE_OFFSET))


@app.context_processor
def inject_config():
    return {
        'Config': Config,
        'default_cover_url': url_for('static', filename=Config.DEFAULT_COVER),
        'default_avatar_url': url_for('static', filename=Config.DEFAULT_AVATAR),
    }


def get_now_str():
    """Текущее время в Москве в формате из конфига."""
    return datetime.now(MOSCOW_TZ).strftime(Config.TIMESTAMP_FORMAT)


def extensions_to_str(exts):
    """Превращает set расширений в строку 'PNG, JPG, GIF'."""
    return ', '.join(sorted(e.upper() for e in exts))


def get_random_default_cover():
    default_folder = os.path.join(app.root_path, Config.COVERS_DEFAULT_FOLDER)
    default_covers = [f for f in os.listdir(default_folder)
                      if f.lower().endswith(Config.ALLOWED_IMAGE_SUFFIXES)]

    if default_covers:
        return f'{Config.COVERS_DEFAULT_URL_PREFIX}/{random.choice(default_covers)}'
    return f'{Config.COVERS_DEFAULT_URL_PREFIX}/{Config.DEFAULT_COVER_NAME}'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.template_filter('format_duration')
def format_duration(seconds):
    if not seconds:
        return Config.DURATION_ZERO
    m = seconds // Config.SECONDS_PER_MINUTE
    s = seconds % Config.SECONDS_PER_MINUTE
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
            flash(Config.MSG_LOGIN_SUCCESS, 'success')
            return redirect(url_for('index'))
        flash(Config.MSG_LOGIN_FAILED, 'danger')

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
        flash(Config.MSG_REGISTER_SUCCESS, 'success')
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

        if audio_file and audio_file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_AUDIO_EXTENSIONS:
            filename = secure_filename(audio_file.filename)
            filename = f'{get_now_str()}_{filename}'

            upload_folder = os.path.join(app.root_path, Config.UPLOAD_FOLDER)
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            audio_file.save(file_path)

            try:
                audio = MutagenFile(file_path)
                duration_seconds = int(audio.info.length) if audio and hasattr(audio.info, 'length') else 0
            except Exception as e:
                app.logger.warning(f"Не удалось прочитать длительность: {e}")
                duration_seconds = 0
        else:
            exts = extensions_to_str(Config.ALLOWED_AUDIO_EXTENSIONS)
            flash(Config.MSG_INVALID_AUDIO.format(exts=exts), 'danger')
            return render_template('upload.html', form=form)

        if cover_file and cover_file.filename != '':
            ext = cover_file.filename.rsplit('.', 1)[1].lower()
            if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
                cover_filename = secure_filename(f"cover_{current_user.id}_{get_now_str()}.{ext}")

                cover_folder = os.path.join(app.root_path, Config.COVERS_DOWNLOAD_FOLDER)
                os.makedirs(cover_folder, exist_ok=True)
                cover_file.save(os.path.join(cover_folder, cover_filename))

                cover_path = f'{Config.COVERS_DOWNLOAD_URL_PREFIX}/{cover_filename}'
            else:
                exts = extensions_to_str(Config.ALLOWED_IMAGE_EXTENSIONS)
                flash(Config.MSG_COVER_FALLBACK.format(exts=exts), 'warning')
                cover_path = get_random_default_cover()
        else:
            cover_path = get_random_default_cover()

        new_track = Track(
            title=form.title.data,
            artist=form.artist.data,
            genre=form.genre.data,
            file_path=f'{Config.UPLOAD_URL_PREFIX}/{filename}',
            cover_path=cover_path,
            duration=duration_seconds,
            author=current_user,
            source=Config.SOURCE_MANUAL
        )
        db.session.add(new_track)
        db.session.commit()

        flash(Config.MSG_UPLOAD_SUCCESS, 'success')
        return redirect(url_for('music_library'))

    return render_template('upload.html', form=form)


@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash(Config.MSG_FILE_NOT_SELECTED, 'danger')
        return redirect(url_for('settings'))

    file = request.files['avatar']
    if file.filename == '':
        flash(Config.MSG_FILE_NOT_SELECTED, 'danger')
        return redirect(url_for('settings'))

    if file and (file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        upload_folder = os.path.join(app.root_path, Config.AVATAR_FOLDER)
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        current_user.avatar_url = f'{Config.AVATAR_URL_PREFIX}/{filename}'
        db.session.commit()
        flash(Config.MSG_AVATAR_SUCCESS, 'success')
    else:
        exts = extensions_to_str(Config.ALLOWED_IMAGE_EXTENSIONS)
        flash(Config.MSG_INVALID_IMAGE.format(exts=exts), 'danger')

    return redirect(url_for('settings'))


@app.route('/api/reorder_tracks', methods=['POST'])
@login_required
def reorder_tracks():
    data = request.json
    track_ids = data.get('track_ids', [])

    for index, track_id in enumerate(track_ids):
        track = db.session.get(Track, track_id)
        if track and track.user_id == current_user.id:
            track.track_order = index

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/delete_track/<int:track_id>', methods=['DELETE'])
@login_required
def delete_track(track_id):
    track = Track.query.get_or_404(track_id)

    if track.user_id != current_user.id and current_user.role != Config.ROLE_ADMIN:
        return jsonify({'success': False, 'message': Config.MSG_NO_DELETE_RIGHTS}), 403

    try:
        file_path = os.path.join(app.root_path, Config.STATIC_FOLDER, track.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        app.logger.error(f"Ошибка при удалении файла: {e}")

    db.session.delete(track)
    db.session.commit()

    return jsonify({'success': True, 'message': Config.MSG_DELETE_SUCCESS})


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

    hours = total_duration // Config.SECONDS_PER_HOUR
    minutes = (total_duration % Config.SECONDS_PER_HOUR) // Config.SECONDS_PER_MINUTE

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
    tracks = Track.query.filter_by(user_id=user.id).filter(
        (Track.source == Config.SOURCE_MANUAL) | (Track.source == None)
    ).order_by(Track.uploaded_at.desc()).all()
    return render_template('user_tracks_manual.html', user=user, tracks=tracks)


# ===== ТРЕКИ, ДОБАВЛЕННЫЕ ИЗ JSON =====
@app.route('/tracks-json/<username>')
def user_tracks_json(username):
    user = User.query.filter_by(username=username).first_or_404()
    tracks = Track.query.filter_by(user_id=user.id, source=Config.SOURCE_JSON).order_by(Track.uploaded_at.desc()).all()
    return render_template('user_tracks_json.html', user=user, tracks=tracks)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(Config.MSG_LOGOUT, 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
