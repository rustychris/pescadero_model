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
    flows='impaired'
))

# Not entirely sure what happened with r00.

# ---------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004_r00',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016long',
    status='complete', 
    flows='impaired'
))

# -----------------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00_r00',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016long',
    status='running',
    flows='impaired'
))

# 7/22: v007 got off to a rocky start with a bad node. 224d remaining, but projected 7d to go.
# 7/25: v007 173d / 9d to go.  meh.
# 8/1:  v007 111d / 9d to go. :-(
# 8/2:       103d / 9d to go. :-(((
# 8/3:       100d / 9d to go
# 8/5:        88d / 8.5d to go.
# 8/21:       12d / 7d to go.

# NEXT:
#   pray

# ----------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010_r00',
    scen=3,
    slr=0.0,
    period='2016long',
    layers=100,
    status='running',
    flows='impaired'
))

# v010: 191d remaining (8/1).  Checked 7/25 and it is 10 days out, 158d remaining. (8/4)
#     Checked 8/1, 74d remaining, (8/6 finish).
#     8/2 64d remaining. 8/6 finish.
#     8/5 48d remaining. 8/9 finish.
#    8/21: 7d / 3d remaining. 8/25 finish.

# NEXT:
#  - continue to check on v010

# -------------------------------

# SLR

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v006_r00',
    scen=0,
    layers=100,
    period='2016long',
    status='running',
    flows='impaired',
    slr=0.61
))
# 8/21: 48d / 9d remaining

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m_l100-v006',
    scen=1, layers=100, status='running', flows='impaired', slr=0.61,
    period='2016long'))

# 8/21: 37d / 4d remaining.


# Old grid:
# recs.append(dict(
#     run_dir='data_2016long_3d_asbuilt_impaired_scen3_slr0.61m_l100-v002',
#     scen=3,layers=100, status='stopped at 161d remaining', flows='impaired', slr=0.61))
# 
# recs.append(dict(
#     run_dir='data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v005',
#     scen=0,layers=100, status='stopped at 54d remaining', flows='impaired', slr=0.61))

# ----------------------


# NM Scenarios, 2D:
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired',
    scen=0,
    layers=1,
    period='2016',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen1-v001',
    scen=1,
    period='2016',
    layers=1,
    status='completed',
    flows='impaired'
))
    
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen2-v001',
    scen=2,
    layers=1,
    period='2016',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen3-v001',
    scen=3,
    layers=1,
    period='2016',
    status='completed',
    flows='impaired'
))

# 2D, tidal runs
recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired/flowfmrtidal.mdu',
    scen=0,
    layers=1,
    period='2016tidal',
    status='completed',
    flows='impaired'
))


recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen1/flowfmrtidal.mdu',
    scen=1,
    layers=1,
    period='2016tidal',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen2/flowfmrtidal.mdu',
    scen=2,
    layers=1,
    period='2016tidal',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016_2d_asbuilt_impaired_scen3/flowfmrtidal.mdu',
    scen=3,
    layers=1,
    period='2016tidal',
    status='completed',
    flows='impaired'
))

##

# 3D tidal runs
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v027rtidal',
    scen=0,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    flows='impaired'
))


recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rtidal',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rtidal',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rtidal',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016tidal',
    status='completed',
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
    flows='impaired'
))


recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_l100-v004rbreach',
    scen=1,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2_l100-v007_r00rbreach',
    scen=2,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    flows='impaired'
))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3_l100-v010rbreach',
    scen=3,
    layers=100,
    slr=0.0,
    period='2016breach',
    status='completed',
    flows='impaired'
))

#####################
all_runs=pd.DataFrame(recs)
