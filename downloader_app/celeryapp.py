import os
import sys

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


# Create the app and set the broker location (RabbitMQ).
app = Celery(
    "downloader_app",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_BACKEND"),  #
    include=["downloader_app.tasks"],
)

app.config_from_object("downloader_app.celeryconfig")
