import os
#from stompy.io.local import usgs_nwis
import numpy as np
# import matplotlib.pyplot as plt
# cache_dir='cache'
# if not os.path.exists(cache_dir):
#     os.makedirs(cache_dir)

# pesc_ds=usgs_nwis.nwis_dataset(11162500,
#                                start_date=np.datetime64("2010-01-01"),
#                                end_date=np.datetime64("2020-12-01"),
#                                products=[60],
#                                cache_dir=cache_dir)
# 
#                                
#                        
# ##
# 
# plt.figure(1).clf()
# fig.set_size_inches([12,4.8],forward=True)
# fig,ax=plt.subplots(1,1,num=1)
# ax.semilogy( pesc_ds.time, pesc_ds['stream_flow_mean_daily'] ,
#              label="USGS 11162500, Pescadero Ck")
# 
# ax.legend(loc='upper right')
# ax.set_ylabel("Discharge (cfs)")
# fig.savefig('usgs-11162500-Q-overview.png')
# 
# ##

# Load in daily flows from spreadsheet:
tu_flow_xls=("../../../"
             "data/OneDrive/Data and References/TU_UnimpairedFlows/"
             "Pescadero & Butano Hydrologic Analysis/"
             "Pescadero Hydrologic Analysis Results.xlsx")

# Sheets are
sheet_names=[
    "Impaired flow Pe USGS",
    "Unimpaired flow Pe USGS",
    "Impaired flow Butano USGS",
    "Unimpaired flow Butano USGS",
    "Impaired flow Pe TIDAL",
    "Unimpaired flow Pe TIDAL",
    "Impaired flow Butano TIDAL",
    "Unimpaired flow Butano TIDAL",
    "Impaired flow Entering Marsh",
    "Unimpaired flow Entering Marsh",
]

# Each sheet has dates on rows, and years on columns
# First data value at B5 on each sheet.
import pandas as pd
import xarray as xr

dfs=[]

for sheet_i,sheet_name in enumerate(sheet_names):
    print(sheet_name)
    df=pd.read_excel(tu_flow_xls,
                     sheet_name=sheet_name,
                     skiprows=[0,1,2])
    df.rename(columns={df.columns[0]:'Date'},inplace=True)
    
    # This gets long-format, but Date has a fake year.
    df1=df.melt(id_vars=['Date'],var_name='year',value_name='flow_cfs')
    # Drop mising flows first, since they are Feb 29 that will cause an
    # error in the next step
    df2=df1[ ~df1.flow_cfs.isnull() ].copy()
    # Make a proper date.
    # But year is WATER year.
    def add_year(rec):
        year=int(rec['year'])
        if rec['Date'].month>=10:
            year-=1
        return rec['Date'].replace(year=year)
    
    df2['time']=df2.apply(add_year, axis=1)
    df2['flow_cms']=df2['flow_cfs']*0.028316847
    df2['flow_desc']=sheet_name
    dfs.append(df2.loc[:,['flow_desc','time','flow_cms']])

df_comb=pd.concat(dfs).set_index(['flow_desc','time'])
df_comb.to_csv("TU_flows_SI.csv")




