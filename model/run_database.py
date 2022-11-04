import pandas as pd
import stompy.model.delft.dflow_model as dfm

recs=[]

#
# NM Scenarios, 100 Layer, Present SL
# ==

# ----------------------
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027_r01',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004_r00',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete', 
    terrain='asbuilt',
    flows='impaired'
))

# -----------------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00_r00',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
))

# ----------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010_r00',
    scen=3,
    slr=0.0,
    period='2016long',
    layers=100,
    status='complete',
    terrain='asbuilt',
    flows='impaired'
))

# -------------------------------

# SLR

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006_r01',
    scen=0,
    layers=100,
    period='2016long',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
))
# tidal version of that
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006rtidal2',
    scen=0,
    layers=100,
    period='2016tidal',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
))
# breach version
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006_r00rbreach',
    scen=0,
    layers=100,
    period='2016breach',
    status='complete',
    flows='impaired',
    terrain='asbuilt',
    slr=0.61
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006_r00',
    scen=1, layers=100, status='complete', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long'))

# tidal version
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006rtidal2',
    scen=1, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal'))

# breach version
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006rbreach',
    scen=1, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach'))

recs.append(dict(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000',
    scen=2, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long'))

# tidal version
recs.append(dict(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000rtidal2',
    scen=2, layers=100, status='queued', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal'))

# Breach version
recs.append(dict(
    run_dir='datacws_2016long_3d_asbuilt_impaired_scen2_slr0.61m_l100-v000rbreach',
    scen=2, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach'))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003',
    scen=3, layers=100, status='running', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016long'))

# tidal version
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003rtidal2',
    scen=3, layers=100, status='queued', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016tidal'))

# breach version -- this one failed with bus error. running a new copy. this one
# has maybe 6 days of output already.  Too much work to continue that run.
recs.append(dict(
    run_dir='temp-data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v003rbreach',
    scen=3, layers=100, status='interrupted', flows='impaired', slr=0.61,
    terrain='asbuilt',
    period='2016breach'))

# ----------------------

# NM Scenarios, 2D:
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired',
    scen=0,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen1-v001',
    scen=1,
    period='2016',
    layers=1,
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))
    
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen2-v001',
    scen=2,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen3-v001',
    scen=3,
    layers=1,
    period='2016',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

# 2D, tidal runs
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired/flowfmrtidal.mdu',
    scen=0,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))


recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen1/flowfmrtidal.mdu',
    scen=1,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen2/flowfmrtidal.mdu',
    scen=2,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen3/flowfmrtidal.mdu',
    scen=3,
    layers=1,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

##

# 3D tidal runs
recs.append(dict(
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
))


recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rtidal2',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rtidal2',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016tidal',
    terrain='asbuilt',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rtidal2',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))


# 3D breach runs
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027rbreach',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))


recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rbreach',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rbreach',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rbreach',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    terrain='asbuilt',
    flows='impaired'
))

# 2013 and unimpaired flow runs

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_unimpaired_scen0_l100-v000_r01',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='running',
    terrain='asbuilt',
    flows='unimpaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v000_r01',
    scen=0,
    layers=100,
    slr=0.61,
    period='2016long',
    status='running',
    terrain='asbuilt',
    flows='unimpaired'
))

recs.append(dict(
    run_dir='data_2013_3d_asbuilt_impaired_scen0_l100-v000',
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    status='complete',
    terrain='asbuilt',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2013_3d_asbuilt_unimpaired_scen0_l100-v000_r01',
    scen=0,
    layers=100,
    slr=0.0,
    period='2013',
    terrain='asbuilt',
    status='resumed',
    flows='unimpaired'
))

recs.append(dict(
    run_dir='data_2013_3d_asbuilt_impaired_scen0_slr0.61m_l100-v000_r00',
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    terrain='asbuilt',
    status='running',
    flows='impaired'
))

# There is a run for this on cws that is probably completed, but inaccessible.

recs.append(dict(
    run_dir='data_2013_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v000',
    scen=0,
    layers=100,
    slr=0.61,
    period='2013',
    terrain='asbuilt',
    status='running',
    flows='unimpaired'
))


#########

recs.append(dict(
    run_dir='data_2016long_3d_existing_impaired_scen0_l100-v000',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016long',
    status='running',
    flows='impaired',
    terrain='existing'
))


#####################
all_runs=pd.DataFrame(recs)


def select(load_model=False,single=False,**kw):
    sel=None
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


