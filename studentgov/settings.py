import os
from pathlib import Path
import dj_database_url  # You need to add this to requirements.txt

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# On Render, we set an environment variable DEBUG = False
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-%-g(0l+axl!@7#7fuvos)e)6tc7_u5-gc5o5r+sk&=@+q51ay0')

# Combined ALLOWED_HOSTS
ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1', '*']

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
    'whitenoise.middleware.WhiteNoiseMiddleware', # Place right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- DATABASE ---
# This logic checks if DATABASE_URL exists (Render's Postgres), 
# otherwise it uses your local db.sqlite3
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# --- STATIC & MEDIA ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# WhiteNoise handles static files on Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cloudinary Storage
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dchpzmzu4'), 
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '825596883238774'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'PVpxQ6tJ_RWWm4odK-ijjt2iDRY')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

# --- THE REST ---
ROOT_URLCONF = 'studentgov.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True