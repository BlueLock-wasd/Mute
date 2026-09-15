from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from config import Config

with app.app_context():
    # Удаляем старые таблицы (если есть)
    db.drop_all()
    print("✅ Старые таблицы удалены")

    # Создаём новые
    db.create_all()
    print("✅ Новые таблицы созданы")

    # Добавляем админа
    admin = User(
        username=Config.ADMIN_USERNAME,
        email=Config.ADMIN_EMAIL,
        password_hash=generate_password_hash(Config.ADMIN_PASSWORD),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Администратор создан: admin / admin123")
    print("🎉 База данных готова!")