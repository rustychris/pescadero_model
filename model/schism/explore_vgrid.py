from stompy.spatial import wkb2shp, linestring_utils
from stompy import utils

## 

feats=wkb2shp.shp2geom("../../grids/pesca_butano_v03/line_features.shp")
g=unstructured_grid.UnstructuredGrid.read_gr3('pesca_butano_existing_deep_bathy_mod3.gr3')

# [N,{x,y}] points from ocean to PC3
thalweg=np.array(feats[ feats['name']=='thalweg_pesc' ][0]['geom'])
thalweg=linestring_utils.resample_linearring(thalweg,5,closed_ring=0)

# 
##

points=thalweg

tri,tsrcs=g.mpl_triangulation(return_sources=True)
tf=tri.get_trifinder()
cells=tf(points[:,0],points[:,1])
coeffs=tri.calculate_plane_coefficients(g.nodes['depth'])

z_interp=coeffs[cells, 0] * points[:,0]  + coeffs[cells, 1] * points[:,1] + coeffs[cells, 2]
z_interp=-z_interp # => elevation

dist=utils.dist_along(thalweg)

## 

eta=1.2*np.ones_like(z_interp)

# parameters of a 
hc=0.1


plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
ax.plot(dist,z_interp,label='bathy')
ax.plot(dist,eta,label='$\eta$')


ax.legend(loc='lower right')
##

