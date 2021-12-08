#!/usr/bin/env python

import os
import sys

import pandas as pd
from downloader_app import shapefile_module as shpm
from downloader_app.tasks import download_source

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORK_DIR = os.path.join(BASE_DIR, 'downloader_app')

sys.path.insert(0, WORK_DIR)

# Set the filepath and load in a shapefile.
DOWNLOADFILES_PATH = os.path.join(WORK_DIR, 'DownloadedFiles')
# TODO: Will be resolved within issue #60
SHP_PATH = os.path.join(
    WORK_DIR, 'shapefiles/RJ_Mun97_region/RJ_Mun97_region.shp'
)


# TODO: Parameters will be treated outside of functions in issue #60
class DownloaderSources:
    # Parameters
    # date_start date_end last week
    # argparser(dt_start, dt_end)
    # Extract bounding box from shapefile by uf
    # iterate source list
    def LandDAAC_v5_day():
        point1, point2 = shpm.extract_shp_boundingbox(SHP_PATH)
        source = 'LandDAAC-v5-day'
        dates = (
            pd.date_range('2016-07-20', '2016-08-05', freq='8D')
            .strftime('%Y-%m-%d')
            .tolist()
        )
        options = {
            'regrid': [3, 'cubic'],
            'keep_original': False,
            'time_series': True,
            'close_browser': True,
        }

        download_source.delay(source, dates, point1, point2, options)

    def LandDAAC_v5_night():
        point1, point2 = shpm.extract_shp_boundingbox(SHP_PATH)
        source = 'LandDAAC-v5-night'
        dates = (
            pd.date_range('2016-07-20', '2016-08-05', freq='8D')
            .strftime('%Y-%m-%d')
            .tolist()
        )
        options = {
            'regrid': [3, 'cubic'],
            'keep_original': False,
            'time_series': True,
            'close_browser': True,
        }

        download_source.delay(source, dates, point1, point2, options)


if __name__ == '__main__':
    # Pass the functions with the parameters
    DownloaderSources.LandDAAC_v5_day()
    # DownloaderSources.LandDAAC_v5_night()
