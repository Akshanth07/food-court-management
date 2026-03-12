from app import create_app
from extensions import db, bcrypt, User

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        user.password = bcrypt.generate_password_hash('password123').decode('utf-8')
        print(f"Reset password for: {user.email}")
    db.session.commit()
    print("✅ All passwords reset to: password123")