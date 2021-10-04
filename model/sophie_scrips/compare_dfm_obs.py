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
from datetime import datetime, timedelta

run_name ="run_tide_test-v113"
run_desc = 'Grid v03-deep, mouth wider+deeper, QCM adjusted' 
yr = '2016'     

odir ='E:/proj/Pescadero/Model_Runs/Testing/'
figure_dir = 'E:/proj/Pescadero/Model_Runs/Figures/'



#Load Model
# model=pesca_base.PescaButano.load(odir+run_name)
# his_ds=xr.open_dataset(model.his_output())



fname = odir+run_name+'/DFM_OUTPUT_flowfm/flowfm_his.nc'
his_ds=xr.open_dataset(fname)
# f_name= 'E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v13-DS/Project1.dsproj_data/flowfm/output/flowfm_his.nc'
# his_ds=xr.open_dataset(f_name)

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

if yr =='2016':
    bml_odir ='E:/proj/Pescadero/data/BML_data/2016/all_concatenated/csv/'
    
    d = {'model_st_nb':[7,5,4,10],
          'BML_fname':['NCK_wll_concatenated.csv','CH2_wll_concatenated.csv','BC3_wll_concatenated.csv','PC3_wll_concatenated.csv'],
          'Title':['NCK','CH2','BC3','PC3']}

if yr =='2017':
    # bml_odir ='E:/proj/Pescadero/data/BML_data/2017/all_concatenated/csv/'
    
    # d = {'model_st_nb':[7,5,4,10],
    #       'BML_fname':['2017_NCK_wll_concat.csv','2017_CH2_wll_concat.csv','2017_BC3_wll_concat.csv','2017_PC3_wll_concat.csv'],
    #       'Title':['NCK','CH2','BC3','PC3']}
    
    bml_odir ='E:/proj/Pescadero/data/BML_data/2017/water_level/elevationNAVD88/'
    
    d = {'model_st_nb':[7,5,4,10],
          'BML_fname':['2017_NCK_wll_referenced_concat.csv','2017_CH2_wll_referenced_concat.csv',
                       '2017_BC3_wll_referenced_concat.csv','2017_PC3_wll_referenced_concat.csv'],
          'Title':['NCK','CH2','BC3','PC3']}



def formatBML(fname):

    if yr =='2016':
        df = pd.read_csv(fname)
        df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']]) 
        df['waterlevel']=df['depth m']
    # if yr =='2017':
    #     df = pd.read_csv(fname, parse_dates=['dtime'])
    #     df['time']=pd.to_datetime(df['dtime'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    #     df['waterlevel']=df['depth']
    if yr =='2017':
        df = pd.read_csv(fname)
        df['time']=pd.to_datetime(df[['year','month','day','hour','minute','second']])+ timedelta(hours = 8)
        df['waterlevel']=df['NAVD88']
    
    wll=df.set_index('time')
    bml_ds = xr.DataArray.from_series(wll.waterlevel).assign_coords(label='BML-observed')
    
    return bml_ds



df_station = pd.DataFrame(data=d)


# loop to make a figure of subplot with all the comparison stations. 

fig, ax = plt.subplots(4, 1, sharex='col',figsize=(8,16))

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

# fig1, ax1 = plt.subplots()
# his_ds.cross_section_discharge.sel(cross_section = 1).plot()
# plt.show()

# fig1, ax = plt.subplots()
# his_ds.waterlevel.sel(stations = 14).plot(label='WL at mouth thalweg')
# his_ds.waterlevel.sel(stations = 13).plot(label='WL at mid-mouth')
# qcm_ds.z_ocean.sel(time=slice('2016-10-30','2016-11-01' )).plot(label='WL ocean qcm')
# qcm_ds.z_thalweg.sel(time=slice('2016-10-30','2016-11-01' )).plot(label='thalweg elev')
# his_ds.general_structure_s1up.sel(general_structures=1).plot(label='WL upstr of mouth_out', color='b')
# #qcm_ds.w_inlet.sel(time=slice('2016-10-13','2016-10-19' )).plot(label='inlet width')
# ax.legend()

# fig2, ax2 = plt.subplots()

# his_ds.general_structure_s1up.sel(general_structures=0).plot(label='WL upstr of mouth_in', color='r')
# his_ds.general_structure_s1dn.sel(general_structures=0).plot(label='WL downstr of mouth_in', color='orange')
# his_ds.general_structure_s1up.sel(general_structures=1).plot(label='WL upstr of mouth_out', color='b')
# his_ds.general_structure_s1dn.sel(general_structures=1).plot(label='WL downstr of mouth_out', color='cyan')
# ax2.legend()


#%% Old stuff

# run_name13C ="run_tide_test-v13C"
# run_name17 ="run_tide_test-v17"
# run_name17A ="run_tide_test-v17A"
 
# yr = '2016'     

# odir ='E:/proj/Pescadero/Model_Runs/Testing/'
# figure_dir = 'E:/proj/Pescadero/Model_Runs/Figures/'

# #Load Model
# model13C=pesca_base.PescaButano.load(odir+run_name13C)
# his_ds13C=xr.open_dataset(model13C.his_output())

# model17=pesca_base.PescaButano.load(odir+run_name17)
# his_ds17=xr.open_dataset(model17.his_output())

# model17A=pesca_base.PescaButano.load(odir+run_name17A)
# his_ds17A=xr.open_dataset(model17A.his_output())



# fig, ax = plt.subplots(4, 1, sharex='col',figsize=(8,16))

# for i, row in df_station.iterrows():
#     # Load DFM model data
#     predicted = (his_ds17.waterlevel
#                     .sel(stations = row['model_st_nb'])
#                     .assign_coords(label='Modeled'))
    
#     # Load the BML observations
#     fname = row['BML_fname']
#     bml_ds = formatBML(bml_odir + fname)
    
#     sources=[predicted,bml_ds]
    
#     #To include QCM at the NCK station
#     if row['Title'] == 'NCK':  
        
#         qcm_ds = xr.open_dataset('E:/proj/Pescadero/data/ESA_QCM/ESA_PescaderoQCM_4.28.2021.nc')
#         qcm_WL = qcm_ds.calQCM_lagoon_WL.assign_coords(label='NCK QCM')
        
#         sources=[predicted,bml_ds,qcm_WL]


    
#     dc.calibration_axe_1panel (sources,row['Title'],ax[i], trim_time=True,num=1)
    
    
#     print(row['Title'])

# # Print run info
# fig.text(0.5, 0.98, run_name,fontsize=16,horizontalalignment='center')
# fig.text(0.5, 0.95, run_desc,fontsize=10,horizontalalignment='center')


