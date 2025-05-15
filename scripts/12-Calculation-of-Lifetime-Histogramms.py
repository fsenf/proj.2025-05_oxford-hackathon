#!/usr/bin/env python
# coding: utf-8

# # Calculation of Lifetime Histogramms

# ## Libs Sections 

# In[1]:


import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
#sns.set_context('talk')
import cartopy.crs as ccrs
import cartopy.feature as cf


import glob

import tobac
import sys
import json
import datetime


# ## Arguments

# In[2]:


if 'launcher' in sys.argv[0]:
    config_file = '../scripts/config/config_precip200.json'
    date = '202006'
    interactive = True
else:
    config_file = sys.argv[1]
    date = sys.argv[2]
    interactive = False


# ## Configuration

# In[3]:


with open(config_file, "r") as fp:
    conf = json.load(fp)
globals().update(conf)


# ## Input Data 

# In[ ]:


main_dir = "/work/bb1376/user/fabian/data/oxford-hackathon"
subname = f"{vname}_tracks_thresh{threshold}"

input_dir = f"/{main_dir}/{model}/{experiment}/tracks"
infile = f'{input_dir}/monthly_{subname}_{date}.nc'

tracks = xr.open_dataset( infile, chunks = 'auto' )

# tracks = tracks.isel(index = slice(0,100000)).load()

tracks = tracks.dropna('index').load()

tracks['ones'] = xr.ones_like(tracks['total'])
del tracks['timestr']


# ## Lifetime Calculations

# In[ ]:


tg = tracks.groupby('cell')


# In[ ]:


track_sum = tg.sum()


# In[ ]:


t0 = datetime.datetime(2020,6,1)
track_sum['time'] = np.datetime64(t0) + track_sum['time_cell']


# In[ ]:


dt = 0.25
d = xr.Dataset()
d['lifetime'] = dt * track_sum['ones']
d['time'] = track_sum['time']


# In[ ]:


d


# In[ ]:


d['lifetime'].min(), d['lifetime'].max()


# In[ ]:


dt = 1
lifetime_bins = np.arange(0,48, dt)
ltime_mean = 0.5 * (lifetime_bins[1:] + lifetime_bins[:-1])


# In[ ]:


clist = []
n = 0
for time, tr in d.groupby('time.day'):
    counts, _ = np.histogram( tr['lifetime'], bins=lifetime_bins )
    cset = xr.DataArray(counts.reshape(-1,1), coords=[lifetime_bins[:-1], [time,]], dims=['lifetime', 'day'])

    clist +=[ cset,]
    n += 1


# In[ ]:


c = xr.concat( clist, dim = 'day')
PDF_daily = c / (c.sum('lifetime') * dt )


# ## Plotting

# In[ ]:


if interactive:
    mPDF = PDF_daily.mean('day')
    semPDF = 2*PDF_daily.std('day') / np.sqrt(30)

    plt.errorbar(ltime_mean, mPDF, yerr = semPDF ) 
    sns.despine()
    plt.xlabel('lifetime / hr')
    plt.ylabel('PDF $dP / dT$')
    plt.title(f'Precip Cell Lifetime Distribution (cells > 50 mm day-1) for {date}', fontweight = 'bold') 
    #plt.xscale('log')
    plt.yscale('log')
    #plt.xticks( [25, 50, 100, 200], [25, 50, 100, 200]);


# ## Output

# In[ ]:


main_dir = "/work/bb1376/user/fabian/data/oxford-hackathon"
outdir = f"/{main_dir}/{model}/{experiment}/statistics"

PDF_daily.attrs['name'] = 'PDF_Lifetime'
PDF_daily.attrs['long_name'] = 'PDF of global lifetime distribution'
PDF_daily.attrs['unit'] = '-'

outfile = f'{outdir}/global_lifetime_{subname}_{date}.nc'


# In[ ]:


out = xr.Dataset()
out['PDF_CSD'] = PDF_daily
out.to_netcdf( outfile )

