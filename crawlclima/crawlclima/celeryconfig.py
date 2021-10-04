# Parameters are used in the celery app
# Optional configuration, see the application user guide.

import os

from dotenv import load_dotenv

load_dotenv()

broker_url = os.getenv('CELERY_BROKER_URL')
result_backend = os.getenv('CELERY_RESULT_BACKEND')
result_expires = os.getenv('CELERY_TASK_RESULT_EXPIRES')
include = ('crawlclima.tasks',)
accept_content = ['application/json']
result_serializer = 'json'
worker_max_tasks_per_child = 10
timezone = 'America/Sao_Paulo'
task_always_eager = False
