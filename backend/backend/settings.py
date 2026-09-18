"""Django settings for local development and AWS EC2 deployment."""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# --------------------------------------------------
# BASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from backend/.env
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    """Read a boolean environment variable."""
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_list(name, default=""):
    """Read a comma-separated environment variable as a list."""
    return [
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]


# --------------------------------------------------
# DEBUG / SECRET KEY / HOSTS
# --------------------------------------------------

DEBUG = env_bool("DEBUG", True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        # Safe fallback for local development only.
        SECRET_KEY = "django-insecure-local-development-only-change-me"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when DEBUG=False."
        )


# For AWS, ALLOWED_HOSTS is supplied through .env.
#
# Example:
# ALLOWED_HOSTS=localhost,127.0.0.1,13.201.18.103
#
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1" if DEBUG else "",
)

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be set when DEBUG=False."
    )


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    "users",
    "jobs",
    "proposals",
    "projects",
    "chat",
    "disputes",
]


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# URL / WSGI
# --------------------------------------------------

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

# Local development:
#     SQLite
#
# AWS production:
#     PostgreSQL / RDS
#
# Enable PostgreSQL using:
#     USE_POSTGRES=True
#

if env_bool("USE_POSTGRES", False):

    required_database_vars = (
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
    )

    missing = [
        name
        for name in required_database_vars
        if not os.getenv(name)
    ]

    if missing:
        raise ImproperlyConfigured(
            f"USE_POSTGRES=True requires: {', '.join(missing)}"
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(
                os.getenv("DB_CONN_MAX_AGE", "60")
            ),
        }
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = []


# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}


# --------------------------------------------------
# MEDIA FILES
# --------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------------
# AWS S3 MEDIA STORAGE
# --------------------------------------------------

# Local:
#     USE_S3_MEDIA=False
#
# AWS:
#     USE_S3_MEDIA=True
#

USE_S3_MEDIA = env_bool("USE_S3_MEDIA", False)

if USE_S3_MEDIA:

    required_s3_vars = (
        "AWS_STORAGE_BUCKET_NAME",
        "AWS_S3_REGION_NAME",
    )

    missing = [
        name
        for name in required_s3_vars
        if not os.getenv(name)
    ]

    if missing:
        raise ImproperlyConfigured(
            f"USE_S3_MEDIA=True requires: {', '.join(missing)}"
        )

    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage"
    }

    AWS_STORAGE_BUCKET_NAME = os.environ[
        "AWS_STORAGE_BUCKET_NAME"
    ]

    AWS_S3_REGION_NAME = os.environ[
        "AWS_S3_REGION_NAME"
    ]

    AWS_S3_FILE_OVERWRITE = False

    AWS_DEFAULT_ACL = None

    AWS_QUERYSTRING_AUTH = env_bool(
        "AWS_QUERYSTRING_AUTH",
        False,
    )


# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------
# CUSTOM USER MODEL
# --------------------------------------------------

AUTH_USER_MODEL = "users.User"


# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


# --------------------------------------------------
# JWT CONFIGURATION
# --------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# --------------------------------------------------
# CORS
# --------------------------------------------------

LOCAL_ORIGINS = (
    "http://localhost:3000,"
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    LOCAL_ORIGINS if DEBUG else "",
)

CORS_ALLOW_CREDENTIALS = True


# --------------------------------------------------
# CSRF
# --------------------------------------------------

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    LOCAL_ORIGINS if DEBUG else "",
)


# --------------------------------------------------
# SECURITY SETTINGS
# --------------------------------------------------

# Keep HTTP working during the initial EC2 deployment.
# Enable HTTPS-related settings after SSL/domain setup.

SECURE_SSL_REDIRECT = env_bool(
    "SECURE_SSL_REDIRECT",
    False,
)

SESSION_COOKIE_SECURE = env_bool(
    "SESSION_COOKIE_SECURE",
    False,
)

CSRF_COOKIE_SECURE = env_bool(
    "CSRF_COOKIE_SECURE",
    False,
)

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"