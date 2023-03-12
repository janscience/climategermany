""" DWD grid data

Functions for loading climate data provided by the DWD at opendata.dwd.de.

## Functions

- `load_grid()`: load DWD grid data from a single file.
- `load_grids()`: load many DWD grid data files.
"""

import numpy as np


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
    # extract year from file name:
    year = float(file_path.split('_')[-1][:4])
    # read in meta data from file header:
    meta_data = {}
    with open(file_path, 'r') as sf:
        for k, line in enumerate(sf):
            if k >= 6:
                break
            key, value = line.split(' ')
            meta_data[key] = float(value)
    # extract some meta data:
    xorigin = meta_data.pop('XLLCORNER')
    yorigin = meta_data.pop('YLLCORNER')
    dxy = meta_data.pop('CELLSIZE')
    nodata = int(meta_data.pop('NODATA_VALUE'))
    # read in data:
    data = np.loadtxt(file_path, skiprows=6)
    data[data==nodata] = np.nan
    data *= 0.1
    # make coordinates:
    xcoords = np.arange(data.shape[1])*dxy + xorigin
    ycoords = np.arange(data.shape[0])*dxy + yorigin
    return year, xcoords, ycoords, data[::-1,:]


def load_grids(file_paths):
    """Load many DWD grid data files.

    Parameters
    ----------
    file_paths: list of string
        Paths of all files to be loaded.

    Returns
    -------
    years: array of float
        Years of the data.
    xcoords: array of floats
        Gauss-Krueger x coordinates (Rechtswert).
    ycoords: array of floats
        Gauss-Krueger y coordinates (Hochwert).
    data: 3D array
        Data on the grid defined by `xcoords` and `ycoords`.
        First dimension is the year, second the y-coordinates, and
        third the x-coordinates.
    """
    years = np.zeros(len(file_paths))
    datas = np.array([])
    xcoords = np.array([])
    ycoords = np.array([])
    for k, file_path in enumerate(file_paths):
        print(f'load {file_path} ...')
        year, xcoords, ycoords, data = load_grid(file_path)
        if len(datas) == 0:
            # once we loaded the first file we can allocate the data cube:
            datas = np.empty((len(file_paths), *data.shape))
        years[k] = year
        datas[k] = data
    return years, xcoords, ycoords, datas

