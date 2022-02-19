"""
Compile wind speed, air temperature and relative humidity data for
Pescadero/Butano model.

Source datasets: 
  SFEI wind station compilation
  Megan Williams met station

Air temperature 
"""
import matplotlib.pyplot as plt
import xarray as xr
from scipy.io import loadmat
from stompy.model import data_comparison
import statsmodels.formula.api as smf

import numpy as np
import pandas as pd
from stompy import utils
utils.path("../../model")
import local_config

##
# Load the SFEI data, adjusting to UTC.
dss=[]

for year in [2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]:
    # Downloaded from
    # https://drive.google.com/drive/folders/1MNFXUUs6CaDyacxN5oCmtK_OjMHVQI7f
    ds_year=xr.open_dataset(os.path.join(local_config.data_dir,'sfei_wind',f'SFB_hourly_wind_and_met_data_{year}.nc'))
    ds_year['julian']=('time',),ds_year['time'].values
    ds_year['time']=('time',),( np.timedelta64(8,'h')
                                + np.datetime64(f'{year}-01-01')+np.timedelta64(1,'h')*np.round(24*(ds_year['julian'].values-1)))
    dss.append(ds_year)

ds=xr.concat(dss,dim='time',coords='minimal',data_vars='minimal')
sta_idx=np.nonzero((ds.station_name=='HAF').values)[0][0]
ds_haf=ds.isel(station=sta_idx)

##

# What does Megan's data look like?

met=loadmat(os.path.join(local_config.data_dir,"M.Williams/data_for_dsepulveda/pescadero_estuary/meteorological_station/met_20111027_20120510.mat"))
tz_met=np.squeeze(met['tz_met'])
#met_time=utils.to_dt64(np.squeeze(met['tz_met'])-366)
met_time=utils.matlab_to_dt64(np.squeeze(met['tz_met']))

# Compared to .dat file straight from Campbell logger. Documentation
# says that is in local time
# That gives 2011-10-27 22:42  to  2012-05-10 19:18
# The second CR200 data file starts 2011-10-27 15:42, and is known to
# be local time ish.
# So can assume that the mat file is in UTC.

# Assume that met station reports in weather convention.
# 0 means wind is coming from the north.
# So 270-0=270 gives the math convention angle
ds_met=xr.Dataset()
ds_met['time']=('time',),met_time
ds_met['u']=('time',),np.squeeze(met['ws_mps'])* np.cos(np.squeeze(270-met['wdir_deg'])*np.pi/180.)
ds_met['v']=('time',),np.squeeze(met['ws_mps'])* np.sin(np.squeeze(270-met['wdir_deg'])*np.pi/180.)
t_sel=np.r_[True,np.diff(ds_met.time.values)>np.timedelta64(0)]
ds_met=ds_met.isel(time=t_sel)

## 

if 0:
    plt.figure(1).clf()
    fig,axs=plt.subplots(2,1,num=1,sharex=True)

    axs[0].plot(ds.time,ds['u10'].isel(station=sta_idx),label='U10')
    axs[1].plot(ds.time,ds['v10'].isel(station=sta_idx),label='V10')

    axs[0].plot(ds_met.time, ds_met.u, label='U10 MW')
    axs[1].plot(ds_met.time, ds_met.v, label='V10 MW')

##
if 0:
    # General bias/amplitude/correlation tests to refine timezone and
    # direction conversions
    # reference is the met station data in the lagoon
    u_metrics=data_comparison.calc_metrics(ds_haf['u10'],ds_met['u'],combine=True)
    v_metrics=data_comparison.calc_metrics(ds_haf['v10'],ds_met['v'],combine=True)

    # For U, bias is minimal, lag is less than 10 minutes
    # amplitude is 0.57, which I think is specific to the U component
    print(u_metrics)
    print(v_metrics)

## 
# Fit u_lagoon ~ u_HAF + v_HAF
# Fit v_lagoon ~ u_HAF + v_HAF
ds_comb=data_comparison.combine_sources([ds_haf['u10'],ds_haf['v10'],ds_met['u'],ds_met['v']],
                                        dt=np.timedelta64(1,'h'))
df_comb=ds_comb.to_dataframe().unstack(0) 
df_comb.columns=['haf_u','haf_v','lag_u','lag_v']

# Just linear scaling, no offset
u_mod = smf.ols(formula='lag_u ~ haf_u + haf_v + 0', data=df_comb)
u_res = u_mod.fit()
print(u_res.summary())

v_mod = smf.ols(formula='lag_v ~ haf_u + haf_v + 0', data=df_comb)
v_res = v_mod.fit()
print(v_res.summary())

# Final formulae:
# u_lagoon=0.307*u_haf - 0.517*v_haf
# v_lagoon=0.097*u_haf + 0.673*v_haf

##

# Generate a single csv with the predicted values:
ds_pred=xr.Dataset()
ds_pred['time']=('time',), ds_haf.time.values

u_coeff_u= 0.307
u_coeff_v=-0.517
v_coeff_u= 0.097
v_coeff_v= 0.673

ds_pred['u_wind']=('time',),utils.fill_invalid( (u_coeff_u*ds_haf['u10'] + u_coeff_v*ds_haf['v10']).values )
ds_pred['u_wind'].attrs['units']='m s-1'
ds_pred['u_wind'].attrs['desc']=f'extrapolated wind from ASOS HAF station, {u_coeff_u}*u10 + {u_coeff_v}*v10'

ds_pred['v_wind']=('time',),utils.fill_invalid( (v_coeff_u*ds_haf['u10'] + v_coeff_v*ds_haf['v10']).values )
ds_pred['v_wind'].attrs['units']='m s-1'
ds_pred['u_wind'].attrs['desc']=f'extrapolated wind from ASOS HAF station, {v_coeff_u}*u10 + {v_coeff_v}*v10'

ds_pred['T']=('time',), utils.fill_invalid(ds_haf['Ta'].values)
ds_pred['T'].attrs.update(ds_haf['Ta'].attrs)
ds_pred['rh']=('time',), utils.fill_invalid(ds_haf['rh'].values)
ds_pred['rh'].attrs.update(ds_haf['rh'].attrs)

##
ds_pred.to_netcdf('lagoon-met-updated.nc',mode='w')
