# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 09:35:07 2021

@author: smunger
"""
import os
import xarray as xr
import numpy as np
import pandas as pd

import numpy as np
from pylab import date2num as d2n
import matplotlib.pyplot as plt

import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

# run_names =['run_tide_test-v87','run_tide_test-v88','run_tide_test-v89']
# labels = ['1 mouth structure','2 adjacent mouth structures','5 across structures']
#param_list= 'general_structure_discharge'

run_names =['run_tide_test-v95','run_tide_test-v109','run_tide_test-v110','run_tide_test-v113','run_tide_test-v114'   ]
labels = ['Base run', 'new bathy (wider)', 'Crest width=100','deeper QCM','deeper QCm og bathy']
param_list= 'waterlevel'   

odir ='E:/proj/Pescadero/Model_Runs/Testing/'
figure_dir = 'E:/proj/Pescadero/Model_Runs/Figures/comparison/'

fig1, ax1 = plt.subplots()
for run, label in zip(run_names,labels) :
    
    print('Processing '+run)
    
    #Load Model
    model=pesca_base.PescaButano.load(odir+run)
    his_ds=xr.open_dataset(model.his_output())
    
    #thelabel = runs + ' / '+ his_ds.coords['general_structure_id'].values[0].decode('utf8').strip()  
    #his_ds[param_list].sel(general_structures=0).plot(label=thelabel)
    
    his_ds[param_list].sel(stations = 7).plot(label=label)

time_start = his_ds.time[0]
time_stop = his_ds.time[-1]    
qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc')
qcm_WL = qcm_ds.calQCM_lagoon_WL.assign_coords(label='NCK QCM')
qcm_WL.sel(time = slice(time_start, time_stop)).plot(label='QCM', color = 'black')



fname ='E:/proj/Pescadero/data/BML_data/2016/all_concatenated/csv/NCK_wll_concatenated.csv'
df = pd.read_csv(fname)
df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']])
df['waterlevel']=df['depth m']-10.4
wll=df.set_index('time')
bml_ds = xr.DataArray.from_series(wll.waterlevel).assign_coords(label='BML-observed')
bml_ds.sel(time = slice(time_start, time_stop)).plot(label='BML, NCK', color = 'black',ls='--')

ax1.legend()
ax1.set_title(param_list)

#%%

run_names =['run_tide_test-v91','run_tide_test-v80']
labels = ['var friction','constant friction']
param_list= 'general_structure_discharge'


odir ='E:/proj/Pescadero/Model_Runs/Testing/'
figure_dir = 'E:/proj/Pescadero/Model_Runs/Figures/comparison/'

fig1, ax1 = plt.subplots()
for run, label in zip(run_names,labels) :
    
    print('Processing '+run)
    
    #Load Model
    model=pesca_base.PescaButano.load(odir+run)
    his_ds=xr.open_dataset(model.his_output())
    

    his_ds[param_list].sel(general_structures=0).plot(label=label)
    

ax1.legend()
ax1.set_title(param_list)






#------------------------------------

# fname='E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v52/roughness.xyz'
# data = pd.read_csv(fname, sep=" ", names = ['lat','lon','manning'])


# ds = xr.Dataset(data)

# ds.set_coords(("lat", "lon"))
# ds.set_dims('y','x','m')


# ds.plot.scatter(x='lon', y ='lat', hue='manning')




