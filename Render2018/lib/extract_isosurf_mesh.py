import numpy as np
import h5py as h5
from converters import convgeo2ply

def extract_geometry(data_file, output_dir, nth_coord):
    """
    Extracts the geometry of the body used in Abhiram's simulations of flow around an axisymmetric ramp body.
    In his simulations, the geometry is located at [k,j,i]=[1,:,:] (non-cartesian coordinate system)
    Geometry is saved to a .ply file.
    :param data_file: File to extract geometry from
    :param output_dir: Output directory within which to save geometry file (just directory, no filename).
    :param nth_coord: Save geometry with every nth coordinate (i.e. skip n-1 coords before saving the nth one). This helps reduce unnecessary mesh complexity. Higher is less detailed.
    """

    # Open file
    data = h5.File(data_file, "r")

    # Extract mesh coords
    xpt2f = np.ndarray.flatten(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, ::nth_coord, ::nth_coord], order="C")  # k,j,i
    ypt2f = np.ndarray.flatten(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][1, ::nth_coord, ::nth_coord], order="C")
    zpt2f = np.ndarray.flatten(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][1, ::nth_coord, ::nth_coord], order="C")

    # Get resolutions of each surface geometry dimension
    ires = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, 1, ::nth_coord])
    jres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, ::nth_coord, 1])

    # close data file
    data.close()

    # Compile list of vertices as columns
    verts = np.swapaxes(np.array([xpt2f,ypt2f,zpt2f]),0,1)

    # Compile list of triangles - each triangle consists of 3 vertex IDs, and these lines make each "upper left" and "lower right" triangle (which forms a quadrilateral) out of adjacent vertices
    upper_lefts = np.swapaxes(np.array([range(0, ires * (jres - 1) - 1), range(1, ires * (jres - 1)), range(ires, ires * jres - 1)]), 0, 1)
    lower_rights = np.swapaxes(np.array([range(ires, ires * jres - 1), range(1, ires * (jres - 1)), range(ires + 1, ires * jres)]), 0, 1)
    num_tris_half = np.shape(upper_lefts)[0]

    # Delete "wraparound" faces
    upper_lefts = np.delete(upper_lefts, np.arange(ires - 1, num_tris_half + 1, ires), 0)
    lower_rights = np.delete(lower_rights, np.arange(ires - 1, num_tris_half + 1, ires), 0)

    # Concatenate triangle arrays together
    tris = np.concatenate((upper_lefts, lower_rights), axis=0)

    # Convert geometry to a .ply file for Blender
    convgeo2ply(verts=verts, tris=tris, output_path_ply=output_dir + "/body.ply")

def extract_geometry_general(data_file, output_dir, nth_coord, axis="K", level=1):
    """
    Extracts geometry from any surface in ijk coordinates. An axis, and the level along that axis, is specified, where the surface lies along the other two axes at the specified level.
    :param data_file: File to extract geometry from
    :param output_dir: Output directory within which to save geometry file (just directory, no filename).
    :param nth_coord: Save geometry with every nth coordinate (i.e. skip n-1 coords before saving the nth one). This helps reduce unnecessary mesh complexity. Higher is less detailed.
    """

    # Open file
    data = h5.File(data_file, "r")

    # Extract mesh coords
    if axis.upper()=="I":
        xpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][::nth_coord, ::nth_coord, level],
            order="C")  # k,j,i
        ypt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][::nth_coord, ::nth_coord, level], order="C")
        zpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][::nth_coord, ::nth_coord, level], order="C")
        # Get resolutions of each surface geometry dimension
        xres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, ::nth_coord, 1])
        yres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][::nth_coord, 1, 1])

    elif axis.upper()=="J":
        xpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][::nth_coord, level, ::nth_coord],
            order="C")  # k,j,i
        ypt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][::nth_coord, level, ::nth_coord],
            order="C")
        zpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][::nth_coord, level, ::nth_coord],
            order="C")
        xres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, 1, ::nth_coord])
        yres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][::nth_coord, 1, 1])

    elif axis.upper()=="K":
        xpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][level, ::nth_coord, ::nth_coord],
            order="C")  # k,j,i
        ypt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][level, ::nth_coord, ::nth_coord],
            order="C")
        zpt2f = np.ndarray.flatten(
            data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][level, ::nth_coord, ::nth_coord],
            order="C")
        # Get resolutions of each surface geometry dimension
        xres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, 1, ::nth_coord])
        yres = len(data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1, ::nth_coord, 1])

    data.close()

    # Compile list of vertices as columns
    verts = np.swapaxes(np.array([xpt2f, ypt2f, zpt2f]), 0, 1)

    # Compile list of triangles - each triangle consists of 3 vertex IDs, and these lines make each "upper left" and "lower right" triangle (which forms a quadrilateral) out of adjacent vertices
    upper_lefts = np.swapaxes(
        np.array([range(0, xres * (yres - 1) - 1), range(1, xres * (yres - 1)), range(xres, xres * yres - 1)]), 0, 1)
    lower_rights = np.swapaxes(
        np.array([range(xres, xres * yres - 1), range(1, xres * (yres - 1)), range(xres + 1, xres * yres)]), 0, 1)
    num_tris_half = np.shape(upper_lefts)[0]

    # Delete "wraparound" faces
    upper_lefts = np.delete(upper_lefts, np.arange(xres - 1, num_tris_half + 1, xres), 0)
    lower_rights = np.delete(lower_rights, np.arange(xres - 1, num_tris_half + 1, xres), 0)

    # Concatenate triangle arrays together
    tris = np.concatenate((upper_lefts, lower_rights), axis=0)

    # Convert geometry to a .ply file for Blender
    convgeo2ply(verts=verts, tris=tris, output_path_ply=output_dir + "/body_axis" + str(axis) + "level" + str(level) + ".ply")