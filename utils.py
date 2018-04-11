# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import time

from matplotlib.patches import CirclePolygon
import numpy as np
from osgeo import gdal, ogr, osr

# Define KM_PER_DEGREE
KM_PER_DEGREE = 40075.16/360.0

# Setup projection and geo-transformation
LatLonWGS84 = osr.SpatialReference()
LatLonWGS84.ImportFromEPSG(4326)

def km2degree(km):
    return km / KM_PER_DEGREE
    
def getGeoT(extent, nlines, ncols):
    resx = (extent[2] - extent[0]) / ncols
    resy = (extent[3] - extent[1]) / nlines
    return [extent[0], resx, 0, extent[3] , 0, -resy]

def create_circle(lon, lat, radius, resolution=64):
    # Build circle
    circle = CirclePolygon((lon, lat), radius, resolution, facecolor='b')
    
    # Get coordinates
    path = circle.get_path()
    transform = circle.get_transform()
    path = transform.transform_path(path)
    
    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for v in path.vertices:
        ring.AddPoint(v[0], v[1])
        
    # Create polygon (from OGR API)
    p = ogr.Geometry(ogr.wkbPolygon)
    p.AddGeometry(ring)
    
    return p

def create_random_circles(extent, min, max, n):
    # Build random centers and radius
    x = np.random.uniform(low=extent[0], high=extent[2], size=n)
    y = np.random.uniform(low=extent[1], high=extent[3], size=n)
    radius = np.random.uniform(low=km2degree(min), high=km2degree(max), size=n)
    # Create set of circles
    circles = []
    for x, y, r in zip(x, y, radius):
        circles.append(create_circle(x, y, r))

    return circles

def export2file(path, format, geoms):
    # Create output file
    driver = ogr.GetDriverByName(format)
    datasource = driver.CreateDataSource(path)

    # Create spatial layer
    layer = datasource.CreateLayer('', LatLonWGS84, ogr.wkbPolygon)
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

    # Generate identifiers
    ids = range(0, len(geoms))
    
    # Export each geometry
    for c, i in zip(geoms, ids):
        # Build feature (id + geom)
        f = ogr.Feature(layer.GetLayerDefn())
        f.SetField('id', i)
        f.SetGeometry(c)
        # Add to spatial layer
        layer.CreateFeature(f)

def create_image(extent, resolution, path='', driver='MEM'):
    # Compute grid dimension
    sizex = int(((extent[2] - extent[0]) * KM_PER_DEGREE) / resolution)
    sizey = int(((extent[3] - extent[1]) * KM_PER_DEGREE) / resolution)

    # Create data
    array = np.random.uniform(0.0, 1024.0, size=(sizey, sizex))

    # Get memory driver
    driver = gdal.GetDriverByName(driver)

    # Create grid
    grid = driver.Create(path, sizex, sizey, 1, gdal.GDT_Float32)
    grid.GetRasterBand(1).SetNoDataValue(0.0)
    grid.GetRasterBand(1).Fill(0.0)

    # Setup projection and geo-transformation
    grid.SetProjection(LatLonWGS84.ExportToWkt())
    grid.SetGeoTransform(getGeoT(extent, grid.RasterYSize, grid.RasterXSize))

    # Write data
    grid.GetRasterBand(1).WriteArray(array)

    return grid

class Timer():
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print('Time:', time.time() - self.start)
