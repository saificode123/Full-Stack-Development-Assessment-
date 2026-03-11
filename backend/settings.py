"""
Django settings for backend project.
"""
import os
import dj_database_url  # Parses your Neon database link
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Uses environment variable on Render, falls back to local key
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-r23a_l_*po@@z#4(8*k%5l(9qx7*=qmz$==721ml=&(u=3me9l')

# SECURITY WARNING: don't run with debug turned on in production!
# Reads from environment variable. Defaults to False for safety.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allow Render to host your backend
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'corsheaders',
    'core', 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database Configuration
# Uses the DATABASE_URL environment variable on Render (Neon Postgres)
# Falls back to SQLite for local development if not found
database_url = os.environ.get("DATABASE_URL")

if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', 
    ),
}

# CORS Configuration
# Allow requests from your Frontend and Backend URLs
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://full-stack-development-assessment-ty8x.onrender.com", 
    "https://full-stack-development-assessment-frontend.onrender.com", 
]

# CSRF Trusted Origins
# Required for POST/PUT requests from the frontend
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://full-stack-development-assessment-ty8x.onrender.com",
    "https://full-stack-development-assessment-frontend.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True 

# ==========================================
# PRODUCTION SECURITY SETTINGS
# ==========================================

# Tells Django we are behind a proxy that uses HTTPS (Render uses HTTPS)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies must be secure in production to work over HTTPS
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Prevent javascript access to session cookie (Security best practice)
SESSION_COOKIE_HTTPONLY = True
# CSRF cookie HttpOnly can be False (allows JS to read it for headers)
CSRF_COOKIE_HTTPONLY = False