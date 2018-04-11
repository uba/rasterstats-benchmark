# -*- coding: utf-8 -*-

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

import matplotlib.pyplot as plt
from utils import create_image

# Define geo extent
llx = -75.0; lly = -35.50; urx = -34.0; ury = 5.54
extent = [llx, lly, urx, ury]

# Define resolution
resolution = 2.0 # km

# Create image
image = create_image(extent, resolution, path='./data/grid.tif', driver='GTiff')

# Show result
plt.imshow(image.ReadAsArray())
plt.show()
