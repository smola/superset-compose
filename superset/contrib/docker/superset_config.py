import os

from werkzeug.contrib.cache import RedisCache


# Helper functions

def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = 'The environment variable {} was missing, abort...'\
                        .format(var_name)
            raise EnvironmentError(error_msg)

# Branding

APP_NAME = 'Source{d}'
APP_ICON = '/static/assets/images/sourced-logo-2x.png'
APP_ICON_WIDTH = 126

# Main DB settings

POSTGRES_USER = get_env_variable('POSTGRES_USER')
POSTGRES_PASSWORD = get_env_variable('POSTGRES_PASSWORD')
POSTGRES_HOST = get_env_variable('POSTGRES_HOST')
POSTGRES_PORT = get_env_variable('POSTGRES_PORT')
POSTGRES_DB = get_env_variable('POSTGRES_DB')
SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (POSTGRES_USER,
                                                           POSTGRES_PASSWORD,
                                                           POSTGRES_HOST,
                                                           POSTGRES_PORT,
                                                           POSTGRES_DB)

# Cache settings

REDIS_HOST = get_env_variable('REDIS_HOST')
REDIS_PORT = get_env_variable('REDIS_PORT')

CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,  # 1 day default (in secs)
    'CACHE_KEY_PREFIX': 'superset_results',
    'CACHE_REDIS_URL': 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT),
}

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST, port=REDIS_PORT, key_prefix='superset_results')

# Celery configuration. CeleryConfig doesn't inherit defaults from superset/config.

class CeleryConfig(object):
    BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    CELERY_IMPORTS = ('superset.sql_lab', 'superset.tasks')
    CELERY_RESULT_BACKEND = 'redis://%s:%s/1' % (REDIS_HOST, REDIS_PORT)
    CELERYD_LOG_LEVEL = 'INFO'
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = True
    CELERY_ANNOTATIONS = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }

CELERY_CONFIG = CeleryConfig

# Gitbase configuration

IS_EE = get_env_variable('MODE', 'Community') == 'Enterprise'
GITBASE_USER = get_env_variable('GITBASE_USER')
GITBASE_PASSWORD = get_env_variable('GITBASE_PASSWORD', '')
GITBASE_HOST = get_env_variable('GITBASE_HOST')
GITBASE_PORT = get_env_variable('GITBASE_PORT')
GITBASE_DB = get_env_variable('GITBASE_DB')
GITBASE_PREFIX = 'sparksql' if IS_EE else 'mysql'
GITBASE_DATABASE_URI = '%s://%s:%s@%s:%s/%s' % (GITBASE_PREFIX,
                                                GITBASE_USER,
                                                GITBASE_PASSWORD,
                                                GITBASE_HOST,
                                                GITBASE_PORT,
                                                GITBASE_DB)

SQLLAB_DEFAULT_DBID = 2  # set gitbase as default DB in SQL Lab

# Log Settings

LOG_LEVEL = 'INFO'

# Bblfsh-web configuration

BBLFSH_WEB_HOST = get_env_variable('BBLFSH_WEB_HOST')
BBLFSH_WEB_PORT = get_env_variable('BBLFSH_WEB_PORT')
BBLFSH_WEB_ADDRESS = 'http://%s:%s' % (BBLFSH_WEB_HOST, BBLFSH_WEB_PORT)
WTF_CSRF_EXEMPT_LIST = ['superset.bblfsh.views.api']

# Alter flask application

def mutator(f):
    from superset.bblfsh import views  # noqa

FLASK_APP_MUTATOR = mutator

