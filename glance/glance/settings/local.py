try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import os

from .base import *

DEBUG = True

ALLOWED_HOSTS = []

SERVER_ALIAS = 'local'

# glance ini file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
# instantiate
config = ConfigParser()

config.read(os.path.join(INI_DIR, 'glance.ini'))

# local SECRET_KEY
SECRET_KEY = config.get('local', 'SECRET_KEY')
external_db_user = config.get('local', 'external_db_user')
external_db_password = config.get('local', 'external_db_password')
external_db_host = config.get('local', 'external_db_host')
external_db_port = config.get('local', 'external_db_port')


DATABASES = {
    'default': {
        # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'glance',
        'USER': 'root',
        'PASSWORD': '1qaz@WSX',
        'HOST': 'localhost',
        'PORT': '3306',
        # Set this to True to wrap each HTTP request in a transaction on this
        # database.
        'ATOMIC_REQUESTS': True,
    },
    'external': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecmall',
        'USER': external_db_user,
        'PASSWORD': external_db_password,
        'HOST': external_db_host,
        'PORT': external_db_port,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    },
}
