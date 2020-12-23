import pandas as pd
df=pd.read_excel( ("../../data/OneDrive/Data and References/"
                   "Marsh Water Level Data/Pescadero_Lagoon_WLs_2010_2016_metadata.xlsx"),
                  sheet_name="continuous data",
                  skiprows=[0,1,2,3,4],names=["matlab_date","datestr","waterlevel_ft_navd88"])
t=utils.to_dt64(utils.dnum_mat_to_py(df['matlab_date']))
## 
# toss in some rounding to avoid annoying floating point date inaccuracy
df['time_pst']=utils.round_dt64(t,dt=np.timedelta64(60,'s'))
df['time']=df['time_pst']+np.timedelta64(8,'h')

ds=xr.Dataset.from_dataframe(df.loc[:,['time','waterlevel_ft_navd88']].set_index('time'))
ds['waterlevel']=('time',),ds['waterlevel_ft_navd88'].values * 0.3048
ds['time'].attrs['timezone']='UTC'
ds['waterlevel'].attrs['datum']='NAVD88'
ds['waterlevel'].attrs['units']='m'

ds.to_netcdf('esa_compiled_waterlevel.nc')

##

plt.figure(1).clf()
plt.plot(ds.time,ds.waterlevel,label='ESA Compiled WSE')
plt.legend(loc='upper right')

plt.ylabel('m NAVD88')

