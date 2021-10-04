# -*- coding: utf-8 -*-
"""
Spyder Editor

This Scipt load an .nc grid 
Write a shapefiles of the Edges and one of w node depth

"""

from stompy.grid import unstructured_grid
import matplotlib.pyplot as plt
from stompy.model.delft import dfm_grid

##
nc_gride='E:/proj/Pescadero/pescadero_model/grids/pesca_butano_v03/pesca_butano_existing_deep_bathy.nc'
#nc_grida='E:/proj/Pescadero/pescadero_model/grids/pesca_butano_v01/pesca_butano_v01_asbuilt_bathy.nc'
out_dir = 'E:/proj/Pescadero/GIS_files'


ge=unstructured_grid.UnstructuredGrid.from_ugrid(nc_gride)
#ga=unstructured_grid.UnstructuredGrid.from_ugrid(nc_grida)

plt.figure(1).clf()
ge.plot_edges(color='k',lw=0.5)
ge.plot_cells(values=ge.cells_area(), cmap='jet')



##

# write just the edges as a shapefile.
ge.write_edges_shp(out_dir+'/Mesh/pesca_butano_v03_existing.shp')
#ga.write_edges_shp(out_dir+'/Mesh/pesca_butano_v01_asbuilt.shp')


plt.figure(3).clf()
ge.plot_nodes(values=ge.nodes['node_z_bed'],cmap='jet',vmin=-10,vmax=5)
#ge.plot_nodes(values=ge.nodes['mesh2d_node_z'],cmap='jet',vmin=-10,vmax=5)
ge.write_nodes_shp(out_dir+'/Mesh/pesca_butano_v03_existing_node_w_depth.shp')
#ga.write_nodes_shp(out_dir+'/Mesh/pesca_butano_v01_asbuilt_node_w_depth.shp')

#%%




