# Precip Analysis during Oxford Hackathon 2025

## Workflow

1. jupyternotebooks are developed in `nbooks`
2. notebooks are converted with e.g. `juconvert nbooks/06-Linking-of-Individual-Features.ipynb`
3. scripts are stored under `scripts` to make automated execution
4. runners under `scripts/runner`: for parallel submission of python script into levante slurm
4. starters under `scripts/runner`: used to actually start the submission


## Utilities

**python envs**
```bash
> conda activate /home/b/b380352/proj/2025-05_oxford-hackathon/hackathon_env
```

**jupyter converter**
```bash
> which juconvert
alias juconvert='jupyter nbconvert --to script --output-dir scripts/'
```

**parallel starter**

```bash
> export PATH=/work/bb1376/tools/utils:$PATH
```
