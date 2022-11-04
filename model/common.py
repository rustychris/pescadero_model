import numpy as np
import os
import stompy.model.delft.dflow_model as dfm
from stompy.spatial import field
import xarray as xr
from stompy import utils

section_signed_fields=['cross_section_discharge',
                       'cross_section_salt',
                       'cross_section_cumulative_discharge',
                       'cross_section_velocity',
                       'cross_section_cumulative_salt']
section_geom_fields=['cross_section_geom_node_coordx',
                       'cross_section_geom_node_coordy',
                       'cross_section_geom']
def prechain(dss):
    if len(dss)<2:
        return dss
    else:
        out=[dss[0]]
        # check for sections changing:
        # starting from the beginning
        secs0=dss[0].cross_section.values
        geoms0=dss[0].cross_section_geom
        for ds in dss[1:]:
            secs=ds.cross_section.values
            if np.all(secs[:len(secs0)]==secs0):
                if len(secs)>len(secs0):
                    sec_slice=slice(None,len(secs0))
                    secNode_slice=slice(None,dss[0].dims['cross_section_geom_nNodes'])
                    ds=ds.isel(cross_section=sec_slice,cross_section_geom_nNodes=secNode_slice)
                    print("Trimming out extra sections from later output")
            else:
                raise Exception("Section names don't match")
                
            # And check for n_complex_xs being flipped. For now, go with
            # the starting orientation:
            # prechain() is called *after* these become dask dataframes, which has a 
            # side effect of making the shapely geometries into arrays. 
            for sec in ['n_complex_xs']:
                geom0=geoms0.sel(cross_section=sec).values
                geomN=ds.cross_section_geom.sel(cross_section=sec).values
                if np.allclose(geom0,geomN):
                    print("Geometries match?")
                    continue
                elif np.allclose(geom0,geomN[::-1]):
                    # Probably have to construct a list of signed variables,
                    # flip each one...
                    flipper=np.where(secs0==sec,-1,1)
                    ds['flipper']=('cross_section',),flipper
                    for fld in section_signed_fields:  # e.g. 'cross_section_discharge'
                        print(f"Flipping variable {fld}")
                        ds[fld] = ds[fld] * ds['flipper']
                    del ds['flipper']
                    for fld in section_geom_fields:
                        ds[fld]=dss[0][fld]
            out.append(ds)
        return out



# Slimmed-down history files
def his_cache(model,variable='salinity',cache_dir="cache",force=False,
              chain=True, **sel_kws):
    """
    Extract one variable at one station from chained history output, backed by
    file cache.
    'stations' is plural because the dimension in the nc file is plural -- just specify
    a single station, by coordinate (string).
    """
    # This would probably be better as non-chained, and chain the results at
    # a higher level.
    # N.B. cache_dir is under the model run dir
    his_fn=model.his_output()
    cache_path=os.path.join(os.path.dirname(his_fn),cache_dir)
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)

    if chain:
        nochain=""
    else:
        nochain="nochain"
        
    sel_str="-".join( [f"{k}_{sel_kws[k]}" for k in sel_kws])
        
    cache_fn=os.path.join(cache_path,
                          f"v00{nochain}-{sel_str}-var_{variable}.nc")
    if force or utils.is_stale(cache_fn,[his_fn],tol_s=7200):
        print(f"{cache_fn} cache miss")
        his=model.his_dataset(chain=chain,prechain=prechain)
        da=his[variable].sel(**sel_kws)
        da.to_netcdf(cache_fn)
        return da
    else:
        ds=xr.load_dataset(cache_fn)
        return ds[variable]
    
def save_as_layers(fig,img_fn,labels,**save_args):
    ax=fig.axes[0]

    # Remove starting at the end
    for i in range(len(labels))[::-1]:
        label=labels[i]
        line_labels=[l.get_label() for l in ax.lines]
        idx=line_labels.index(label)
        del ax.lines[idx]
        fig.savefig(img_fn.replace('.png',f'{i}.png'),**save_args)
                       
     
def load_or_none(rd):
    try:
        return dfm.DFlowModel.load(rd)
    except FileNotFoundError:
        return None
    
scen_names={0:'Base',1:'Low',2:'Medium',3:'High'}
slr_names={0:'',0.61:'+SLR'}

def name_runs(df):
    df['name']=[scen_names[row['scen']]+slr_names[row['slr']]
                for _,row in df.iterrows()]

events=[(np.datetime64('2016-08-11'),' Closure'),
        (np.datetime64('2016-11-01'),' Sm. Breach'),
        (np.datetime64('2016-12-11'),' Lg. Breach'),
        (np.datetime64('2017-02-07'),' Peak\n Flow'),
       ]

def label_events(ax,ticklabels=True):
    # Label events
    trans=ax.get_xaxis_transform()
    for t,name in events:
        if ticklabels:
            ax.text(t,0.01,name,transform=ax.get_xaxis_transform(),va='bottom',clip_on=1)
        ax.plot([t,t],[0.,0.03],transform=trans,color='k',lw=0.75)


# Choose an ebb period and a flood period

# For the older runs:
#ebb_period=[np.datetime64('2016-08-04 06:30:00'),
#            np.datetime64('2016-08-04 13:30:00')]
#flood_period=[np.datetime64('2016-08-04 13:30:00'),
#              np.datetime64('2016-08-04 20:00:00')]

# For tidal runs based on 2016long:
# This has been supplanted by code near the end, and longer rtidal2 runs.
ebb_period=[np.datetime64('2016-07-31 03:30:00'), # large ebb.
            np.datetime64('2016-07-31 11:00:00')]
flood_period=[np.datetime64('2016-07-31 11:00:00'),
              np.datetime64('2016-07-31 17:00:00')]

# manually nudge so that lagged sections still recover ebb
# This has been supplanted by a later tidal period that is cleaner
# and at max spring.
ebb_time=ebb_period[0]+(ebb_period[1]-ebb_period[0])/2 + np.timedelta64(1,'h')


# Updated time periods for 72h runs
spring_ebb_mid=np.datetime64("2016-08-02 10:00")
spring_flood_mid=np.datetime64("2016-08-02 04:00")

# Approximately cover tidal phase across all runs -- a little narrow
# to avoid times that are in a different phase depending on the run.
spring_ebb=[np.datetime64("2016-08-02 06:00"),
            np.datetime64("2016-08-02 16:00")]
spring_flood=[np.datetime64("2016-08-02 01:00"),
              np.datetime64("2016-08-02 05:00")]


def dem(version):
    if version=='asbuilt':
        #return field.GdalGrid("../../bathy/compiled-dem-asbuilt-20210920-1m.tif")
        return field.GdalGrid("../../bathy/compiled-dem-asbuilt-20210826-1m.tif")
    else:
        raise Exception(f"Need to add in version={version} to {__file__}")
