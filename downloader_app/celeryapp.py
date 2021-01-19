# Create app celery to start Downloader_app

from celery import Celery

app = Celery("downloader_app",)

app.config_from_object("downloader_app.celeryconfig")

if __name__ == "__main__":
    app.start()
