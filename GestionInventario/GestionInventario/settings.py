"""
Django settings for GestionInventario project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --------------------------------------------
# RUTAS BASE
# --------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------
# CONFIG. GENERAL
# --------------------------------------------
SECRET_KEY = 'django-insecure-febgc=!#41$9q=vujv%3ji!s-5m&zsw=l4vym!%yes5o@nes0e'
DEBUG = True
ALLOWED_HOSTS = []


# --------------------------------------------
# APLICACIONES
# --------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sistemas'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GestionInventario.urls'


# --------------------------------------------
# LOGIN / LOGOUT
# --------------------------------------------
LOGIN_REDIRECT_URL = '/usuarios/'
LOGOUT_REDIRECT_URL = '/login/'


# --------------------------------------------
# TEMPLATES
# --------------------------------------------
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
                'sistemas.context_processors.user_roles',
            ],
        },
    },
]

WSGI_APPLICATION = 'GestionInventario.wsgi.application'


# --------------------------------------------
# BASE DE DATOS SUPABASE (POSTGRES)
# --------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NAME'),
        'USER': os.getenv('USER'),
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': os.getenv('HOST'),
        'PORT': os.getenv('PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'options': '-c search_path=public'
        }
    }
}


# --------------------------------------------
# VALIDADORES PASSWORD
# --------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --------------------------------------------
# LOCALIZACIÓN / IDIOMA
# --------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --------------------------------------------
# ARCHIVOS ESTÁTICOS
# --------------------------------------------
STATIC_URL = 'static/'


# --------------------------------------------
# CONFIG EMAIL
# --------------------------------------------
DEVELOPER_EMAIL = 'sebastiannayar25@gmail.com'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# --------------------------------------------
# DEFAULT PK
# --------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# --------------------------------------------

# --------------------------------------------
# SUPABASE CLIENT (AL FINAL DEL ARCHIVO)
# --------------------------------------------
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")

print(">>> [SETTINGS] CARGANDO SUPABASE_URL:", SUPABASE_URL)

if SUPABASE_URL and SUPABASE_KEY:
    SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(">>> [SETTINGS] SUPABASE_CLIENT CREADO OK")
else:
    SUPABASE_CLIENT = None
    print(">>> [SETTINGS] SUPABASE_CLIENT = None (FALTAN VARIABLES)")
# --------------------------------------------