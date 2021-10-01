# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 16:43:07 2021

@author: smunger
"""
import pandas as pd
from stompy import utils
import numpy as np
import xarray as xr
from pylab import date2num as d2n
import matplotlib.pyplot as plt
from scipy.interpolate import splev, splrep


#%% load QCM output - reformat in xarray and save in netCDF --> add in the other flow source and save in metric

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

qcm['seepage']= qcm['Modeled seepage'] * 0.02831685 # from ft3/s to m3/s
# evapotranspiration convert form ft3/s to m3/s
qcm['evapotr']= qcm['Modeled ET'] * 0.02831685
qcm['wave_overtop']= qcm['Modeled wave overtopping'] * 0.02831685 # from ft3/s to m3/s

ds=xr.Dataset.from_dataframe(
    qcm[ ['time','z_ocean','z_thalweg','w_inlet','seepage','evapotr','wave_overtop','obs_lagoon_WL','calQCM_lagoon_WL']]
    .set_index('time'))


ds=ds.assign_attrs({'datum':'NAVD88',
                    'waterlevel':'m',
                    'flow':'m3/s',
                    'time_zone':'UTC'})


out_file = 'E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021_wsinks.nc'
ds.to_netcdf(path=out_file)

#%% Load the netCDF file and reformat to use as input in dflow with the proper unit and sign. Save in csv.

qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021_wsinks.nc')

outdir = 'E:/proj/Pescadero/Model_Runs/Testing/run_tide_test_v16F-DS/cvs_files'

time_start = '2016-10-25'
time_stop = '2016-11-09' 

grid_area= 1940000 # m2


qcm_df = qcm_ds.sel(time=slice(time_start,time_stop )).to_dataframe()

qcm_df.to_csv(outdir+'z_ocean.csv',columns=['z_ocean'])
qcm_df.to_csv(outdir+'z_thalweg.csv',columns=['z_thalweg'])
qcm_df.to_csv(outdir+'w_inlet.csv',columns=['w_inlet'],na_rep='0' ) # replace NaN with 0

# the seepage has to be absolute value. Plus remove value < 0 seepage will always be from lagoon to ocean
qcm_df['seepage_abs']=qcm_df['seepage']*-1
qcm_df.loc[qcm_df['seepage_abs'] < 0,'seepage_abs'] = 0 
qcm_df.to_csv(outdir+'seepage_abs.csv',columns=['seepage_abs'])


qcm_df.to_csv(outdir+'wave_overtop.csv',columns=['wave_overtop'])


# Evapotranspiration is in m3/s need mm/day per area
# Values are already [-]. Negative rainfall --> evaporation
# /grid_area*1000 --> m3 to mm
# *3600 --> s to hour
qcm_df['evapotr_mmhour']=qcm_df['evapotr']/grid_area*1000*3600

qcm_df.to_csv(outdir+'evapotr.csv',columns=['evapotr_mmhour'])

#%%
# Make the file with the interpolated WL of the QCM

qcm_wl = qcm_ds.z_ocean.to_series()
y = qcm_wl.values
x = qcm_wl.index
x_day = d2n(x)

xnew = np.arange(x[0], x[-1],np.timedelta64(6,'m'), dtype='datetime64')
xnew_day = d2n(xnew)

spl = splrep(x_day, y)
qcm_wl_interp = splev(xnew_day, spl)

plt.plot(x, y, 'ko', xnew, qcm_wl_interp , 'r')
plt.legend(['data', 'Spline'], loc = 'best')

# Let's write in in a cvs for now since it's just a time serie

wl_serie = pd.Series(data=qcm_wl_interp, index=xnew)

wl_serie.to_csv(outdir+'QCM_WL_Interp.csv',header=['waterlevel'], index_label='time')




