#!/bin/bash
#SBATCH --job-name=runner
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --exclusive
#SBATCH --time=08:00:00
#SBATCH --mail-type=FAIL
#SBATCH --account=bb1376
#SBATCH --output=LOG/my_job.%j.%a.out
#SBATCH --mem=0
#SBATCH --array=0-9


# limit stacksize ... adjust to your programs need
# and core file size
ulimit -s 204800
ulimit -c 0



#module load python3/unstable
source $HOME/.bashrc
source $HOME/.bash_mambainit
conda activate /home/b/b380352/proj/2025-05_oxford-hackathon/hackathon_env


cmd=./segmentation_analysis.py

conf_file_trunc=`readlink -f $1` 
lfile=`readlink -f $2`

conf_file=${conf_file_trunc}0${SLURM_ARRAY_TASK_ID}

cd ..
start_proc_from_list -n 64 -p $cmd $lfile $conf_file
cd -


