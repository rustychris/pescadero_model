# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 10:07:31 2021

@author: smunger
"""
import os
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt





# load BML
fig1, ax1 = plt.subplots()
fname16 ='E:/proj/Pescadero/data/BML_data/2016/water_level/elevationNAVD88/2016_NCK_wll_referenced_concat.csv'
df16 = pd.read_csv(fname16)
df16['time']=pd.to_datetime(df16[['year','month','day','hour','minute','second']])
wll16=df16.set_index('time')

fname17 ='E:/proj/Pescadero/data/BML_data/2017/water_level/elevationNAVD88/2017_NCK_wll_referenced_concat.csv'
df17 = pd.read_csv(fname17)
df17['time']=pd.to_datetime(df17[['year','month','day','hour','minute','second']])
wll17=df17.set_index('time')
# merge the 2016 and 2017 record
bml_df = pd.concat([wll16,wll17])
bml_ds = xr.DataArray.from_series(bml_df.NAVD88).assign_coords(label='BML-observed')
bml_ds.plot(label='BML, NCK', color = 'black')



# Load QCM
qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021_wsinks.nc')
qcm_ds.calQCM_lagoon_WL.plot(label='QCM', color = 'blue',alpha=0.7)

#plt.figure(4).clf()
# load the 2021-2021 record. 
fname20 = 'E:/proj/Pescadero/data/BML_data/2020_2021/waterlevel_processed/NCK_processed.csv'
df20 = pd.read_csv(fname20)

offset = -.2
dtime_off = timedelta(days = 1460.7)
df20['time_offset'] = pd.to_datetime(df20.time)-dtime_off
df20['depth_m_off'] = df20['depth_m']+offset
df_off = df20.set_index('time_offset')
bml20_ds = xr.DataArray.from_series(df_off.depth_m_off).assign_coords(label='BML-2020')
bml20_ds.plot(label='BML 2020, NCK',color='red',alpha=0.7)


ax1.legend()
ax1.grid()