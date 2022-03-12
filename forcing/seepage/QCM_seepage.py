import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## 
df=pd.read_csv("../../../data/ESA_QCM/ESA_draft_PescaderoQCM_output_4.28.2021.csv",
               parse_dates=["Date (PST)"],skiprows=1,
               low_memory=False)
df=df.rename({'Date (PST)':'time',
              'Modeled seepage':'seepage',
              'Modified Ocean Level (feet NAVD88)':'z_ocean',
              'Modeled Lagoon Level (feet NAVD88)':'z_lagoon',
              'Observed Lagoon Level (feet NAVD88)':'z_lagoon_obs',
              'Modeled Inlet Width (feet)':'width',
              'Modeled inlet flow':'Qinlet',
              'Modeled Inlet Depth (feet)':'inlet_depth',
              'Modeled Inlet thalweg elevation (feet NAVD88)':'z_inlet'},
             axis=1)
df.loc[df.width.isnull(),'width']=0.0
df['head_ft'] = df['z_lagoon'] - df['z_ocean']

for fld in ['z_inlet','inlet_depth','z_ocean','z_lagoon','width']:
    values=df[fld].values.copy()
    values[1:]=values[:-1]
    df['old_'+fld]=values

##

plt.figure(2).clf()
fig,ax=plt.subplots(num=2)

# From Dupuit, expect
# Q = W*k*(h1^2 - h2^2)/2L

# sel=(df['width']==0.0)&(df['seepage'].notnull())
sel=df['inlet_depth'].isnull()
df_sel=df[sel]

#pred_seepage=df['head_ft']*(-0.1632)
# -0.01 = -k * W / 2L
# If L=30, then k*W ~ 0.6
#L=30 - 0.25*df_sel['z_lagoon'] - 0.25*df_sel['z_ocean']

# L=200
# kW=3.5
# power=2.
# z_bedrock=-4.5  #in ft, but still crazy

# For closed conditions:
L=200
W=50
k=0.068 # ft/s
z_bedrock=-4.5
# z_bedrock=0.00

pred_seepage=-k*W/(2*L)*((df_sel['z_lagoon']- z_bedrock)**2 - (df_sel['z_ocean']-z_bedrock)**2)

# This looks quite close, but has not justification
#pred_seepage = np.sign(pred_seepage)*np.abs(pred_seepage)**1.25

# Based on Dane's description:
#         ft/s     m   /   m           ft**2                        ft**2
#pred_DB=-(0.012/0.3048)*(100)/(2*200)*((df_sel['z_lagoon']-0.00)**2 - (df_sel['z_ocean']-0.00)**2)
# Actually, updated with more information from Dane:

# DB specified 0.012 m/s for hydraulic conductivity, but the 1.65 is needed to get tight alignment with
# existing QCM output.
hyd_cond=0.012 * 1.65
z_bedlevel=0.00
width=100.
L_alongshore=100
L_crossshore=100 # Dane modulates this with the open/closed state
pred_DB=np.where( df_sel['z_lagoon']>z_bedlevel,
                  -hyd_cond*(L_alongshore)*(df_sel['z_lagoon']-z_bedlevel)*(df_sel['z_lagoon']-df_sel['z_ocean'])/L_crossshore,
                  -hyd_cond*(1*0.001)*(df_sel['z_lagoon']-df_sel['z_ocean'])/L_crossshore)

# the closed width=0 samples seem to fall all on one curve
scat=ax.scatter(df_sel['seepage'],
                pred_seepage,5,
                df_sel['z_inlet'],
                # df_sel['width'],
                alpha=0.3)

scat2=ax.scatter(df_sel['seepage'],
                 pred_DB,5,
                 df_sel['z_inlet'],
                 alpha=0.3,
                 cmap='inferno')

plt.colorbar(scat,label='z_inlet')
ax.plot([-2,1],[-2,1],'k-',zorder=2,lw=0.5)
ax.axis('equal')
ax.axis([-2,1.,-2,1.])
ax.set_ylabel('Q prediction')
ax.set_xlabel('Q QCM')
##

# For the open case:
# Still a lot of time that it's on the slow curve.
# Figure out an okay formula, then come back to refine the selection

plt.figure(2).clf()
fig,ax=plt.subplots(num=2)

sel=slice(None) # (df['width']>0.0)&(df['seepage'].notnull())
#sel=sel&(df['z_inlet']<2)
df_sel=df[sel]

Lopen=40
W=50
k=0.068 # ft/s
z_bedrock=-4.5


pred_seepage_open=-k*W/(2*Lopen)*((df_sel['z_lagoon']-df_sel['inlet_depth']- z_bedrock)**2 - (df_sel['z_ocean']-z_bedrock)**2)
# For closed conditions:
Lclosed=200
pred_seepage_closed=-k*W/(2*Lclosed)*((df_sel['z_lagoon']- z_bedrock)**2 - (df_sel['z_ocean']-z_bedrock)**2)

err_closed=np.abs(pred_seepage_closed-df_sel['seepage'])
err_open=np.abs(pred_seepage_open-df_sel['seepage'])
is_closed=err_closed<err_open

# the closed width=0 samples seem to fall all on one curve
scat=ax.scatter(df_sel['seepage'],
                pred_seepage_open,5,
                is_closed )

plt.colorbar(scat,label='z_inlet')
ax.plot([-2,1],[-2,1],'k-',zorder=2,lw=0.5)
ax.axis('equal')
ax.axis([-2,1.,-2,1.])
ax.set_ylabel('Q prediction')
ax.set_xlabel('Q QCM')

##

changing=np.r_[ 0, np.diff(is_closed.values.astype(np.int32))]
plt.figure(3).clf()
fig,axs=plt.subplots(1,3,num=3)
#axs[0].scatter(is_closed, df_sel['z_ocean'] , 15, changing, alpha=0.2)
axs[0].scatter(is_closed, df_sel['width'] , 15, changing, alpha=0.2)
axs[0].set_ylabel('width')
axs[1].scatter(is_closed, df_sel['z_lagoon'], 15, changing, alpha=0.2)
axs[1].set_ylabel('z_lagoon')
axs[2].scatter(is_closed, df_sel['inlet_depth'] , 15, changing, alpha=0.2)
axs[2].set_ylabel('inlet depth')

for ax in axs:
    ax.set_xticks([0,1])
    ax.set_xticklabels(['open','closed'])
    
##

plt.figure(1).clf()
fig,axs=plt.subplots(5,1,num=1,sharex=True)
axs[0].plot(df.time,df['seepage'],label='Qseep')
axs[1].plot(df.time,df['z_ocean'],label='ocean')
axs[1].plot(df.time,df['z_lagoon'],label='lagoon')
axs[1].plot(df.time,df['z_inlet']+df['inlet_depth'],label='z_i+d_i')

axs[1].legend(loc='upper left',ncol=2)
axs[2].plot(df.time,df['inlet_depth'],label='inlet depth')
axs[2].plot(df.time,df['z_inlet'],label='z_inlet')
axs[3].plot(df.time,is_closed,label='is closed')
axs[0].legend(loc='upper left')
axs[2].legend(loc='upper left')
axs[3].legend(loc='upper left')
axs[4].plot(df.time, df['width'],label='width')
axs[4].legend(loc='upper left')

# 1. What does inlet depth mean?
#    tracks z_lagoon mostly.
#    z_inlet + depth_inlet = max(z_ocean,z_lagoon)
#     at least very close. scatter of maybe 0.05 ft
#     could be time staggering. If it is time staggering,
#     it is at some internal timestep shorter than the output

##

plt.figure(5).clf()
plt.scatter( np.maximum( df['z_lagoon'], df['z_ocean']),
             df['z_inlet'] + df['inlet_depth'])

##

# If the mouth is open, then the seepage is not of much interest.
# it may be larger than when closed, but generally in the noise
# compared to the inlet flow.
