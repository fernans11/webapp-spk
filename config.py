import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "spk-sepatu-uas-2025-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///spk_sepatu.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

