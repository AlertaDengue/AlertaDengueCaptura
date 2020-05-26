from celery import Celery
import os

from os.path import join, dirname

from dotenv import load_dotenv
dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path)


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
