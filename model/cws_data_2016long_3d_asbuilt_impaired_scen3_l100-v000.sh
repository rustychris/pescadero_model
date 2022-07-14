#!/bin/bash 

. /opt/anaconda3/bin/activate general
. /home/rusty/intel/oneapi/setvars.sh

export DFM_ROOT=/opt/delft3dfm_2022.03/lnx64
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

# start with v001 so all runs have the suffix
python run_production_bmi.py --run-dir datacws_2016long_3d_asbuilt_impaired_scen3_l100-v001 -n 16 --three-d --terrain asbuilt -l 100 -p 2016long -f impaired -s scen3



