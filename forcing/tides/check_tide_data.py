import numpy as np
import matplotlib.pyplot as plt
import os

from stompy.io.local import noaa_coops
from stompy import utils
import xarray as xr
## 

noaa_monterey=9413450
noaa_sf=9414290

cache_dir="cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# To bracket the WSE data:
start=np.datetime64("2010-07-07")
stop =np.datetime64("2016-06-01")
# To bracket Mathilde's runs:
#start=np.datetime64("2012-04-01")
#stop =np.datetime64("2012-05-30")

ds_monterey,ds_sf=[ noaa_coops.coops_dataset(station=station,
                                             start_date=start,
                                             end_date=stop,
                                             days_per_request='M',
                                             cache_dir="cache",
                                             products=['water_level'])
                    for station in [noaa_monterey,noaa_sf]]
##

plt.figure(1).clf()

fig,ax=plt.subplots(1,1,num=1)

ax.plot( ds_monterey.time,
         ds_monterey.water_level.isel(station=0),
         label='NOAA Monterey')
ax.plot( ds_sf.time,
         ds_sf.water_level.isel(station=0),
         label='NOAA SF')
ax.legend(loc='upper right')

##

lag=utils.find_lag_xr( data=ds_monterey.water_level.isel(station=0),
                       ref=ds_sf.water_level.isel(station=0) )
lag_s=lag/np.timedelta64(1,'s')
print(f"Monterey lags SF by {lag_s:.0f} seconds")

# Monterey lags SF by -3204 seconds
# SF has larger amplitude by maybe 5%.

##

# Verify timing against the in-lagoon WSE data
lagoon_wse=xr.open_dataset("../../calibration/esa_compiled_waterlevel.nc")

##

# Verify a chunk of Megan's data too.
from scipy.io import loadmat
mat=loadmat("../../../data/M.Williams/data_for_dsepulveda/CTD data/octdec2011/NM_ctds.mat")

nm=xr.Dataset()
nm['time']=('time',),utils.to_dt64(utils.dnum_mat_to_py(mat['tz_nm1'].squeeze()))
nm['depth']=('time',),mat['da_nm1'].squeeze()

##

plt.figure(2).clf()
fig,ax=plt.subplots(1,1,num=2)

ax.plot( ds_monterey.time,
         ds_monterey.water_level.isel(station=0),
         label='NOAA Monterey')
ax.plot( ds_sf.time,
         ds_sf.water_level.isel(station=0),
         label='NOAA SF')

ax.plot( lagoon_wse.time, lagoon_wse.waterlevel, label='Lagoon WSE')
ax.plot( nm.time, nm.depth+0.41, label="MW NM1")
ax.legend(loc='upper right')
ax.axis( (734454.5300028515, 734456.2446132009, 0.3449726830137707, 1.8448001794491278))
##

# NM1 vs. ESA:
#  NM1 is clipped on the top, while ESA is not. Assume that ESA came from the
#  ADCP or some other CTD.
#  Phasing is close, with NM1 either the same or lagged a fraction of an hour.

# ESA vs. NOAA SF:
#  During the Oct-Dec 2011 period:
#   ESA maybe 30 minutes later than NOAA
#   Entirely possible that ESA and MW are both an hour late?
#  2012-01-13: ESA looks only slightly lagged relative to
#   NOAA Monterey, and ahead of SF.
#  But when 2012-04-20 comes around, ESA is again lagged about an
#   hour.

# Does Megan's dissertation show good comparisons?
# Figure 2.12, kind of. Just compares to SF.
# 
