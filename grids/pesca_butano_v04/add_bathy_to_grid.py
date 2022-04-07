import os,sys
import numpy as np
from stompy.grid import unstructured_grid
from stompy.spatial import field, wkb2shp,linestring_utils
from stompy import utils
import stompy.model.delft.io as dio
import matplotlib.pyplot as plt

##

bathy_dir="../../../bathy"
bathy_asbuilt_fn=os.path.join(bathy_dir,'compiled-dem-asbuilt-20210920-1m.tif')
bathy_existing_fn=os.path.join(bathy_dir,'compiled-dem-existing-20210920-1m.tif')


##
gen_weirs=True
gen_grids=True
dems= [
    (bathy_asbuilt_fn,'asbuilt'),
    (bathy_existing_fn,'existing')
]


if gen_grids:
    grid_dir="../../../grid"
    grid_fn=os.path.join(grid_dir,'quad_tri_v21-edit11.nc')
    g=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)
    g.renumber()
    
if gen_weirs:
    lines=wkb2shp.shp2geom('line_features.shp')

for dem_fn, name in dems:
    if not os.path.exists(dem_fn):
        print("----  DEM file %s doesn't exist ----"%dem_fn)
        continue
    print("Loading DEM for %s"%name)
    dem=field.GdalGrid(dem_fn)

    if gen_weirs:
        print("Generating fixed weirs")
        fixed_weir_fn="fixed_weirs-%s.pliz"%name
        fixed_weirs=[] # suitable for write_pli
        dx=5.0 # m. discretize lines at this resolution
        for i in range(len(lines)):
            feat=lines[i]
            if feat['type']!='fixed_weir': continue

            print(f"Processing levee feature {feat['name']}")
            xy=np.array(feat['geom'])
            xy=linestring_utils.upsample_linearring(xy,dx,closed_ring=False)
            z=dem(xy)
            fixed_weirs.append( (feat['name'],
                                 np.c_[xy,z,0*z,0*z]))    
        dio.write_pli(fixed_weir_fn,fixed_weirs)

    if gen_grids:
        print("Setting bathymetry for %s"%name)

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

if gen_grids:
    plt.figure(1).clf()
    #at.grid.plot_edges(lw=0.4,color='k')
    g.plot_edges(lw=0.7,color='k',alpha=0.5)

    g.plot_cells(labeler='id',alpha=0.2,centroid=True)
    g.plot_edges(labeler='id',label_jitter=0.5)
    g.plot_nodes(labeler='id',label_jitter=0.5)

