"""
Configuration — edit DB credentials to match your XAMPP setup
"""
import os

class Config:
    # ── MySQL (XAMPP default) ──────────────────────────────
    MYSQL_HOST      = os.getenv('DB_HOST',     'localhost')
    MYSQL_PORT      = int(os.getenv('DB_PORT', 3306))
    MYSQL_USER      = os.getenv('DB_USER',     'root')
    MYSQL_PASSWORD  = os.getenv('DB_PASSWORD', '')          # XAMPP default = empty
    MYSQL_DB        = os.getenv('DB_NAME',     'foodcourt_db')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ───────────────────────────────────────────────
    JWT_SECRET_KEY          = os.getenv('JWT_SECRET', 'foodcourt-super-secret-key-2026')
    JWT_ACCESS_TOKEN_EXPIRES = 86400   # 24 hours in seconds

    # ── General ───────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'flask-secret-key-change-in-prod')
    DEBUG      = True

    # ── Discount Rule ─────────────────────────────────────
    DISCOUNT_THRESHOLD  = 400   # Apply discount when subtotal >= this
    DISCOUNT_RATE       = 0.10  # 10% discount
    TAX_RATE            = 0.05  # 5% tax
