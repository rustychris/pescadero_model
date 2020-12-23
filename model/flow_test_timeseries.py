import stompy.model.delft.dflow_model as dfm
from stompy.grid import unstructured_grid
import matplotlib.pyplot as plt
##

model=dfm.DFlowModel.load("run/flowfm.mdu")

## 

ds=xr.open_dataset(model.map_outputs()[0])

g=unstructured_grid.UnstructuredGrid.read_ugrid(ds)
c=g.select_cells_nearest([553151., 4124136.],inside=True)

## 
plt.figure(1).clf()
g.plot_edges()

##

eta=ds.s1.isel(nFlowElem=c)

##

plt.figure(2).clf()
plt.plot(eta.time,eta)
