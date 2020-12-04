import os

from stompy.grid import unstructured_grid
from stompy.spatial import field

##

bathy_dir="../../../bathy"
bathy_fn=os.path.join(bathy_dir,'compiled-dem-20201201-1m.tif')

dem=field.GdalGrid(bathy_fn)

##

grid_dir="../../../grid"

grid_fn=os.path.join(grid_dir,'quad_tri_v18frontcc-edit17.nc')

g=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)

g.renumber()

# Simplest option:
#   Put bathy on nodes, just direct sampling.

z_node=dem( g.nodes['x'] )
g.add_node_field('node_z_bed',z_node,on_exists='overwrite')

g.write_ugrid('pesca_butano_v00_w_bathy.nc',overwrite=True)

