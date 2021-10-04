import matplotlib.pyplot as plt
import glob
import stompy.model.delft.dflow_model as dfm
import xarray as xr
from shapely import geometry
import numpy as np

## 
run_dirs=[
    # 'data_onlymouth_v034', # weir at 0.8m, free weir flow
    # 'data_onlymouth_v035', # increase free weir coeffs
    # 'data_onlymouth_v036', # increase drowned weir coeffs, too
    # 'data_onlymouth_v037', # increase flow to 40 m3/s
    
    # 'data_onlymouth_v041_1.50',
    # 'data_onlymouth_v041_1.00',
    # 'data_onlymouth_v041_0.80',# Q=20, crest=0.80, extra=3
    # 'data_onlymouth_v041_0.60',
    # 'data_onlymouth_v041_0.20',
    
    # Trying to tune in coefficient to mimic mouth_as_bathy
    # Q=20
    # 'data_onlymouth_v042_z0.80_Q020',
    # 'data_onlymouth_v043_z0.80_Q020_ex20_co1', # match to bathy
    # 'data_onlymouth_v043_z0.80_Q020_ex5_co0.5', # very close
    # 'data_onlymouth_v043_z0.80_Q020_ex0_co0.55',

    # Q=5
    # 'data_onlymouth_v042_z0.80_Q005',
    # 'data_onlymouth_v043_z0.80_Q005_ex40_co1', # can't get there with just extraresistance
    # 'data_onlymouth_v043_z0.80_Q005_ex40_co0.5', # can't get there with extra resistance
    # 'data_onlymouth_v043_z0.80_Q005_ex0_co0.55', # good

    # Q=10
    #'data_onlymouth_v042_z0.80_Q010',
    #'data_onlymouth_v043_z0.80_Q010_ex0_co0.55', 

    # Q=10, crest=0.4
    'data_onlymouth_v042_z0.40_Q010',
    'data_onlymouth_v043_z0.40_Q010_ex0_co0.55', # close
    'data_onlymouth_v043_z0.40_Q010_ex0_co0.5',  # maybe 0.47 is the real deal
    
]

# e.g. data_onlymouth_v042_z1.50_Q040
#run_dirs=glob.glob('data_onlymouth_v042_*Q020')
#run_dirs.sort()

models=[dfm.DFlowModel.load(rd) for rd in run_dirs]

plt.figure(1).clf()
ax=plt.subplot(1,1,1)

t=None
for model in models:
    his_ds=xr.open_dataset(model.his_output())

    if t is None:
        t=his_ds.time.values[-1]
    tran=dfm.extract_transect_his(his_ds,'thalweg_pesc_.*')
    ls=ax.plot( tran.d_sample, tran.waterlevel.sel(time=t,method='nearest'),
                label=model.run_dir.replace('data_onlymouth_',''),
                lw=0.8)
    plt.plot( tran.d_sample, tran.bedlevel,label='__nolabel__',color=ls[0].get_color(),
              lw=2.25)

    # Can I draw in crest level, too?
    if len(model.structures):
        struct=model.structures[0]
        crest_level=struct['CrestLevel']
        try:
            crest_level=crest_level.val1.sel(time=t,method='nearest')
        except AttributeError:
            pass
        geo_tran=geometry.LineString(np.c_[ tran.x_sample, tran.y_sample])
        geo_strt=geometry.LineString(struct['geom'])
        d=geo_tran.project(geo_tran.intersection(geo_strt))
        plt.plot([d,d],[0,crest_level],
                 marker='x',label='__nolabel__',
                 color=ls[0].get_color())
             
    t_actual=tran.time.sel(time=t,method='nearest').values
    print("Requested time:",t)
    print("Actual time:   ",t_actual)

    
ax.legend(loc='lower left')
