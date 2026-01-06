from pathlib import Path
import os
import pymysql

# -------------------- CONFIGURACIÓN BASE --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6palvkt#ir*kf(uw1gudi0uqf=4*szyk@a1-^e$p68z$7!_sc4'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Habilitar PyMySQL como reemplazo de MySQLdb
pymysql.install_as_MySQLdb()

# -------------------- APLICACIONES --------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 🔹 Apps de terceros
    'rest_framework',

    # 🔹 Tu app principal
    'core',
    'corsheaders',
]

# -------------------- MIDDLEWARE --------------------
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

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


ROOT_URLCONF = 'ecotachostec_backend.urls'
CORS_ALLOWED_ORIGINS.append("http://192.168.54.59:19000")




TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ecotachostec_backend.wsgi.application'
ASGI_APPLICATION = 'ecotachostec_backend.asgi.application'


# -------------------- BASE DE DATOS (MySQL Workbench) --------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecotachostec_db',
        'USER': 'root',              # 👈 tu usuario MySQL (ajústalo)
        'PASSWORD': '1234',   # 👈 tu contraseña MySQL (ajústala)
        'HOST': 'localhost',         # o 'localhost'
        'PORT': '3306',              # puerto por defecto MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}


# -------------------- AUTH PERSONALIZADO --------------------
AUTH_USER_MODEL = 'core.Usuario'


# -------------------- REST FRAMEWORK --------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}


# -------------------- INTERNACIONALIZACIÓN --------------------
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# -------------------- ESTÁTICOS --------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py

# ... (tu configuración existente)

# -------------------- EMAIL (GMAIL) --------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kawsana375@gmail.com'
# ⚠️ OJO: Aquí pon la contraseña de APLICACIÓN de 16 letras, NO tu contraseña normal.
EMAIL_HOST_PASSWORD = 'bvgt qcgi onro ikgc' 
DEFAULT_FROM_EMAIL = 'Ecotachos Tecnología <kawsana375@gmail.com>'

# URL del Frontend (para enviar el link de recuperación)
FRONTEND_URL = "http://localhost:5173"  # O tu IP si usas expo: "http://192.168.54.59:19000"
