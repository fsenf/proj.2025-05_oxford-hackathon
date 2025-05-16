#!/bin/bash
#SBATCH --job-name=linker
#SBATCH --partition=shared
#SBATCH --time=02:00:00
#SBATCH --mail-type=FAIL
#SBATCH --account=bb1376
#SBATCH --output=LOG/my_job.%j.out
#SBATCH --mem=10G

# limit stacksize ... adjust to your programs need
# and core file size
ulimit -s 204800
ulimit -c 0


#module load python3/unstable
source $HOME/.bashrc
source $HOME/.bash_mambainit
conda activate /home/b/b380352/proj/2025-05_oxford-hackathon/hackathon_env

lfile=`readlink -f $1` 

cmd=./16-Explore-Tracking-in-Daily-Chunks.py

cd ..
start_proc_from_list -n 1 -p $cmd $lfile
cd -
