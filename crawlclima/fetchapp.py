from celery import Celery
from decouple import config

app = Celery('crawlclima',
            broker=config('CELERY_BROKER_URL'),
            backend=config('CELERY_BACKEND'), #
            include=['crawlclima.tasks']
        )

app.config_from_object('crawlclima.celeryconfig')
# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
