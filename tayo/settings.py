import os
import os.path
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '+(%$1+c-jt$7x-tjt1@qat&tza18v3yukk2yscd#l++b8v-!u='

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django_crontab',
    'schedule',
    'passenger',
    'monitor',
    'optimizer',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'simple_history',
    'api',
    'institute',
    'indicator',
    'corsheaders',
    'fcm',
    'util',
    'fcmdev',
    'fcm_django',
    'drivermanager',
    #'traccar',
]

SASS_ROOT = os.path.join(BASE_DIR, 'drivermanager', 'static', 'scss')

#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': True,
#    'formatters': {
#        'standard': {
#            'format': '%(asctime)s|%(levelname)s|%(message)s',
#            'datefmt' : "%d/%b/%Y %H:%M:%S"
#        }
#    },
#    'handlers': {
#        'file': {
#            'level':'DEBUG',
#            'class':'logging.handlers.RotatingFileHandler',
#            'filename':'/root/debug/debug.log',
#            'maxBytes':10192*10192*1,
#            'backupCount':10,
#            'formatter':'standard'
#        },
#    },
#    'loggers':{
#        'django':{
#            'handlers':['file'],
#            'level': 'DEBUG',
#            'propagate':True,
#        }
#    }
#}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'tayo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/home/ubuntu/lee/django_project/templates',],
        #'DIRS': [],
        #'DIRS': [os.path.join(os.path.dirname(__file__),'templates'),],
        'DIRS': [BASE_DIR + '/templates/',],
        #'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'institute.context_processors.getAcademy',
            ],
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
        },
    },
]

FCM_APIKEY = "AAAAFt1BOGQ:APA91bEHypaznqDJeVzBcRuyBcqjtNDbIK-POYriP5w4_uW9exqHf9zKyS-nZJkNIFQbVvcceLx6JK1gQcXOY8NqjvGqIwZXhe2kaNq4Qq4l2rTOA-r9fYggMImvwKHEPiEfytrfwboy"

WSGI_APPLICATION = 'tayo.wsgi.application'

TAYO_TMP_DIR = BASE_DIR + '/tmp/'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

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

CRONJOBS = [
    #('01 23 * * *', 'schedule.cron.store_historyschedule'),
    #('00 21 * * *', 'schedule.cron.store_historyschedule_old'),
    #('00 22 * * sun', 'schedule.cron.reset_lflag_on_every_schedule'),
    ('30 23 * * sun', 'schedule.cron.weekly_update'),
    ('30 23 * * sat', 'schedule.cron.resetTodayLoad'),
    #('00 23 31 12 *', 'schedule.test.move_schedule'),
    #('00 23 31 12 *', 'schedule.test.regist_student')
]


CORS_ORIGIN_ALLOW_ALL = True

LOGIN_REDIRECT_URL = '/'

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

try:
	from local_settings import *
except ImportError as e:
	pass
