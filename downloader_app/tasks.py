import tiff_downloader as td
from celery import Celery

# Create the app and set the broker location (RabbitMQ).
app = Celery("downloader_app", backend="rpc://", broker="pyamqp://")


@app.task
def download(source, dates, point1, point2, options):
    """
    Download satelite tiff files and save it to the directory 'downloadedFiles'.
    """

    td.download_tiffs(source, dates, point1, point2, opt=options)
    return
