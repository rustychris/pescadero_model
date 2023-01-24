import numpy as np
import pandas as pd
import os
import stompy.model.delft.dflow_model as dfm
from stompy import filters, memoize, utils
from stompy.spatial import field,wkb2shp
import xarray as xr
from collections import defaultdict
from stompy import utils
import matplotlib.pyplot as plt
import local_config

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

def name_runs(df,overtop=False):
    if not overtop:
        df['name']=[scen_names[row['scen']]+slr_names[row['slr']]
                    for _,row in df.iterrows()]
    else:
        overtop_names={True:'-OT',False:''}
        df['name']=[scen_names[row['scen']]+slr_names[row['slr']]+overtop_names[row['overtop']]
                    for _,row in df.iterrows()]


flow_names={'impaired':'impaired', 'unimpaired':'unimpaired'}
period_names={'2016long':'2016', '2013':'2013'}
def name_runs_flows(df):
    df['name']=[period_names[row['period']] + slr_names[row['slr']] + " " + flow_names[row['flows']]
                for _,row in df.iterrows()]
    
events=[
    (np.datetime64('2013-05-15'),' Closure',{}),
    (np.datetime64('2014-03-01'),'Breach ',{'ha':'right'}),
    
    (np.datetime64('2016-08-11'),' Closure',{}),
    (np.datetime64('2016-11-01'),' Sm. Breach',{}),
    (np.datetime64('2016-12-11'),' Lg. Breach',{}),
    (np.datetime64('2017-02-07'),' Peak\n Flow',{}),
]

def label_events(ax,ticklabels=True):
    # Label events
    trans=ax.get_xaxis_transform()
    for t,name,kw in events:
        if ticklabels:
            ax.text(t,0.01,name,transform=ax.get_xaxis_transform(),va='bottom',clip_on=1,**kw)
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

# Salt plotting 
def fig_salinity_bystation_timeseries(runs,station,label,min_depth=0.0):
    fig,ax=plt.subplots(1,1,figsize=(7.5,4))
    
    colors=['tab:Blue','tab:Orange','tab:Green','tab:Red']
    #colors=list(Colors)
    alpha=0.12
    t_starts=[]
    t_stops =[]
    
    for color,(_,rec) in zip(colors,runs.iterrows()):
        salt=his_cache(rec['model'],stations=station,variable='salinity')        
        zorder=2
        salt_min=np.nanmin(salt,axis=1)
        salt_max=np.nanmax(salt,axis=1)
        
        if min_depth>0.0:
            eta=his_cache(rec['model'],stations=station,variable='waterlevel')
            z_bed=his_cache(rec['model'],stations=station,variable='bedlevel')
            depth=eta-z_bed
            valid=depth>=min_depth
            salt_min[~valid]=np.nan
            salt_max[~valid]=np.nan
            
        # Data dt is 15 min.
        win=60*4
        salt_min=filters.lowpass_fir(salt_min,win)
        salt_max=filters.lowpass_fir(salt_max,win)
        
        #color=colors.pop(0)
        ax.fill_between(salt.time,
                        salt_min,salt_max,
                        label=rec['name'],color=color,
                        lw=1.2,alpha=alpha,zorder=zorder)
        ax.plot(salt.time,salt_min,lw=0.75,color=color,zorder=3)
        ax.plot(salt.time,salt_max,lw=0.75,color=color,zorder=3)
        t_starts.append(salt.time.values[0])
        t_stops.append(salt.time.values[-1])
        
    ax.legend(loc='upper center',bbox_to_anchor=[0.45,1.12],ncol=len(runs),
              frameon=0)
    label_events(ax)
    # in case some runs are truncated.
    ax.axis(xmin=np.min(t_starts),xmax=np.max(t_stops))
    
    for color,t_stop in zip(colors,t_stops):
        if t_stop<np.max(t_stops):
            ax.axvline(t_stop,color=color,ls=':',lw=0.75)
    
    ax.set_ylabel('Salinity (ppt)')
    ax.text(0.03,0.97,label,transform=ax.transAxes,ha='left',va='top')
    fig.autofmt_xdate()
    fig.subplots_adjust(right=0.98,left=0.1,top=0.92, bottom=0.14)
    return fig

def twin_stage(fig,runs,station='nck',top_frac=0.33,ylabel='Stage (m)',
               scen_styles=defaultdict(dict)):
    fig.subplots_adjust(right=0.89)
    ax0=fig.axes[0]
    # Manually twin the axes to get some control over y position
    pos=ax0.get_position()
    pad_frac=0.03
    new_pos=[pos.xmin,pos.ymin+(1-top_frac+pad_frac)*pos.height,pos.width,(top_frac-pad_frac)*pos.height]
    ax1=fig.add_axes(new_pos,sharex=ax0)
    ax1.yaxis.tick_right()
    #ax1.set_ylabel(ylabel)
    ax1.yaxis.set_label_position("right")
    ax1.xaxis.set_visible(0)
    ax1.patch.set_visible(0)
    plt.setp(list(ax1.spines.values()),visible=0)
    model=runs['model'].values[0]
    print("Loading stage from for twin_stage from ",model)
    stage=his_cache(model,stations=station,variable='waterlevel')
    ax1.plot(stage.time, stage, 'k-',alpha=0.5,lw=0.8)
    yy=ax0.get_ylim()
    ax0.axis(ymax=yy[0]+(yy[1]-yy[0])/(1-top_frac))
    ticks=ax0.get_yticks()
    ax0.set_yticks([t for t in ax0.get_yticks() if t>=0 and t<=yy[1]])
    
    stage_thresholds=[2.1, 2.75, 3.25]
    if scen_styles is not None:
        stage_labels=['L/M culv','H levee','M levee']
        ax1.set_yticks(stage_thresholds)
        ax1.set_yticklabels(stage_labels)
        kws={'lw':0.5}
        ax1.axhline(stage_thresholds[0],**{**kws,**scen_styles['Low']})
        ax1.axhline(stage_thresholds[0],**{**kws,**scen_styles['Medium']})
        ax1.axhline(stage_thresholds[1],**{**kws,**scen_styles['High']})
        ax1.axhline(stage_thresholds[2],**{**kws,**scen_styles['Medium']})
        ax1.text(1.01,stage_thresholds[0],"\nLagoon\nstage",transform=ax1.get_yaxis_transform(),
                 fontstyle='italic',
                 va='top')
    else:
        # Try to sneak it in under the ticks.
        ax1.text(1.045,2.,"Lagoon stage",transform=ax1.get_yaxis_transform(),
                 rotation=90, va='center')
        #ax1.set_ylabel('Lagoon stage')
        #ax1.yaxis.set_label_coords(1.05,0.7)

    # touch up layout
    txt=fig.axes[0].texts[-1]
    #fig.text(0.02,0.99,txt.get_text()[:13],ha='left',va='top',fontweight='bold')
    txt.set_visible(0)
    return ax1

# @memoize.memoize(key_method='str',cache_dir='cache')
def fresh_wet_area(mod,thresholds,min_depth=0.1,region_names=None,
                   poly_shp="../grids/pesca_butano_v08/polygon_features.shp"):
    cache_fn=os.path.join(mod.run_dir, "fresh_wet_area_cached.pkl")
    
    if utils.is_stale(cache_fn,mod.map_outputs()):
        #mod=rec['model']
        mds=mod.map_dataset(chain=True)

        features=wkb2shp.shp2geom("../grids/pesca_butano_v08/polygon_features.shp")
        polys=[]
        for name in region_names:
            # no need to filter on dye, and now we can use existing lagoon poly, too.
            sel=(features['desc']==name) # &(features['type']=='dye')
            poly=features['geom'][sel]
            assert len(poly)==1
            polys.append( poly[0] )

        result=xr.Dataset()
        result['time']=mds.time.compute()
        result['min_depth']=(),min_depth
        result['thresholds']=('threshold',),thresholds
        if region_names is None:
            result['region']=('region',),np.arange(len(polys))
        else:
            result['region']=('region',),region_names

        result['poly_area']=('region',),[poly.area for poly in polys]

        Ac=mds.grid.cells_area()

        poly_masks=[mds.grid.select_cells_intersecting(poly)
                    for poly in polys]

        # previously used the polygon, but that's an overestimate
        # more comment
        result['region_area']=('region',),[Ac[mask].sum() for mask in poly_masks]

        areas=np.zeros( (mds.dims['time'],len(thresholds),len(polys)),np.float64)
        for ti,t in enumerate(mds.time.values):
            print(f"{ti}/{mds.dims['time']}")
            salt=mds['mesh2d_sa1'].isel(time=ti).values
            depth=mds['mesh2d_waterdepth'].isel(time=ti).values
            salt_max=np.nanmax(salt,axis=1)

            for thresh_i,threshold in enumerate(thresholds):
                for region_i,poly_mask in enumerate(poly_masks):
                    valid=poly_mask & np.isfinite(salt_max) & (salt_max<threshold) & (depth>=min_depth)
                    area=Ac[valid].sum()
                    areas[ti,thresh_i,region_i]=area
        result['habitat']=('time','threshold','region'),areas

        result.to_netcdf(cache_fn)

    # Always load from file to avoid inconsistent behavior.
    result=xr.load_dataset(cache_fn)
    return result    

def fig_habitat(result):
    fig,axs=plt.subplots(result.dims['region'],1,sharex=True,figsize=(8,5))

    for region in range(result.dims['region']):
        ax=axs[region]
        ax.text(0.02,0.98,result['region'].values[region],va='top',transform=ax.transAxes)
        for thrsh in range(result.dims['threshold']):
            area=result.habitat.isel(threshold=thrsh,region=region)
            percent=100*area/result.region_area.values[region]
            thresh_val=result.thresholds.values[thrsh]
            if np.isfinite(thresh_val):
                label=f"<{thresh_val} ppt"
            else:
                label='wet'
            ax.plot(result.time, percent, label=label)
    fig.autofmt_xdate()
    for ax in axs:
        ax.set_ylabel('% wet and fresh')
        label_events(ax) # may need tweaking, or hide text on first ax.
    axs[0].legend(loc='upper left',bbox_to_anchor=[1.02,1],frameon=False)
    fig.subplots_adjust(left=0.1,right=0.82,top=0.97,bottom=0.13)
    return fig

def fig_habitat_by_region(result):
    """
    Similar, but combine scenarios on one figure
    """
    fig,axs=plt.subplots(result.dims['threshold'],1,
                         sharex=True,figsize=(8,5))

    for thrsh in range(result.dims['threshold'])[::-1]:
        ax=axs[thrsh]
        for name in range(result.dims['name']):
            sub=result.isel(name=name,threshold=thrsh)
            area=sub.habitat 
            percent=100*area/sub.region_area 
            thresh_val=sub.threshold.item() 
            name_str=sub.name.item()
            ax.plot(sub.time, percent, label=sub.name.item(), **scen_styles[name_str])
        if np.isfinite(thresh_val):
            label=f"% <{thresh_val} ppt"
        else:
            label='% wet'
        ax.set_ylabel(label)
        label_events(ax,ticklabels=(ax==axs[-1])) 
        ax.axis(xmin=result.time.values[0],xmax=result.time.values[-1])
    fig.autofmt_xdate()
    axs[0].legend(loc='upper left',bbox_to_anchor=[1.02,1],frameon=False)
    fig.subplots_adjust(left=0.1,right=0.82,top=0.97,bottom=0.13)
    return fig


def fig_habitat_by_region_relative(result,scen_styles=defaultdict(dict)):
    """
    Minor difference: show the salinity thresholds as a fraction of wetted area, and wetted area as
    absolute m^2
    """
    fig,axs=plt.subplots(result.dims['threshold'],1,
                         sharex=True,figsize=(8,5))
    n_thresh=result.dims['threshold']
    
    for thrsh_i,ax in enumerate(axs):
        thrsh=n_thresh-thrsh_i-1 # plot inundation first, then brackish, then fresh.
        for name in range(result.dims['name']):
            sub=result.isel(name=name,threshold=thrsh)
            thresh_val=sub.threshold.item() 
            area=sub.habitat 
            name_str=sub.name.item()
            if np.isinf(thresh_val):
                # 1e4: convert to hectares
                ax.plot(sub.time, area/1e4, label=sub.name.item(), **scen_styles[name_str])
            else:
                wet_area=result.isel(name=name,threshold=n_thresh-1).habitat
                percent=100*area/wet_area # sub.region_area 
                ax.plot(sub.time, percent, label=sub.name.item(), **scen_styles[name_str])
        if np.isfinite(thresh_val):
            label=f"% <{thresh_val:.0f} ppt"
        else:
            label='Wet area (ha)'
        ax.set_ylabel(label)
        label_events(ax,ticklabels=(ax==axs[-1])) 
        ax.axis(xmin=result.time.values[0],xmax=result.time.values[-1])
    fig.autofmt_xdate()
    axs[0].legend(loc='upper left',bbox_to_anchor=[1.02,1],frameon=False)
    ax.axis(ymin=-20) # make space for event labels
    fig.subplots_adjust(left=0.1,right=0.82,top=0.97,bottom=0.13)
    return fig


def forcing_figure(panels=['pesca_ck','lagoon_wse','source_sink','wind'],
                   period=[np.datetime64("2016-07-01"),
                           np.datetime64("2017-02-28")],
                   Qlims=[0.05,82]):

    import pesca_base
    pbm=pesca_base.PescaButanoMixin()
    qcm_ds=pbm.prep_qcm_data()

    df=pd.read_csv(os.path.join(local_config.model_dir,
                                "../forcing/tu_flows/TU_flows_SI.csv"),
                   parse_dates=['time'])

    
    df_sel=df[ (df.time.values>=period[0])&(df.time.values<=period[1])]

    npanel=len(panels)
    fig,axs=plt.subplots(npanel,1,sharex=True,figsize=(8,2+1.75*npanel),squeeze=False)
    axs=axs[:,0]
    # add second axis with different units, update it whenever ax1 changes
    m2ft=1./0.3048

    def twinscale(ax,factor,units):
        #return # DBG
        ax_f = ax.twinx()
        ax_f.set_ylabel(units)
        def convert_ax2(_,ax=ax,ax_f=ax_f):
            y1, y2 = ax.get_ylim()
            ax_f.set_yscale(ax.get_yscale())
            ax_f.set_ylim(y1*factor, y2*factor)
            # This kills interactive usage
            #try:
            #    ax_f.figure.canvas.draw()
            #except AttributeError:
            #    pass # while printing this may fail.

        cid=ax.callbacks.connect("ylim_changed", convert_ax2)   
        
    sel=(qcm_ds.time.values>=period[0])&(qcm_ds.time.values<=period[1])
    qcm_sel=qcm_ds.isel(time=sel)
    
    for ax,panel in zip(axs,panels):
        if panel=='pesca_ck':
            df_pesca=df_sel[ df_sel.flow_desc=="Impaired flow Pe TIDAL" ]

            twinscale(ax,m2ft**3,"cfs")
            ax.set_ylabel('m$^3$/s')

            ax.semilogy(df_pesca.time, df_pesca.flow_cms,label="Pescadero Ck")
            ax.set_xlim(period)
            ax.set_ylim(Qlims)
            ax.legend(loc='upper left',frameon=False)
        elif panel=='pesca_ck_imp_unimp':
            df_pesca_imp  =df_sel[ df_sel.flow_desc=="Impaired flow Pe TIDAL" ]
            df_pesca_unimp=df_sel[ df_sel.flow_desc=="Unimpaired flow Pe TIDAL" ]

            twinscale(ax,m2ft**3,"cfs")
            ax.set_ylabel('m$^3$/s')

            ax.semilogy(df_pesca_imp.time, df_pesca_imp.flow_cms,label="Pescadero Ck, impaired")
            ax.semilogy(df_pesca_unimp.time, df_pesca_unimp.flow_cms,label="Pescadero Ck, unimpaired")
            ax.set_xlim(period)
            ax.set_ylim(Qlims)
            ax.legend(loc='upper left',frameon=False)
        elif panel=='lagoon_wse':
            twinscale(ax,m2ft,"ft NAVD88")
            ax.plot(qcm_sel.time, qcm_sel.z_lagoon,
                    label='Lagoon WSE')
            ax.legend(loc='upper left',frameon=False)
            ax.set_ylabel('m NAVD88')
        elif panel=='source_sink':
            twinscale(ax,m2ft**3,"cfs")
            # This used to omit the sign, but I think it makes more sense to negate
            # so that all 3 fluxes have consistent signs.
            # Undo the calcs from pesca_base to get back m3/s
            grid_area=1940000 # m2
            Q_ET=qcm_sel['evapotr_mmhour']*0.75*grid_area/(1000*3600)


            if 0:
                ax.plot(qcm_sel.time, Q_ET, label="ET")
                ax.plot(qcm_sel.time, -qcm_sel.seepage_abs,label="Seepage")
                ax.plot(qcm_sel.time, qcm_sel.wave_overtop,label="Wave overtop")
            else:
                qcm_dt=np.median( np.diff(qcm_sel.time)/np.timedelta64(3600,'s') )
                winsize=int(50/qcm_dt)
                def lp(x):
                    return filters.lowpass_fir(x,winsize=winsize)
                ax.fill_between(qcm_sel.time, lp(Q_ET), label="ET")
                ax.fill_between(qcm_sel.time, lp(Q_ET), lp(Q_ET-qcm_sel.seepage_abs),label="Seepage")
                ax.fill_between(qcm_sel.time, lp(qcm_sel.wave_overtop),label="Wave overtop")
                
            
            ax.legend(loc='upper left',frameon=False)
            ax.set_ylabel('m$^3$/s')
        elif panel=='wind':
            twinscale(ax,1.94,"kts")
            met_sel=met_ds.isel(time=(met_ds.time.values>=period[0])&(met_ds.time.values<=period[1]))
            ax.plot(met_sel.time, met_sel.u_wind,label='East component')
            ax.plot(met_sel.time, met_sel.v_wind,label='North component')
            ax.set_ylabel('Wind speed (m/s)')
    fig.autofmt_xdate()
    label_events(axs[-1])
    fig.subplots_adjust(left=0.10,top=0.98,right=0.90,bottom=0.10)
    return fig



# Similar plots, but each panel is one station.
def fig_waterlevel_bystation_timeseries(runs,station,label,as_depth=False,
                                        chain=True,min_depth=0.0,
                                        scen_styles=defaultdict(dict),
                                        zorder=['Low','Medium','High','Base']):
    # zorder: lowest to highest. default puts base on top, because in the lagoon
    # it has the smallest tidal range.
    fig,ax=plt.subplots(1,1,figsize=(7.5,4))

    datas=[] # double plural
    
    for _,rec in runs.iterrows():
        data = his_cache(rec['model'],stations=station,
                         variable='waterlevel',chain=chain)
        scen=rec['name']
        zord=2
        if scen in zorder:
            zord+=zorder.index(scen)
            
        if as_depth or min_depth>0.0:
            z_bed=his_cache(rec['model'],stations=station,variable='bedlevel',
                            chain=chain)
            depth=data-z_bed
            if as_depth:
                data=depth
            if min_depth>0.0:
                data=data.load().copy() # make dask happy, don't contaminate cache.
                data[depth<min_depth]=np.nan
                
        ax.plot(data.time, data,
                label=scen,
                lw=1.2,alpha=1,zorder=zord,**scen_styles[scen])
        datas.append(data)

    ax.legend(loc='upper center',bbox_to_anchor=[0.45,1.12],ncol=len(runs),
              frameon=0)
    label_events(ax)

    t_min=min([data.time.values[0] for data in datas])
    t_max=max([data.time.values[-1] for data in datas])
    ax.axis(xmin=t_min,xmax=t_max)

    if as_depth:
        ax.set_ylabel('Depth (m)')
    else:
        ax.set_ylabel('Stage (m)')
        
    ax.text(0.03,0.97,label,transform=ax.transAxes,ha='left',va='top')
    fig.autofmt_xdate()
    fig.subplots_adjust(right=0.98,left=0.1,top=0.92, bottom=0.14)
    return fig
