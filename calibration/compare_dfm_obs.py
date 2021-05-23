# -*- coding: utf-8 -*-
"""
Created on Tue May 11 12:29:55 2021

@author: smunger
"""
import os
import xarray as xr
import numpy as np
import pandas as pd
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import matplotlib.pyplot as plt
import data_comparison_SM as dc  # this is in E:\proj\Pescadero\User\Sophie\scrips

#%% Load data

run_name ="run_tide_test-v09"
run_desc = 'This run simple gate with QCM values, no adjustment'

odir ='E:/proj/Pescadero/Model_Runs/Testing/'
figure_dir = 'E:/proj/Pescadero/Model_Runs/Figures/'

#Load Model
model=pesca_base.PescaButano.load(odir+run_name)
his_ds=xr.open_dataset(model.his_output())

# # Dimension stations: 15
# 0: b'pch_up                                                                                                                                                                                                                                                          ',
# 1: b'pch_down                                                                                                                                                                                                                                                        ',
# 2: b'lag1                                                                                                                                                                                                                                                            ',
# 3: b'nmc_down                                                                                                                                                                                                                                                        ',
# 4: b'BC3                                                                                                                                                                                                                                                             ',
# 5: b'ch2                                                                                                                                                                                                                                                             ',
# 6: b'bc1                                                                                                                                                                                                                                                             ',
# 7: b'nck                                                                                                                                                                                                                                                             ',
# 8: b'bbr                                                                                                                                                                                                                                                             ',
# 9: b'bbrch                                                                                                                                                                                                                                                           ',
# 10: b'pc3                                                                                                                                                                                                                                                             ',
# 11: b'nmp                                                                                                                                                                                                                                                             ',
# 12: b'nmc_up                                                                                                                                                                                                                                                          ',
# 13: b'mid_mouth                                                                                                                                                                                                                                                       ',
# 14: b'mouth_thalweg                                                                                                                                                                                                                                                   ']


bml_odir ='E:/proj/Pescadero/data/BML_data/2016/all_concatenated/csv/'

def formatBML(fname):
    df = pd.read_csv(fname)
    df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']])
    df['waterlevel']=df['depth m']
    wll=df.set_index('time')
    bml_ds = xr.DataArray.from_series(wll.waterlevel).assign_coords(label='BML-observed')
    
    return bml_ds

d = {'model_st_nb':[7,6,5,4,10],
     'BML_fname':['NCK_wll_concatenated.csv','BC1_wll_concatenated.csv','CH2_wll_concatenated.csv','BC3_wll_concatenated.csv','PC3_wll_concatenated.csv'],
     'Title':['NCK','BC1','CH2','BC3','PC3']}

df_station = pd.DataFrame(data=d)


# loop to make a figure of subplot with all the comparison stations. 

fig, ax = plt.subplots(5, 1, sharex='col',figsize=(8,16))

for i, row in df_station.iterrows():
    # Load DFM model data
    predicted = (his_ds.waterlevel
                    .sel(stations = row['model_st_nb'])
                    .assign_coords(label='Modeled'))
    
    # Load the BML observations
    fname = row['BML_fname']
    bml_ds = formatBML(bml_odir + fname)
    
    sources=[predicted,bml_ds]
    
    #To include QCM at the NCK station
    if row['Title'] == 'NCK':  
        
        qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc')
        qcm_WL = qcm_ds.calQCM_lagoon_WL.assign_coords(label='NCK QCM')
        
        sources=[predicted,bml_ds,qcm_WL]


    
    dc.calibration_axe_1panel (sources,row['Title'],ax[i], trim_time=True,num=1)
    
    
    print(row['Title'])

# Print run info
fig.text(0.5, 0.98, run_name,fontsize=16,horizontalalignment='center')
fig.text(0.5, 0.95, run_desc,fontsize=10,horizontalalignment='center')

plt.show()

fig.savefig(figure_dir+run_name+'.png',dpi=200 )


#%% Old stuff


