import os
import sys
import logging
from pathlib import Path
import environ

# 1. 基礎路徑定義
BASE_DIR = Path(__file__).resolve().parent.parent

# 初始化環境變數讀取
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 關鍵：確保 Python 能正確識別 apps 資料夾下的模組
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# 2. 安全設定
SECRET_KEY = env('SECRET_KEY', default='django-insecure-prod-key-please-change-in-env')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['*']

# 3. 模組定義
INSTALLED_APPS = [
    "unfold",  # 必須第一
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "django.contrib.admin", # 確保在 unfold 之後
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "import_export", # 這裡放後端邏輯元件
    "apps.hr",
    "apps.finance",
    "apps.crm",
]

# 4. RBAC 權限核心
AUTH_USER_MODEL = 'hr.User'

# 5. 認證跳轉設定
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# 6. 中間件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 7. 安全性與跨域設定
CORS_ALLOW_ALL_ORIGINS = DEBUG
CSRF_TRUSTED_ORIGINS = ['http://localhost:8888', 'http://127.0.0.1:8888']

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# 8. 資料庫與快取
DATABASES = {
    'default': env.db('DATABASE_URL')
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS_URL', default='redis://redis:6379/0'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 9. 國際化設定
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True
DEBUG = env.bool('DEBUG', default=False) 

# 10. 靜態檔案處理
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 11. Django Unfold 自定義視覺設定
UNFOLD = {
    "SITE_TITLE": "Nexus ERP 管理系統",
    "SITE_HEADER": "Nexus Enterprise Suite",
    "SITE_SYMBOL": "corporate_fare",
    "SITE_FAVICON": "/static/favicon.ico",
    "SHOW_HISTORY": True,
    "COLORS": {
        "primary": {
            "50": "241, 245, 249",
            "100": "226, 232, 240",
            "200": "186, 201, 224",
            "300": "133, 160, 201",
            "400": "81, 116, 173",
            "500": "15, 23, 42",
            "600": "13, 20, 36",
            "700": "11, 17, 30",
            "800": "9, 14, 25",
            "900": "7, 12, 20",
        },
    },
    "STYLES": [
        lambda request: "/static/css/custom.css",
    ],
}

# 12. 💡 Laravel 風格「每日」日誌配置 (Daily Logging)
# ------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 1. 定義過濾器類別 (放在 LOGGING 變數之前)
class SuppressNoiseFilters(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # 1. 排除瀏覽器與框架產生的雜訊
        noise_keywords = ['com.chrome.devtools.json', '/admin/jsi18n/', 'favicon.ico']
        if any(keyword in msg for keyword in noise_keywords):
            return False
            
        # 2. 💡 關鍵：只過濾 INFO 等級且包含 GET 200 的存取紀錄
        # 這樣就不會誤傷 DEBUG 等級的 SQL 語句
        if record.levelno == logging.INFO and 'GET' in msg and ' 200 ' in msg:
            return False
            
        return True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'hide_noise': {
            '()': SuppressNoiseFilters,
        },
    },
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'sql': {
            'format': '\033[34m[SQL]\033[0m %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['hide_noise'], # 一般日誌過濾雜訊
        },
        'sql_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
            'level': 'DEBUG', # 💡 強制確保 SQL Handler 接收 DEBUG
            # 注意：這裡不掛 filters，確保 SQL 100% 通過
        },
        'daily_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'when': 'midnight',
            'backupCount': 30,
            'formatter': 'standard',
            'encoding': 'utf-8',
            # 檔案日誌也不掛過濾器，方便事後排查所有細節
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'daily_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['sql_console', 'daily_file'],
            'level': 'DEBUG',
            'propagate': False, # 💡 阻止向上传递给 django logger，避免重複或被攔截
        },
    },
}