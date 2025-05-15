import xarray as xr
import numpy as np

import healpy

######################################################################
######################################################################

def get_nn_lon_lat_index(dataset, lons, lats):
    
    lon = xr.DataArray(lons, dims=("lon",), name="lon", attrs=dict(units="degrees", standard_name="longitude"))
    lat = xr.DataArray(lats, dims=("lat",), name="lat", attrs=dict(units="degrees", standard_name="latitude"))
    
    pix = xr.DataArray(
        healpy.ang2pix(dataset.crs.healpix_nside, *np.meshgrid(lon, lat), nest=True, lonlat=True),
        coords=(lat, lon),
    )
    return pix

######################################################################
######################################################################

def get_equivalent_size_for_reglonlat( d_lon_lat ):
    
    

    dlon = d_lon_lat.lon.diff('lon').mean().data
    dlat = d_lon_lat.lat.diff('lat').mean().data

    lat0 = d_lon_lat.lat.data




    R_earth = 6371e3

    dlambda = np.deg2rad( dlon )
    dphi = np.deg2rad( dlat )
    phi0 = np.deg2rad( lat0 )

    dA = R_earth**2 * np.cos( phi0 ) * dphi * dlambda

    dX = np.sqrt( dA.mean() )
    
    return dX

######################################################################
######################################################################
