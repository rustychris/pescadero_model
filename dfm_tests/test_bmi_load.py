# worked on farm with no further imports..
# But will it work with all these imports?
import os # ok
from stompy import utils # ok
import numpy as np # ok

# from stompy.model import hydro_model # no
#from stompy.model.delft import dflow_model
# from stompy.grid import unstructured_grid # no!

# after a lot of bisection, appears that gdal and netCDF4
# are both sources of conflict.

# from osgeo import ogr,osr # NO
from shapely import wkt,geometry,wkb,ops # ok
import matplotlib.pyplot as plt # ok
# from stompy.spatial import gen_spatial_index
# ?, proj_utils
# import netCDF4 # NO

## 
import xarray as xr # ok

# import local_config # no, specifically the dfm import
###

###

utils.path("../model") # ok
# import pesca_base




import subprocess, shutil # ok
# from numpy.ctypeslib import ndpointer  # nd arrays
from ctypes import (
    # Types
    c_double, c_int, c_char_p, c_bool, c_char, c_float, c_void_p,
    # Complex types
    # ARRAY, Structure,
    # Making strings
    # Pointering
    POINTER, byref, # CFUNCTYPE,
    # Loading
    # cdll
)

# ----
# Sorting out linking issues
# just ctypes: okay.

import bmi.wrapper

# Resetting rpath on libdflowfm helps.
# Put all the non-system libraries in lib-safe.
# That all works fine.
# Turns out that libdflowfm implicitly requires libmetis.so
# so add it with patchelf --add-needed
# And this works!

sim=bmi.wrapper.BMIWrapper(engine="/home/rustyh/src/dfm/delft3dfm_2021.03/lnx64/lib/libdflowfm.so")

# What about here? it's okay here.
import stompy.model.delft.dflow_model as dfm # ?

# This loads everything, 
sim.initialize('../model/data_salt_filling-v05_existing_impaired/flowfm.mdu')

# on farm, this seems to work on the head node, and via srun.
# suggests there is an issue with the longer script, or sometging about
# running in mpi

