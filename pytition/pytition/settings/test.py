from .base import *
import os

SECRET_KEY = "test-secret-key-for-unit-tests"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "testdb.sqlite3"),
    }
}

DEBUG = False
