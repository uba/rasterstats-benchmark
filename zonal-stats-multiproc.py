# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import itertools
import multiprocessing

import matplotlib.pyplot as plt
from utils import create_image, create_random_circles, Timer
import numpy as np

from affine import Affine
from rasterstats import zonal_stats

# Define geo extent
llx = -75.0; lly = -35.50; urx = -34.0; ury = 5.54
extent = [llx, lly, urx, ury]

# Define resolution
resolution = 2.0 # km

# Create image
image = create_image(extent, resolution, driver='MEM')

# Get Affine object in order to run zonal_stats
aff = Affine.from_gdal(*image.GetGeoTransform())

# Extract values
values = image.ReadAsArray()

# Get no-data value
nodata = image.GetRasterBand(1).GetNoDataValue()

# User-defined statistics example
def model(x):
    value = np.max(x) - np.min(x)
    if np.ma.is_masked(value):
        value = None
    return value

def chunks(data, n):
    """Yield successive n-sized chunks from a slice-able iterable."""
    for i in range(0, len(data), n):
        yield data[i:i+n]

def compute_stats_partial(geoms):
    #  Create WKT representation for each polygon
    wkts = []
    for g in geoms:
        wkts.append(g.ExportToWkt())

    # Compute stats for each polygon
    stats = zonal_stats(wkts, values, stats=['min', 'max', 'count', 'std'], affine=aff,
                        nodata=nodata, raster_out=False, prefix='', add_stats={'model' : model}, geojson_out=True)
    return stats

if __name__ ==  '__main__':

    # Create random geometries
    geoms = create_random_circles(extent, min=0.5, max=30.0, n=32000)

    # Create a process pool using all cores
    cores = multiprocessing.cpu_count()
    p = multiprocessing.Pool(cores)

    # Parallel map
    with Timer():
        stats_lists = p.map(compute_stats_partial, chunks(geoms, cores))

    # Flatten to a single list
    stats = list(itertools.chain(*stats_lists))
    
    assert len(stats) == len(geoms)

    import json
    result = {'type': 'FeatureCollection', 'features': stats}
    with open('./data/geoms-multiproc.geojson', 'w') as file:
        json.dump(result, file)

