import os
import glob
import numpy as np
import matplotlib.pyplot as plt


def load_grid(file_path):
    """ Load DWD grid data from a single file.

    Parameters
    ----------
    file_path: string
        File to be loaded.

    Returns
    -------
    year: float
        Year of the data.
    xcoords: array of floats
        Gauss-Krueger x coordinates (Rechtswert)
    ycoords: array of floats
        Gauss-Krueger y coordinates (Hochwert)
    data: 2D array
        Data on the grid defined by `xcoords` and `ycoords`.
    """
    year = float(os.path.basename(file_path).split('_')[-1][:4])
    meta_data = {}
    with open(file_path, 'r') as sf:
        for k, line in enumerate(sf):
            if k >= 6:
                break
            key, value = line.split(' ')
            meta_data[key] = float(value)
    xorigin = meta_data.pop('XLLCORNER')
    yorigin = meta_data.pop('YLLCORNER')
    dxy = meta_data.pop('CELLSIZE')
    nodata = int(meta_data.pop('NODATA_VALUE'))
    data = np.loadtxt(file_path, skiprows=6)
    data[data==nodata] = np.nan
    data *= 0.1
    xcoords = np.arange(data.shape[1])*dxy + xorigin
    ycoords = np.arange(data.shape[0])*dxy + yorigin
    return year, xcoords, ycoords, data[::-1,:]


def load_grids(file_pathes):
    """Load many DWD grid data files.

    Parameters
    ----------
    file_pathes: list of string
        Pathes of all files to be loaded.

    Returns
    -------
    years: float
        Years of the data.
    xcoords: array of floats
        Gauss-Krueger x coordinates (Rechtswert)
    ycoords: array of floats
        Gauss-Krueger y coordinates (Hochwert)
    data: 3D array
        Data on the grid defined by `xcoords` and `ycoords`.
        First dimension is the year, second the y-coordinates, and
        third the x-coordinates.
    """
    years = np.zeros(len(files))
    datas = np.array([])
    xcoords = np.array([])
    ycoords = np.array([])
    for k, file in enumerate(files):
        print(f'load {file} ...')
        year, xcoords, ycoords, data = load_grid(file)
        if len(datas) == 0:
            datas = np.empty((len(files), *data.shape))
        years[k] = year
        datas[k] = data
    return years, xcoords, ycoords, datas


def show_spines(ax, spines='lrtb'):
    """ Show and hide spines.

    From https://github.com/bendalab/plottools

    Parameters
    ----------
    ax: matplotlib figure, matplotlib axis, or list of matplotlib axes
        Axis on which spine and ticks visibility is manipulated.
        If figure, then apply manipulations on all axes of the figure.
        If list of axes, apply manipulations on each of the given axes.
    spines: string
        Specify which spines and ticks should be shown. All other ones or hidden.
        'l' is the left spine, 'r' the right spine, 't' the top one and 'b' the bottom one.
        E.g. 'lb' shows the left and bottom spine, and hides the top and and right spines,
        as well as their tick marks and labels.
        '' shows no spines at all.
        'lrtb' shows all spines and tick marks.

    Examples
    --------
    ```py
    import matplotlib.pyplot as plt

    fig, (ax0, ax1, ax2) = plt.subplots(1, 3)
    show_spines(ax0, 'lb')
    show_spines(ax1, 'bt')
    show_spines(ax2, 'tr')
    ```
    """
    # collect spine visibility:
    xspines = []
    if 't' in spines:
        xspines.append('top')
    if 'b' in spines:
        xspines.append('bottom')
    yspines = []
    if 'l' in spines:
        yspines.append('left')
    if 'r' in spines:
        yspines.append('right')
    # collect axes:
    if isinstance(ax, (list, tuple, np.ndarray)):
        axs = ax
    elif hasattr(ax, 'get_axes'):
        # ax is figure:
        axs = ax.get_axes()
    else:
        axs = [ax]
    if not isinstance(axs, (list, tuple)):
        axs = [axs]
    for ax in axs:
        # hide spines:
        ax.spines['top'].set_visible('top' in xspines)
        ax.spines['bottom'].set_visible('bottom' in xspines)
        ax.spines['left'].set_visible('left' in yspines)
        ax.spines['right'].set_visible('right' in yspines)
        # ticks:
        if len(xspines) == 0:
            ax.xaxis.set_ticks_position('none')
            ax.xaxis.label.set_visible(False)
            ax.xaxis._orig_major_locator = ax.xaxis.get_major_locator()
            ax.xaxis.set_major_locator(plt.NullLocator())
        else:
            if hasattr(ax.xaxis, '_orig_major_locator'):
                ax.xaxis.set_major_locator(ax.xaxis._orig_major_locator)
                delattr(ax.xaxis, '_orig_major_locator')
            elif isinstance(ax.xaxis.get_major_locator(), plt.NullLocator):
                ax.xaxis.set_major_locator(plt.AutoLocator())
            if len(xspines) == 1:
                ax.xaxis.set_ticks_position(xspines[0])
                ax.xaxis.set_label_position(xspines[0])
            else:
                ax.xaxis.set_ticks_position('both')
                ax.xaxis.set_label_position('bottom')
        if len(yspines) == 0:
            ax.yaxis.set_ticks_position('none')
            ax.yaxis.label.set_visible(False)
            ax.yaxis._orig_major_locator = ax.yaxis.get_major_locator()
            ax.yaxis.set_major_locator(plt.NullLocator())
        else:
            if hasattr(ax.yaxis, '_orig_major_locator'):
                ax.yaxis.set_major_locator(ax.yaxis._orig_major_locator)
                delattr(ax.yaxis, '_orig_major_locator')
            elif isinstance(ax.yaxis.get_major_locator(), plt.NullLocator):
                ax.yaxis.set_major_locator(plt.AutoLocator())
            if len(yspines) == 1:
                ax.yaxis.set_ticks_position(yspines[0])
                ax.yaxis.set_label_position(yspines[0])
            else:
                ax.yaxis.set_ticks_position('both')
                ax.yaxis.set_label_position('left')


if __name__ == '__main__':
    # load data:
    file_path = 'annual/air_temperature_mean/'
    files = sorted(glob.glob(file_path + '*017.asc'))
    #files = sorted(glob.glob(file_path + '*.asc'))
    years, xcoords, ycoords, temps = load_grids(files)

    # statistics:
    min_temp = np.nanmin(temps)
    max_temp = np.nanmax(temps)
    print(min_temp)
    print(max_temp)
    vmin = min_temp
    vmax = max_temp
    vmin = 0.0
    vmax = 12.0
    mean_temps = np.array([np.nanmean(t) for t in temps])

    # plot:
    fig, axs = plt.subplot_mosaic('.AB\nCAB\n.AB\nDDD', figsize=(6, 5),
                                  gridspec_kw=dict(width_ratios=[1, 8, 8],
                                                   height_ratios=[1, 3, 1, 3]))
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.05, hspace=0.1)
    ax = axs['A']
    show_spines(ax, '')
    i = 0
    mesh = ax.pcolormesh(xcoords, ycoords, temps[i],
                         cmap='plasma', vmin=vmin, vmax=vmax)
    ax.set_aspect('equal')
    ax.set_title(f'{years[i]:.0f}')
    
    ax = axs['B']
    show_spines(ax, '')
    i = -1
    mesh = ax.pcolormesh(xcoords, ycoords, temps[i],
                         cmap='plasma', vmin=vmin, vmax=vmax)
    ax.set_aspect('equal')
    ax.set_title(f'{years[i]:.0f}')
    
    ax = axs['C']
    fig.colorbar(mesh, cax=ax,
                 ticks=np.arange(0, 15, 2),
                 format=plt.FormatStrFormatter('%.0f°C'))
    ax.yaxis.set_ticks_position('left')
    
    ax = axs['D']
    show_spines(ax, 'lb')
    yy = np.linspace(years[0], years[-1], 5000)
    tt = np.interp(yy, years, mean_temps)
    ax.scatter(yy, tt, s=6, c=tt,
               cmap='plasma', vmin=vmin, vmax=vmax)
    #ax.set_xlabel('Year')
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.0f°C'))
    ax.set_ylim(6, 12)
    fig.savefig('images/air_temp_mean.png', dpi=200)
    plt.show()
