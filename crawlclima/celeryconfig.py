from celery.schedules import crontab
from datetime import datetime, timedelta, date

## Broker settings.
BROKER_URL = 'amqp://'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('crawlclima.tasks', )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'mongodb'
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.

CELERY_ROUTES = {
    'tasks.pega_dados_cemaden': 'high-priority',
}

CELERY_ANNOTATIONS = {'tasks.pega_dados_cemaden': {'rate_limit': '10/s'}}

#Celery beat configurations

CELERY_TIMEZONE = 'America/Sao_Paulo'



CELERYBEAT_SCHEDULE = {
    # Executes every monday morning at 9:30 A.M
    'fetch-tweets-monday-morning': {
        'task': 'tasks.pega_tweets',
        'schedule': crontab(hour=9, minute=30, day_of_week=1),
        'args': ((date.today()-timedelta(8)).isoformat(), date.today().isoformat(), ['3304557', '3303302', '3106200', '4104808'], "A90"),
    },
    'fetch-cemaden-monday-morning-RJ': {
        'task': 'tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=1, day_of_week=1),
        'args': ('RJ', datetime.fromordinal(date.today().toordinal())-timedelta(8), datetime.fromordinal(date.today().toordinal())),
    },
    'fetch-cemaden-monday-morning-MG': {
        'task': 'tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=10, day_of_week=1),
        'args': ('MG', datetime.fromordinal(date.today().toordinal())-timedelta(8), datetime.fromordinal(date.today().toordinal())),
    },
    'fetch-cemaden-monday-morning-PR': {
        'task': 'tasks.pega_dados_cemaden',
        'schedule': crontab(hour=8, minute=20, day_of_week=1),
        'args': ('PR', datetime.fromordinal(date.today().toordinal())-timedelta(8), datetime.fromordinal(date.today().toordinal())),
    },
}
