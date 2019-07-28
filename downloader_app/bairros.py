import rasterio
import rasterio.plot
import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
import shapely
from rasterstats import zonal_stats
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np


def extract_shp_boundingbox(shp_filename):
    """
    Given a shapefile dataset_map, this function extracts the coordinates defining the bounding box of the shapefile.

    Inputs
    ------
    dataset_map: shapefile

    Outputs
    -------
    min_x, max_x, min_y, max_y: floats
        (min_x, max_y) is the upper left point and (max_x, min_y) is the bottom right point.
    """

    min_x = np.inf
    max_x = -np.inf
    min_y = np.inf
    max_y = -np.inf

    # Load shapefile.
    dataset_map = gpd.read_file(shp_filename)

    g = [i for i in dataset_map.geometry]

    for h in g:
        if type(h) == shapely.geometry.polygon.Polygon:
            all_coords = mapping(h)["coordinates"]
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
                all_coords = mapping(i)["coordinates"]
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

    return min_x, max_x, min_y, max_y


def zonal_means(shp_filename, raster_filename):
    """
    Given a shapefile and a raster, this function computes the mean of the raster pixel inside each poylgon. The
    original shapefile must have a column called 'BAIRRO' with the borough names. Additionally, the polygons with means
    equal to None receive the overall mean with respect to the other polygons.

    This function uses the column 1 of dataset_map (the shapefile) to extract the borough names. Be sure that this is
    the right column before anything.

    Inputs
    ------
    shp_filename: str
        String with the shapefile filename.
    raster_filename: str
        String with the raster filename.

    Outputs
    -------
    z_means: dataframe
        A dataframe with the means of the boroughs.
    """

    # Load statistics.
    z_stats = zonal_stats(shp_filename, raster_filename, stats="count mean", nodata=None)

    # Create dictionary with all means.
    dataset_map = gpd.read_file(shp_filename)
    column_name = dataset_map.columns[1]
    overall_mean = 0
    num_zones = len(dataset_map)
    z_means = {}
    for i in range(num_zones):
        z_means[dataset_map[column_name][i]] = z_stats[i]['mean']
        if z_stats[i]['mean'] is not None:
            overall_mean += z_stats[i]['mean']
    overall_mean = overall_mean / num_zones

    # Use the dictionary to create a dataframe.
    z_means = pd.DataFrame({'MEDIAS': z_means})
    for i in range(num_zones):
        # Verify for anomalies and fix them substituting by the overall mean.
        if np.isnan(z_means.iloc[i, 0]) or z_means.iloc[i, 0] < 0:
            z_means.iloc[i, 0] = overall_mean

    return z_means


def raw_plot(shp_filename, raster_filename, cmap='jet'):
    """
    This function plots both layers of raster and shapefile in a single image.

    Inputs
    ------
    shp_filename: str
        String with the shapefile filename.
    raster_filename: str
        String with the raster filename.
    cmap: str
        String for the colormap.
    """

    dataset_map = gpd.read_file(shp_filename)
    with rasterio.open(raster_filename) as dataset:
        array = dataset.read()[0, :, :]
        fig, ax = plt.subplots(figsize=(15, 15))
        rasterio.plot.show(dataset, ax=ax, cmap=cmap)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=np.max(array), vmax=np.min(array)))
        sm._A = []
        cbar = fig.colorbar(sm, fraction=0.028)
        dataset_map.plot(ax=ax, facecolor='none', edgecolor='black')
        return


def zonal_plot(shp_filename, z_means, cmap='jet'):
    """
    Given a shapefile dataset_map and dataframe z_means from some raster data, this function merges the map with the
    information from the means and makes a plot. The image is saved to the disk with the name 'map_image.png'.

    This function uses the column 1 of dataset_map to make the join between the datasets. Be sure that this column is
    adequate to perform this operation.
    """

    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
        """
        Given a colormap cmap and a interval contained in [0,1], this function truncates the colormap to the interval
        with n points.
        """

        new_cmap = colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
            cmap(np.linspace(minval, maxval, n)))
        return new_cmap

    # Load shapefile.
    dataset_map = gpd.read_file(shp_filename)
    # Merge the shapefile with the dataframe of the means obtained from the raster data.
    column_name = dataset_map.columns[1]
    merged = dataset_map.set_index(column_name).join(z_means)
    # Set a variable that will call whatever column we want to visualise on the map.
    variable = 'MEDIAS'
    # Convert column of interest to numeric type.
    merged[variable] = pd.to_numeric(merged[variable])
    # Set the range.
    vmin, vmax = min(merged[variable]), max(merged[variable])
    # Make the truncation.
    cmap = plt.get_cmap(cmap)
    new_cmap = truncate_colormap(cmap, 0.4, 1.0)
    # Create figure and axes for Matplotlib.
    fig, ax = plt.subplots(1, figsize=(18, 8))
    # Create map.
    merged.plot(column=variable, cmap=new_cmap, linewidth=0.8, ax=ax, edgecolor='0.8')
    # Remove the axis.
    ax.axis('off')
    # Add a title.
    ax.set_title('TEMPERATURA MÉDIA POR BAIRRO', fontdict={'fontsize': '25', 'fontweight': '3'})
    # Create an annotation for the data source.
    ax.annotate('Fonte: FioCruz',
                xy=(0.1, .08),
                xycoords='figure fraction',
                horizontalalignment='left',
                verticalalignment='top',
                fontsize=12,
                color='#555555')
    # Create colorbar as a legend.
    sm = plt.cm.ScalarMappable(cmap=new_cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # Empty array for the data range.
    sm._A = []
    # Add the colorbar to the figure.
    cbar = fig.colorbar(sm)
    # Save image.
    fig.savefig("map_image.png", dpi=300)

    return


def time_series(shp_filename, raster_filename_list, bairro, plot=False):
    """
    Given a shapefile, a list of raster files and a borough name, this function plots the time series of the raster data
    relative to the specific borough.

    Inputs
    ------
    shp_filename: str
    raster_filename: list
        List of strings with all raster filenames of interest.
    bairro: str
        Name of the borough of interest.
    plot: bool
        If True (default is False), then the time series is plotted.

    Outputs
    -------
    t_series: array
        Each t_series[i] is the the mean of the ith raster with respect to the borough.
    dates: list
        List with the corresponding dates.
    """

    # Create variables.
    num_files = len(raster_filename_list)
    t_series = np.zeros(num_files)
    i = 0
    dates = []

    for raster_filename in raster_filename_list:
        z_means = zonal_means(shp_filename, raster_filename)
        current_mean = z_means.loc[bairro].values[0]
        t_series[i] = current_mean
        i += 1
        dates.append(raster_filename.replace('new_', '').replace('.tiff', ''))

    if plot:
        plt.figure(figsize=[16, 5])
        plt.plot(dates, t_series)
        title = 'Time series of ' + bairro
        plt.title(title)
        plt.xticks(rotation=90)
        plt.grid()
        plt.show()

    return t_series, dates
