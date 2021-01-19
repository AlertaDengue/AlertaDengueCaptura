# Create app celery  to start Crawlclima

from celery import Celery

app = Celery("crawlclima")

app.config_from_object("crawlclima.celeryconfig")
app.conf.update(CELERY_TASK_RESULT_EXPIRES=3600)


if __name__ == "__main__":
    app.start()
