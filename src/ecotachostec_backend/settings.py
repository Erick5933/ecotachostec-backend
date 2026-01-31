from pathlib import Path
import os
from dotenv import load_dotenv
from core.middleware import whitenoise_add_headers

# Cargar variables de entorno desde .env
load_dotenv(os.path.join(Path(__file__).resolve().parent, '.env'))

# PRIMERO: Parchear PyMySQL ANTES de que Django lo importe
import pymysql
pymysql.install_as_MySQLdb()

# Parchear el check de versión ANTES de importar Django DB
import sys
if 'django.db.backends.mysql' not in sys.modules:
    import MySQLdb
    MySQLdb.__version__ = '2.2.4'

# -------------------- CONFIGURACIÓN BASE --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6palvkt#ir*kf(uw1gudi0uqf=4*szyk@a1-^e$p68z$7!_sc4'

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = ['*']

# 🔒 Ocultar información de versión de Django
DJANGO_SETTINGS_MODULE = 'ecotachostec_backend.settings'

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
    'drf_yasg',

    # 🔹 Tu app principal
    'core',
    'corsheaders',
]

# -------------------- MIDDLEWARE --------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.IPWhitelistMiddleware',  # 🔒 Restringe rutas sensibles por IP (no autenticados)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.SecurityHeadersMiddleware',  # 🔒 Encabezados de seguridad
    'core.middleware.StaticFilesSecurityMiddleware',  # 🔒 Seguridad para archivos estáticos
]

# 🔒 CORS - Configuración restrictiva (NO usar CORS_ALLOW_ALL_ORIGINS=True en producción)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/api/.*$"

_env_allowed = os.getenv('CORS_ALLOWED_ORIGINS', '')
if _env_allowed:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _env_allowed.split(',') if o.strip()]
else:
    # Por defecto, solo orígenes de desarrollo comunes
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Métodos HTTP permitidos en CORS
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Headers permitidos en CORS
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Confiar en orígenes del frontend para CSRF (formularios/POST con cookies)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

ROOT_URLCONF = 'ecotachostec_backend.urls'




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


# -------------------- BASE DE DATOS (MySQL) --------------------
# Configurar para usar MySQL por defecto con PyMySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'ecotachostec_db'),
        'USER': os.getenv('DB_USER', 'Frosdh'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'blancoss'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': int(os.getenv('DB_PORT', '3306')),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'ATOMIC_REQUESTS': True,
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

# -------------------- SWAGGER --------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ADD_HEADERS_FUNCTION = whitenoise_add_headers

# -------------------- MEDIA (IMÁGENES) --------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------- SEGURIDAD HTTP --------------------
# Fuerza HTTPS en producción
SECURE_SSL_REDIRECT = False  # Cambiar a True en producción

# Headers de seguridad
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = False  # Lo manejamos en middleware

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
FRONTEND_URL = os.getenv('FRONTEND_URL', "http://localhost:5174")  # O tu IP si usas expo

# -------------------- IP WHITELIST (opcional) --------------------
# Lista de IPs confiables separadas por coma (ej: "127.0.0.1,192.168.1.10")
TRUSTED_IP_WHITELIST = [ip.strip() for ip in os.getenv('TRUSTED_IP_WHITELIST', '').split(',') if ip.strip()]
# Prefijos de ruta donde aplicar whitelist a usuarios NO autenticados
IP_WHITELIST_PATH_PREFIXES = [p.strip() for p in os.getenv('ENFORCE_IP_WHITELIST_PATHS', '/admin/,/swagger/,/redoc/').split(',') if p.strip()]
