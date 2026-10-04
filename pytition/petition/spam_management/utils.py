from django.conf import settings
from django.utils.module_loading import import_string

def get_spam_detectors():
    for path in settings.SPAM_DETECTORS:
        klass = import_string(path)
        yield klass()