from celery.schedules import crontab
from datetime import datetime, timedelta, date

## Broker settings.
BROKER_URL = 'amqp://'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('crawlclima.tasks', )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'mongodb'
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.

# CELERY_ROUTES = {
#     'crawlclima.tasks.pega_dados_cemaden': 'high-priority',
# }

CELERY_ANNOTATIONS = {'crawlclima.tasks.pega_dados_cemaden': {'rate_limit': '10/s'}}

#Celery beat configurations

CELERY_TIMEZONE = 'America/Sao_Paulo'

today = datetime.fromordinal(date.today().toordinal())
week_ago = datetime.fromordinal(date.today().toordinal())-timedelta(8)

CELERYBEAT_SCHEDULE = {
    # Executes every monday morning at 9:30 A.M
    'fetch-tweets-monday-morning': {
        'task': 'crawlclima.tasks.pega_tweets',
        'schedule': crontab(hour=9, minute=30, day_of_week=1),
        'args': ((date.today()-timedelta(8)).isoformat(), date.today().isoformat(), ['3304557', '3303302', '3106200', '4104808'], "A90")
    },
    'fetch-cemaden-monday-morning-RJ': {
        'task': 'crawlclima.tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=1, day_of_week=1),
        'args': ('RJ', week_ago, today, 'uf')
    },
    'fetch-cemaden-monday-morning-MG': {
        'task': 'crawlclima.tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=1, day_of_week=1),
        'args': ('MG', week_ago, today, 'uf')
    },
    'fetch-cemaden-monday-morning-PR': {
        'task': 'crawlclima.tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=1, day_of_week=1),
        'args': ('PR', week_ago, today, 'uf')
    },
}
