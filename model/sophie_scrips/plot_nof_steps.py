from netCDF4 import Dataset
import matplotlib.pyplot as plt
from stompy.model.delft import dfm_grid
import numpy as np
import xarray as xr
import gdal

nw = 10 # the number of worst cell displayed

var = 'mesh2d_Numlimdt' #'numlimdt'

p_dir = 'E:/proj/Pescadero/Model_runs/Testing'
#f_path = '/run_tide_test-v13/DFM_OUTPUT_flowfm/FlowFM_map.nc'
f_path = '/run_tide_test-v13-DS/Project1.dsproj_data/flowfm/output/FlowFM_map.nc'
nc_file = p_dir + f_path

dta_grid = dfm_grid.DFMGrid(nc_file)
xy = dta_grid.cells_center()
#nc = Dataset(nc_file)
nc = xr.open_dataset(nc_file)

numlim = nc[var].isel(time=-1)
fig,ax = plt.subplots(1,1,figsize=(10,8))
coll = dta_grid.plot_cells(values=numlim, ax=ax, clim=[0,100],
                           edgecolor='none')

cbar = fig.colorbar(coll,label='Number of Times Limiting')
bad_cells = numlim > 100

plt.plot(xy[bad_cells][:,0], xy[bad_cells][:,1], 'o', markersize=60,
         markerfacecolor='none')

# pass to labeler: idx is the cell index, record is the
# structure array for the cell.
def label_numlim(idx,record):
    return "%d"%numlim.values[idx]

# Plot just the bad cells, add label with numlim values

coll2 = dta_grid.plot_cells(values=numlim, ax=ax, clim=[0,100],
                           edgecolor='none',mask=bad_cells,
                           labeler=label_numlim)


# ax.text(xy[bad_cells][1,0], xy[bad_cells][1,1],  , size=15 )


plt.show()
