import os
import sys

from celery.utils.log import get_task_logger
from downloader_app.celeryapp import app
from downloader_app.tiff_downloader import download_tiffs as td

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK_DIR = os.path.join(BASE_DIR, 'downloader_app')
sys.path.insert(0, WORK_DIR)


logger = get_task_logger('downloader_app')


@app.task
def download_source(source, dates, point1, point2, opt=False):
    """
    Download satelite tiff files and save it to the directory 'downloadedFiles'.
    """

    try:
        logger.info('Fetch {} {}'.format(source, dates))
        td(source, dates, point1, point2, opt)

    except Exception as e:
        logger.error(
            '[EE] fetching from {} at {} error: {}'.format(source, dates, e)
        )
        return

    return
