import os

from stompy.grid import unstructured_grid
from stompy.spatial import field

##

bathy_dir="../../../bathy"
# in the future, this has asbuilt in the name
bathy_asbuilt_fn=os.path.join(bathy_dir,'compiled-dem-20201211-1m.tif') 
bathy_existing_fn=os.path.join(bathy_dir,'compiled-dem-existing-20201211-1m.tif')

##

grid_dir="../../../grid"
grid_fn=os.path.join(grid_dir,'quad_tri_v19frontcc-opt-edit00.nc')
g=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)
g.renumber()

##
for dem_fn, name in [ (bathy_asbuilt_fn,'asbuilt'),
                      (bathy_existing_fn,'existing') ]:
    print("Setting bathymetry for %s"%name)
    dem=field.GdalGrid(dem_fn)

    # Simplest option:
    #   Put bathy on nodes, just direct sampling.
    z_node=dem( g.nodes['x'] )
    g.add_node_field('node_z_bed',z_node,on_exists='overwrite')
    g.write_ugrid(f'pesca_butano_v00_{name}_bathy.nc',overwrite=True)

    del dem



