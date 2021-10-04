# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:55:52 2021

@author: smunger
"""
import os
import xarray as xr
import numpy as np
import pandas as pd
from stompy import (xr_utils, utils)

import numpy as np
from pylab import date2num as d2n

import matplotlib.pyplot as plt




qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc')

qcm_ds.calQCM_lagoon_WL.plot(color='r')
qcm_ds.obs_lagoon_WL.plot(color='b')

df = qcm_ds.to_dataframe() # Working in pandas will be easier
df['residual']=df.obs_lagoon_WL - df.calQCM_lagoon_WL # lets look at the residual
df.residual.plot(color='gray')
plt.legend(['Calculated QCM', 'Obs Lagoon', 'residual'], loc = 'best')

norm = df.obs_lagoon_WL.max() - df.obs_lagoon_WL.min()  # normilized against maximum amplitude
df['norm_error'] = df.residual/norm
df.norm_error.plot()  # I don't like it, camouflage areas where error is large

df['percent_error'] = df.residual/df.obs_lagoon_WL
df.percent_error.plot()  # I don't like it, camouflage areas where error is large


# Compare QCM to NOAA BC
# Load currently used BC

# for run 16A - when lagoon is close
fname = 'E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v16A-DS/Original_Files/Ocean_BC_NOAA.csv'
df = pd.read_csv(fname, parse_dates=['Time'], index_col ='Time')

fig, ax = plt.subplots()

qcm_ds.z_ocean.sel(time=slice('2016-10-13','2016-11-19' )).plot(label='QCM_Ocean')
df.WaterLevel_m.plot(label='Current NOAA BC')
ax.legend()


# interpret QCM

qcm_wl = qcm_ds.z_ocean.sel(time=slice('2016-10-13','2016-10-19' )).to_series()
y = qcm_wl.values
x = qcm_wl.index
x_day = d2n(x)

f = interp1d(x_day, y)
f2 = interp1d(x_day, y, kind='cubic')
f3 = interp1d(x_day, y, kind='quadratic')
spl = splrep(x_day, y)
yspl = splev(xnew_day, spl)
xnew = np.arange('2016-10-13', '2016-10-19',np.timedelta64(5,'m'), dtype='datetime64')
xnew_day = d2n(xnew)
fig2, ax2 = plt.subplots()
plt.plot(x, y, 'x', 
         xnew, f(xnew_day), 'b', 
         xnew, f2(xnew_day), 'k.',
         xnew, f3(xnew_day), 'g.', 
         xnew, yspl,'r--')
plt.legend(['data', 'linear', 'cubic','quadratic','spline'], loc = 'best')


#just spline



xnew = np.arange('2016-10-13', '2016-10-19',np.timedelta64(5,'m'), dtype='datetime64')
xnew_day = d2n(xnew)

spls0 = splrep(x_day, y,s=0)
yspls0 = splev(xnew_day, spls0)

spls1 = splrep(x_day, y,s=1)
yspls1 = splev(xnew_day, spls1)


fig3, ax = plt.subplots()
plt.plot(x, y, 'x', 
         xnew, f(xnew_day), 'b', 
         xnew, yspls0, 'r.', 
         xnew,yspls1 , 'k.')
plt.legend(['data', 'linear', 's=0','s=1'], loc = 'best')











# run 13C longer calibration run
fname2 = 'E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v13C/Ocean_BC_NOAA.csv'
df2 = pd.read_csv(fname2, parse_dates=['Time'], index_col ='Time')















fig2, ax2 = plt.subplots()

qcm_ds.z_ocean.sel(time=slice('2016-7-12','2016-7-23' )).plot(label='QCM_Ocean')
df2.WaterLevel_m.plot(label='Current NOAA BC')
ax2.legend()









#%%
# Write the QCM waterlevel data into a csv to import into deltashell
qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021_wsinks.nc')

outdir = 'E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v16A-DS/csv_files/'
time_start = '2016-10-13'
time_stop = '2016-10-19' 
grid_area= 1940000 # m2


qcm_df = qcm_ds.sel(time=slice(time_start,time_stop )).to_dataframe()

qcm_df.to_csv(outdir+'z_ocean.csv',columns=['z_ocean'])
qcm_df.to_csv(outdir+'z_thalweg.csv',columns=['z_thalweg'])
qcm_df.to_csv(outdir+'w_inlet.csv',columns=['w_inlet'],na_rep='0' )

# the seepage has to be absolute value. Plus remove value < 0 seepage will always be from lagoon to ocean
qcm_df['seepage_abs']=qcm_df['seepage']*-1
qcm_df.loc[qcm_df['seepage_abs'] < 0,'seepage_abs'] = 0 
qcm_df.to_csv(outdir+'seepage_abs.csv',columns=['seepage_abs'])


qcm_df.to_csv(outdir+'wave_overtop.csv',columns=['wave_overtop'])


# Evapotranspiration is in m3/s need mm/day per area
# *-1--> negative rainfall
# /grid_area*1000 --> m3 to mm
# *86400 --> s to day 
qcm_df['evapotr_mmday']=qcm_df['evapotr']*-1/grid_area/1000*86400 

qcm_df.to_csv(outdir+'evapotr.csv',columns=['evapotr_mmday'])

