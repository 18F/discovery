DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'oasis',
        'USER': 'oasis',
        'PASSWORD': ''
    }
}

SAM_API_KEY = ''

# SECURITY WARNING: keep the secret key used in production secret!
# change this before deploying to your own server!
SECRET_KEY = '&%7l9-fvi7_9ykzb*kr1bhjfx%x=(vd0r8z4w#p154eb1o+t=o'

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

SAUCE = False
SAUCE_USERNAME = ''
SAUCE_ACCESS_KEY = ''
DOMAIN_TO_TEST = 'domain.of.your.mirage.installation.gov'

#The below settings turn on S3 bucket storage
#Lines 25-26 are commented out to force the loading of static assets from the local dev server by default
#uncomment them and fill in the extra AWS settings to hook it up to an S3 bucket

#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_ACCESS_KEY_ID = ''
AWS_QUERYSTRING_AUTH = False
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''

DEBUG = True
TEMPLATE_DEBUG = True

