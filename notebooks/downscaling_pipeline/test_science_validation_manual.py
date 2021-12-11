import pytest
import xarray as xr
import numpy as np
from science_validation_manual import *

def _datasetfactory(x, start_time="1950-01-01", variable_name="fakevariable"):
    """Populate xr.Dataset with synthetic data for testing"""
    start_time = str(start_time)
    if x.ndim != 1:
        raise ValueError("'x' needs dim of one")

    time = xr.cftime_range(
        start=start_time, freq="D", periods=len(x), calendar="standard"
    )

    out = xr.Dataset(
        {variable_name: (["time", "lon", "lat"], x[:, np.newaxis, np.newaxis])},
        coords={
            "index": time,
            "time": time,
            "lon": (["lon"], [1.0]),
            "lat": (["lat"], [1.0]),
        },
    )
    # need to set variable units to pass xclim 0.29 check on units
    out[variable_name].attrs["units"] = "K"
    return out

def _years():

    return {'hist': {'start_yr': '1950', 'end_yr': '1951'},
              '1952_1953': {'start_yr': '1952', 'end_yr': '1953'}}

def _maps_color_range():
    return {'tasmax': [260, 320]}

gcm = 'CAMS-CSM1-0'
ssp = 'ssp370' # ssp options: 'ssp126', 'ssp245', 'ssp370', 'ssp585'
variable = 'tasmax' # variable options: 'tasmax', 'tasmin', 'dtr', 'pr'
basic_diagnostic_types = ['min','mean','max']
projection_time_period = '2080_2100' # for difference plots, '2020_2040', '2040_2060', '2060_2080', '2080_2100'
units = {'tasmax': 'K', 'tasmin': 'K', 'dtr': 'K', 'pr': 'mm'}


def test_plot_diagnostic_climo_periods():
    ds_future, ds_hist, ssp, years, variable, metric, data_type, units, vmin = 240, vmax = 320, transform = ccrs.PlateCarree(), xr_func = None
    plot_diagnostic_climo_periods(ds_future=_datasetfactory(np.random.normal(size=730), start_time='1952-01-01'),
                                  ds_hist=_datasetfactory(np.random.normal(size=730), start_time='1950-01-01'),
                                  ssp='ssp370',
                                  years=years(),
                                  variable='fakevariable',
                                  metric='mean',
                                  data_type='fakedatatype',
                                  units='fakeunit',
                                  vmin=-1,
                                  vmax=1)

def test_plot_change_from_historical():


    plot_change_from_historical(ds_future=_datasetfactory(np.random.normal(size=730), start_time='1952-01-01'),
                                ds_hist=_datasetfactory(np.random.normal(size=730), start_time='1950-01-01'),
                                data_type='fakedatatype',
                                variable='fakevariable',
                                units='fakeunit',
                                years=years(),
                                robust=True,
                                ssp='ssp370',
                                time_period='1952_1953',
                                xr_func=None)

def test_plot_downscale_bias_correction_differences():


    plot_downscale_bias_correction_differences(ds_future_bc=_datasetfactory(np.random.normal(size=730), start_time='1952-01-01'),
                                               ds_future_ds=_datasetfactory(np.random.normal(size=730), start_time='1952-01-01'),
                                               ds_hist_bc=_datasetfactory(np.random.normal(size=730),
                                                            start_time='1950-01-01'),
                                               ds_hist_ds=_datasetfactory(np.random.normal(size=730),
                                                                            start_time='1950-01-01'),
                                               variable='fakevariable',
                                               units='fakeunit',
                                               years=years(),
                                               robust=True,
                                               ssp='ssp370',
                                               time_period='1952_1953',
                                               xr_func=None)