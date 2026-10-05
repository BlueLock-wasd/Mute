import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ===== Основное =====
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')

    # ===== Время =====
    TIMEZONE_OFFSET = int(os.environ.get('TIMEZONE_OFFSET', 3))
    TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'   
    MONTH_KEY_FORMAT = '%Y-%m'
    MONTH_LABEL_FORMAT = '%m.%y'
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600
    DURATION_ZERO = '0:00'

    # ===== Источники треков =====
    SOURCE_MANUAL = 'manual'
    SOURCE_JSON = 'json'

    # ===== Роли =====
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    # ===== Лимиты =====
    HOME_TRACKS_LIMIT = 10
    TOP_LIMIT = 5

    # ===== Админ по умолчанию =====
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@mute.ru')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

    # ===== Физические пути (от корня проекта) =====
    STATIC_FOLDER = 'static'
    UPLOAD_FOLDER = 'static/uploads'
    AVATAR_FOLDER = 'static/uploads/avatar'
    DEFAULT_AVATAR = 'uploads/avatar/default.png'
    DEFAULT_COVER = 'images/covers_default/default_1.jpg'
    COVERS_DEFAULT_FOLDER = 'static/images/covers_default'
    COVERS_DOWNLOAD_FOLDER = 'static/images/covers_download'

    # ===== Пути для БД (относительно static/) =====
    UPLOAD_URL_PREFIX = 'uploads'
    COVERS_DOWNLOAD_URL_PREFIX = 'images/covers_download'
    COVERS_DEFAULT_URL_PREFIX = 'images/covers_default'
    AVATAR_URL_PREFIX = 'uploads/avatar'

    # ===== Дефолтные значения =====
    DEFAULT_COVER_NAME = 'default_1.jpg'

    # ===== Расширения без точки =====
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}

    # ===== Расширения с точкой =====
    ALLOWED_IMAGE_SUFFIXES = tuple(f'.{ext}' for ext in ALLOWED_IMAGE_EXTENSIONS)
    ALLOWED_AUDIO_SUFFIXES = tuple(f'.{ext}' for ext in ALLOWED_AUDIO_EXTENSIONS)

    # ===== Тексты сообщений (flash) =====
    MSG_LOGIN_SUCCESS = 'Вы успешно вошли!'
    MSG_LOGIN_FAILED = 'Неверное имя или пароль'
    MSG_REGISTER_SUCCESS = 'Регистрация успешна! Теперь войдите'
    MSG_UPLOAD_SUCCESS = 'Трек успешно загружен!'
    MSG_AVATAR_SUCCESS = 'Аватар обновлён!'
    MSG_LOGOUT = 'Вы вышли'
    MSG_FILE_NOT_SELECTED = 'Файл не выбран'
    MSG_INVALID_AUDIO = 'Пожалуйста, загрузите файл в формате {exts}'
    MSG_INVALID_IMAGE = 'Недопустимый формат файла (только {exts})'
    MSG_COVER_FALLBACK = 'Обложка должна быть в формате {exts} (использована случайная)'
    MSG_NO_DELETE_RIGHTS = 'У вас нет прав для удаления этого трека'
    MSG_DELETE_SUCCESS = 'Трек успешно удалён'

    GENRES = [
        ('Rock', 'Рок'),
        ('Pop', 'Поп'),
        ('Electronic', 'Электроника'),
        ('Jazz', 'Джаз'),
        ('Hip-Hop', 'Хип-Хоп'),
    ]
    GENRE_VALUES = {value for value, _ in GENRES}  # для валидации

    MOODS = [
        ('focus', 'Концентрация'),
        ('chill', 'Релакс'),
        ('cyberpunk', 'Киберпанк'),
        ('night-drive', 'Ночная поездка'),
        ('lofi', 'Lo-fi'),
        ('electronic', 'Электроника'),
    ]

    # ===== Цвета графиков =====
    CHART_COLORS = [
        '#00c8ff',  # neon-blue
        '#ff00e4',  # neon-pink
        '#ffc107',  # yellow
        '#28a745',  # green
        '#dc3545',  # red
        '#6f42c1',  # purple
        '#fd7e14',  # orange
        '#20c997',  # teal
    ]
    CHART_BORDER_COLOR = 'rgba(11, 16, 38, 0.9)'
    CHART_TEXT_COLOR = '#a0a5b9'
    CHART_GRID_COLOR = 'rgba(255, 255, 255, 0.1)'
    CHART_FONT_FAMILY = "'Segoe UI', Tahoma, sans-serif"

    # ===== Настройки графиков =====
    CHART_BAR_ALPHA = 0.5          # Прозрачность заливки столбцов
    CHART_BAR_BORDER_WIDTH = 2      # Толщина рамки столбцов
    CHART_BAR_RADIUS = 8            # Скругление углов столбцов
    CHART_LINE_WIDTH = 3            # Толщина линии
    CHART_LINE_TENSION = 0.4        # Плавность линии
    CHART_LINE_FILL_ALPHA = 0.15    # Прозрачность под линией
    CHART_POINT_RADIUS = 5          # Размер точек на линии
    CHART_POINT_HOVER_RADIUS = 8    # Размер точек при наведении

    # ===== Месяцы для графика динамики =====
    CHART_MONTHS_COUNT = 12         # Сколько месяцев показывать