import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os

## 
run_dir="runs/vertpliz11"
map_ds=xr.open_dataset(os.path.join(run_dir,'DFM_OUTPUT_flowfm','flowfm_map.nc'))

##

# Shows up with 10 layers.

