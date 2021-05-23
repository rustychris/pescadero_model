import pandas as pd
from stompy import utils
import numpy as np
import xarray as xr
## 

'''load QCM output - reformat in xarray and save in netCDF'''

qcm_2016_2017=pd.read_csv("E:/proj/Pescadero/data/ESA_QCM/ESA_draft_PescaderoQCM_output_4.28.2021.csv", 
                          skiprows=[0],usecols=range(14),
                          parse_dates=['Date (PST)'])
# some extra rows in the csv
qcm=qcm_2016_2017[ ~qcm_2016_2017['Date (PST)'].isnull() ]


qcm['time']=qcm['Date (PST)'] + np.timedelta64(8,'h')  # Shift to UTC.
# These are both NAVD88, converted ft=>m
# Prefer the modified data when available:
ocean_modified=qcm['Modified Ocean Level (feet NAVD88)']
# Otherwise the observed data.
ocean_level=qcm['Ocean level (feet NAVD88)']
qcm['z_ocean']=0.3048 * ocean_modified.combine_first(ocean_level)
qcm['z_thalweg']=0.3048 * qcm['Modeled Inlet thalweg elevation (feet NAVD88)']
# width
qcm['w_inlet']=0.3048* qcm['Modeled Inlet Width (feet)']
qcm['obs_lagoon_WL'] = 0.3048* qcm['Observed Lagoon Level (feet NAVD88)']
qcm['calQCM_lagoon_WL'] = 0.3048* qcm['Modeled Lagoon Level (feet NAVD88)']


ds=xr.Dataset.from_dataframe(
    qcm[ ['time','z_ocean','z_thalweg','w_inlet','obs_lagoon_WL','calQCM_lagoon_WL']]
    .set_index('time'))


ds=ds.assign_attrs({'datum':'NAVD88',
                    'units':'m', 
                    'time_zone':'UTC'})


out_file = 'E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc'
ds.to_netcdf(path=out_file)























                  skiprows=[0,1,2,3,4],names=["matlab_date","datestr","waterlevel_ft_navd88"])
t=utils.to_dt64(utils.dnum_mat_to_py(df['matlab_date']))
## 
# toss in some rounding to avoid annoying floating point date inaccuracy
df['time_pst']=utils.round_dt64(t,dt=np.timedelta64(60,'s'))
df['time']=df['time_pst']+np.timedelta64(8,'h')

ds=xr.Dataset.from_dataframe(df.loc[:,['time','waterlevel_ft_navd88']].set_index('time'))
ds['waterlevel_orig']=('time',),ds['waterlevel_ft_navd88'].values * 0.3048
ds['time'].attrs['timezone']='UTC'
ds['waterlevel_orig'].attrs['datum']='NAVD88'
ds['waterlevel_orig'].attrs['units']='m'$

##

from stompy.io.local import noaa_coops
start=np.datetime64("2010-07-07")
stop =np.datetime64("2016-06-01")
noaa_monterey=9413450
noaa_sf=9414290

# Check for lags against USGS data and adjust
ds_monterey,ds_sf=[ noaa_coops.coops_dataset(station=station,
                                             start_date=start,
                                             end_date=stop,
                                             days_per_request='M',
                                             cache_dir="../forcing/tides/cache",
                                             products=['water_level'])
                    for station in [noaa_monterey,noaa_sf]]

##

import matplotlib.pyplot as plt

plt.figure(2).clf()
fig,ax=plt.subplots(num=2)

ax.plot( ds_monterey.time, ds_monterey.water_level.isel(station=0),label='NOAA Monterey')
ax.plot( ds_sf.time, ds_sf.water_level.isel(station=0),label='NOAA SF')

ax.plot(ds.time, ds.waterlevel_orig,label='ESA compiled')

ax.plot(ds.time, ds.waterlevel,label='ESA compiled, shifted')
ax.legend(loc='upper right')

##

# Best guess at shifts

shifts=[ (np.datetime64('2012-04-20'),
          np.datetime64('2012-06-06'),
          np.timedelta64(-1,'h'))  ]

dt=np.median(np.diff(ds.time.values))

new_wl=ds.waterlevel_orig.values.copy()

for start,stop,offset in shifts:
    steps=int(np.round(offset/dt))
    start_i,stop_i = np.searchsorted(ds.time.values,[start,stop])
    cut=new_wl[start_i:stop_i].copy()
    new_wl[start_i:stop_i]==np.nan
    new_wl[start_i+steps:stop_i+steps]=cut

ds['waterlevel']=('time',),new_wl
ds['waterlevel'].attrs['description']='Waterlevel with approximate time shifts after comparison tide gauges'

##

#ds.to_netcdf('esa_compiled_waterlevel.nc')

##

plt.figure(1).clf()
plt.plot(ds.time,ds.waterlevel,label='ESA Compiled WSE')
plt.legend(loc='upper right')

plt.ylabel('m NAVD88')

