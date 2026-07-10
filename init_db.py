from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Удаляем старые таблицы (если есть)
    db.drop_all()
    print("✅ Старые таблицы удалены")

    # Создаём новые
    db.create_all()
    print("✅ Новые таблицы созданы")

    # Добавляем админа
    admin = User(
        username='admin',
        email='admin@mute.ru',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Администратор создан: admin / admin123")
    print("🎉 База данных готова!")