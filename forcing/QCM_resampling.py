# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:55:52 2021

@author: smunger
"""
import os
import xarray as xr
import numpy as np
import pandas as pd

import numpy as np
from pylab import date2num as d2n

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.interpolate import splev, splrep



qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc')
outdir = 'E:/proj/Pescadero/pescadero_model/forcing/'

#%% test different interpolation methods for a small slice of time

qcm_wl = qcm_ds.z_ocean.sel(time=slice('2016-10-13','2016-10-19' )).to_series()
y = qcm_wl.values
x = qcm_wl.index
x_day = d2n(x)

# new time vector
xnew = np.arange('2016-10-13', '2016-10-19',np.timedelta64(5,'m'), dtype='datetime64') # new time vector
xnew_day = d2n(xnew)


f = interp1d(x_day, y)
f2 = interp1d(x_day, y, kind='cubic')
f3 = interp1d(x_day, y, kind='quadratic')
spl = splrep(x_day, y)
yspl = splev(xnew_day, spl) # spline


fig, ax = plt.subplots()
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

# s=0 no smoothing. Gives the best fit I think. 

#%% Apply the spline to the entire record and save it in the csv file

qcm_wl = qcm_ds.z_ocean.to_series()
y = qcm_wl.values
x = qcm_wl.index
x_day = d2n(x)

xnew = np.arange(x[0], x[-1],np.timedelta64(6,'m'), dtype='datetime64') # at 6 minutes intervals. 
xnew_day = d2n(xnew)

spl = splrep(x_day, y)
qcm_wl_interp = splev(xnew_day, spl)

plt.plot(x, y, 'ko', xnew, qcm_wl_interp , 'r')
plt.legend(['data', 'Spline'], loc = 'best')

# Let's write in in a cvs for now since it's just a time serie

wl_serie = pd.Series(data=qcm_wl_interp, index=xnew)

wl_serie.to_csv(outdir+'QCM_WL_Interp.csv',header=['waterlevel'], index_label='time')







