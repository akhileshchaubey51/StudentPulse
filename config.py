import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'studentpulse_default_dev_secret_key_92741')
    
    # Database - Absolute path with forward slashes for Windows compatibility
    DB_DIR = BASE_DIR / 'database'
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DB_FILE = (DB_DIR / 'student_pulse.db').resolve()
    
    # Resolve DATABASE_URL safely
    env_db = os.getenv('DATABASE_URL', '')
    if env_db and env_db.startswith('sqlite:///'):
        db_subpath = env_db.replace('sqlite:///', '')
        # If relative path, anchor to BASE_DIR
        if not (len(db_subpath) > 1 and db_subpath[1] == ':'):
            resolved_file = (BASE_DIR / db_subpath).resolve()
        else:
            resolved_file = Path(db_subpath).resolve()
        resolved_file.parent.mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{resolved_file.as_posix()}"
    elif env_db:
        SQLALCHEMY_DATABASE_URI = env_db
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # CSRF & Security
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ollama AI Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5-coder:1.5b')
    OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '10'))
