"""World

Plot shapes provided by [Natural Earth](https://www.naturalearthdata.com).

You need to install [PyShp](https://github.com/GeospatialPython/pyshp):
```
pip3 install PyShp
```

## Functions

- `load_shapes()`: load shapes from file.
- `plot_outlines()`: plot outlines of shapes.
"""

import numpy as np
import shapefile


def load_shapes(file_path):
    """ Load shapes from file.

    Parameter
    ---------
    file_path: str
        Path to the shape file (can be a zip file).

    Returns
    -------
    sf: shapefile
        Shape file object.
    """
    sf = shapefile.Reader(file_path)
    return sf


def plot_outlines(ax, sf, **kwargs):
    """ Plot outlines of shapes.

    Parameter
    ---------
    sf: shapefile
        File handle holding the shape data.
    ax: matplotlib axis
        Axis where to plot the shapes.
    kwargs: dict
        kwargs for the plot function.
    """
    for shape in sf.shapeRecords():
        #print(shape.record[3])
        points = np.array(shape.shape.points)
        parts = shape.shape.parts
        parts.append(len(points))
        for i0, i1 in zip(parts[:-1], parts[1:]):
            ax.plot(points[i0:i1,0], points[i0:i1,1], **kwargs)

            
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    countries = load_shapes('maps/ne_10m_admin_0_countries.zip')
    fig, ax = plt.subplots()
    plot_outlines(ax, countries, color='k')
    ax.set_aspect('equal')
    plt.show()

