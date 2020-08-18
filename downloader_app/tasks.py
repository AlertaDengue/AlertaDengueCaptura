import os
import sys

from dotenv import load_dotenv

from downloader_app import tiff_downloader as td
from downloader_app.celeryapp import app

# from downloader_app.utils import ee_authenticate

load_dotenv()


@app.task
def download(source, dates, point1, point2, options):
    """
    Download satelite tiff files and save it to the directory 'downloadedFiles'.
    """

    # ee_authenticate()

    td.download_tiffs(source, dates, point1, point2, opt=options)
    return
