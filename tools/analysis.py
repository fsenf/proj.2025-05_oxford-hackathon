import tobac
import numpy as np
import xarray as xr
import pandas as pd

from spacetools import get_equivalent_size_for_reglonlat

######################################################################
######################################################################


def segmentation_with_tobac(
    v, thresholds, threshold_target="maximum", do_iris_conversion=True
):

    dxy = get_equivalent_size_for_reglonlat(v)

    if do_iris_conversion:
        RR = v.to_iris()
    else:
        RR = v

    # Dictionary containing keyword arguments for segmentation step:
    parameters_segmentation = {}
    parameters_segmentation["method"] = "watershed"
    parameters_segmentation["threshold"] = thresholds

    statistics = {}
    statistics[f"mean"] = np.mean
    statistics[f"total"] = np.sum
    statistics[f"max"] = np.max
    statistics[f"min"] = np.min

    for p in [0.1, 1, 5, 90, 95, 99, 99.9]:
        statistics[f"percentile{p}"] = (np.percentile, {"q": p})

    features = tobac.feature_detection_multithreshold(
        RR,
        dxy,
        thresholds,
        target=threshold_target,
        position_threshold="weighted_diff",
        statistic=statistics,
    )

    # a 2nd segmentation for aera calculation
    # --> this is inefficient and needs to be improved

    Mask_Precip, Features_Precip = tobac.segmentation_2D(
        features, RR, dxy, **parameters_segmentation
    )

    final_features = tobac.calculate_area(features, Mask_Precip)
    # final_features["time"] = xr.CFTimeIndex(final_features["time"].to_numpy()).to_datetimeindex()

    xfeat = final_features.to_xarray()

    return xfeat


######################################################################
######################################################################


def cumsum_data_fraction(h, divide_by_total_sum=True):
    """
    The function uses iso-lines of equal density and maps the fraction
    of data enclosed by these lines onto it.


    Parameters
    ----------
    h : numpy array (n-dim)
        histogram / density or other variable for which cumsum makes sense

    divide_by_total_sum : bool, optional, default = True
        switch if cumsum field should be divided by total sum
        this generates a relative field with range (0, 1)


    Returns
    --------
    f : numpy array (n-dim)
        data fraction field
    """

    # (i) make vector out of field matrix............................
    hvec = h.flatten()

    # (ii) sort the field ............................................
    hsort = np.sort(hvec)

    # (iii) calculate the ranks of the field .........................
    hrank = np.searchsorted(hsort, hvec)

    # (iv) cummulative sum of hsort ..................................
    hs = hsort[::-1]  # turn order

    if divide_by_total_sum:
        hc = 100.0 * hs.cumsum() / hs.sum()  # get cummulative sum / in percent
    else:
        hc = hs.cumsum()

    hc = hc[::-1]  # turn order back again

    # (v) map it onto the field structure ............................
    f = hc[hrank].reshape(h.shape)

    return f


######################################################################
######################################################################


def rank_transformation(f, normalize=True, gamma=1.0):
    """
    The routine performs rank transformation of a field, meaning that
    the ranks of the individual field values are returned.


    Parameters
    ----------
    f : numpy array (n-dim)
        field to be transformed

    normalize : bool, optional, default = True
        option if the rank field should be normalized to one

    gamma : float, optional, default = 1.
        gamma correction factor


    Returns
    --------
    f : numpy array (n-dim)
        field ranks
    """

    # (i) make vector out of field matrix............................
    fvec = f.flatten()

    # (ii) sort the field ............................................
    fsort = np.sort(fvec)

    # (iii) calculate the ranks of the field .........................
    frank = np.searchsorted(fsort, fvec).reshape(f.shape)

    # optional things ................................................
    if normalize:
        frank = (1.0 * frank) / frank.max()

    if gamma != 1:
        frank = frank**gamma

    return frank


######################################################################
######################################################################


def threshold_calculation(vname, variable, transformed_threshold):

    use_specific_threshold_calculation = True

    if "logstd" in vname:

        transformed_variable = log_standardize(variable)

    elif "rank" in vname:

        v_rank = 100 * rank_transformation(variable.data)

        transformed_variable = xr.zeros_like(variable)
        transformed_variable[:] = v_rank
        
    elif "cumsum" in vname:

        # change in area in ignored --> okay for healpix grid
        v_cumsum = cumsum_data_fraction(variable.data)

        transformed_variable = xr.zeros_like(variable)
        transformed_variable[:] = v_cumsum

    else:
        transformed_variable = variable
        use_specific_threshold_calculation = False


    if use_specific_threshold_calculation:
        deviation = np.abs(transformed_variable - transformed_threshold)

        argmin = deviation.load().argmin(("cell", "time"))

        variable_threshold = variable.isel(argmin).load().data.tolist()
    else:
        variable_threshold = transformed_threshold

    return variable_threshold


######################################################################
######################################################################


def log_standardize(RR, min_value=0, NaN_factor=-999):

    mask = RR > min_value
    NaN = NaN_factor * xr.ones_like(mask)

    logRR = xr.where(mask, np.log(RR), NaN)

    logRR_mean = logRR.where(mask).mean()
    logRR_std = logRR.where(mask).std()

    v = (logRR - logRR_mean) / logRR_std

    return v


######################################################################
######################################################################


def num2xr(num, date):

    z = xr.DataArray(np.zeros(1), dims=("date",))
    z["date"] = [
        date,
    ]
    z[:] = num

    return z


######################################################################
######################################################################


def monthly_cell_average_statistics(xfeat, date):

    # some important vars
    A = xfeat["area"] * 1e-6
    A.load()

    Deq = 2 * np.sqrt(A / np.pi)

    P = xfeat["total"]
    P.load()

    # initialize stats dataset
    stats = xr.Dataset()
    stats.expand_dims("date")
    stats["date"] = [
        date,
    ]

    # ### Total Number
    stats["total_number"] = num2xr(len(xfeat.index), date)

    # ### Total Area
    v = A.sum().data
    stats["total_area"] = num2xr(v, date)

    # ### Total Precip
    v = P.sum().data
    stats["total_precip"] = num2xr(v, date)

    # ### Area-weighted Diameter
    v = (Deq * A).sum() / A.sum()
    stats["area_weighted_diameter"] = num2xr(v, date)

    # ### Precip-weighted Diameter
    v = (Deq * P).sum() / P.sum()
    stats["precip_weighted_diameter"] = num2xr(v, date)

    # ## Cells that contribute 50%
    iidx = Deq.argsort().data  # sort from small to large
    Dsorted = Deq.isel(index=iidx)

    Afrac = A.isel(index=iidx).cumsum() / A.sum()  # fraction of area covered
    DA50_idx_of_sorted_array = np.abs(Afrac - 0.5).argmin()
    DA50_idx = Afrac.isel(index=DA50_idx_of_sorted_array.data).index

    DA50 = Deq.sel(index=DA50_idx)
    stats["diameter_contrib_50_to_area"] = num2xr(DA50, date)

    Pfrac = P.isel(index=iidx).cumsum() / P.sum()  # fraction of precip contributed
    DP50_idx_of_sorted_array = np.abs(Pfrac - 0.5).argmin()
    DP50_idx = Pfrac.isel(index=DP50_idx_of_sorted_array).index

    DP50 = Deq.sel(index=DP50_idx)
    stats["diameter_contrib_50_to_precip"] = num2xr(DP50, date)

    for vname in xfeat.data_vars:
        v = xfeat[vname]
        vm = v.mean("index")
        vm = vm.expand_dims("date")
        vm["date"] = [
            date,
        ]

        stats[f"{vname}_monthly_averaged"] = vm

    return stats


######################################################################
######################################################################
