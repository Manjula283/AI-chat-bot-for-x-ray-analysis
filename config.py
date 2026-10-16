"""
Configuration module for AI Chest X-ray Analysis Chatbot (PRD v2.0).
Supports MySQL via PyMySQL/SQLAlchemy ORM in production and falls back cleanly
to a persistent SQLite database when no MySQL server is reachable.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


def build_database_uri() -> str:
    """
    Constructs the SQLAlchemy database URI.
    Prioritizes explicit DATABASE_URL or MYSQL_* environment variables,
    and falls back to a local SQLite database file in /instance for zero-config execution.
    """
    explicit_url = os.environ.get("DATABASE_URL")
    if explicit_url:
        return explicit_url

    mysql_host = os.environ.get("MYSQL_HOST")
    if mysql_host:
        mysql_user = os.environ.get("MYSQL_USER", "root")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "")
        mysql_port = os.environ.get("MYSQL_PORT", "3306")
        mysql_db = os.environ.get("MYSQL_DB", "chest_xray_ai_db")
        return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"

    sqlite_path = os.path.join(INSTANCE_DIR, "chest_xray_ai_db.sqlite")
    return f"sqlite:///{sqlite_path}"


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "thorax-ai-clinical-workspace-prd-v2-secret-2026")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Cross-origin iframe cookie compatibility
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    # Upload & Image Validation Settings (FR-03, Section 7 Security)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    SAMPLE_FOLDER = os.path.join(BASE_DIR, "static", "samples")
    ACTIVE_SESSION_FILE = os.path.join(INSTANCE_DIR, "active_session.json")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

    # Model Metadata (Section 8, 10.2, 11)
    DEFAULT_VLM_VERSION = "ThoraxVLM-v2.4 (DenseNet121-CXR + BioBART Decoder)"
    DEFAULT_CHAT_MODEL = "RadExplain-Instruct-7B (Report-Grounded Clinical QA)"
    APP_LANGUAGE = "en-US"  # FR-08: Strictly English-Only Interface
