# Read history time series from the various fill-drain
# tests to compare
import os
import six

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from stompy import utils
from stompy.grid import unstructured_grid
import stompy.plot.cmap as scmap
import stompy.model.delft.dflow_model as dfm
turbo=scmap.load_gradient('turbo.cpt')
##
plt.figure(1).clf()
fig,ax=plt.subplots(num=1)

for run_dir in ["run-drainfill-v00",
                "run-drainfill-v01",
                "run-drainfill-v02",
                "run-drainfill-v03" ]:
    his_fn=os.path.join(run_dir,'DFM_OUTPUT_flowfm','flowfm_0000_his.nc')
    his_ds=xr.open_dataset(his_fn)

    stn_idx=np.nonzero( his_ds.station_name.values==b'lag1')[0][0]
    
    ax.plot(his_ds.time, his_ds.waterlevel.isel(stations=stn_idx),
            label=run_dir)

if 1: # Grab BC data from the last one:
    six.moves.reload_module(dfm)
    model=dfm.DFlowModel.load('run-drainfill-v03')
    bcs=model.load_bcs()
    ocean=[bc for bc in bcs if bc['name']=='ocean_bc'][0]
    ocean_data=ocean['data']
    ax.plot(ocean_data.time, ocean_data.stage.isel(node=0),
            color='k',lw=1,ls='--',label='Ocean BC')

ax.legend(loc='upper right')

ax.axhline(0.55,color='k',lw=0.5)

fig.autofmt_xdate()

## 

fig.savefig("compare-fill_drain.png")

##

# Plot the final state of the domain:
map_dss=[xr.open_dataset(fn) for fn in model.map_outputs()]

## 
fig=plt.figure(2)
fig.clf()
fig.set_size_inches([7,9],forward=True)
ax=fig.add_axes([0,0,1,1])
cax=fig.add_axes([0.65,0.6,0.03,0.3])

from matplotlib import cm
gray_clip=scmap.cmap_clip(cm.gray,0.3,0.9)
contours=np.linspace(-1,4,64)

wcolls=[]
zcolls=[]

for map_ds in map_dss:
    g=unstructured_grid.UnstructuredGrid.read_ugrid(map_ds)
    waterdepth=map_ds.waterdepth.isel(time=-1)

    wcolls.append( g.plot_cells(values=waterdepth,mask=waterdepth>0.01,
                                cmap=cm.Blues,ax=ax) )
    #zcolls.append( g.contourf_node_values(map_ds.NetNode_z.values,
    #                                      contours,cmap=gray_clip,
    #                                      zorder=-1,ax=ax))
    zcolls.append( g.plot_cells(color='0.7',ax=ax,zorder=-1) )

ax.axis('tight')
ax.axis('equal')
ax.axis('off')

plt.setp(wcolls,clim=[0,0.5])
plt.colorbar(wcolls[0],label='Water depth',cax=cax)

fig.savefig('drained.png')
