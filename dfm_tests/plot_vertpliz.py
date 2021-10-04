import xarray as xr
import matplotlib.pyplot as plt
import numpy as np


## 

hiss=[
    # starting point.
    # xr.open_dataset('runs/vertpliz00/DFM_OUTPUT_flowfm/flowfm_0000_his.nc')
    # Change VertAdvSal=>4
    # xr.open_dataset('runs/vertpliz01/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'),
    # xr.open_dataset('runs/vertpliz05/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'),
    # xr.open_dataset('runs/vertpliz07/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'), # twitchy
    xr.open_dataset('runs/vertpliz08/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'), 
    # xr.open_dataset('runs/vertpliz09/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'), # also kind of twitchy
    xr.open_dataset('runs/vertpliz10/DFM_OUTPUT_flowfm/flowfm_0000_his.nc'), 
    ]


plt.figure(1).clf()
fig,axs=plt.subplots(2,1,num=1,sharex=True,sharey=True)

for ax,his in zip(axs,hiss):
    his_left=his.isel(stations=0,time=slice(300,None,None))
    ax.imshow(his_left.salinity.values.T,cmap='jet',origin='lower',aspect='auto',
              vmin=0,vmax=32.)

plt.figure(2).clf()
fig,ax=plt.subplots(1,1,num=2)

salts=[ his.isel(stations=0,time=slice(300,None,None))
        for his in hiss]

img=ax.imshow(salts[1].salinity.values.T - salts[0].salinity.values.T,
          cmap='coolwarm',origin='lower',aspect='auto',
          vmin=-2,vmax=2)
plt.colorbar(img)

##


from stompy.grid import multi_ugrid
from shapely import geometry

maps=[
    multi_ugrid.MultiUgrid('runs/vertpliz08/DFM_OUTPUT_flowfm/flowfm_*_map.nc',cleanup_dfm=True),
    multi_ugrid.MultiUgrid('runs/vertpliz09/DFM_OUTPUT_flowfm/flowfm_*_map.nc',cleanup_dfm=True),
    ]

plt.figure(3).clf()
fig,axs=plt.subplots(len(maps)+1,1,sharex=True,sharey=True,num=3)

tran_line=geometry.LineString( [[0,50],[600,50]] )

cells=np.nonzero(m.grid.select_cells_intersecting(tran_line))[0]
cc=m.grid.cells_center()[cells]
cells=cells[ np.argsort(cc[:,0]) ]

salts=[m['mesh2d_sa1'].isel(time=20).values[cells,:]
       for m in maps]

for salt,ax in zip(salts,axs):
    ax.imshow(salt.T, aspect='auto',
              cmap='jet',vmin=0,vmax=40,origin='lower')
    
names=[ m.paths[0].split('/')[1]
        for m in maps]
names.append("B-A")


for ax,name in zip(axs,names):
    ax.text(0.95,0.02,name,
            ha='right',color='w',
            transform=ax.transAxes)
    
axs[-1].imshow((salts[1]-salts[0]).T,aspect='auto',
               cmap='coolwarm',vmin=-1,vmax=1,origin='lower')

