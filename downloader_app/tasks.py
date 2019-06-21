from celery import Celery
import tiff_downloader as td


# Create the app and set the broker location (RabbitMQ).
app = Celery('downloader_app',
             backend='rpc://',
             broker='pyamqp://')


@app.task
def download(source, date1, date2, point1, point2, path, options):
    """
    Download satelite tiff files and save it to the directory 'downloadedFiles'.
    """

    td.download_tiffs(source, date1, date2, point1, point2, path, opt=options)
    return

