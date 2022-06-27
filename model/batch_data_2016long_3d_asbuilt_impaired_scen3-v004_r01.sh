#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general

# back to local dfm. stock dfm quickly reported an 80d run time.
. /share/apps/intel-2019/bin/compilervars.sh intel64
PREFIX=/home/rustyh/src/dfm/t140737
export DFM_ROOT=$PREFIX/build/dfm/src/build_dflowfm/install
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime

python run_production_bmi.py --mdu data_2016long_3d_asbuilt_impaired_scen3-v004/flowfm.mdu --resume -p 2016long -s scen3 -f impaired