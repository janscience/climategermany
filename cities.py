"""Cities

Load locations of cities and their names.

## Functions

- `load_cities()`: load coordinates and names of cities.
"""

import numpy as np
import pandas as pd


def load_cities(file_path='worldcities.csv'):
    """ Load coordinates and names of cities.

    Uses World Cities Database from
    [simplemaps](https://simplemaps.com/data/world-cities).  Download the
    file and unzip it. For the load_cities() function use the file
    `worldcities.csv`.

    Parameters
    ----------
    file_path: str
        Path of csv file holding the data.

    Returns
    -------
    lon: ndarray of floats
        Longtitudes of cities.
    lat: ndarray of floats
        Latitudes of cities.
    names: list of str
        Names of cities.
    pop: ndarray of floats
        Population of the cities.
    """
    cities = pd.read_csv(file_path, sep=',')
    lat = np.array(cities.lat)
    lon = np.array(cities.lng)
    names = list(cities.city)
    pop = np.array(cities.population)
    return lon, lat, names, pop


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    lon, lat, names, pop = load_cities('maps/worldcities/worldcities.csv')
    plt.scatter(lon, lat, s=1+pop*0.5e-5)
    for k in np.where(pop > 1e6)[0]:
        plt.text(lon[k], lat[k], names[k])
    plt.show()
