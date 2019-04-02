import numpy as np
import scipy.interpolate
#Temporary
import mcubes
import cgns_load_data

def conv_noncart_to_cart(points, values, xrange, yrange, zrange):
    """

    :param points: Data point locations (non-cartesian system)
    :param vals: Values corresponding to each data point
    :param xrange: Range of x values to include on output cartesian grid
    :param yrange: y
    :param zrange: z
    :return: 3d array with sides (xrange, yrange, zrange) of values
    """

    # Get all points on cartesian grid specified
    xv, yv, zv = np.meshgrid(xrange, yrange, zrange)
    print(xv)
    print(yv)
    print(zv)

    # Determine interpolated values of points on the cartesian grid
    valarray = scipy.interpolate.griddata(points=points, values=values, xi=(xv, yv, zv), method="linear")

    # Returns 3D array of vals on cartesian grid
    return(valarray)


# pts = np.array([[0,0.5,0.2],[0.1,0.3,0.2],[0.4,0.2,0.4],[0.1,0.1,0.15],[0.5,0.1,0.1]])
# vals = np.array([1,2,3,4,5])
#
# print(conv_noncart_to_cart(points=pts, values=vals, xrange=np.linspace(0,0.5,6), yrange=np.linspace(0,0.5,6), zrange=np.linspace(0,0.5,6)))


cgnsVIZ = cgns_load_data.cgns_data("/home/thedges/Documents/CFM/h5dnsData/VIZ.cgns")
pts = cgnsVIZ.obtain_points()
vals = cgnsVIZ.obtain_field_timestep("Lambda2", 1)
print(pts)
print(vals)
field_cart = conv_noncart_to_cart(points=pts, values=vals, xrange=np.linspace(0,30,31), yrange=np.linspace(0,11,11), zrange=np.linspace(0,11,11))
print(field_cart)
verts, tris = mcubes.marching_cubes(field_cart, -5)
print(verts)
print(tris)