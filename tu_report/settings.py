"""
Django settings for tu_report project.
"""

from pathlib import Path
import dj_database_url
from decouple import config, Csv
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# GDAL Configuration for Windows
if os.name == 'nt':  # Windows
    # Try to find GDAL from QGIS or OSGeo4W
    import glob

    # Check QGIS installation paths
    qgis_paths = [
        r'C:\Program Files\QGIS 3.40.11',
        r'C:\Program Files\QGIS 3.40',
        r'C:\Program Files\QGIS 3.38',
        r'C:\Program Files\QGIS 3.34',
        r'C:\OSGeo4W',
        r'C:\OSGeo4W64',
    ]

    gdal_found = False
    for qgis_path in qgis_paths:
        if os.path.exists(qgis_path):
            # Find GDAL DLL
            gdal_dll = glob.glob(os.path.join(qgis_path, 'bin', 'gdal*.dll'))
            if gdal_dll:
                GDAL_LIBRARY_PATH = gdal_dll[0]
                GEOS_LIBRARY_PATH = os.path.join(qgis_path, 'bin', 'geos_c.dll')

                # Add to PATH
                bin_path = os.path.join(qgis_path, 'bin')
                if bin_path not in os.environ['PATH']:
                    os.environ['PATH'] = bin_path + ';' + os.environ['PATH']

                # Set GDAL_DATA and PROJ_LIB
                gdal_data = os.path.join(qgis_path, 'share', 'gdal')
                proj_lib = os.path.join(qgis_path, 'share', 'proj')

                if os.path.exists(gdal_data):
                    os.environ['GDAL_DATA'] = gdal_data
                if os.path.exists(proj_lib):
                    os.environ['PROJ_LIB'] = proj_lib

                gdal_found = True
                break

    if not gdal_found:
        print("⚠️  GDAL not found! Please install QGIS or OSGeo4W")
        print("   Download: https://qgis.org/download/")

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Add GIS support only if not using SQLite
if not USE_SQLITE:
    INSTALLED_APPS.append('django.contrib.gis')

INSTALLED_APPS += [
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'channels',         # WebSocket support

    # Local apps
    'authentication',
    'tickets',
    'dashboard',
    'technician',
    'notify',           # Notification Center
    'reports',          # Analytics & Reports
    'user_profile',     # Profile & Settings
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom Security Middleware
    'authentication.middleware.NoCacheAfterLogoutMiddleware',  # Prevent back button after logout
    'authentication.middleware.SessionSecurityMiddleware',     # Session validation
]

ROOT_URLCONF = 'tu_report.urls'

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
                'notify.context_processors.unread_notifications',  # Notification badge
            ],
        },
    },
]

WSGI_APPLICATION = 'tu_report.wsgi.application'
ASGI_APPLICATION = 'tu_report.asgi.application'

# Channels Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # For development
        # For production, use Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {
        #     "hosts": [('127.0.0.1', 6379)],
        # },
    },
}

# Database
# Use SQLite for local development (if GDAL not installed) or PostgreSQL+PostGIS for production
if USE_SQLITE:
    # SQLite WITHOUT GIS for local development (no GDAL required)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PostgreSQL with PostGIS for production
    DATABASES = {
        'default': dj_database_url.config(
            default=config(
                'DATABASE_URL',
                default='postgresql://postgres:postgres@localhost:5432/tu_report'
            ),
            conn_max_age=600,
            engine='django.contrib.gis.db.backends.postgis'
        )
    }

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

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
LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Security Settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# CSRF Settings (Development & Production)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'tu_report_csrftoken'

# Clickjacking Protection
X_FRAME_OPTIONS = 'DENY'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours (1 day)
SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session after browser close
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_NAME = 'tu_report_sessionid'  # Custom session cookie name

# Security: Clear session on logout (prevent back button after logout)
LOGOUT_CLEAR_SESSION = True

# Login Settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/tickets/my-tickets/'
LOGOUT_REDIRECT_URL = '/login/'

# TU API Settings
TU_API_ENABLED = config('TU_API_ENABLED', default=False, cast=bool)
TU_API_BASE_URL = config('TU_API_BASE_URL', default='https://restapi.tu.ac.th')
TU_API_ENDPOINT = config('TU_API_ENDPOINT', default='/api/v1/auth/Ad/verify')
TU_APPLICATION_KEY = config('TU_APPLICATION_KEY', default='')
TU_API_TIMEOUT = config('TU_API_TIMEOUT', default=10, cast=int)
TU_API_MAX_RETRIES = config('TU_API_MAX_RETRIES', default=3, cast=int)

# Additional TU API Endpoints
TU_API_LOG_ENDPOINT = config('TU_API_LOG_ENDPOINT', default='/api/v1/auth/Log/auth/')
TU_API_DEPARTMENT_ENDPOINT = config('TU_API_DEPARTMENT_ENDPOINT', default='/api/v2/emp/dep/all')
TU_API_EMPLOYEE_INFO_ENDPOINT = config('TU_API_EMPLOYEE_INFO_ENDPOINT', default='/api/v2/profile/emp/info/')

# Feature Flags
ENABLE_TU_LOG_INTEGRATION = config('ENABLE_TU_LOG_INTEGRATION', default=False, cast=bool)
ENABLE_TU_DEPARTMENT_SYNC = config('ENABLE_TU_DEPARTMENT_SYNC', default=False, cast=bool)
ENABLE_TU_EMPLOYEE_INFO = config('ENABLE_TU_EMPLOYEE_INFO', default=False, cast=bool)

# Caching
DEPARTMENT_CACHE_TTL = config('DEPARTMENT_CACHE_TTL', default=86400, cast=int)  # 24 hours
EMPLOYEE_INFO_CACHE_TTL = config('EMPLOYEE_INFO_CACHE_TTL', default=3600, cast=int)  # 1 hour

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'tickets': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# CORS Settings (if needed for API)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
