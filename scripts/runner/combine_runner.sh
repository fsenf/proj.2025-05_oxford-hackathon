#!/bin/bash
#SBATCH --job-name=combiner
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --mail-type=FAIL
#SBATCH --account=bb1376
#SBATCH --output=LOG/my_job.%j.out
#SBATCH --mem=0


# limit stacksize ... adjust to your programs need
# and core file size
ulimit -s 204800
ulimit -c 0



#module load python3/unstable
source $HOME/.bashrc
source $HOME/.bash_mambainit
conda activate /home/b/b380352/proj/2025-05_oxford-hackathon/hackathon_env


cmd=./05-Combine_Features.py

conf_file=`readlink -f $1` 
lfile=`readlink -f $2`


cd ..
start_proc_from_list -n 64 -p $cmd $lfile $conf_file
cd -


