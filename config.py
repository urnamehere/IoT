import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'iot_security.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CONTENT_DIR = os.path.join(BASE_DIR, "content")
