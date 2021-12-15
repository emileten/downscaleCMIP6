import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm
import xclim as xc

def _compute_gmst(da, lat_name='lat', lon_name='lon'):
    lat_weights = np.cos(da[lat_name] * np.pi / 180.)
    ones = xr.DataArray(np.ones(da.shape), dims=da.dims, coords=da.coords)
    weights = ones * lat_weights
    masked_weights = weights.where(~da.isnull(), 0)

    gmst = (
            (da * masked_weights).sum(dim=(lat_name, lon_name))
            / (masked_weights).sum(dim=(lat_name, lon_name)))

    return gmst

def xr_conditional_count(ds, threshold=95, convert=lambda x : (x - 32) * 5 / 9 + 273.15):
    if convert is not None :
        threshold = convert(threshold)
    ds = ds.where(ds > threshold)
    return ds.groupby(ds.time.dt.year).count().rename({'year':'time'})

def xc_maximum_consecutive_dry_days(ds, thresh=0.0005):
    return xc.indicators.atmos.maximum_consecutive_dry_days(ds, thresh=thresh, freq='YS')

def xc_RX5day(ds):
    return xc.indicators.icclim.RX5day(ds, freq='YS')


def plot_colored_maps(ds, common_title, units, color_bar_range):
    """
    Produces a grid of maps colored with the data of a sequence of arrays containing lon and lat dimensions.

    Parameters
    ----------
    ds : dict
        keys are str pointing to xr.DataArray objects with lat and lon dimension
    title : str
    units : str
    color_bar_range : tuple
    """

    fig, axes = plt.subplots(1, len(ds), figsize=(45, 12), subplot_kw={'projection': ccrs.PlateCarree()})
    cmap = cm.cividis
    i = 0
    for name, subds in ds.items():

        im = subds.plot(ax=axes[i],
                       cmap=cmap,
                       transform=ccrs.PlateCarree(), add_colorbar=False, vmin=color_bar_range[0], vmax=color_bar_range[1])

        axes[i].coastlines()
        axes[i].add_feature(cfeature.BORDERS, linestyle=":")
        axes[ind].set_title('{} {}'.format(title, name))

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.02, top=0.9, left=0.05, right=0.95,
                        wspace=0.1, hspace=0.01)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.2, 0.6, 0.06])

    # Draw the colorbar
    cbar_title = '{} ({})'.format(variable, units)
    cbar = fig.colorbar(im, cax=cbar_ax, label=cbar_title, orientation='horizontal')



def plot_colored_timeseries(ds, title, units):

    """
    Produces overlayed colored line graphs from data sequences that have a time dimension.

    Parameters
    ----------
    ds : dict
        keys are str pointing to a dict['temporal_data', 'color', 'linestyle']. The former entry is a xr.DataArray object.
    title : str
    units : str
    """

    fig = plt.figure(figsize=(12, 4))
    for name, material in ds:
        subds = material['temporal_data']
        subds.plot(label=name, linestyle=material['linestyle'], color=material['color'])
    plt.legend()
    plt.title('{} {}'.format(title, units))

