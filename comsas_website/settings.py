"""
Django settings for comsas_website project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s#06#%yxzr8w7inp@r#-7s3ie+43jx3g6w!_@4)qneruqdak$1"

DEBUG = True

ALLOWED_HOSTS = ['comsas-uy1.com', 'www.comsas-uy1.com', 'localhost', '127.0.0.1', '167.86.88.92', '*']
SITE_URL = 'https://comsas-uy1.com'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party apps
    'ckeditor',
    'ckeditor_uploader',
    'modeltranslation',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local apps
    'main',
    'admin_dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'admin_dashboard.middleware.AdminAuthMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.CustomErrorMiddleware',

]

ROOT_URLCONF = 'comsas_website.urls'

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
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',  # Pour l'accès aux fichiers média
            ],
        },
    },
]

WSGI_APPLICATION = 'comsas_website.wsgi.application'

# Database
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Override with PostgreSQL if environment variables are present
if os.environ.get('DB_NAME') and os.environ.get('DB_USER'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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

# Configuration i18n améliorée
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Langues supportées
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]

# Chemin vers les fichiers de traduction
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Configuration du changement de langue
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = None
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CONFIGURATION DASHBOARD ADMIN
# =============================================================================

# URLs de redirection après login/logout
LOGIN_URL = '/dashboard/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/auth/login/'

# Configuration email pour les notifications admin
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'comsas@univ-yaounde1.cm'
EMAIL_HOST_PASSWORD = 'uzmu fsij sycj zsdj'
DEFAULT_FROM_EMAIL = 'COMS.A.S <comsas@univ-yaounde1.cm>'

# Messages framework avec Bootstrap classes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Sécurité pour les sessions admin
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # True en production avec HTTPS

# Configuration des uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Formats d'images et vidéos autorisés
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
ALLOWED_VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'wmv', 'webm']

# Cache pour améliorer les performances
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'admin-cache',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Configuration de logging pour l'admin
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'admin.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'admin_dashboard': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# =============================================================================
# CONFIGURATION CKEDITOR
# =============================================================================

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'toolbarGroups': [
            {'name': 'clipboard', 'groups': ['clipboard', 'undo']},
            {'name': 'editing', 'groups': ['find', 'selection', 'spellchecker']},
            {'name': 'links'},
            {'name': 'insert'},
            {'name': 'forms'},
            {'name': 'tools'},
            {'name': 'document', 'groups': ['mode', 'document', 'doctools']},
            {'name': 'others'},
            '/',
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup']},
            {'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align', 'bidi']},
            {'name': 'styles'},
            {'name': 'colors'},
        ],
        'removePlugins': 'elementspath',
        'extraPlugins': 'codesnippet',
    }
}

# =============================================================================
# CONFIGURATION CRISPY FORMS
# =============================================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =============================================================================
# CONTACTS ET INFORMATIONS ASSOCIATION
# =============================================================================

# Contacts WhatsApp
WHATSAPP_PRESIDENT = '+237673583241'
WHATSAPP_TREASURER_MTN = '683533430'
WHATSAPP_TREASURER_ORANGE = '698810079'
ASSOCIATION_EMAIL = 'comsas@univ-yaounde1.cm'

# Informations de l'association
ASSOCIATION_INFO = {
    'NAME': 'A²ELBM2',
    'FULL_NAME': 'Computer Science Association de l\'Université de Yaoundé 1',
    'PRESIDENT': 'NEUSSI NJIETCHEU Patrice Eugene',
    'ADDRESS': 'Yaoundé, Cameroun',
    'PHONE': '+237673583241',
    'EMAIL': 'comsas@univ-yaounde1.cm',
    'WEBSITE': 'https://comsas-uy1.com',
    'FACEBOOK': 'https://facebook.com/comsas.uy1',
    'LINKEDIN': 'https://linkedin.com/company/comsas-uy1',
}

# =============================================================================
# CONFIGURATION DE SÉCURITÉ (PRODUCTION)
# =============================================================================

if not DEBUG:
    # Configuration de sécurité pour la production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Configuration pour les emails en production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    # Configuration des hosts autorisés
    ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']
    
    # Configuration de la base de données pour la production
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': 'a2elbm2_db',
    #         'USER': 'a2elbm2_user',
    #         'PASSWORD': 'votre_mot_de_passe',
    #         'HOST': 'localhost',
    #         'PORT': '5432',
    #     }
    # }

# =============================================================================
# CONFIGURATION DE DÉVELOPPEMENT
# =============================================================================

if DEBUG:
    # Outils de développement
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass
    
    # Email backend pour le développement
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# CONFIGURATION PERSONNALISÉE
# =============================================================================

# Pagination par défaut
DEFAULT_PAGINATION = {
    'MEMBERS': 20,
    'PROJECTS': 10,
    'EVENTS': 10,
    'NEWS': 10,
    'GALLERY': 12,
    'MESSAGES': 15,
}

# Formats de date
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/y'

# Configuration des notifications
NOTIFICATION_SETTINGS = {
    'NEW_MEMBER_NOTIFICATION': True,
    'NEW_MESSAGE_NOTIFICATION': True,
    'EVENT_REGISTRATION_NOTIFICATION': True,
    'PROJECT_UPDATE_NOTIFICATION': True,
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'


# Limite de taille pour les fichiers
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

CSRF_TRUSTED_ORIGINS = [
    "https://comsas-uy1.com",
    "https://www.comsas-uy1.com",
    'http://185.218.126.7',
]
