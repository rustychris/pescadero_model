import pandas as pd
import stompy.model.delft.dflow_model as dfm

recs=[]

def register(**kw):
    if 'overtop' not in kw:
        kw['overtop']=False
        
    recs.append(dict(kw))
    
#
# NM Scenarios, 100 Layer, Present SL
# ==

# ----------------------
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027_r01',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004_r00',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete', 
    terrain='asbuilt',
    flows='impaired'
)

# -----------------------------------

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00_r00',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
)

# ----------------------------

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010_r00',
    scen=3,
    slr=0.0,
    period='2016long',
    layers=100,
    status='complete',
    terrain='asbuilt',
    flows='impaired'
)

# -------------------------------

# SLR

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006_r01',
    scen=0,
    layers=100,
    period='2016long',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
)
# tidal version of that
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006rtidal2',
    scen=0,
    layers=100,
    period='2016tidal',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
)
# breach version
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006_r00rbreach',
    scen=0,
    layers=100,
    period='2016breach',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006_r00',
    scen=1, layers=100, status='complete', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long')

# tidal version
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006rtidal2',
    scen=1, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal')

# breach version
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006rbreach',
    scen=1, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach')

register(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000',
    scen=2, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long')

# tidal version
register(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000rtidal2',
    scen=2, layers=100, status='queued', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal')

# Breach version
register(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000rbreach',
    scen=2, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach')

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003',
    scen=3, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long')

# tidal version
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003rtidal2',
    scen=3, layers=100, status='queued', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal')

# breach version -- this one failed with bus error. running a new copy. this one
# has maybe 6 days of output already.  Too much work to continue that run.
register(
    run_dir='temp-data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003rbreach',
    scen=3, layers=100, status='interrupted', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach')

# ----------------------

# NM Scenarios, 2D:
register(
    run_dir='data_2016_2d_asbuilt_impaired',
    scen=0,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016_2d_asbuilt_impaired_scen1-v001',
    scen=1,
    period='2016',
    layers=1,
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)
    
register(
    run_dir='data_2016_2d_asbuilt_impaired_scen2-v001',
    scen=2,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016_2d_asbuilt_impaired_scen3-v001',
    scen=3,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

# 2D, tidal runs
register(
    run_dir='data_2016_2d_asbuilt_impaired/flowfmrtidal.mdu',
    scen=0,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)


register(
    run_dir='data_2016_2d_asbuilt_impaired_scen1/flowfmrtidal.mdu',
    scen=1,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016_2d_asbuilt_impaired_scen2/flowfmrtidal.mdu',
    scen=2,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016_2d_asbuilt_impaired_scen3/flowfmrtidal.mdu',
    scen=3,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

##

# 3D tidal runs
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027rtidal2',
    # this one is only 36h
    #run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027rtidal',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)


register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rtidal2',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rtidal2',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016tidal',
    terrain='asbuilt',
    status='completed',
    flows='impaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rtidal2',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)


# 3D breach runs
register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027rbreach',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)


register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rbreach',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rbreach',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rbreach',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
)

# 2013 and unimpaired flow runs

register(
    run_dir='data_2016long_3d_asbuilt_unimpaired_scen0_l100-v000_r01',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='running',
    terrain='asbuilt',
    flows='unimpaired'
)

register(
    run_dir='data_2016long_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v000_r01',
    scen=0,
    layers=100,
    slr=0.61,
    period='2016long',
    status='running',
    terrain='asbuilt',
    flows='unimpaired'
)

register(
    run_dir='data_2013_3d_asbuilt_impaired_scen0_l100-v000',
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
)

register(
    # run_dir='data_2013_3d_asbuilt_unimpaired_scen0_l100-v000_r01',
    # Sort of breaks the overtop logic. this is an overtop=True run, but
    # register will set overtop=False.
    # This is the only run where overtopping makes a difference. I can't just
    # switch everything to overtopping runs, because the SLR overtopping runs
    # aren't complete. And I'm too lazy to introduce another layer of 'default'
    # status.
    run_dir="data_2013_3d_asbuilt_unimpaired_scen0_l100-v001",
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    terrain='asbuilt',
    status='complete',
    flows='unimpaired'
)

register(
    run_dir='data_2013_3d_asbuilt_impaired_scen0_slr0.61m_l100-v000_r00',
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    terrain='asbuilt',
    status='running',
    flows='impaired'
)

register(
    run_dir='data_2013_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v000_r00',
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    terrain='asbuilt',
    status='running',
    flows='unimpaired'
)


#########

register(
    run_dir='data_2016long_3d_existing_impaired_scen0_l100-v000',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='running',
    flows='impaired',
    terrain='existing'
)

##### Overtopping runs:
# only worrying about the unimpaired flows ones for now...

register(
    run_dir="data_2013_3d_asbuilt_unimpaired_scen0_l100-v001",
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    status='complete',
    flows='unimpaired',
    terrain='asbuilt',
    overtop=True
)

register(
    run_dir="data_2013_3d_asbuilt_impaired_scen0_l100-v001",
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    overtop=True
)

# This one appears not to have the overtopping though!
# verified it's not the same run as the non-overtopping run (that's v000)
# run_production_bmi looks okay.
register(
    run_dir="data_2013_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v001",
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    status='running',
    flows='unimpaired',
    terrain='asbuilt',
    overtop=True,
)

register(
    run_dir="data_2013_3d_asbuilt_impaired_scen0_slr0.61m_l100-v001",
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    status='running',
    flows='impaired',
    terrain='asbuilt',
    overtop=True,
)

register(
    run_dir="data_2016long_3d_asbuilt_unimpaired_scen0_l100-v001",
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete',
    flows='unimpaired',
    terrain='asbuilt',
    overtop=True,
)

register(
    run_dir="data_2016long_3d_asbuilt_impaired_scen0_l100-v028_r00", # there is also a v001 that's running, not sure why.
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='truncated',
    flows='impaired',
    terrain='asbuilt',
    overtop=True,
)

register(
    run_dir="data_2016long_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v001",
    scen=0,
    layers=100,
    slr=0.61,
    period='2016long',
    status='running',
    flows='unimpaired',
    terrain='asbuilt',
    overtop=True,
)


register(
    run_dir="data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v007",
    scen=0,
    layers=100,
    slr=0.61,
    period='2016long',
    status='running',
    flows='impaired',
    terrain='asbuilt',
    overtop=True,
)

#####################
all_runs=pd.DataFrame(recs)


def select(load_model=False,single=False,**kw):
    sel=None
    if 'overtop' not in kw:
        kw['overtop']=False
        
    for k in kw:
        v=kw[k]
        if isinstance(v,list):
            sel_k=all_runs[k].isin(v)
        else:
            sel_k=all_runs[k]==v
        if sel is None:
            sel=sel_k
        else:
            sel=sel & sel_k
    runs=all_runs[sel].copy()
    if load_model:
        def load_or_none(rd):
            try:
                return dfm.DFlowModel.load(rd)
            except FileNotFoundError:
                return None
        runs['model']=runs['run_dir'].map(load_or_none)
    if single:
        assert len(runs)==1
        return runs.iloc[0,:]
    return runs


