#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH --mem-per-cpu 4G
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --time 5-00:00:00

conda activate general
python run_highflow_2019.py
