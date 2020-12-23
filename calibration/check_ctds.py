# Compare with CTD data to confirm time zones.
from scipy.io import loadmat
from stompy import utils

ctd_path="../../../data/M.Williams/data_for_dsepulveda/CTD data"

# This does in fact have 2012-01-18 -- 2012-03-20 data
# s_* variables are salinity at one or more heights
# d_* variables are depth.
ctd_mat_fn=os.path.join(ctd_path,'janmar2012','ctd_allstn_same_timeaxis.mat')

ctd_mat=loadmat(ctd_mat_fn)

# Make that into a xr.Dataset

ctd_ds=xr.Dataset()
ctd_ds['t_matlab']=('time',),ctd_mat['t_all'].squeeze()
ctd_ds['time']=('time',), utils.to_dt64( utils.dnum_mat_to_py(ctd_ds['t_matlab']) )

# okay.
# So s_nm is salinity at nm
# d_nm is going to be depth
# no temperature??  must be in the source files.

for station in ['s_nm','d_nm','s_ac','d_ac','s_dc','d_dc',
                's_pc','d_pc','s_bc','d_bc']:
    value=ctd_mat[station+'_all'].squeeze()

    if value.ndim==1:
        ctd_ds[station]=('time'),value
    elif value.shape[1]==4:
        ctd_ds[station]=('time','ctdT'),value # ??
    elif value.shape[1]==3:
        ctd_ds[station]=('time','ctd'),value # ??
    elif value.shape[1]==2:
        ctd_ds[station]=('time','ct'),value # ??
    else:
        assert False
        
##     

# s_nm[0] is salinity, bottom
# s_nm[1] is salinity, mid
# s_nm[2] is salinity, top

fig=plt.figure(2)
fig.clf()
fig,ax=plt.subplots(1,1,num=2)
ax.plot(ctd_ds.time,ctd_ds.s_nm.values[:,0],label='NM salinity, bottom')
ax.plot(ctd_ds.time,ctd_ds.s_nm.values[:,1],label='NM salinity, mid')
ax.plot(ctd_ds.time,ctd_ds.s_nm.values[:,2],label='NM salinity, top')
ax.legend(loc='upper right')
fig.autofmt_xdate()

## 

# d_nm: bottom, mid, top depth sensors.
# Top is floating, not useful. Bottom is good.
# Mid is maybe out of the water sometimes?
# Doesn't quite capture the tides at the end of the
# period.

fig=plt.figure(3)
fig.clf()
fig,ax=plt.subplots(1,1,num=3)
ax.plot(ctd_ds.time,ctd_ds.d_nm.values[:,0],label='NM depth, bottom')
ax.plot(ctd_ds.time,ctd_ds.d_nm.values[:,1],label='NM depth, mid')
ax.plot(ctd_ds.time,ctd_ds.d_nm.values[:,2],label='NM depth, top')
ax.legend(loc='upper right')
fig.autofmt_xdate()

##

# Appears to just be Nov 12 to Nov 29.  I don't see December data..
mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/all_ctds_novdec2010.mat")

for k in mat.keys():
    if not k.startswith('tz_'): continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# => 
# tz_ds1 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_ds3 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_ds4 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_ds5 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_us1 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_us2 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000
# tz_ds2 2010-11-12T06:00:00.000000000 to 2010-11-29T18:00:00.000000000


plt.figure(11).clf()
for k in mat.keys():
    if not k.startswith('pres'): continue
    plt.plot(mat[k].squeeze(),label=k)

plt.legend(loc='upper right')
##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/AC_ctds.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_')): continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# =>    
# tz_ac1 2012-01-17T18:14:00.000000000 to 2012-03-23T09:55:50.000000000
# tl_ac1 2012-01-17T10:14:00.000000000 to 2012-03-23T01:55:50.000000000
# tz_ac2 2012-01-17T18:00:00.000000000 to 2012-03-20T15:04:10.000000000
# tl_ac2 2012-01-17T10:00:00.000000000 to 2012-03-20T07:04:10.000000000

##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/BC_ctds.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_')): continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# =>    
# tz_bc 2012-01-17T14:00:00.000000000 to 2012-02-08T05:27:30.000000000
# tl_bc 2012-01-17T06:00:00.000000000 to 2012-02-07T21:27:30.000000000

##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/ctd_20mMA.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
        print(f"{k} skip")
        continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# =>
# t_20mMA 2012-01-18T00:00:10.000000000 to 2012-03-07T18:26:40.000000000

##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/ctd_20mMApart.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
        print(f"{k} skip")
        continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# No time data.

## 

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/DC_ctds_fixed_gmt.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
        print(f"{k} skip")
        continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
# =>
# tl_dc1 2012-01-17T12:30:00.000000000 to 2012-03-21T21:47:30.000000000
# tl_dc2 2012-01-17T11:30:00.000000000 to 2012-03-20T12:44:20.000000000
# tl_dc3 2012-01-17T11:10:00.000000000 to 2012-03-20T11:47:50.000000000
# tl_dc4 2012-01-17T12:10:00.000000000 to 2012-03-18T00:18:30.000000000
# tz_dc1 2012-01-17T20:30:00.000000000 to 2012-03-22T05:47:30.000000000
# tz_dc2 2012-01-17T19:30:00.000000000 to 2012-03-20T20:44:20.000000000
# tz_dc3 2012-01-17T19:10:00.000000000 to 2012-03-20T19:47:50.000000000
# tz_dc4 2012-01-17T20:10:00.000000000 to 2012-03-18T08:18:30.000000000

# ignoring DC_ctds.mat, same size as this, presumably just time offsets.

##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/NM_ctds.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
        print(f"{k} skip")
        continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")
    
# =>    
# tz_nm1 2012-01-17T14:00:00.000000000 to 2012-03-20T21:37:30.000000000
# tl_nm1 2012-01-17T06:00:00.000000000 to 2012-03-20T13:37:30.000000000
# tz_nm2 2012-01-17T18:30:00.000000000 to 2012-03-22T19:50:00.000000000
# tl_nm2 2012-01-17T10:30:00.000000000 to 2012-03-22T11:50:00.000000000
# tz_nm3 2012-01-17T14:00:00.000000000 to 2012-03-09T02:57:00.000000000
# tl_nm3 2012-01-17T06:00:00.000000000 to 2012-03-08T18:57:00.000000000

##

mat=loadmat("../../data/M.Williams/data_for_dsepulveda/CTD data/janmar2012/PC_ctds.mat")
for k in mat.keys():
    if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
        print(f"{k} skip")
        continue
    t_mat=mat[k].squeeze()
    t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
    print(f"{k} {t[0]} to {t[-1]}")

fig=plt.figure(13)
fig.clf()
tz=utils.to_dt64(utils.dnum_mat_to_py(mat['tz_pc'].squeeze()))
plt.plot( tz,mat['da_pc'].squeeze(),
          label='PC')
plt.legend(loc='upper right')
fig.autofmt_xdate()

# =>     
# tz_pc 2012-01-17T14:00:00.000000000 to 2012-04-13T01:16:30.000000000
# tl_pc 2012-01-17T06:00:00.000000000 to 2012-04-12T17:16:30.000000000

# So in all of that, looks like PC was out the longest, and maybe there
# was another deployment of PC a few days later which Mathilde used.

##

# There is some 2011-September data, but mostly 2011 Oct-Dec.
for stn in ['AC','DC','NM']:
    print(f"-------{stn}------")
    fn=f"../../data/M.Williams/data_for_dsepulveda/CTD data/octdec2011/{stn}_ctds.mat"
    print(fn)
    mat=loadmat(fn)
    for k in mat.keys():
        if k.startswith('_'): continue
        
        if not (k.startswith('tz_') or k.startswith('tl_') or k.startswith('t_') ):
            print(f"{k} skip")
            continue
        t_mat=mat[k].squeeze()
        t=utils.to_dt64(utils.dnum_mat_to_py(t_mat))
        print(f"{k} {t[0]} to {t[-1]}")
    if stn=='NM': break

fig=plt.figure(14)
fig.clf()
tz=utils.to_dt64(utils.dnum_mat_to_py(mat['tz_nm1'].squeeze()))
plt.plot(tz, mat['da_nm1'].squeeze(), label='NM depth')
plt.legend(loc='upper right')
fig.autofmt_xdate()

# =>    
# -------AC------
# ../../data/M.Williams/data_for_dsepulveda/CTD data/octdec2011/AC_ctds.mat
# tz_ac1 2011-09-09T17:00:00.000000000 to 2011-12-05T21:04:00.000000000
# tl_ac1 2011-09-09T09:00:00.000000000 to 2011-12-05T13:04:00.000000000
# tz_ac2 2011-10-27T16:00:00.000000000 to 2011-12-21T19:21:50.000000000
# tl_ac2 2011-10-27T08:00:00.000000000 to 2011-12-21T11:21:50.000000000

# -------DC------
# ../../data/M.Williams/data_for_dsepulveda/CTD data/octdec2011/DC_ctds.mat
# tz_dc1 2011-10-27T16:00:00.000000000 to 2011-12-18T19:32:10.000000000
# tl_dc1 2011-10-27T08:00:00.000000000 to 2011-12-18T11:32:10.000000000
# tz_dc2 2011-10-27T16:00:00.000000000 to 2011-12-19T07:00:10.000000000
# tl_dc2 2011-10-27T08:00:00.000000000 to 2011-12-18T23:00:10.000000000
# tz_dc3 2011-10-27T16:00:00.000000000 to 2011-12-21T20:13:40.000020000
# tl_dc3 2011-10-27T08:00:00.000000000 to 2011-12-21T12:13:40.000000000
# tz_dc4 2011-10-27T16:00:00.000000000 to 2011-12-17T22:21:10.000000000
# tl_dc4 2011-10-27T08:00:00.000000000 to 2011-12-17T14:21:10.000000000

# -------NM------
# ../../data/M.Williams/data_for_dsepulveda/CTD data/octdec2011/NM_ctds.mat
# tz_nm1 2011-09-09T17:00:00.000000000 to 2011-12-12T22:20:00.000000000
# tl_nm1 2011-09-09T09:00:00.000000000 to 2011-12-12T14:20:00.000000000
