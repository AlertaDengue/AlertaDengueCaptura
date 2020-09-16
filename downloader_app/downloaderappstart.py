import os
import sys

import geopandas as gpd
import pandas as pd
import pytest
import requests

from downloader_app import shapefile_module as shpm
from downloader_app import tiff_downloader as td
from downloader_app.settings import BASE_DIR
from downloader_app.tasks import download_source

LOCAL = os.path.join(BASE_DIR, "downloader_app")
sys.path.insert(0, LOCAL)


# Set the filepath and load in a shapefile.
SHP_PATH = os.path.join(LOCAL, "RJ_Mun97_region/RJ_Mun97_region.shp")
DOWNLOADFILES_PATH = os.path.join(LOCAL, "DownloadedFiles")


def main():
    # Parameters
    # Extract bounding box from shapefile.
    point1, point2 = shpm.extract_shp_boundingbox(SHP_PATH)
    source = 'LandDAAC-v5-day'

    for dates in (
        pd.date_range('2016-07-20', '2016-10-30', freq='8D')
        .strftime("%Y-%m-%d")
        .tolist()
    ):
        print(dates)

    options = {
        'regrid': [3, 'cubic'],
        'keep_original': False,
        'time_series': True,
        'close_browser': True,
    }

    # Call funcrion
    # download_tiffs(source, dates, point1, point2, opt=False)
    download_source.delay(source, dates, point1, point2, options)


if __name__ == "__main__":
    main()
