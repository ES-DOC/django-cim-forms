####################
#   ES-DOC CIM Questionnaire
#   Copyright (c) 2015 ES-DOC. All rights reserved.
#
#   University of Colorado, Boulder
#   http://cires.colorado.edu/
#
#   This project is distributed according to the terms of the MIT license [http://www.opensource.org/licenses/MIT].
####################

"""
Django settings for Q project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

from ConfigParser import SafeConfigParser, NoOptionError
import os
import sys

rel = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

# Path to the configuration file containing secret values.
CONF_PATH = os.path.join(os.path.expanduser('~'), '.config', 'esdoc-questionnaire.conf')
parser = SafeConfigParser()
parser.read(CONF_PATH)

SECRET_KEY = parser.get('settings', 'secret_key', raw=True)

DEBUG = parser.getboolean('debug', 'debug')

if 'test' not in sys.argv:

    DATABASES = {
        'default': {
            'ENGINE': parser.get('database', 'engine'),
            'NAME': parser.get('database', 'name'),
            'USER': parser.get('database', 'user'),
            'PASSWORD': parser.get('database', 'password', raw=True),
            'HOST': parser.get('database', 'host'),
            'PORT': parser.get('database', 'port'),
        }
    }

else:

    # actually testing postgres is  r e a l l y  s l o w
    # so, for most testing, just use sqlite3

    DATABASES = {
        'default':  {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': rel("questionnaire/tests/db/testdb.sqlite3")
        }
    }

    # also, have a convenient way to test emails in unit tests
    # (w/out actually sending messages)...
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
try:
    ALLOWED_HOSTS = parser.get('settings', 'allowed_hosts').split(',')
except NoOptionError:
    assert DEBUG, "ALLOWED_HOSTS is required if DEBUG is set to 'false'"
    ALLOWED_HOSTS = []

# SITE_ID is overwritten by DynamicSitesMiddleware on a per-request basis
# (so this value doesn't matter)
DEFAULT_SITE_ID = 1


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # secret honeypot fields to deter bots...
    'honeypot',
    # support for compressing static files (and for using less w/ css)...
    'compressor',
    # API...
    'rest_framework',
    # easy form integration w/ ng...
    'djangular',
    # efficient model hierarchies...
    'mptt',
    # the questionnaire app...
    'questionnaire',
    # viewing remote mindmaps...
    'mindmaps',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # allows site to be set dynamically based on request URL...
    'questionnaire.middleware.dynamic_sites.DynamicSitesMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,  # I explicitly specify the "app_directories.Loader" below rather than relying on default behavior (see https://docs.djangoproject.com/en/1.8/ref/templates/api/#configuring-an-engine)
        'OPTIONS': {
            'context_processors': [

                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # gives me access to MEDIA files from templates...
                'django.template.context_processors.media',
                # lets me check whether I'm in DEBUG mode...
                # (w/out requiring a whitelist of IP addresses)...
                'questionnaire.context_processors.debug',
            ],
            "loaders": [
                # cache templates for faster loading in PROD mode...
                ('django.template.loaders.cached.Loader', ['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader'])
                if not DEBUG else
                # don't cache templates in DEBUG mode...
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# honeypot trickery
HONEYPOT_FIELD_NAME = "account"

# Static files (CSS, JS, Images, Less)
STATIC_ROOT = rel(parser.get('settings', 'static_root', raw=True))
STATIC_URL = '/static/'
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = rel(STATIC_ROOT, "questionnaire/")
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # compressed (including less) files...
    'compressor.finders.CompressorFinder',
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = rel('site_media/')

# URL that handles the media served from MEDIA_ROOT.
# Make sure to use a trailing slash.
MEDIA_URL = '/site_media/'

# email stuff...
# (note the use of EMAIL_BACKEND in the "test" section above)
EMAIL_HOST = parser.get('email', 'host')
EMAIL_PORT = parser.get('email', 'port')
EMAIL_HOST_USER = parser.get('email', 'username')
EMAIL_HOST_PASSWORD = parser.get('email', 'password')
EMAIL_USE_TLS = True

# Caching...
DEFAULT_CACHE_PORT = "11211"  # (standard memcached port)
if parser.has_option("cache", "host"):
    CACHE_HOST = parser.get('cache', 'host')
else:
    CACHE_HOST = parser.get('database', 'host')
if parser.has_option("cache", "port"):
    CACHE_PORT = parser.get('cache', 'port')
else:
    CACHE_PORT = DEFAULT_CACHE_PORT

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': CACHE_HOST + ":" + CACHE_PORT,
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,  # allow some more entries (default is 300)
            },
    }
}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# PROFILING...
PROFILE = parser.getboolean('debug', 'profile')
if PROFILE:
    # can either use "signal" or "setprofile" mode, as per https://github.com/joerick/pyinstrument#signal-or-setprofile-mode
    # ("signal" mode has less overhead, but requires a single-threaded application)
    PYINSTRUMENT_USE_SIGNAL = False
    MIDDLEWARE_CLASSES += (
        'pyinstrument.middleware.ProfilerMiddleware',
    )

# LOGGING...
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # logging format can be found here: https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': "[%(asctime)s] %(levelname)s [%(filename)s#%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%d %b %Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            # use separate log files depending on whether the code is running in "test" mode
            'filename': rel("logs/q_log.log") if 'test' not in sys.argv else rel("logs/q_test_log.log"),
            'maxBytes': 8000000,  # rotate files every 8 MBs
            'backupCount': 9,  # keep the last 9 logs
            'formatter': 'verbose',
        },
    },
    # don't bother filtering anything; just log all messages
    'filters': {},
    'loggers': {
        # don't log django messages...
        # 'django': {
        #     'handlers': ['file'],
        #     'propagate': True,
        #     'level': 'DEBUG',
        # },
        # do log questionnaire messages...
        'questionnaire': {
            'handlers': ['file'],
            'level': 'DEBUG',  # log DEBUG and higher (everything)
        },
    },
}

# API...
REST_FRAMEWORK = {
    # TODO: GET PAGINATION WORKING
    # TODO: (FOR NOW I'M ASSUMING I WON'T HAVE MORE THAN 100 CUSTOMIZATIONS OR REALIZATIONS PER PROJECT)
    'PAGE_SIZE': 100,

    # generic filtering...
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
}
