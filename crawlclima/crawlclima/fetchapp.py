# Create app celery  to start Crawlclima

from celery import Celery

app = Celery('crawlclima')

app.config_from_object('crawlclima.celeryconfig')

if __name__ == '__main__':
    app.start()
