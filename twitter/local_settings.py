# checkout https://www.neilwithdata.com/django-sql-logging

AWS_ACCESS_KEY_ID = 'AKIAYZTT7ISWZPL7ZQF2'
AWS_SECRET_ACCESS_KEY = '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'

LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',

        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}