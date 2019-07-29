from configparser import ConfigParser
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import urllib.request
import os
import sys
import glob
import rasterio
from rasterio.warp import reproject, Resampling
import xarray as xr
import geoviews as gv
from celery import Celery
from celery.utils.log import get_task_logger


logger = get_task_logger("downloader_app")

# instantiate
config = ConfigParser()
# parse existing file
config.read('settings.ini')
# read values 
PATH = config.get('settings', 'path')


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
            accepted format at the moment is 'year-month-day'. Months and days should
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
    
    # Check extra options to be included.
    opt = create_options(opt)
    
    # Obtains the frequency of the source.
    freq = source_freq(source)
    
    # Extract the values from the dates.
    year1, month1, day1 = date1
    year2, month2, day2 = date2

    # Dates of interest.
    dates = pd.date_range(year1 + month1 + day1, year2 + month2 + day2, freq=freq)
        
    # Download maps by date.
    length = len(dates)
    for l in range(length-1):
        current_date = dates[l]
        next_date = dates[l+1]
        url = single_download(source, current_date, next_date, x1, x2, y1, y2, opt)
                        
    # View time series after the downloads.
    if opt.time_series:
        construct_time_series(dates, opt)
                
    return 


def single_download(source, date1, date2, x1, x2, y1, y2, opt):
    """ Function responsible for each satellite image download. """

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
    filename = str(year1) + '-' + str(month1) + '-' + str(day1) + '.tiff'
    path = os.path.join(PATH, filename)

    # Remove duplicate file with same name if it exists.
    exists = os.path.isfile(path)
    if exists:
        os.remove(path)

    # Download and save url content.
    try:
        # Download.
        with urllib.request.urlopen(url) as response, open(path, 'wb') as file:
            data = response.read() 
            file.write(data)
        
        # Fix values scale (the images are downloaded as uint8, not float).
        url_dods = start_url + time_range + bounding_box + time + 'dods'
        remote_data = xr.open_dataset(url_dods, decode_times=False)
        a = remote_data['LST'].scale_min
        b = remote_data['LST'].scale_max
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
        regrid_image(filename, opt)
        
        # Log message of success.
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + ') (' + year2 + '-' + month2 + '-' + day2 + '):success'
        logger.info(msg)
        
    except urllib.error.HTTPError:
        # Log message of failure.
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + ') (' + year2 + '-' + month2 + '-' + day2 + '):failure'
        logger.error(msg)
        
    except urllib.error.URLError:
        # Log message of failure.
        msg = 'Download (' + year1 + '-' + month1 + '-' + day1 + ') (' + year2 + '-' + month2 + '-' + day2 + '):failure'
        logger.error(msg)
        
    # If the treated image is the only one required, the original image is deleted.
    if not opt.keep_original:
        exists = os.path.isfile(path)
        if exists:
            os.remove(path)
    
    return url


def source_freq(source):
    """ Gets the frequency (in days) with which the respective satellite sends the data. """
    
    if source == "LandDAAC-v5-day" or source == "LandDAAC-v5-night":
        freq = '8D'
    else:
        freq = '16D'
        
    return freq


def month_to_string(month):
    """ Converts numeric month to string with abbreviated month name. """
    
    months = ["Jan", "Fev", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i in range(1,13):
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
    elif source == "LandDAAC-v6-reflectance":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.reflectance/"
    elif source == "LandDAAC-v6-VI_Quality":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.VI_Quality/"
    elif source == "LandDAAC-v6-view_zenith_angle":
        url = "http://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.view_zenith_angle/"
    else:
        sys.exit("Wrong source name")
    
    return url


def create_options(Opt):
    """ Extract the optional parameter """

    if Opt == False:
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
            if time_series:
                keep_original = False
        if 'cmap' in Opt:
            cmap = Opt['cmap']
            
    return OptOut


def about(x):
    """ Displays information from available sources for download (if x = 'sources') or possible options (if x = options). """
    
    if x == 'sources':
        print('LandDAAC-v5-day')
        print('---------------')
        print('Day LST from USGS LandDAAC MODIS 1km 8day version_005 Terra SSA: Day and Night Land Surface Temperature of Southern South America.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (5-12 Mar 2000) (13-20 Mar 2000) (21-28 Mar 2000) ... (22-29 Mar 2017)] N= 785 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99467W) to (40.002W) by 0.01064817 N= 3569 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00532S) to (56.99707S) by 0.01064817 N= 3475 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/.SSA/.Day/.LST/')
        print()
        
        print('LandDAAC-v5-night')
        print('-----------------')
        print('Night LST from USGS LandDAAC MODIS 1km 8day version_005 Terra SSA: Day and Night Land Surface Temperature of Southern South America.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (5-12 Mar 2000) (13-20 Mar 2000) (21-28 Mar 2000) ... (22-29 Mar 2017)] N= 785 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99467W) to (40.002W) by 0.01064817 N= 3569 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00532S) to (56.99707S) by 0.01064817 N= 3475 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.1km/.8day/.version_005/.Terra/.SSA/.Night/.LST/')
        print()
        
        print('LandDAAC-v6-EVI')
        print('---------------')
        print('LandDAAC MODIS version_006 SSA EVI from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) (24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.EVI/')
        print()
        
        print('LandDAAC-v6-NDVI')
        print('----------------')
        print('LandDAAC MODIS version_006 SSA NDVI from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) (24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.NDVI/')
        print()
        
        print('LandDAAC-v6-reflectance')
        print('-----------------------')
        print('LandDAAC MODIS version_006 SSA reflectance from USGS: United States Geological Survey.')
        print('Band: grid: /band (ids) unordered [ (MIR) (NIR) (red) (blue)] :grid')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) (24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.reflectance/')
        print()
        
        print('LandDAAC-v6-VI_Quality')
        print('----------------------')
        print('LandDAAC MODIS version_006 SSA VI_Quality from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) (24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.VI_Quality/')
        print()
        
        print('LandDAAC-v6-view_zenith_angle')
        print('-----------------------------')
        print('LandDAAC MODIS version_006 SSA view_zenith_angle from USGS: United States Geological Survey.')
        print('Time: grid: /T (days since 2003-01-01) ordered [ (22 Apr 2000 - 7 May 2000) (8-23 May 2000) (24 May 2000 - 8 Jun 2000) ... (6-21 Mar 2019)] N= 435 pts :grid')
        print('Longitude: grid: /X (degree_east) ordered (77.99867W) to (40.00067W) by 0.002662043 N= 14275 pts :grid')
        print('Latitude: grid: /Y (degree_north) ordered (20.00133S) to (57.00107S) by 0.002662043 N= 13900 pts :grid')
        print('Link: https://iridl.ldeo.columbia.edu/SOURCES/.USGS/.LandDAAC/.MODIS/.version_006/.SSA/.view_zenith_angle/')
        print()
        
    if x == 'options':   
        print('cmap (string)')
        print('-------------')
        print('The name of the colormap to use when plotting images. Default is `jet`.')
        print()
        
        print('regrid (list)')
        print('-------------')
        print('When downloading the images you also have the option to make a downsampling or upsampling over all the images and download these new pack of images. You should pass a list of two items. The first is a positive float, the ratio of the regrid. For example, if the original image is 120x120 and regrid[0] = 2, them the program will create a image of shape 240x240. The second is the method of the resampling, which can be `nearest`, `average`, `bilinear`, `cubic`, `cubic_spline`, `mode`, `lanczos`, `max`, `min`,`q1` and `q3`.')
        print('Link: https://github.com/mapbox/rasterio/blob/master/rasterio/enums.py#L28')
        print()
              
        print('plot (bool)')
        print('-----------')
        print('When this option is set to True the program plots each one of the images downloaded. At the moment this only works when some regrid is done. Default is False.')
        print()
        
        print('keep_original (bool)')
        print('--------------------')
        print('When this option is set to True (default) the program stores the original files. When it is False, the program only saves the treated data.')
        print()
        
        print('time_series (bool)')
        print('--------------------')
        print('When this option is set to True the program opens an interactive session with the data just downloaded. Default is False.')
        print()
        
    return


def regrid_image(filename, opt):
    """ This function is responsible for upsampling or downsampling the images using some precribed method. """
    
    path = os.path.join(PATH, filename)
    
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
        new_filename = 'new_' + filename
        new_path = os.path.join(PATH, new_filename)
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


def construct_time_series(dates, opt):
    """ 
    This function creates a netcdf file from the downladed tiffs (as a time series) and open an interactive session
    to explore this time series. To enable this function you must pass the option time_series as True to the function
    download_tiffs. The folder (where the just downloaded tiffs are) must not contain any other tiffs, otherwise the
    netcdf file will be corrupted. 
    """
    
    exists = os.path.isfile('time_series.nc')
    if exists:
        os.remove('time_series.nc')
    
    # Enable extensions of geoviews
    gv.extension('bokeh', 'matplotlib')
    
    # Create list with all tiff filenames in chronological order.
    filenames = glob.glob('*.tiff')
    filenames.sort()
    
    # Extract sequence of dates and size of the images. 
    time = xr.Variable('time', dates[:-1])
    with rasterio.open(filenames[0]) as dataset:
        dataset_array = dataset.read()
        width, height = dataset_array.shape[1], dataset_array.shape[2]
        chunks = {'x': width, 'y': height, 'band': 1}
    
    # Create netcdf file containing the time series of all downloaded tiffs.
    with xr.concat([xr.open_rasterio(f, chunks=chunks) for f in filenames], dim=time) as da:
        da.to_netcdf('time_series.nc')
    
    # Open geoviews interactive session.
    with xr.open_dataset('time_series.nc', decode_times=False) as da:
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
    filenames = glob.glob('*.tiff')
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
                dates.append(f.replace('new_', '').replace('.tiff', ''))
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
    filenames = glob.glob('*.tiff')
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
