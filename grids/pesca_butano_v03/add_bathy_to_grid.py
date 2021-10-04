import os
import numpy as np
from stompy.grid import unstructured_grid
from stompy.spatial import field
from stompy import utils

##

bathy_dir="../../../bathy"
bathy_asbuilt_fn=os.path.join(bathy_dir,'compiled-dem-asbuilt-20210920-1m.tif')
bathy_existing_fn=os.path.join(bathy_dir,'compiled-dem-existing-20210928-1m.tif')

##

grid_dir="../../../grid"
grid_fn=os.path.join(grid_dir,'quad_tri_v21-edit05.nc')
g=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)
g.renumber()

##
for dem_fn, name in [ (bathy_asbuilt_fn,'asbuilt'),
                      (bathy_existing_fn,'existing') ]:
    print("Setting bathymetry for %s"%name)
    if not os.path.exists(dem_fn):
        print("----  DEM file %s doesn't exist ----"%dem_fn)
        continue
    dem=field.GdalGrid(dem_fn)

    if 0: # Simplest option:
        #   Put bathy on nodes, just direct sampling.
        z_node=dem( g.nodes['x'] )
    if 1: # Bias deep
        name+="_deep"
        # Maybe a good match with bedlevtype=5.
        # BLT=5: edges get shallower node, cells get deepest edge.
        # So extract edge depths (min,max,mean), and nodes get deepest
        # edge.

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

        z_node=np.zeros(g.Nnodes())
        for n in utils.progress(range(g.Nnodes())):
            # This is the most extreme bias: nodes get the deepest
            # of the deepest points along adjacent edgse
            z_node[n]=edge_data[g.node_to_edges(n),0].min()
        
    g.add_node_field('node_z_bed',z_node,on_exists='overwrite')
    g.write_ugrid(f'pesca_butano_{name}_bathy.nc',overwrite=True)

    del dem



