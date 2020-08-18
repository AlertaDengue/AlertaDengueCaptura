import os

import geopandas as gpd
import pandas as pd
import pytest
import requests

from downloader_app import shapefile_module as shpm
from downloader_app import tiff_downloader as td
from downloader_app.settings import BASE_DIR
from downloader_app.tasks import download

app_path = os.path.join(BASE_DIR, "downloader_app")

# Set the filepath and load in a shapefile.
shp_path = os.path.join(app_path, "RJ_Mun97_region/RJ_Mun97_region.shp")


def main():
    # Parameters
    # Extract bounding box from shapefile.
    point1, point2 = shpm.extract_shp_boundingbox(shp_path)
    source = 'LandDAAC-v5-day'
    dates = []
    for time in (
        pd.date_range('2016-07-20', '2016-07-30', freq='8D')
        .strftime("%Y-%m-%d")
        .tolist()
    ):
        dates.append(time)
    options = {
        'regrid': [3, 'cubic'],
        'keep_original': False,
        'time_series': True,
        'close_browser': True,
    }

    # Call funcrion
    # download_tiffs(source, dates, point1, point2, opt=False)
    td.download.delay(source, dates, point1, point2, opt=options)


if __name__ == "__main__":
    main()
