import pandas as pd
import stompy.model.delft.dflow_model as dfm

recs=[]

#
# NM Scenarios, 100 Layer, Present SL
# ==

# ----------------------
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen0_l100-v026',
    scen=0,
    layers=100,
    status='resumed running',
    flows='impaired'
))

# v022 has clean salt, at least up to 50% complete. killed, b/c v020 was further along.
# resumed v020 with batch_data_2016long_3d_asbuilt_impaired-v020_r00.sh, but stock dfm wedged.
# resumed from the same spot, with local DFM
# started a new run with new grid:
#  data_2016long_3d_asbuilt_impaired_scen0_l100-v024
# two more grid updates, and we're at v026, which looks promising.

# NEXT: 
#   Check on r01 -- on track to finish 7/6.
#   Check on v026 -- on track to finish 7/6

# ---------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1-v003',
    scen=1,
    layers=100,
    status='running', 
    # 6/24: anticipate 7/12 finish roughly 
    flows='impaired'
))
# v001 died at 49.6%. Mass balance okay so far. keep as backup
# let v002 continue as the main run
# was bogging down during the breaches and hit time limit
# 6/21 resumed 51113704.
# 6/22: very slow - predicting 21d 10h run for 112 days.
#   this is around 2016-11-09 -- shouldn't be that slow...
#   a lot of substepping, scalar is at dt=0.01s
# 6/24: still pretty slow -- looks like almost 20d remaining for 98d
#   global dt 1.7s, okay. limitation on proc 9, 15. proc 9: getting stuck in a layer
#   with volume 0.0864. flows don't look crazy, I think it's just a really shallow layer.
# 6/30: stopped scen1-r00 to try run with new grid. accidentally nuked v002. v001
#   remains as a backup.

# NEXT: 
#  - check for progress on v003

# -----------------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2-v004_r01',
    scen=2,
    layers=100,
    status='running',
    flows='impaired'
))
# v004 is also 100 layers, it's running, it's at 50.3%
#   salt balance okay. I think it died in the mysterious way that others have died (editing driving script)
#   and then a bug in restarts led to restarts being bad.
# r00 resume suffered from restart bug.  -- archived
# r01 started 6/23, but was slow. killed.
# new r00 started with old DFM compile.  Got slow around 11/27/2016, projecting 40 days.
#   Gambling on the new grid, killed r00.

# Substantial grid edits, and started a new data_2016long_3d_asbuilt_impaired_scen2_l100-v005
# At 24h, it's 18 days in, projecting a 13 day run total.
# - salt balance? fine so far.

# NEXT:
#  - check progress of v005

# ----------------------------

# similar to the 30 layer version of this (v003, later v005),
# this has stalled out. It's at 67.5%, 163d
# dt is down to 0.016s, with 64 substeps for scalar.
# will kill this, in order to see if the restart of v003 is telling
# at all. then consider a restart using the standard compile
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3-v004_r00',
    scen=3,
    layers=100,
    status='dead',
    flows='impaired'
))

# r00, r01, r02: these are basically useless, as they had the wrong fixed weirs, and have been
# archived.

# v006: projecting 24 days total
# v007: projecting 71 days. wtf? this should be similar to previous runs, just with more output?
#       it should be using the new compile. possible it's on a bad node.
#       node seems okay. but most(?) of the processes for this run are using a fraction of available
#       CPU. Makes me wonder if one node is substepping a huge amount. only oddity in the output
#       is proc 4 has 40 "nonglobal" -- a lot more than anyone else. also proc 7 gets some negative
#       salinity. unclear what's going on.  for now, let it ride.
#       Eventually killed it. 

# ends with some moderate salt issues.
# restart before 12/10.  the 1208 restart is fine

# added more debugging, tried and failed to resume with new compile (r02)
# also started a fresh run, 51109133, -v006, with the other option for 
# keepzlayeringatbed.
# and a fresh start v007, with the new debugging output.

# found bug in restarts for scenario 2, scenario 3, and all SLR runs.
# r03 is now running, should be better. but it's a slow compile for some reason.
# a new r00 is now running, and looking a lot faster. This new r00 got wedged around Jan 7, 2017.

# Substantial grid edits, and started a new data_2016long_3d_asbuilt_impaired_scen3_l100-v008
# At 24h, it's 18 days in, projecting a 13 day run total.
# Trying to decide if/when to switch horses.
# - salt balance? fine (not surprising, it's early)


# NEXT:
#  - check on progress, balance of r03, and r00
#  - check on progress of the fresh run.

# -------------------------------

# NM Scenarios, 30 Layers, Present SL
# ==


# I thought one of 17,18,19 were supposed to be a correct
# run with evap. 

# v019 was stopped after a few days, at 47% complete. CANCELLED by 1515435
# v018 similarly stopped, at 35.9% complete. -- CANCELLED by 1515435
# v017 stopped at 31% -- CANCELLED by 1515435
# v016: Completed, but no evaporation

# recs.append(dict(
#     run_dir='data_2016long_3d_asbuilt_impaired-v016',
#     scen=0,
#     layers=30,
#     status='complete misconfigured',
#     flows='impaired',
#     comments='no evap, replacement queued'
# ))

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired-v023',
    scen=0,
    layers=30,
    status='complete salty', 
    flows='impaired',
    comments='replaced a slow run'
))


# ----------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1',
    scen=1,
    layers=30,
    status='complete',
    flows='impaired'
))


# ----------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2-v002',
    scen=2,
    layers=30,
    status='complete',
    flows='impaired'
))


# --------------------


# lots of substepping, dt=0.03s.
# stuck at 191 days, 79.2%
# Check on this run -- is it toast?
# Appears to have gone salty.
# It's having salt mass balance problems.
# though it's not entirely clear what's going on,
# esp. since evaporation is included.
# It slowed down from dt=0.5 to 0.04 at 190d 14:40
# Currently at 191d 15:00
# numlimdt shows a non-strafied cell up on Pescadero on
# the inside of a bend.

# duplicate run is also going, v005. Not entirely sure why.
# v003 has 1e-7 diffusivity, v005 has 1e-8
# recs.append(dict(
#     run_dir='data_2016long_3d_asbuilt_impaired_scen3-v003',
#     scen=3,
#     layers=30,
#     status='salty, stuck, cancelled',
#     flows='impaired'
# ))

recs.append(dict(
    # an r00 restart, with stock dfm, did not get very far.
    # praying that r01, with local dfm, does better.
    run_dir='data_2016long_3d_asbuilt_impaired_scen3-v003_r01',
    scen=3,
    layers=30,
    status='resumed running',
    flows='impaired'
    # picks up from v003 before salt issues come up
))

# This got to 29.8%, and is not running any more?
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen3-v005',
    scen=3,
    layers=30,
    status='dead',
    flows='impaired'
))

# broken, but focus on fixing 100 layer runs.
# NEXT:
# - could try more restarts, though it only got 10 days with r00, may not
#   even have a usable restart file.
# - lower priority for now.
# - cause of death for v005?

# -------------------------

# NM Scenarios, 30 Layers, 2ft SLR
# ==

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_slr0.61m-v003',
    scen=0,
    layers=30,
    # some steps of 4+% salt balance error.
    status='completed salt_imbalance',
    flows='impaired',
    slr=0.61
))
# There is also a v004 run with the only difference that background 
# viscosity is 1e-6 instead of 1e-7.this run also salt imbalance issues.
# Both of these include CFLmax=0.4.
# So either that's not enough, or perhaps evaporation is causing problems.
# the v004 appears to be dead, ran with the same job id as v003, and now
# there is a v005, also same job id. It's like these runs keep getting 
# resubmitted. deleted v005 since it's useless.


# ------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1_slr0.61m',
    scen=1,
    layers=30,
    status='completed salt_imbalance',
    flows='impaired',
    slr=0.61
))


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



#####################
all_runs=pd.DataFrame(recs)
