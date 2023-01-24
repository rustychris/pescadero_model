#!/bin/sh

# this is the finally completed step of the old setup. Minor problem though-
# it used the new code which allows the berm to overtop. That's probably going
# to give bad results since the earlier part of the run is not like that.

#      	data_2013_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v000_r00

# verify that the restart that actually finished has the new script: YES
# verify that the restart actually rewrote the mouth inputs: NO.
# so that restart is valid. Should be okay for the non-overtopping runs.

# The one that had a tough time finishing and is currently truncated in the report
# is 2013 unimpaired SLR.

# These are the new runs, with flow over the berm.
./show_status \
        data_2013_3d_asbuilt_impaired_scen0_l100-v001 \
        data_2013_3d_asbuilt_impaired_scen0_slr0.61m_l100-v001 \
       	data_2013_3d_asbuilt_unimpaired_scen0_l100-v001 \
        data_2013_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v001 \
	data_2016long_3d_asbuilt_impaired_scen0_l100-v028_r00 \
	data_2016long_3d_asbuilt_impaired_scen0_slr0.61m_l100-v007 \
	data_2016long_3d_asbuilt_unimpaired_scen0_l100-v001 \
	data_2016long_3d_asbuilt_unimpaired_scen0_slr0.61m_l100-v001 



#                JOBID PARTITION     NAME     USER  ACCOUNT ST        TIME   TIME_LEFT NODES CPU MIN_ME NODELIST(REASON)
#             59293562     high2    pesca   rustyh rustyhgr  R 24-00:31:14 10-23:28:46     1 32  1000M  c6-58
#             59293555     high2    pesca   rustyh rustyhgr  R 24-00:31:46 15-23:28:14     1 32  1000M  c4-89
#             59293554     high2    pesca   rustyh rustyhgr  R 24-00:32:00 25-23:28:00     1 32  1000M  c4-89
#             59293550     high2    pesca   rustyh rustyhgr  R 24-00:32:17 15-23:27:43     1 32  1000M  c4-89
#             60354285     high2    pesca   rustyh rustyhgr  R       45:04 49-23:14:56     1 32  1000M  c6-66
#             60354284     high2    pesca   rustyh rustyhgr  R       59:09 34-23:00:51     1 32  1000M  c6-77
