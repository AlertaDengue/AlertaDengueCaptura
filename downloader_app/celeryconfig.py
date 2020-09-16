import os

from dotenv import load_dotenv

load_dotenv()

# Broker settings.
BROKER_URL = os.getenv("CELERY_BROKER_URL")
# List of modules to import when celery starts.
CELERY_IMPORTS = ("downloader_app.tasks",)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERYD_MAX_TASKS_PER_CHILD = 10
CELERY_TIMEZONE = "America/Sao_Paulo"
CELERY_ALWAYS_EAGER = os.getenv("CELERY_ALWAYS_EAGER", default=False)
