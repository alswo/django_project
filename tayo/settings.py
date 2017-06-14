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
    'optimizer',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'simple_history',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': ['/home/ubuntu/lee/venv_tayo/django_project/templates',],
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
            ],
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
        },
    },
]

WSGI_APPLICATION = 'tayo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tayo',
        'USER': 'postgres',
        'PASSWORD': 'beclear048@',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

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
    ('01 23 * * *', 'schedule.cron.store_historyschedule'),
    ('00 21 * * *', 'schedule.cron.store_historyschedule_old'),
    ('00 22 * * sun', 'schedule.cron.reset_lflag_on_every_schedule'),
    ('30 12 * * *', 'schedule.cron.find_update'),
    #('00 23 31 12 *', 'schedule.test.move_schedule'),
    #('00 23 31 12 *', 'schedule.test.regist_student')
]

#LOGGING = {
    #'version': 1,
    #'disable_existing_loggers': False,
    #'handlers': {
        #'file': {
            #'level': 'DEBUG',
            #'class': 'logging.FileHandler',
            #'filename': BASE_DIR + '/logs/debug.log',
        #},
    #},
    #'loggers': {
        #'django': {
            #'handlers': ['file'],
            #'level': 'DEBUG',
            #'propagate': True,
        #},
        #'"django_crontab': {
            #'handlers': ['file'],
            #'level': 'DEBUG',
            #'propagate': True,
        #},
    #},
#}

#CRONTAB_COMMAND_SUFFIX = '2>&1'

LOGIN_REDIRECT_URL = '/'

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
