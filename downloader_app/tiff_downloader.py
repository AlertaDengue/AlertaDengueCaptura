from configparser import ConfigParser
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import urllib.request
import os
import sys
import glob
import gzip
import rasterio
from rasterio.warp import reproject, Resampling
import xarray as xr
import geoviews as gv
import logging
import ee
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sqlalchemy import create_engine
from datetime import date


# instantiate
config = ConfigParser()
# parse existing file
config.read('settings.ini')
# read values 
PATH = config.get('settings', 'path')

# Initialize Google Earth Engine.
ee.Initialize()
# Iinitialize (authenticate) Google Driver.
gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
gauth.LocalWebserverAuth()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)
# Avoid displaying some log warnings. See https://github.com/googleapis/google-api-python-client/issues/299.
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


def download_tiffs(source, date1, date2, point1, point2, opt=False):
    """ Function responsible for the main calls. 
    
        Inputs
        ------
        source: string
            It is the name of the source from which we will take the captured images. 
            For example 'LandDAAC-v5-day' is a valid name. Other possible names may
            be seen with the command about('sources').
        date1, date2: list or tuple of strings
            Initial and final date of the interval in which we are interested. The only 
            accepted format at the moment is ['year', 'month', 'day']. Months and days should
            have two digits. 
        point1, point2: tuple
            point1 is a tuple (x, y) corresponding to the upper left point of the image, 
            while point2 corresponds to the lower right point.
        opt: classe
            All possible extra options are passed as variables of this class. If no class 
            is passed, the default(False) is assumed, which means that no extra options 
            will be executed in the program.       
    """
    
    # Extracts input information.
    x1, y1 = point1
    x2, y2 = point2
    bbox = str(point1) + str(point2)
    
    # Check extra options to be included.
    opt = create_options(opt)

    # Obtains the frequency of the source.
    freq = source_freq(source)
    
    # Extract the values from the dates.
    year1, month1, day1 = date1
    year2, month2, day2 = date2

    # Extract dates fom date range.
    dates = pd.date_range(year1 + month1 + day1, year2 + month2 + day2, freq=freq)
        
    # Download maps by date.
    length = len(dates)
    for l in range(length-1):
        # First variables.
        current_date = dates[l]
        next_date = dates[l+1]
        current_date_tmp = str(date.today())
        
        # Verify if the file has been already downloaded. In this case the program skips this download.
        skip = skip_download(source, bbox, current_date_tmp, opt)
                
        if not skip:
            if source in ["LandDAAC-v5-day", "LandDAAC-v5-night",
                          "LandDAAC-v6-EVI", "LandDAAC-v6-NDVI",
                          "LandDAAC-v6-view_zenith_angle"]:
                success, path = single_download_LandDAAC(source, current_date, next_date, x1, x2, y1, y2, opt)
            elif source == "chirps-2.0":
                success, path = single_download_chirps(source, current_date, x1, x2, y1, y2, opt)
            elif source in ["LST_Day_1km", "LST_Night_1km", "CHIRPS", "NDVI", "EVI"]:
                success, path = single_download_gee(source, current_date, next_date, x1, x2, y1, y2, opt)

            # Save information about the downloads in a database.
            if success:
                exists = os.path.exists('downloads.db')
                engine = create_engine('sqlite:///downloads.db')
                conn = engine.connect()
                item = (source, bbox, current_date_tmp, path)
                if not exists:
                    conn.execute('CREATE TABLE DOWNLOADS ([SOURCE] text, [BOUNDING BOX] integer, [DOWNLOAD DATE] date, [PATH] text)')    
                if opt.keep_original:
                    conn.execute('INSERT INTO DOWNLOADS VALUES (?,?,?,?)', item)
                if opt.regrid: 
                    path = path[:-5] + '-treated.tiff'
                    item = (source, bbox, current_date_tmp, path)
                    conn.execute('INSERT INTO DOWNLOADS VALUES (?,?,?,?)', item)
                conn.close()

    # View time series after the downloads.
    if opt.time_series:
        construct_time_series(dates, opt)
                
    return 


def skip_download(source, bbox, current_date_tmp, opt):
    """This function verifies if the requested download has been already requested before."""
    
    exists = os.path.exists('downloads.db')
    skip = False
    
    if exists:
        # Open database.
        engine = create_engine('sqlite:///downloads.db')
        conn = engine.connect()
        data = pd.read_sql_query('select * from DOWNLOADS', con=engine)
        L = len(data)
        
        # Verify, row by row, if the set of parameters was already used to make a download.
        for i in range(L):
            row_source = data.iloc[i]['SOURCE']
            row_bbox = data.iloc[i]['BOUNDING BOX']
            row_date = data.iloc[i]['DOWNLOAD DATE']
            row_regrid = data.iloc[i]['PATH'][-12:-5]
            if (source == row_source) and (bbox == row_bbox) and (current_date_tmp == row_date):
                if opt.keep_original and row_regrid != 'treated':
                    skip = True
                    msg = 'Skipping download. Skipping request.'
                    logging.info(msg)
                    break
                if opt.regrid and row_regrid == 'treated':
                    skip = True
                    msg = 'Skipping download. Skipping request.'
                    logging.info(msg)
                    break
    
    return skip


def single_download_LandDAAC(source, date1, date2, x1, x2, y1, y2, opt):
    """ Function responsible for each satellite image download from the IRI dataset. """

    # Convert numeric data values to string format. 
    year1 = str(date1.year)
    month1 = str(date1.month)
    day1 = str(date1.day)
    year2 = str(date2.year)
    month2 = str(date2.month)
    day2 = str(date2.day)
    if len(month1) == 1:    month1 = '0' + month1
    if len(day1) == 1:      day1 = '0' + day1
    if len(month2) == 1:    month2 = '0' + month2
    if len(day2) == 1:      day2 = '0' + day2
    
    # Converts numeric month to written month.
    month1_str = month_to_string(date1.month)
    month2_str = month_to_string(date2.month)
    
    # Generate url with specifications.
    start_url = source_url(source)
    time_range = "T/(" + day1 + "%20" + month1_str + "%20" + year2 + \
                 ")/(" + day2 + "%20" + month2_str + "%20" + year2 + ")/"
    bounding_box = "RANGE/X/" + str(float(x1)) + "/" + str(float(x2)) + \
                   "/RANGE/Y/" + str(float(y1)) + "/" + str(float(y2)) + "/"
    time = "RANGE/T/4015.5/4017.5/RANGE/"
    end_url = "%5BX/Y/%5D/palettecolor.tiff?filename=data" + year2 + "{}{}-{}.tiff"
    url_base = start_url + time_range + bounding_box + time + end_url
    url = url_base.format(month1, day1, day2)

    # Generate filename.
    filename = source + '-' + str(year1) + '-' + str(month1) + '-' + str(day1) + '.tiff'
    # Create source folder if it doesn't exists.
    path_tmp = os.path.join(PATH, source)
    exists = os.path.exists(path_tmp)
    if not exists:
        os.mkdir(path_tmp)
    # Path to the file.
    path = os.path.join(path_tmp, filename)

    # Remove duplicate if it exists.
    exists = os.path.isfile(path)
    if exists:
        os.remove(path)

    # Download and save url content.
    try:
        # Download.
        with urllib.request.urlopen(url) as response, open(path, 'wb') as file:
            data = response.read() 
            file.write(data)

        # Fix values scale (because the images are downloaded as uint8, not float).
        url_dods = start_url + time_range + bounding_box + time + 'dods'
        remote_data = xr.open_dataset(url_dods, decode_times=False)
        a, b = scale_min_max(source, remote_data)
        with rasterio.open(path) as dataset:
            profile = dataset.profile
            profile.update(dtype=rasterio.float32)
            array = dataset.read()
            m = 0
            M = 255
        new_array = (b-a)/(M-m)*array[0, :, :] + a - m*(b-a)/(M-m)
        new_array = np.array(new_array, dtype=np.float32)
        with rasterio.open(path, 'w', **profile) as dataset:
            dataset.write(new_array, 1)        
        
        # After saving the image, the treatment process begins.
        regrid_image(source, filename, opt)
        
        # Log message of success.
        success = True
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + '): success'
        logging.info(msg)
        
    except urllib.error.HTTPError:
        # Log message of failure.
        success = False
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + '): failure'
        logging.error(msg)
        
    except urllib.error.URLError:
        # Log message of failure.
        success = False
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + '): failure'
        logging.error(msg)
        
    # If the treated image is the only one required, the original image is deleted.
    if not opt.keep_original:
        exists = os.path.isfile(path)
        if exists:
            os.remove(path)
    
    return success, path


def single_download_chirps(source, date, x1, x2, y1, y2, opt):
    """ Function responsible for each satellite image download from Chirps. """

    # Convert numeric data values to string format.
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    if len(month) == 1:    month = '0' + month
    if len(day) == 1:      day = '0' + day

    # Generate url with specifications.
    url_base = "ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/{}/chirps-v2.0.{}.{}.{}.tif.gz"
    url = url_base.format(year, year, month, day)
    
    # Generate filename.
    compressed_filename = source + '-' + year + '-' + month + '-' + day + '.tif.gz'
    # Create source folder if it doesn't exists.
    path_tmp = os.path.join(PATH, source)
    exists = os.path.exists(path_tmp)
    if not exists:
        os.mkdir(path_tmp)
    # Path to the file.
    path = os.path.join(path_tmp, compressed_filename)
    
    # Remove duplicate file with same name if it exists.
    exists = os.path.isfile(path)
    if exists:
        os.remove(path)

    # Download and save url content.
    try:
        # Download
        with urllib.request.urlopen(url) as response, open(path, 'wb') as file:
            data = response.read()
            file.write(data)

        # Create uncompressed file in the same folder where the compressed file is located.
        filename = 'chirps-v2.0-' + year + '-' + month + '-' + day + '.tiff'
        path2 = os.path.join(path_tmp, filename)
        fp = open(path2, "wb")
        with gzip.open(path, "rb") as f:
            d = f.read()
        fp.write(d)
        fp.close()

        # Delete compressed file.
        os.remove(path)

        # Restrict to bounding box.
        with rasterio.open(path2) as dataset:
            p1 = np.round(~dataset.transform * (x1, y1)).astype(np.int64)
            p2 = np.round(~dataset.transform * (x2, y2)).astype(np.int64)
            array = dataset.read()
            array = array[0, :, :]
            array[array == -9999] = np.nan
            new_array = array[p1[1]:p2[1], p1[0]:p2[0]]
            a = dataset.transform.a
            b = dataset.transform.b
            c = x1
            d = dataset.transform.d
            e = dataset.transform.e
            f = y1
            new_transform = (a, b, c, d, e, f)
            new_profile = dataset.profile.copy()
            new_profile.update({
                'dtype': 'float32',
                'height': new_array.shape[0],
                'width': new_array.shape[1],
                'transform': new_transform})

        filename = 'chirps-v2.0-' + year + '-' + month + '-' + day + '.tiff'
        path = os.path.join(path_tmp, filename)
        exists = os.path.isfile(path)
        if exists:
            os.remove(path)

        with rasterio.open(path, 'w', **new_profile) as new_dataset:
            new_dataset.write_band(1, new_array)

        # After saving the image, the treatment process begins.
        regrid_image(source, filename, opt)

        # Log message of success.
        success = True
        msg = 'Download (' + year + '-' + month + '-' + day + ') :success'
        logging.info(msg)

    except urllib.error.HTTPError:
        # Log message of failure.
        success = False
        msg = 'Download (' + year + '-' + month + '-' + day + '): failure1'
        logging.error(msg)

    except urllib.error.URLError:
        # Log message of failure.
        success = False
        msg = 'Download (' + year + '-' + month + '-' + day + '): failure2'
        logging.error(msg)

    # If the treated image is the only one required, the original image is deleted.
    if not opt.keep_original:
        exists = os.path.isfile(path)
        if exists:
            os.remove(path)

    return success, path


def single_download_gee(source, date1, date2, x1, x2, y1, y2, opt):
    """ Function responsible for each satellite image download from Google Earth Engine. """

    # Convert numeric data values to string format.
    year1 = str(date1.year)
    month1 = str(date1.month)
    day1 = str(date1.day)
    if len(month1) == 1:    month1 = '0' + month1
    if len(day1) == 1:      day1 = '0' + day1

    # Satellite parameters.
    bbox = str([[x1, y1], [x1, y2], [x2, y1], [x2, y2]])

    if source in ['LST_Day_1km', 'LST_Night_1km']:
        scale = 500
        mod11 = ee.ImageCollection("MODIS/MOD11A2")
        img = mod11.filterDate(date1, date2) \
            .sort('system:time_start', False) \
            .select(source) \
            .mean() \
            .multiply(0.02) \
            .subtract(273.15) \
            .rename("Celsius") \
            .set('date', date1) \
            .set('system:time_start', date1)

    elif source == 'CHIRPS':
        scale = 5000
        CHIRPS = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD")
        img = CHIRPS.filterDate(date1, date2) \
            .sort('system:time_start', False) \
            .mean() \
            .rename("Precipitation") \
            .set('date', date1) \
            .set('system:time_start', date1)

    elif source == 'NDVI':
        scale = 500
        MYD13Q1 = ee.ImageCollection("MODIS/MYD13Q1")
        img = MYD13Q1.filterDate(date1, date2) \
            .sort('system:time_start', False) \
            .select(source) \
            .mean() \
            .rename(source) \
            .set('date', date1) \
            .set('system:time_start', date1)

    elif source == 'EVI':
        scale = 500
        MYD13Q1 = ee.ImageCollection("MODIS/MYD13Q1")
        img = MYD13Q1.filterDate(date1, date2) \
            .sort('system:time_start', False) \
            .select(source) \
            .mean() \
            .rename(source) \
            .set('date', date1) \
            .set('system:time_start', date1)

    # Export data to Google Drive.
    filename = source + '-' + str(year1) + '-' + str(month1) + '-' + str(day1)
    task_config = {'scale': scale, 'region': bbox}
    task = ee.batch.Export.image(img, filename, task_config)
    task.start()

    # Download Google Drive data to local machine.
    count = 0
    wait = True
    while wait:
        # Get file list within Driver.
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['title'] == filename + '.tif':
                wait = False
                # Download file from Google Drive.
                file.GetContentFile(filename + '.tif')
                # Delete downloaded file from Google Drive.
                file.Delete()
                break
        if wait:
            # Wait one minute before repeating the search.
            time.sleep(60)
            count += 1
            # After one hour the program gives up.
            if count == 60:
                wait = False
                
    # Create source folder if it doesn't exists.
    path_tmp = os.path.join(PATH, source)
    exists = os.path.exists(path_tmp)
    if not exists:
        os.mkdir(path_tmp)
    # Path to the file.
    path = os.path.join(path_tmp, filename + '.tiff')
    with open(path, "wb") as fp:
        with open(filename + '.tif', "rb") as f:
            d = f.read()
        fp.write(d)

    # Remove original file.
    os.remove(filename + '.tif')

    # After saving the image, the treatment process begins.
    regrid_image(source, filename + '.tiff', opt)

    # Log message of success.
    success = True
    if count < 60:
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + '): success'
        logging.info(msg)

    else:
        # Log message of failure.
        success = False
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + '): failure'
        logging.error(msg)

    # If the treated image is the only one required, the original image is deleted.
    if not opt.keep_original:
        exists = os.path.isfile(path)
        if exists:
            os.remove(path)

    return success, path


def regrid_image(source, filename, opt):
    """ This function is responsible for upsampling or downsampling the images using some precribed method. """
    
    path_tmp = os.path.join(PATH, source)
    path = os.path.join(path_tmp, filename)
    
    if opt.regrid:
        factor = opt.regrid[0]
        method = opt.regrid[1]

        with rasterio.open(path) as dataset:
            a = dataset.transform.a
            b = dataset.transform.b
            c = dataset.transform.c
            d = dataset.transform.d
            e = dataset.transform.e
            f = dataset.transform.f
            array = dataset.read()
            new_array = np.ones((int(factor*array.shape[1]), int(factor*array.shape[2])), dtype=np.float32)
            new_transform = (a/factor, b, c, d, e/factor, f)
            dataset_crs = dataset.crs        
            new_crs = dataset.crs
        
            if method == 'nearest':
                reproject(
                    array,
                    new_array,
                    src_transform=dataset.transform,
                    src_crs=dataset_crs,
                    dst_transform=new_transform,
                    dst_crs=new_crs,
                    resampling=Resampling.nearest)
            
            if method == 'average':
                reproject(
                    array,
                    new_array,
                    src_transform=dataset.transform,
                    src_crs=dataset_crs,
                    dst_transform=new_transform,
                    dst_crs=new_crs,
                    resampling=Resampling.average)
            
            if method == 'bilinear':
                reproject(
                    array,
                    new_array,
                    src_transform=dataset.transform,
                    src_crs=dataset_crs,
                    dst_transform=new_transform,
                    dst_crs=new_crs,
                    resampling=Resampling.bilinear)
            
            if method == 'cubic':
                reproject(
                    array,
                    new_array,
                    src_transform=dataset.transform,
                    src_crs=dataset_crs,
                    dst_transform=new_transform,
                    dst_crs=new_crs,
                    resampling=Resampling.cubic)
     
            new_profile = dataset.profile.copy()
            new_profile.update({
                'dtype': 'float32',
                'height': new_array.shape[0],
                'width': new_array.shape[1],
                'transform': new_transform})
        
            if opt.plot:
                plt.title(filename.replace('.tiff', ''))
                plt.imshow(new_array, cmap=opt.cmap)
                plt.colorbar(fraction=0.028)
                plt.xlabel('Column #')
                plt.ylabel('Row #')
                plt.show()

        # Remove duplicates before saving new ones.
        new_filename = filename[:-5] + '-treated.tiff'
        new_path = os.path.join(path_tmp, new_filename)
        exists = os.path.isfile(new_path)
        if exists:
            os.remove(new_path)
        
        with rasterio.open(new_path, 'w', **new_profile) as new_dataset:
            new_dataset.write_band(1, new_array)
            
    else:
        with rasterio.open(path) as dataset:
            array = dataset.read()
        if opt.plot:
            plt.title(filename.replace('.tiff', ''))
            plt.imshow(array[0, :, :], cmap=opt.cmap)
            plt.colorbar(fraction=0.028)
            plt.xlabel('Column #')
            plt.ylabel('Row #')
            plt.show()       
        
    return


def scale_min_max(source, remote_data):
    if source == "LandDAAC-v5-day" or source == "LandDAAC-v5-night":
        a = remote_data['LST'].scale_min
        b = remote_data['LST'].scale_max
    elif source == "LandDAAC-v6-EVI":
        a = remote_data['EVI'].scale_min
        b = remote_data['EVI'].scale_max
    elif source == "LandDAAC-v6-NDVI":
        a = remote_data['NDVI'].scale_min
        b = remote_data['NDVI'].scale_max
    elif source == "LandDAAC-v6-view_zenith_angle":
        a = remote_data['view_zenith_angle'].scale_min
        b = remote_data['view_zenith_angle'].scale_max

    return a, b


def source_freq(source):
    """ Gets the frequency (in days) with which the respective satellite sends the data. """
    
    if source == "chirps-2.0":
        freq = '1D'
    elif source == "CHIRPS":
        freq = '5D'
    elif source in ["LandDAAC-v5-day", "LandDAAC-v5-night", "LST_Day_1km", "LST_Night_1km"]:
        freq = '8D'
    elif source in ["LandDAAC-v6-EVI", "LandDAAC-v6-NDVI", "LandDAAC-v6-view_zenith_angle", "NDVI", "EVI"]:
        freq = '16D'
        
    return freq


def month_to_string(month):
    """ Converts numeric month to string with abbreviated month name. """
    
    months = ["Jan", "Fev", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i in range(1, 13):
        if int(month) == i:
            month_str = months[i-1]
            
    return month_str


def source_url(source):
    """ Piece of the url responsible for identifying the source. """
    
    if source == "LandDAAC-v5-day":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/.SSA/.Day/.LST/(Celsius)/unitconvert/"
    elif source == "LandDAAC-v5-night":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/.SSA/.Night/.LST/(Celsius)/unitconvert/"
    elif source == "LandDAAC-v6-EVI":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.EVI/"
    elif source == "LandDAAC-v6-NDVI":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.NDVI/"
    elif source == "LandDAAC-v6-view_zenith_angle":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.view_zenith_angle/"
    else:
        sys.exit("Wrong source name")
    
    return url


def create_options(Opt):
    """ Extract the optional parameter """

    if not Opt:
        class OptOut:
            regrid = False
            plot = False
            keep_original = True
            time_series = False
            cmap = 'jet'

        return OptOut
    
    class OptOut:
        regrid = False
        plot = False
        keep_original = True
        time_series = False
        cmap = 'jet'
        if 'regrid' in Opt:
            if type(Opt['regrid']) == list and len(Opt['regrid']) == 2:
                factor = Opt['regrid'][0]
                method = Opt['regrid'][1]
                regrid = [factor, method]
        if 'plot' in Opt:
            plot = Opt['plot']
        if 'keep_original' in Opt:
            keep_original = Opt['keep_original']
        if 'time_series' in Opt:
            time_series = Opt['time_series']
        if 'cmap' in Opt:
            cmap = Opt['cmap']
            
    return OptOut


def about(x):
    """ Displays information from available sources for download (x = 'sources') or possible options (x = options). """
    
    if x == 'sources':
        print('LandDAAC-v5-day')
        print('---------------')
        print('Day LST from USGS LandDAAC MODIS 1km 8day version_005 Terra SSA: Day and Night Land Surface Temperature '
              'of Southern South America.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (5-12 Mar 2000) (13-20 Mar 2000) (21-28 Mar 2000) ... '
              '(22-29 Mar 2017)] N= 785 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99467W) to (40.002W) by 0.01064817 N= 3569 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00532S) to (56.99707S) by 0.01064817 N= 3475 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/'
              '.SSA/.Day/.LST/')
        print()
        
        print('LandDAAC-v5-night')
        print('-----------------')
        print('Night LST from USGS LandDAAC MODIS 1km 8day version_005 Terra SSA: Day and Night Land Surface '
              'Temperature of Southern South America.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (5-12 Mar 2000) (13-20 Mar 2000) (21-28 Mar 2000) ... '
              '(22-29 Mar 2017)] N= 785 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99467W) to (40.002W) by 0.01064817 N= 3569 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00532S) to (56.99707S) by 0.01064817 N= 3475 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/'
              '.SSA/.Night/.LST/')
        print()
        
        print('LandDAAC-v6-EVI')
        print('---------------')
        print('LandDAAC MODIS version_006 SSA EVI from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) '
              '(24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.EVI/')
        print()
        
        print('LandDAAC-v6-NDVI')
        print('----------------')
        print('LandDAAC MODIS version_006 SSA NDVI from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) '
              '(24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.NDVI/')
        print()
        
        print('LandDAAC-v6-view_zenith_angle')
        print('-----------------------------')
        print('LandDAAC MODIS version_006 SSA view_zenith_angle from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) '
              '(24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.view_zenith'
              '_angle/')
        print()

        print('chirps-2.0')
        print('------------------------------')
        print('Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) is a 35+ year quasi-global '
              'rainfall data set. Spanning 50°S-50°N (and all longitudes) and ranging from 1981 to near-present, '
              'CHIRPS incorporates our in-house climatology, CHPclim, 0.05° resolution satellite imagery, and in-situ '
              'station data to create gridded rainfall time series for trend analysis and seasonal drought monitoring.')
        print('Link: ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/')
        print()

        print('LST_Day_1km / LST_Night_1km')
        print('------------------------------')
        print('The MOD11A2 V6 product provides an average 8-day land surface temperature (LST) in a 1200 x 1200 '
              'kilometer grid. Each pixel value in MOD11A2 is a simple average of all the corresponding MOD11A1 LST '
              'pixels collected within that 8 day period. The 8 day compositing period was chosen because twice that '
              'period is the exact ground track repeat period of the Terra and Aqua platforms. In this product, along '
              'with both the day- and night-time surface temperature bands and their quality indicator (QC) layers, are'
              ' also MODIS bands 31 and 32 and eight observation layers.')
        print('Link: https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MOD11A2')
        print()

        print('NDVI / EVI')
        print('------------------------------')
        print('The MYD13Q1 V6 product provides a Vegetation Index (VI) value at a per pixel basis. There are two '
              'primary vegetation layers. The first is the Normalized Difference Vegetation Index (NDVI) which is '
              'referred to as the continuity index to the existing National Oceanic and Atmospheric '
              'Administration-Advanced Very High Resolution Radiometer (NOAA-AVHRR) derived NDVI. The second vegetation '
              'layer is the Enhanced Vegetation Index (EVI) that minimizes canopy background variations and maintains '
              'sensitivity over dense vegetation conditions. The EVI also uses the blue band to remove residual '
              'atmosphere contamination caused by smoke and sub-pixel thin cloud clouds. The MODIS NDVI and EVI '
              'products are computed from atmospherically corrected bi-directional surface reflectances that have been '
              'masked for water, clouds, heavy aerosols, and cloud shadows.')
        print('Link: https://developers.google.com/earth-engine/datasets/catalog/MODIS_006_MYD13Q1')
        print()

        print('CHIRPS')
        print('------------------------------')
        print('Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) is a 30+ year quasi-global '
              'rainfall dataset. CHIRPS incorporates 0.05° resolution satellite imagery with in-situ station data to '
              'create gridded rainfall time series for trend analysis and seasonal drought monitoring.')
        print('Link: https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_PENTAD')
        print()
        
    if x == 'options':   
        print('cmap (string)')
        print('-------------')
        print('The name of the colormap to use when plotting images. Default is `jet`.')
        print()
        
        print('regrid (list)')
        print('-------------')
        print('When downloading the images you also have the option to make a downsampling or upsampling over all the '
              'images and download these new pack of images. You should pass a list of two items. The first is a '
              'positive float, the ratio of the regrid. For example, if the original image is 120x120 and regrid[0]=2, '
              'them the program will create a image of shape 240x240. The second is the method of the resampling, which'
              ' can be `nearest`, `average`, `bilinear` and `cubic`.')
        print('Link: https://github.com/mapbox/rasterio/blob/master/rasterio/enums.py#L28')
        print()
              
        print('plot (bool)')
        print('-----------')
        print('When this option is set to True the program plots each one of the images downloaded. At the moment this '
              'only works when some regrid is done. Default is False.')
        print()
        
        print('keep_original (bool)')
        print('--------------------')
        print('When this option is set to True (default) the program stores the original files. When it is False, the '
              'program only saves the treated data.')
        print()
        
        print('time_series (bool)')
        print('--------------------')
        print('When this option is set to True the program opens an interactive session with the data just downloaded. '
              'Default is False.')
        print()
        
    return


def construct_time_series(dates, opt):
    """ 
    This function creates a netcdf file from the downladed tiffs (as a time series) and open an interactive session
    to explore this time series. To enable this function you must pass the option time_series as True to the function
    download_tiffs. The folder (where the just downloaded tiffs are) must not contain any other tiffs, otherwise the
    netcdf file will be corrupted. 
    """

    filename = 'time_series.nc'
    path = os.path.join(PATH, filename)
    exists = os.path.isfile(path)
    if exists:
        os.remove(path)
    
    # Enable extensions of geoviews
    gv.extension('bokeh', 'matplotlib')
    
    # Create list with all tiff filenames in chronological order.
    path2 = os.path.join(PATH, '*.tiff')
    filenames = glob.glob(path2)
    filenames.sort()
    
    # Extract sequence of dates and size of the images. 
    time = xr.Variable('time', dates[:-1])
    with rasterio.open(filenames[0]) as dataset:
        dataset_array = dataset.read()
        width, height = dataset_array.shape[1], dataset_array.shape[2]
        chunks = {'x': width, 'y': height, 'band': 1}
    
    # Create netcdf file containing the time series of all downloaded tiffs.
    with xr.concat([xr.open_rasterio(f, chunks=chunks) for f in filenames], dim=time) as da:
        da.to_netcdf(path)
    
    # Open geoviews interactive session.
    with xr.open_dataset(path, decode_times=False) as da:
        dataset = gv.Dataset(da)
        ensemble = dataset.to(gv.Image, ['x', 'y'])
        gv.output(ensemble.opts(cmap=opt.cmap, colorbar=True, fig_size=200, backend='matplotlib'), backend='matplotlib')
    return


def view_time_series(filename, cmap='jet'):
    """ Visualize and interact with time series netcdf files. """
    
    gv.extension('bokeh', 'matplotlib')
    with xr.open_dataset(filename, decode_times=False) as da:
        dataset = gv.Dataset(da)
        ensemble = dataset.to(gv.Image, ['x', 'y'])
        gv.output(ensemble.opts(cmap=cmap, colorbar=True, fig_size=200, backend='matplotlib'), backend='matplotlib')
    return


def point_time_series(points, title='Time series of given coordinates', spatial_coordinates=True):
    """ 
    This function plots the evolution of the time series with respect to a list of points. All tiff files in the current
    folder are sorted and used to construct the time series. Therefore be sure you have the correct files there.
    Additionaly, the values to construct the time series are returned by the function in the form of two lists.
 
    Inputs
    ------
    points: list of tuples
        Each element of points is a tuple (col, row) or (x, y) corresponding to some coordinate of the image.
    spatial_coordinates: bool
        It is set to True, then we interpret the tuple as a spatial coordinate (x, y), otherwise we 
        interpret it as a pixel (col, row) represented by a value in an array.
        
    Outputs
    -------
    info: dict
        info[point] = [dates, values], where dates correspond to the x axis of the plot and the values correspond to the
        y values of the plot.
    """
    
    # Create list with all tiff filenames in chronological order.
    path = os.path.join(PATH, '*.tiff')
    filenames = glob.glob(path)
    filenames.sort()

    # Initialize dictionary defined by info[point] = [dates, values], where dates are the sequence of the dates in
    # the time series and values are the corresponding values attained by the point.
    info = {}

    col_row_format = []
    for point in points:
        # Extracts point input information.
        p1, p2 = point

        # Initialize list of dates and values.
        dates = []
        values = []

        # Save positional coordinates.
        with rasterio.open(filenames[0]) as dataset:
            # x, y to col, row.
            if spatial_coordinates:
                col, row = ~dataset.transform * (p1, p2)
            # col, row to x, y.
            else:
                col, row = p1, p2
            col, row = int(col), int(row)
            col_row_format.append([col, row])

        for f in filenames:
            with rasterio.open(f) as dataset:
                dataset_array = dataset.read()[0, :, :]
                # Split in two cases, where the filename terminates in 'treated.tiff' and the other one.
                if f[-6] == 'd':
                    dates.append(f[-23:-13])
                else:
                    dates.append(f[-15:-5])
                values.append(dataset_array[row, col])

        # Update dictionary.
        info[str(point[0]) + ', ' + str(point[1])] = [[dates[i], values[i]] for i in range(len(dates))]

    plot_point_time_series(info, col_row_format, title, spatial_coordinates)

    return info


def plot_point_time_series(info, col_row_format, title, spatial_coordinates):
    """
    After constructing the time series (in a dictionary) of several points with the fucntion point_time_series, this
    function is responsible for the plots. All inputs to this function are described in the previous function.
    """

    # List with all dates.
    info_keys = [s for s in info.keys()]

    # Create list with all tiff filenames in chronological order.
    path = os.path.join(PATH, '*.tiff')
    filenames = glob.glob(path)
    filenames.sort()

    # Show points in the map for reference.
    with rasterio.open(filenames[0]) as dataset:
        dataset_array = dataset.read()[0, :, :]
    plt.figure(figsize=[10, 8])
    plt.imshow(dataset_array)
    i = 0
    for point in col_row_format:
        col, row = point
        plt.plot(col, row, 's', label='(' + info_keys[i] + ')')
        i += 1
    # Prepare x and y ticks to plot.
    if spatial_coordinates:
        interval = np.linspace(0, 1, 5)
        interval_x = np.linspace(0, dataset.width, 5)
        interval_y = np.linspace(0, dataset.height, 5)
        x = [np.round((1-t)*dataset.bounds.left, 2) + np.round(t*dataset.bounds.right, 2) for t in interval]
        y = [np.round((1-t)*dataset.bounds.top, 2) + np.round(t*dataset.bounds.bottom, 2) for t in interval]
        plt.xticks(interval_x, x)
        plt.yticks(interval_y, y)
    plt.legend()
    plt.show()

    # Plot time series.
    i = 0
    plt.figure(figsize=[16, 5])
    for info_val in info.values():
        num_dates = len(info_val)
        dates = [info_val[i][0] for i in range(num_dates)]
        values = [info_val[i][1] for i in range(num_dates)]
        plt.plot(dates, values, label='(' + info_keys[i] + ')')
        i += 1
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid()
    plt.show()

    return


def timestamp_to_list(dates):
    """
    Given a list or a Pandas DateTimeIndex with many timestamps, this function converts
    them to a list where each entry is of form [year, month, day], where year, month and
    day are strings. This is the format to use as input to the downloader function.
    
    Inputs
    ------
    dates: list or DateTimeIndex
    
    Outputs
    -------
    dates: dates_list
    """
    
    dates_list = []
    for i in range(len(dates)):
        year = str(dates[i].year)
        
        month = dates[i].month
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
            
        day = dates[i].day
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
            
        dates_list.append([year, month, day]) 
        
    return dates_list