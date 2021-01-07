import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

## 
# Match up with a bit of the UCB model period
model=pesca_base.PescaButano(run_start=np.datetime64("2012-04-20 00:00"),
                             run_stop=np.datetime64("2012-04-22 00:00"),
                             run_dir="run_tide_test-v06")

model.mdu

model.write()
model.partition()
model.run_simulation()

## -------

# model=pesca_base.PescaButano.load("run_tide_test")
# 
# his_ds=xr.open_dataset(model.his_output())
# 
# # Load the ESA dataset:
# esa_waterlevel=xr.open_dataset("../calibration/esa_compiled_waterlevel.nc")
# 
# ##
# import stompy.model.data_comparison as dc
# 
# predicted_lag1=his_ds['waterlevel'].isel(stations=np.nonzero( his_ds['station_name'].values==b'lag1' )[0][0])
# predicted_mm=his_ds['waterlevel'].isel(stations=np.nonzero( his_ds['station_name'].values==b'mid_mouth' )[0][0])
# 
# observed=esa_waterlevel['waterlevel'].assign_coords(label="ESA compiled obs.")
# observed.time.values -= np.timedelta64(3600,'s')
# 
# predicted_lag1=predicted_lag1.assign_coords(label='Model (lag1)')
# predicted_mm  =predicted_mm.assign_coords(label='Model (mid_mouth)')
# 
# sources=[observed,predicted_lag1,predicted_mm]
# 
# plt.figure(1).clf()
# dc.calibration_figure_3panel(sources,trim_time=True,num=1)
# 
# ## 
# plt.figure(1).clf()
# fig,ax=plt.subplots(num=1)
# ax.plot(predicted.time,predicted,label='Model')
# 
# sel=slice(*np.searchsorted( esa_waterlevel.time.values,
#                             [predicted.time.values[0], predicted.time.values[-1]] ))
# 
# esa_select=esa_waterlevel.waterlevel.isel(time=sel)
# ax.plot(esa_select.time-np.timedelta64(3600,'s'),
#         esa_select,label='ESA compiled\nobservations')
# ax.legend(loc='upper right')
# 
# ax.set_ylabel('water level (m NAVD88)')
# 
# ##
# plt.figure(2).clf()
# plt.plot( esa_waterlevel.time, esa_waterlevel.waterlevel)
# 
# plt.show()
# 
