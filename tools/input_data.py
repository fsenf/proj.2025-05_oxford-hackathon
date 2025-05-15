
import intake
import xarray as xr
import numpy as np

import analysis



######################################################################
######################################################################

def input_icon_hamlite( time_str, experiment = 'r2b9_lite_1224b', vname = None ):
    
    indir = f'/work/bb1368/b381642/experiments/{experiment}_post/005deg'
    
    fname = f'{indir}/{experiment}_atm_2d_vid_ml_*T000000Z.nc'

    dataset = xr.open_mfdataset( fname, chunks = 'auto' )
    dataset = dataset.sel(time = [time_str,])

    if vname is not None:
        variable_preparations( vname, dataset )

    return dataset

######################################################################
######################################################################




def input_icon_nextgems( time_str, exp_id = "ngc4008", zoom = 9, vname = None ):

    cat = intake.open_catalog("https://data.nextgems-h2020.eu/catalog.yaml")
    dataset = cat.ICON[exp_id](zoom=zoom, time = 'PT3H',
                              # chunks = 'auto'
                              ).to_dask( )

    dataset = dataset.sel(time = time_str)
    
    if vname is not None:
        variable_preparations( vname, dataset )
        
    return dataset

######################################################################
######################################################################


def variable_preparations( vname, dataset ):
    
    
    if  'precip' in vname:
        dataset[vname] = 3600 * 24 * ( dataset['pr'] )  # unit convetion to mm day-1
        dataset[vname].attrs['units'] = 'mm day-1'
        dataset[vname].attrs['long_name'] = 'rain rate'


    elif 'fwp' in vname:
        dataset[vname] = 1e3* (dataset['clivi'] + dataset['qsvi'])
        dataset[vname].attrs['units'] = 'g m-2'
        dataset[vname].attrs['long_name'] = 'frozen water path'

######################################################################
######################################################################


def get_geonames_from_features( xfeat ):
    geodir = '/work/bk1415/b380352/data/aux'

    geofile = f'{geodir}/georegion_reglonlat_30x30.nc'

    geo = xr.open_dataset( geofile )

    geoindex = geo.sel( lon = xfeat.longitude, lat = xfeat.latitude, method = 'nearest' )['georegions']

    Georegions_list = list( np.hstack( geo.region_names.sel( label_index = geoindex.data ).data ) )

    geonames = xr.full_like( geoindex, 'GeoRegion', dtype = '<U10')
    geonames[:] = Georegions_list

    return geonames