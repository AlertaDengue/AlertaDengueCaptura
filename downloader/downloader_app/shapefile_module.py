import os
import sys

import geopandas as gpd
import imageio
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import rasterio.plot
import shapely
from rasterstats import zonal_stats
from shapely.geometry import mapping


def extract_shp_boundingbox(shp_filename):
    """
    Given a shapefile path, this function extracts the spatial coordinates defining the bounding box of the shapefile.

    Inputs
    ------
    shp_filename: str
        path to the shapefile

    Outputs
    -------
    point1, point2: list of floats
        point1 = [min_x, max_y] is the top left point and point2 = [max_x, min_y] is the bottom right point.
    """

    min_x = np.inf
    max_x = -np.inf
    min_y = np.inf
    max_y = -np.inf

    # Load shapefile.
    dataset_map = gpd.read_file(shp_filename)

    # Convert it to coordinate system epsg:4326, which is the default here.
    new_dataset_map = dataset_map.to_crs({'init': 'epsg:4326'})

    # Search for max and min coordinates of polygons and multipolygons
    g = [i for i in new_dataset_map.geometry]
    for h in g:
        if type(h) == shapely.geometry.polygon.Polygon:
            all_coords = mapping(h)['coordinates']
            all_coords = all_coords[0]
            for b in all_coords:
                if b[0] < min_x:
                    min_x = b[0]
                if b[0] > max_x:
                    max_x = b[0]
                if b[1] < min_y:
                    min_y = b[1]
                if b[1] > max_y:
                    max_y = b[1]

        elif type(h) == shapely.geometry.multipolygon.MultiPolygon:
            for i in h:
                all_coords = mapping(i)['coordinates']
                all_coords = all_coords[0]
                for b in all_coords:
                    if b[0] < min_x:
                        min_x = b[0]
                    if b[0] > max_x:
                        max_x = b[0]
                    if b[1] < min_y:
                        min_y = b[1]
                    if b[1] > max_y:
                        max_y = b[1]

    point1 = [min_x, max_y]
    point2 = [max_x, min_y]

    return point1, point2


def zonal_means(shp_path, raster_path, col_pos=1):
    """
    Given a shapefile and a raster, this function computes the mean of the raster pixel inside each poylgon. The
    original shapefile must have a column with the region names. Additionally, the polygons with means
    equal to None receive the overall mean with respect to the other polygons.

    By default this function uses the second column of the shapefile to extract the region names.

    Inputs
    ------
    shp_path: str
        String with the path to the shapefile.
    raster_filename: str
        String with the path to the raster file.
    col_pos: int
        Number of the column with the region names. Default is 1 (the second column).

    Outputs
    -------
    z_means: dataframe
        A dataframe with the means of the regions.
    """

    # Load statistics.
    z_stats = zonal_stats(
        shp_path, raster_path, stats='count mean', nodata=1.0
    )

    # Create dictionary with all means.
    map_df = gpd.read_file(shp_path)
    column_name = map_df.columns[col_pos]
    overall_mean = 0
    num_regions = len(map_df)
    z_means = {}
    for i in range(num_regions):
        z_means[map_df[column_name][i]] = z_stats[i]['mean']
        if z_stats[i]['mean'] is not None:
            overall_mean += z_stats[i]['mean']
    overall_mean = overall_mean / num_regions

    # Use the dictionary to create a dataframe.
    z_means = pd.DataFrame(
        {'MEANS': z_means}, index=map_df[column_name].values
    )
    for i in range(num_regions):
        # Verify for anomalies and fix them substituting by the overall mean.
        x = z_means.iloc[i, 0]
        if (x is None) or (np.isnan(x)) or (x < 0):
            z_means.iloc[i, 0] = overall_mean

    return z_means


def raw_plot(shp_path, raster_path, cmap='jet'):
    """
    This function plots both layers of raster and shapefile in a single image.

    Inputs
    ------
    shp_path: str
        String with the path to the shapefile.
    raster_path: str
        String with the path to the raster file.
    cmap: str
        String for the colormap.
    """

    dataset_map = gpd.read_file(shp_path)
    with rasterio.open(raster_path) as dataset:
        array = dataset.read()[0, :, :]
        fig, ax = plt.subplots(figsize=(15, 15))
        rasterio.plot.show(dataset, ax=ax, cmap=cmap)
        sm = plt.cm.ScalarMappable(
            cmap=cmap,
            norm=plt.Normalize(vmin=np.nanmax(array), vmax=np.nanmin(array)),
        )
        sm._A = []
        cbar = fig.colorbar(sm, fraction=0.028)
        dataset_map.plot(ax=ax, facecolor='none', edgecolor='black')
        return


def zonal_plot(shp_path, z_means, title, cmap='jet', col_pos=1):
    """
    Given a shapefile path shp_path and dataframe z_means, this function merges the map with the information given and
    makes a plot. The image is saved to the disk with the name 'map_image.png'.

    By default this function uses the second column of the shapefile to make the join between the datasets. Be sure
    that this is the adequate column to perform this operation.
    Inputs
    ------
    shp_path: str
        String with the path to the shapefile.
    z_means: dataframe
        A dataframe with the means of the regions.
    title: str
        Title of the image.
    cmap: str
        String for the colormap.
    col_pos: int
        Number of the column with the region names. Default is 1 (the second column).
    """

    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
        """
        Given a colormap cmap and a interval contained in [0,1], this function truncates the colormap to the interval
        with n points.
        """

        new_cmap = colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(
                n=cmap.name, a=minval, b=maxval
            ),
            cmap(np.linspace(minval, maxval, n)),
        )
        return new_cmap

    # Load shapefile.
    dataset_map = gpd.read_file(shp_path)
    # Merge the shapefile with the dataframe of the means obtained from the raster data.
    column_name = dataset_map.columns[col_pos]
    merged = dataset_map.set_index(column_name).join(z_means)
    # Set a variable that will call whatever column we want to visualise on the map.
    variable = z_means.columns[0]
    # Convert column of interest to numeric type.
    merged[variable] = pd.to_numeric(merged[variable])
    # Set the range.
    vmin, vmax = np.nanmin(merged[variable]), np.nanmax(merged[variable])
    # Make the truncation.
    cmap = plt.get_cmap(cmap)
    new_cmap = truncate_colormap(cmap, 0.4, 1.0)
    # Create figure and axes for Matplotlib.
    fig, ax = plt.subplots(1, figsize=(18, 8))
    # Create map.
    merged.plot(
        column=variable, cmap=new_cmap, linewidth=0.8, ax=ax, edgecolor='0.8'
    )
    # Remove the axis.
    ax.axis('off')
    # Add a title.
    ax.set_title(title, fontdict={'fontsize': '25', 'fontweight': '3'})
    # Create colorbar as a legend.
    sm = plt.cm.ScalarMappable(
        cmap=new_cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax)
    )
    # Empty array for the data range.
    sm._A = []
    # Add the colorbar to the figure.
    cbar = fig.colorbar(sm)
    # Save image.
    fig.savefig('map_image.png', dpi=300)

    return


def time_series(shp_path, raster_filename_list, region, plot=False, col_pos=1):
    """
    Given a shapefile, a list of raster files and a name (with respect to the second column of the shapefile
    by default), this function plots the time series of the raster data relative to the specific name given.

    Inputs
    ------
    shp_path: str
    raster_filename_list: list
        List of strings with all raster filenames of interest.
    region: str
        Name of the region of interest, which is one row of the shapefile.
    plot: bool
        If True (default is False), then the time series is plotted.
    col_pos: int
        Number of the column with the region names. Default is 1 (the second column).

    Outputs
    -------
    t_series: array
        Each t_series[i] is the the mean of the ith raster with respect to the name.
    dates: list
        List with the corresponding dates.
    """

    # Create variables.
    num_files = len(raster_filename_list)
    t_series = np.zeros(num_files)
    i = 0
    dates = []

    for raster_filename in raster_filename_list:
        z_means = zonal_means(shp_path, raster_filename, col_pos=col_pos)
        current_mean = z_means.loc[region].values[0]
        t_series[i] = current_mean
        i += 1
        # Split in two cases, where the filename terminates in 'treated.tiff' and the other one.
        if raster_filename[-6] == 'd':
            dates.append(raster_filename[-23:-13])
        else:
            dates.append(raster_filename[-15:-5])

    if plot:
        plt.figure(figsize=[16, 5])
        plt.plot(dates, t_series)
        title = 'Time series of ' + region
        plt.title(title)
        plt.xticks(rotation=90)
        plt.grid()
        plt.show()

    return t_series, dates


def time_series_curve(
    shp_path,
    raster_paths,
    save_path,
    region,
    title,
    labels,
    extra_data=None,
    norm=False,
    framerate=0.5,
    figsize=[18, 8],
    col_pos=1,
):
    """
    This function creates an animated gif with the time series plots based on the many raster
    data over time.
    Inputs
    ------
    shp_path: str
        String with the path to the shapefile.
    raster_paths: list of lists
        This parameter is a list such that each element is a list of strings with the paths to
        the raster files. This list represents a set of some type of raster layer over time.
    save_path: str
        The current path where the file will be saved.
    region: str
        Name of the region associated to one row of the shapefile. This region should be in the
        second column of the shapefile.
    title: str
    labels: list of str
        Since each element of raster_paths represents some raster layer, we need to label them
        in the animation. The element labels[i] is the label to raster_paths[i].
    extra_data: list of float 1D ndarray
        Each element of this list is an array with data to plot together with the raster data.
        Each row of the array represents the value in a specific date. The size of the array
        should match the number of raster files of each kind.
    norm: bool
        If the data is bad scaled, use this to normalize the values.
    framerate: float
        Animation speed.
    figsize: list
        Canvas size.
    col_pos: int
        Number of the column with the region names. Default is 1 (the second column).
    """

    # Any value passed to extra_data must be a list.
    if extra_data is not None and type(extra_data) != list:
        msg = 'Error, extra_data must be a list.'
        sys.exit(msg)

    # Create dictionary such that each element is a time series (as a Numpy array).
    data = {}
    L = len(raster_paths)
    for i in range(L):
        array, dates = time_series(
            shp_path, raster_paths[i], region, plot=False, col_pos=col_pos
        )
        # Normalize data if requested.
        if norm:
            data[i] = array / np.linalg.norm(array)
        else:
            data[i] = array

    # Save each time series.
    if extra_data is not None:
        E = len(extra_data)
    num_days = len(dates)
    filenames = []
    for d in range(1, num_days):
        fig = plt.figure(figsize=figsize)
        for i in range(L):
            data_cp = data[i].copy()
            data_cp[d:] = np.nan
            plt.plot(data_cp, label=labels[i], linewidth=3)
        if extra_data is not None:
            for i in range(E):
                data_cp = extra_data[i].copy()
                data_cp[d:] = np.nan
                plt.plot(data_cp, label=labels[i + L], linewidth=3)
        plt.grid()
        plt.legend(loc='upper left')
        plt.title(title + dates[d])
        plt.xticks(visible=False)
        plt.savefig('fig' + str(d) + '.png')
        filenames.append('fig' + str(d) + '.png')
        plt.close(fig)

    # Create animation.
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(save_path + 'curve.gif', images, duration=framerate)

    # Remove image files.
    for filename in filenames:
        exists = os.path.isfile(filename)
        if exists:
            os.remove(filename)

    return


def time_series_map(map_df, df, save_path, title, framerate=0.5, cmap='Blues'):
    """
    This function creates an animated gif with the colored shapefile evolution based on
    the given dataframe with the region values over time.
    To use this function properly, the index of the shapefile 'shp' and the dataframe 'df'
    must agree. Usually the indexes are the names of the regions of interest. The columns labels
    of df are supposed to be the dates (as timestamps) and the rows are the regions.
    Inputs
    ------
    map_df: shapefile
        Shapefile of interest.
    df: dataframe
        Dataframe with the regions as index, columns as timestamps, and the values to show in the map.
    save_path: str
        The current path where the file will be saved.
    title: str
    framerate: float
    cmap: str
    """

    # Join the shapefile and the dataframe.
    merged = map_df.join(df)

    # Search for the global maximum of df. We do this to fix the min and max of the colorbar choropleth map.
    n = merged.shape[1]
    global_max = -np.inf
    global_min = np.inf
    for i in range(map_df.shape[1], n):
        col_name = merged.columns[i]
        current_max = max(merged[col_name])
        current_min = min(merged[col_name])
        if current_max > global_max:
            global_max = current_max
        if current_min < global_min:
            global_min = current_min

    # Create and save figures.
    filenames = []
    for i in range(map_df.shape[1], n):
        date = merged.columns[i]
        # Create figure and axes for Matplotlib.
        fig, ax = plt.subplots(1, figsize=(14, 10))
        # Create the map.
        merged.plot(
            column=date, cmap=cmap, linewidth=0.8, ax=ax, edgecolor='0.8'
        )
        ax.axis('off')
        current_title = (
            title
            + str(date.year)
            + '-'
            + str(date.month)
            + '-'
            + str(date.day)
        )
        ax.set_title(
            current_title, fontdict={'fontsize': '25', 'fontweight': '3'}
        )
        ax.annotate(
            'Source: FioCruz',
            xy=(0.05, 0.05),
            xycoords='figure fraction',
            horizontalalignment='left',
            verticalalignment='top',
            fontsize=12,
            color='#555555',
        )
        # Set colorbar.
        sm = plt.cm.ScalarMappable(
            cmap=cmap, norm=plt.Normalize(vmin=global_min, vmax=global_max)
        )
        # Empty array for the data range.
        sm._A = []
        # Add the colorbar to the figure.
        cbar = fig.colorbar(sm, fraction=0.02)
        # Save figure.
        fig.savefig('fig' + str(i) + '.png', dpi=80)
        # Save filename.
        filenames.append('fig' + str(i) + '.png')
        # Close figure.
        plt.close(fig)

    # Make animation.
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(save_path + 'map.gif', images, duration=framerate)

    # Remove image files.
    for filename in filenames:
        exists = os.path.isfile(filename)
        if exists:
            os.remove(filename)

    return
