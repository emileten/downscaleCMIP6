

def plot_diagnostic_climo_periods(gcm, ds_future, ssp, years, variable, metric, data_type, units, ds_hist=None,
                                  vmin=240, vmax=320, transform=ccrs.PlateCarree(), xr_func=None):
    """
    plot mean, max, min tasmax, dtr, precip for CMIP6, bias corrected and downscaled data
    """
    fig, axes = plt.subplots(1, 5, figsize=(45, 12), subplot_kw={'projection': ccrs.PlateCarree()})
    cmap = cm.cividis

    for i, key in enumerate(years):

        # different dataset for historical, select years
        if i == 0 and ds_hist != None:
            da = ds_hist[variable].sel(time=slice(years[key]['start_yr'], years[key]['end_yr']))
        else:
            da = ds_future[variable].sel(time=slice(years[key]['start_yr'], years[key]['end_yr']))

        if xr_func is not None:
            da = xr_func(da)  # some user defined transformation preserving the time dimension

        if metric == 'mean':
            data = da.mean(dim='time').load()
        elif metric == 'max':
            data = da.max(dim='time').load()
        elif metric == 'min':
            data = da.min(dim='time').load()

        if ds_hist is not None:
            ind = i
        else:
            ind = i + 1

        im = data.plot(ax=axes[ind],
                       cmap=cmap,
                       transform=ccrs.PlateCarree(), add_colorbar=False, vmin=vmin, vmax=vmax)

        axes[ind].coastlines()
        axes[ind].add_feature(cfeature.BORDERS, linestyle=":")
        if ind == 2:
            axes[ind].set_title('{} {} {}, {} \n {}'.format(gcm, metric, data_type, ssp, key))
        else:
            axes[ind].set_title("{}".format(key))

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.02, top=0.9, left=0.05, right=0.95,
                        wspace=0.1, hspace=0.01)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.2, 0.6, 0.06])

    # Draw the colorbar
    cbar_title = '{} ({})'.format(variable, units)
    cbar = fig.colorbar(im, cax=cbar_ax, label=cbar_title, orientation='horizontal')


def plot_gmst_diagnostic(ds_fut_cmip6, ds_fut_bc, variable='tasmax',
                         ssp='370', ds_hist_cmip6=None, ds_hist_bc=None, ds_hist_downscaled=None,
                         ds_fut_downscaled=None):
    """
    plot GMST diagnostic for cmip6, bias corrected and downscaled data. Downscaled is usually not included since there is not much added benefit
    of computing it on the downscaled data.
    Takes in annual mean DataArray of the above, eager.
    """

    if ds_hist_cmip6 is not None:
        da_cmip6_hist = ds_hist_cmip6[variable].groupby('time.year').mean()
        gmst_hist_cmip6 = _compute_gmst(da_cmip6_hist.load())

    da_cmip6_fut = ds_fut_cmip6[variable].groupby('time.year').mean()
    gmst_fut_cmip6 = _compute_gmst(da_cmip6_fut.load())

    if ds_hist_bc is not None:
        da_bc_hist = ds_hist_bc[variable].groupby('time.year').mean()
        gmst_hist_bc = _compute_gmst(da_bc_hist.load())

    da_bc_fut = ds_fut_bc[variable].groupby('time.year').mean()
    gmst_fut_bc = _compute_gmst(da_bc_fut.load())

    if ds_hist_downscaled is not None:
        da_ds_hist = ds_hist_downscaled[variable].groupby('time.year').mean()
        gmst_hist_ds = _compute_gmst(da_ds_hist.load())

        da_ds_fut = ds_fut_downscaled[variable].groupby('time.year').mean()
        gmst_fut_ds = _compute_gmst(da_ds_fut.load())

    fig = plt.figure(figsize=(12, 4))
    if ds_hist_cmip6 is not None:
        gmst_hist_cmip6.plot(linestyle=':', color='black')
    gmst_fut_cmip6.plot(linestyle=':', color='black', label='cmip6')

    if ds_hist_bc is not None:
        gmst_hist_bc.plot(color='green')
    gmst_fut_bc.plot(color='green', label='bias corrected')

    if ds_hist_downscaled is not None:
        gmst_hist_ds.plot(color='blue')
        gmst_fut_ds.plot(color='blue', label='downscaled')

    plt.legend()
    plt.title('Global Mean {} {}'.format(variable, ssp))


def plot_bias_correction_downscale_differences(ds_future_bc, ds_future_ds, ds_future_cmip, plot_type, data_type,
                                               variable, units, years, robust=True, ds_hist_bc=None, ds_hist_ds=None,
                                               ds_hist_cmip=None,
                                               ssp='370', time_period='2080_2100', xr_func=None):
    """
    plot differences between cmip6 historical and future, bias corrected historical and future, downscaled historical and future, or bias corrected and downscaled.
    produces two subplots, one for historical and one for the specified future time period
    plot_type options: downscaled_minus_biascorrected, change_from_historical (latter takes bias corrected or downscaled or cmip6)
    data_type options: bias_corrected, downscaled, cmip6
    """
    fig, axes = plt.subplots(1, 2, figsize=(45, 12), subplot_kw={'projection': ccrs.PlateCarree()})

    if plot_type == 'change_from_historical':
        if data_type == 'bias_corrected':
            ds_hist = ds_hist_bc
            ds_future = ds_future_bc
        elif data_type == 'downscaled':
            ds_hist = ds_hist_ds
            ds_future = ds_future_ds
        elif data_type == 'cmip6':
            ds_hist = ds_hist_cmip
            ds_future = ds_future_cmip
        ds_hist = ds_hist[variable].sel(time=slice(years['hist']['start_yr'], years['hist']['end_yr']))
        ds_future = ds_future[variable].sel(time=slice(years[time_period]['start_yr'], years[time_period]['end_yr']))

        if xr_func is not None:
            ds_hist = xr_func(ds_hist)
            ds_future = xr_func(ds_future)

        diff1 = ds_hist.mean('time').load()
        diff2 = ds_future.mean('time').load() - diff1

        suptitle = "{} change from historical: {}".format(ssp, data_type)
        cmap = cm.viridis
    elif plot_type == 'downscaled_minus_biascorrected':
        if ds_hist_bc is not None:

            da_hist_ds = ds_hist_ds[variable].sel(time=slice(years['hist']['start_yr'], years[time_period]['end_yr']))
            da_hist_bc = ds_hist_bc[variable].sel(time=slice(years['hist']['start_yr'], years[time_period]['end_yr']))

            if xr_func is not None:
                da_hist_ds = xr_func(da_hist_ds)
                da_hist_bc = xr_func(da_hist_bc)

            diff1 = da_hist_ds - da_hist_bc
            diff1 = diff1.load()

        da_future_ds = ds_future_ds[variable].sel(
            time=slice(years[time_period]['start_yr'], years[time_period]['end_yr']))
        da_future_bc = ds_future_bc[variable].sel(
            time=slice(years[time_period]['start_yr'], years[time_period]['end_yr']))

        if xr_func is not None:
            da_future_ds = xr_func(da_future_ds)
            da_future_bc = xr_func(da_future_bc)

        da_future_ds_mean = da_future_ds.mean('time').load()
        da_future_bc_mean = da_future_bc.mean('time').load()
        diff2 = da_future_ds_mean - da_future_bc_mean
        suptitle = "{} downscaled minus bias corrected".format(ssp)
        cmap = cm.bwr

    cbar_label = "{} ({})".format(variable, units)
    if ds_hist_bc is not None:
        diff1.plot(ax=axes[0], cmap=cmap, transform=ccrs.PlateCarree(), robust=robust,
                   cbar_kwargs={'label': cbar_label})
    diff2.plot(ax=axes[1], cmap=cmap, transform=ccrs.PlateCarree(), robust=robust, cbar_kwargs={'label': cbar_label})

    axes[0].coastlines()
    axes[0].add_feature(cfeature.BORDERS, linestyle=":")
    axes[0].set_title('historical (1995 - 2014)')
    axes[1].set_title(time_period)
    plt.suptitle(suptitle)

    axes[1].coastlines()
    axes[1].add_feature(cfeature.BORDERS, linestyle=":")
