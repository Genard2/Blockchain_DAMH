import os

class Config:
    # Secret Key để bảo mật session, cookie
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'root'  # Đảm bảo SECRET_KEY được cấu hình ở Render hoặc trong môi trường địa phương

    # Cấu hình kết nối với PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://dreamteam_db_ds9f_user:KacppChoTGT9qspWodzzzkEgixS6TlJw@dpg-cvo2353uibrs738aav40-a/dreamteam_db_ds9f'  # DATABASE_URL sẽ được Render cung cấp khi deploy

    # Tắt việc theo dõi sự thay đổi của các đối tượng SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
