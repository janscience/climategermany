""" CRU NC data

Functions for loading climate data of the CRU provided by CEDA at https://data.ceda.ac.uk.

You need to install netCDF4 from [pypi](https://pypi.org/project/netCDF4/):
```
pip3 install netCDF4
```
See [netCDF4 documentation](https://unidata.github.io/netcdf4-python/).

## Functions

- `load_grids()`: load grids from a CEDA NC file.
"""

import numpy as np
import netCDF4 as nc


def info(file_path):
    """Print title and properties of variables on console.

    Parameters
    ----------
    file_path: string
        Path of NC file.

    Returns
    -------
    title: str
        Title of the data set.
    name: str
        Name of the variable contained in the file.
    Unit: str
        Unit of the variable contained in the file.
    """
    with nc.Dataset(file_path) as f:
        print(f.title)
        dname = ''
        dunit = ''
        for i, (k, v) in enumerate(f.variables.items()):
            name = v.long_name if hasattr(v, 'long_name') else v.description
            unit = f'[{v.units}]' if hasattr(v, 'units') else ''
            shape = f'{v.shape}'[1:-1].rstrip(', ')
            print(f'{k:6}: {name:50} {unit:30} {shape}')
            if i == 3:
                dname = name
                dunit = unit.strip('[]')
        return f.title, dname, dunit
    return '', '', ''

        
def load_grids(file_path, key=None):
    """Load a CRU NC data file.

    Parameters
    ----------
    file_paths: list of string
        Paths of all files to be loaded.
    key: string
        Key of the data to be returned.
        Call `info()` for possible values (first olumn of output).

    Returns
    -------
    dates: array of datetimes
        Dates of the data.
    lon: array of floats
        Longitudes.
    lat: array of floats
        Latidues.
    data: 3D array
        Data on the grid defined by `lon` and `lat`.
        First dimension is the date, second the latitude, and
        third the longitude.
    unit: str
        Unit of the data.

    Raises
    ------
    FileNotFoundError:
        Invalid file path.
    """
    dates = np.array([])
    lon = np.array([])
    lat = np.array([])
    data = np.array([])
    unit = ''
    try:
        f = nc.Dataset(file_path)
        # coordinates:
        lon = np.array(f.variables['lon'][:])
        lon = np.append(lon, lon[-1] + lon[1] - lon[0])
        lat = np.array(f.variables['lat'][:])
        lat = np.append(lat, lat[-1] + lat[1] - lat[0])
        # times:
        start_time = np.datetime64('1900-01-01')
        time = f.variables['time']
        days = np.array(time[:], 'timedelta64[D]')
        dates = start_time + days
        if not key:
            key = list(f.variables.keys())[3]
        data = f.variables[key]
        unit = data.units if hasattr(data, 'units') else ''
    except FileNotFoundError:
        print(f'Invalid file {file_path}')
    return dates, lon, lat, data, unit


if __name__ == '__main__':
    import glob
    import matplotlib.pyplot as plt
    for file_path in sorted(glob.glob('ceda/cru*.dat.nc')):
        print(file_path)
        title, dname, dunit = info(file_path)
        dates, lon, lat, data, unit = load_grids(file_path)
        plt.title(f'{title}: {dname} [{dunit}]')
        plt.pcolormesh(lon, lat, data[0])
        plt.show()
        print()



