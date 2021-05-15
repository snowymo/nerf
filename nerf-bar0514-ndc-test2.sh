#!/bin/bash

#SBATCH --job-name=bar0514Test
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=128GB
#SBATCH --time=23:00:00
#SBATCH --gres=gpu:1

module purge

source /scratch/zh719/anaconda3/etc/profile.d/conda.sh
export PATH=/scratch/zh719/anaconda3/bin:$PATH
conda activate nerf

cd /scratch/zh719/nerf

python run_nerf.py --config config_bar0514.txt --NDC True --render_only --render_test

