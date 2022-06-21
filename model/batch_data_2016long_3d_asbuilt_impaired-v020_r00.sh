#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general

# stock dfm
export DFM_ROOT=/home/rustyh/src/dfm/delft3dfm_2022.02/lnx64
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime

python run_production_bmi.py --mdu data_2016long_3d_asbuilt_impaired-v020/flowfm.mdu --resume -p 2016long 
