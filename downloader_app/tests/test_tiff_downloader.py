import os
import sys

import pandas as pd
import pytest
import requests
from netCDF4 import Dataset

from downloader_app import shapefile_module as shpm
from downloader_app import tiff_downloader as td
from downloader_app.settings import BASE_DIR

LOCAL = os.path.join(BASE_DIR, "downloader_app")
sys.path.insert(0, LOCAL)

# Set the filepath and load in a shapefile.
SHP_PATH = os.path.join(LOCAL, "RJ_Mun97_region/RJ_Mun97_region.shp")
DOWNLOADFILES_PATH = os.path.join(LOCAL, "DownloadedFiles")

# url responsible for identifying the source.
source_url = {
    'LandDAAC-v5-day': "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/"
    ".Terra/.SSA/.Day/.LST/(Celsius)/unitconvert/",
    'LandDAAC-v5-night': "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/"
    ".Terra/.SSA/.Night/.LST/(Celsius)/unitconvert/",
    'LandDAAC-v6-EVI': "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.EVI/",
    'LandDAAC-v6-NDVI': "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.NDVI/",
    'LandDAAC-v6-view_zenith_angle': "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/"
    ".SSA/.view_zenith_angle/",
}

# Get source_url status code.
def test_get_url():
    source = source_url
    for url in source.values():
        print(url, "Status OK")
        r = requests.get(url)
        status = r.status_code
        assert status == 200, "We've got a problem; status_code :'{}'".format(
            status
        )


# Download raster data.
def test_downloader_tiff():
    # Extract bounding box from shapefile.
    point1, point2 = shpm.extract_shp_boundingbox(SHP_PATH)
    source = 'LandDAAC-v5-day'
    print(os.getcwd())
    dates = pd.date_range('2016-07-20', '2016-08-05', freq='8D')
    options = {
        'plot': False,
        'keep_original': True,
        'regrid': [3, 'bilinear'],
        'close_browser': True,
    }

    td.download_tiffs(source, dates, point1, point2, opt=options)

    # Checks at source if tiff files were generated.
    files_dir = os.listdir(os.path.join(DOWNLOADFILES_PATH, 'LandDAAC-v5-day'))
    tiff_files_list = [
        'LandDAAC-v5-day-2016-07-20.tiff',
        'LandDAAC-v5-day-2016-08-05-treated.tiff',
        'LandDAAC-v5-day-2016-08-05.tiff',
        'LandDAAC-v5-day-2016-07-28-treated.tiff',
        'LandDAAC-v5-day-2016-07-20-treated.tiff',
        'LandDAAC-v5-day-2016-07-28.tiff',
    ]
    assert set(files_dir) == set(tiff_files_list)


# Download more raster files and test the creation of the netcdf file.
def test_LandDAAC_v5_night():
    source = 'LandDAAC-v5-night'
    dates = pd.date_range('2016-07-20', '2016-08-05', freq='8D')
    point1, point2 = shpm.extract_shp_boundingbox(SHP_PATH)
    # Allow time_series to create a netcdf file
    options = {
        'regrid': [3, 'cubic'],
        'keep_original': False,
        'time_series': True,
        'close_browser': True,
    }
    td.download_tiffs(source, dates, point1, point2, opt=options)

    # Read if the file format is valid.
    filename = 'time_series.nc'
    path_tmp = os.path.join(DOWNLOADFILES_PATH, source)
    nc_filename = os.path.join(path_tmp, filename)

    try:
        # Open the netCDF file and read it.
        nc = Dataset(nc_filename, 'r')
    except OSError:
        print('{} failed in process {}'.format(nc_filename, i))

    nc_model = nc.data_model
    assert nc_model == "NETCDF4", "The {} format is not correct".format(
        nc_model
    )
