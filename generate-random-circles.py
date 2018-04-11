# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import numpy as np
from utils import create_random_circles, export2file

# Define geo extent
llx = -75.0; lly = -35.50; urx = -34.0; ury = 5.54
extent = [llx, lly, urx, ury]

geoms = create_random_circles(extent, min=0.5, max=30.0, n=32768)
    
# Save to ESRI Shapefile
export2file('./data/circles.shp', 'ESRI Shapefile', geoms)
