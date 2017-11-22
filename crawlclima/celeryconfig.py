from decouple import config

# Broker settings.
BROKER_URL = 'amqp://'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('crawlclima.tasks', )

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'rpc://'
# CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.

# CELERY_ROUTES = {
#     'crawlclima.tasks.pega_dados_cemaden': 'high-priority',
# }

CELERY_ANNOTATIONS = {
    'crawlclima.tasks.pega_dados_cemaden': {'rate_limit': '10/s'},
    'crawlclima.tasks.fetch_wunderground': {'rate_limit': '1/s'}
}

CELERY_TIMEZONE = 'America/Sao_Paulo'

CELERY_ALWAYS_EAGER = config('CELERY_ALWAYS_EAGER', default=False)
