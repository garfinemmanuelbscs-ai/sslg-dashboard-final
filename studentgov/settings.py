import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-swap-out-in-production-environments-xyz')

# 🟢 FIXED: Added missing commas to prevent string literal concatenation bugs
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com', 
    'akagami012-sslg-attendance-system.hf.space',
    'akagami012-sslg-admin.hf.space',
    'huggingface.co', 
    '.hf.space',
    '*', 
]

# 🟢 FIXED: Restored complete https:// protocols and clean comma separation matrix
CSRF_TRUSTED_ORIGINS = [
    'https://akagami012-sslg-attendance-system.hf.space',
    'https://akagami012-sslg-admin.hf.space',
    'https://*.hf.space',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- APPS ---
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',  
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    
    'finance.apps.FinanceConfig',
    'inventory.apps.InventoryConfig',
    'attendance.apps.AttendanceConfig',
    'events.apps.EventsConfig',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- DATABASE ---
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
    
    if 'OPTIONS' in DATABASES['default'] and 'pgbouncer' in DATABASES['default']['OPTIONS']:
        del DATABASES['default']['OPTIONS']['pgbouncer']
    
    if os.environ.get('DIRECT_URL') and any(cmd in os.sys.argv for cmd in ['migrate', 'makemigrations']):
        DATABASES['default'] = dj_database_url.parse(os.environ.get('DIRECT_URL'))
        DATABASES['default']['OPTIONS'] = {
            'target_session_attrs': 'read-write',
        }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
            conn_max_age=600
        )
    }

# --- STATIC & STORAGE ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dchpzmzu4'), 
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '825596883238774'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'PVpxQ6tJ_RWWm4odK-ijjt2iDRY')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Kept as local safe backup fallback

# --- TEMPLATES CONFIGURATION ---
ROOT_URLCONF = 'studentgov.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'studentgov.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

X_FRAME_OPTIONS = 'ALLOW-FROM https://huggingface.co/'