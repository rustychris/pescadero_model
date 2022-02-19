# Check 2013 QCM and TU flows to see if there is an obvious time to start/stop
import pandas as pd
import local_config
import matplotlib.pyplot as plt
import pesca_base
import xarray as xr
##

model=pesca_base.PescaButano()
qcm_ds=model.prep_qcm_data()
## 
tu_df=pd.read_csv(os.path.join(local_config.model_dir,"../forcing/tu_flows/TU_flows_SI.csv"),
               parse_dates=['time'])

def extract_da(desc):
    df_desc=tu_df[ tu_df.flow_desc==desc ]
    ds=xr.Dataset.from_dataframe(df_desc.loc[:,['time','flow_cms']].set_index('time'))
    return ds['flow_cms']

# 'Impaired flow Butano TIDAL'

Qpesc=extract_da('Impaired flow Pe TIDAL')

##

plt.figure(1).clf()
fig,axs=plt.subplots(2,1,sharex=True,num=1)

axs[0].plot( Qpesc.time, Qpesc, label='Qpesc')
axs[1].plot( qcm_ds.time,qcm_ds.z_lagoon, label='z_lagoon')

# According to QCM, it was closed, partial breach on 3/22,
# Really breached 4/3, only to reclose 4/17
# two more short-lived openings, then closed until 3/2 of 2014.
# Maybe starting 2013-03-22T12:00, in hopes that the short openings
# will spin up the salt field enough, and it would have to run all
# the way out to 2014-03-08.
# Try a 2D run first, since there will probably be some problems.
