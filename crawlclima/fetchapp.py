import os
from os.path import dirname, join

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


app = Celery(
    "crawlclima",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_BACKEND"),  #
    include=["crawlclima.tasks"],
)

app.config_from_object("crawlclima.celeryconfig")
# Optional configuration, see the application user guide.
app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600,)

if __name__ == "__main__":
    app.start()
