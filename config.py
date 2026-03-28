import os

class Config:
    # PostgreSQL (Render) — uses DATABASE_URL env variable
    # Falls back to MySQL for local development
    DATABASE_URL = os.getenv('DATABASE_URL')

    if DATABASE_URL:
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local MySQL (XAMPP)
        MYSQL_HOST     = os.getenv('DB_HOST',     'localhost')
        MYSQL_PORT     = int(os.getenv('DB_PORT', 3306))
        MYSQL_USER     = os.getenv('DB_USER',     'root')
        MYSQL_PASSWORD = os.getenv('DB_PASSWORD', '')
        MYSQL_DB       = os.getenv('DB_NAME',     'foodcourt_db')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY          = os.getenv('JWT_SECRET', 'foodcourt-super-secret-key-2026')
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    SECRET_KEY  = os.getenv('SECRET_KEY', 'flask-secret-key-change-in-prod')
    DEBUG       = False
    DISCOUNT_THRESHOLD = 400
    DISCOUNT_RATE      = 0.10
    TAX_RATE           = 0.05
