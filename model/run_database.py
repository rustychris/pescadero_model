import pandas as pd
import stompy.model.delft.dflow_model as dfm

recs=[]

#
# NM Scenarios, 100 Layer, Present SL
# ==

# ----------------------
recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired-v020_r01',
    scen=0,
    layers=100,
    status='resumed running',
    flows='impaired'
))

# v020 got to 60%, but it's unclear what stopped it. salt balance is okay 0.0012% a few times.
# could not determine cause of death.
# - cause of death for v020?
#    jobid 49591184 (with siblings)
#    no hints in log-*, *.dia, slrum.out only talks about v022
#    unclear.
# v022 has clean salt, at least up to 50% complete. killed, b/c v020 was further along.

# resumed v020 with batch_data_2016long_3d_asbuilt_impaired-v020_r00.sh
# job 51028340

# that got wedged, quickly jumping up to an 80 day run time.
# resumed from the same spot, but back to local DFM, and it's looking much
# better. killed r00

# NEXT: 
#   Check on r01
#   - check salt balance. 6/21 - good
#   - currently on track to finish 7/1
# 


# ---------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen1-v002',
    scen=1,
    layers=100,
    status='running', 
    # 6/17: anticipate 6/28 finish
    flows='impaired'
))
# squeue shows it still running?
#   looks like the job_id is fucked here, too.
#   the -v002 run has the same job_id, and maybe is the one still running.
# v001 died at 49.6%. Mass balance okay so far.
# v002? also 100 layers. at 48%. running, and mass balance okay.
# let v002 continue, keep v001 as a backup. 

# on 6/17, anticipated a 6/28 finish.
# now on 6/19, looking like a 7/1 finish, and it's running slower than realtime.
# it's at 122d in, dt=0.15, 2016-10-31: this is the partial breach.
# 6/21/22: at 12/01, nearing the big breach, 

# 6/21 - hit time limit.  resumed 51113704

# NEXT: 
#  - check on resumed run

# -----------------------------------


recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2-v004_r00',
    scen=2,
    layers=100,
    status='running',
    # on 5am PDT, 6/17:
    #   10d 10:48 remaining, anticipate a 6/27 finish
    # 1pm PDT, 6/19:
    #    9d 22:46 remaining. 6/28 finish.
    # 4am PDT, 6/21:
    #    9d 23:48 remaining.
    flows='impaired'
))
# v004 is also 100 layers, it's running, it's at 50.3%
#   salt balance okay
# 6/21: resumed to r00, job id 51108911


# NEXT:
#  - check progress of v004_r00. Is it any faster/less wedged than
#    the parent run?

# ----------------------------

# similar to the 30 layer version of this (v003, later v005),
# this has stalled out. It's at 67.5%, 163d
# dt is down to 0.016s, with 64 substeps for scalar.
# will kill this, in order to see if the restart of v003 is telling
# at all. then consider a restart using the standard compile
recs.append(dict(
    # presumably switching to r01 run. r00 got wedged.
    run_dir='data_2016long_3d_asbuilt_impaired_scen3-v004_r01',
    scen=3,
    layers=100,
    status='dead',
    flows='impaired'
))
# ends with some moderate salt issues.
# restart before 12/10.  the 1208 restart is fine
# restarting, job id 51028409
# this went to 80days expected run time.
# switch back to local dfm and resume again (from original) => r01
# it went for 3 days, then stuck again. granted, this is the big breach.
# but it's going to take forever.

# added more debugging, started an r02 in parallel with r01.
# also started a fresh run, 51109133, -v006, with the other option for 
# keepzlayeringatbed.


# NEXT:
#  - check on progress, balance of restart
#  - check on progress of the fresh run.
#  - consider intensive debugging

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
    run_dir='data_2016long_3d_asbuilt_impaired_scen1'
    scen=1,
    layers=30,
    status='complete',
    flows='impaired'
))


# ----------------------------

recs.append(dict(
    run_dir='data_2016long_3d_asbuilt_impaired_scen2-v002'
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




