import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# Force DEBUG to True for your local computer environment
DEBUG = True

# 🟢 FIXED: Restored the missing SECRET_KEY fallback to stop the engine crash
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-swap-out-in-production-environments-xyz')

# Allows both your live production spaces AND your local machine to connect safely
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com', 
    'akagami012-sslg-attendance-system.hf.space',
    'huggingface.co', 
    '*' # The asterisk acts as a wildcard allowing any connection during testing
]

CSRF_TRUSTED_ORIGINS = [
    'https://akagami012-sslg-attendance-system.hf.space',
    'https://*.hf.space'
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- APPS (ADMIN IS KEPT RUNNING IN THE BACKGROUND) ---
INSTALLED_APPS = [
    'cloudinary_storage',
    'django.contrib.admin',  # Kept active to manage database login processing
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
# 🚀 AUTOMATED MULTI-ROUTING FOR SUPABASE & SQLITE
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
    
    # 🩹 CLEANUP PATCH: Strips '?pgbouncer=true' parameters to prevent psycopg2 engine from crashing
    if 'OPTIONS' in DATABASES['default'] and 'pgbouncer' in DATABASES['default']['OPTIONS']:
        del DATABASES['default']['OPTIONS']['pgbouncer']
    
    # 🛠️ Migration Interceptor: If running migrate commands, switch to the DIRECT_URL port
    if os.environ.get('DIRECT_URL') and any(cmd in os.sys.argv for cmd in ['migrate', 'makemigrations']):
        DATABASES['default'] = dj_database_url.parse(os.environ.get('DIRECT_URL'))
        DATABASES['default']['OPTIONS'] = {
            'target_session_attrs': 'read-write',
        }
else:
    # 💻 Local Dev Fallback: Uses standard SQLite if cloud variables are missing
    DATABASES = {
        'default': dj_database_url.config(
            default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
            conn_max_age=600
        )
    }

# --- STATIC & MEDIA ---
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

# Where to drop users who aren't signed in yet
LOGIN_URL = '/login/'

# Where to forward users immediately after a successful sign-in
LOGIN_REDIRECT_URL = '/dashboard/'

# Where to throw users immediately after signing out
LOGOUT_REDIRECT_URL = '/login/'

X_FRAME_OPTIONS = 'ALLOW-FROM https://huggingface.co/'