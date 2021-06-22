import os

from stompy.grid import unstructured_grid
from stompy.spatial import field
from stompy import utils

import matplotlib.pyplot as plt
import numpy as np

##
bathy_dir="../../../bathy"
bathy_existing_fn=os.path.join(bathy_dir,'compiled-dem-existing-20210608-1m.tif')
dem=field.GdalGrid(bathy_existing_fn)

# grid_dir="../../../grid"
# grid_fn=os.path.join(grid_dir,'quad_tri_v21-edit05.nc')
# g=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)
# g.renumber()

##

g=unstructured_grid.UnstructuredGrid.read_ugrid('pesca_butano_existing_deep_bathy.nc')



##

alpha=np.linspace(0,1,5)

edge_data=np.zeros( (g.Nedges(),3), np.float64)

# Find min/max/mean depth of each edge:
for j in utils.progress(range(g.Nedges())):
    pnts=(alpha[:,None] * g.nodes['x'][g.edges['nodes'][j,0]] +
          (1-alpha[:,None]) * g.nodes['x'][g.edges['nodes'][j,1]])
    z=dem(pnts)
    edge_data[j,0]=z.min()
    edge_data[j,1]=z.max()
    edge_data[j,2]=z.mean()
##

# This is bedlevtype=5
z_edge=(g.nodes['node_z_bed'][ g.edges['nodes'] ]).max(axis=1)

plt.figure(1).clf()

plt.plot( z_edge, edge_data[:,0], 'g.')
plt.plot( z_edge, edge_data[:,1], 'b.')

