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


def load_grids(file_path):
    """Load many DWD grid data files.

    Parameters
    ----------
    file_path: string
        Path with wildcards selecting the files to load.

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
    files = sorted(glob.glob(file_path))
    years = []
    datas = []
    xcoords = np.array([])
    ycoords = np.array([])
    for file in files:
        print(f'load {file} ...')
        year, xcoords, ycoords, data = load_grid(file)
        years.append(year)
        datas.append(data)
    return np.array(years), xcoords, ycoords, np.array(datas)


if __name__ == '__main__':
    file_path = 'annual/air_temperature_mean/'
    years, xcoords, ycoords, temps = load_grids(file_path + '*017.asc')
    min_temp = np.nanmin(temps)
    max_temp = np.nanmax(temps)
    print(min_temp)
    print(max_temp)

    i = -1
    fig, ax = plt.subplots()
    mesh = ax.pcolormesh(xcoords, ycoords, temps[i],
                         cmap='plasma', vmin=min_temp, vmax=max_temp)
    ax.set_aspect('equal')
    ax.set_title(f'{years[i]:.0f}')
    fig.colorbar(mesh, ax=ax)
    plt.show()

    """
    df = pd.DataFrame(dict(year=years, temp=temps))
    df.to_csv('meantemp.csv', index=False)
    fig, ax = plt.subplots()
    ax.plot(years, temps)
    ax.set_xlabel('Year')
    ax.set_ylabel('Mean annual temperature [°C]')
    fig.savefig('meantemp.pdf')
    """
    plt.show()
