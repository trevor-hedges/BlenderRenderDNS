import os, os.path
from converters import *
from dircheck import get_output_filepath, check_make, check_file_sanity
from blender_launcher import launch_blender_smooth

def conv_ply(h5dns_path, output_dir, tres):
    """
    For a series of timesteps, converts the VOF field of a data file to droplet interface geometry files (.ply) that can
    be loaded and rendered in Blender. Checks whether files exist before converting, and skips those that already exist.
    :param h5dns_path: Path to h5dns file that contains VOF field
    :param output_dir: Directory to export .ply geometry to
    :param tres: Number of timesteps in .h5dns
    """

    # Make dir for initial (unsmoothed) export of geometry
    output_dir_unsmooth = output_dir + "/unsmooth/"
    check_make(output_dir_unsmooth)

    # Convert all tsteps in .h5dns file
    for tstep in range(0, tres):
        # Determine filepath of .ply to export on this tstep
        ply_path = get_output_filepath(output_dir_unsmooth, tstep, ".ply")

        # Check if file exists already and is larger than the smallest possible size - if so, the file has already been exported on a previous run.
        # If not, export the file. (need to better determine whether a file valid, and add some warning/error for possible bad files)
        if not check_file_sanity(ply_path):
            
            # Convert VOF data to raw vertex/triangle geometry data (Uses marching cubes)
            vertices, triangles = convvof2geo(h5dns_path, tstep)
            
            # Convert vertices/triangles to PLY files at destination directory
            convgeo2ply(verts=vertices, tris=triangles, output_path_ply=ply_path)
 
    # Perform mesh smoothing in Blender. Will export smoothed .ply files to the output dir.
    launch_blender_smooth(output_dir_unsmooth=output_dir_unsmooth, output_dir_smooth=output_dir)

def conv_bvox(h5dns_path, output_dir, tres, vapor_min, fog_halved):
    """
    For a series of timesteps, converts the vapor (YV) field of a data file to voxel data (.bvox) that can be loaded
    and rendered as fog in Blender. Checks whether files exist before converting, and skips those that already exist.
    :param h5dns_path: Path to h5dns file that contains YV field
    :param output_dir: Directory to export .bvox voxel data to
    :param tres: Number of timesteps in .h5dns
    :param vapor_min: Minimum vapor value to render. Vapor intensity is rendered on a logarithmic scale. (max value is determined by taking the maximum YV value in time and space)
    :param fog_halved: Whether or not to cut fog field in half. If true, will export "halved" .bvox data - this is a workaround because Blender is not good at rendering only one half of data, if provided the entire field.
    """

    # Determine max vapor value. We want the maximum value that exists across all timesteps and in the entire domain.
    # Exports max vapor value to a file, so that when scripts are run multiple times on the same data, this value can be reloaded without recalculating.
    # Loads this file if it exists, otherwise, run the calculations.
    vapor_max_filepath = output_dir + "vapor_max.txt"
    if os.path.isfile(vapor_max_filepath):
        with open(vapor_max_filepath, "r") as vapor_max_file:
            vapor_max = float(vapor_max_file.readline())
    else:
        vapor_max = find_max_vapor(h5dns_path)
        with open(vapor_max_filepath, "w") as vapor_max_file:
            vapor_max_file.write(str(vapor_max))

    # Check if file exists already and is larger than the smallest possible size - if so, the file has already been exported on a previous run.
    # If not, export the file. (need to better determine whether a file valid, and add some warning/error for possible bad files)
    for tstep in range(0, tres):
        # Check if file exists before converting
        bvox_path = get_output_filepath(output_dir, tstep, ".bvox")
        if not check_file_sanity(bvox_path):
            # Convert YV data to .bvox and export to output directory.
            convyv2bvox(h5dns_path=h5dns_path, output_path=bvox_path, tstep=tstep, vapor_min=vapor_min, vapor_max=vapor_max, fog_halved=fog_halved)

def conv_color_ply(h5dns_path, output_dir, uncolored_ply_dir, tres, temp_min, temp_max):
    """
    Adds color to the vertices of a droplet interface in a .ply file, which allows interface surface temperature to be visualized.
    Accepts uncolored .ply as input and adds color based on interpolated temperature data at each vertex location.
    :param h5dns_path: Path to h5dns file that contains Temperature field
    :param output_dir: Directory to export colored .ply geometry to
    :param uncolored_ply_dir: Directory in which to find original (uncolored) .ply files exported previously
    :param tres: Number of timesteps in .h5dns
    :param temp_min: Minimum temperature bound to visualize (anything below will just be the lowest color)
    :param temp_max: Maximum temperature bound to visualize
    """

    # Iterate through all timesteps, check if colored .ply already exists, and if not, create it
    for tstep in range(0, tres):
        output_temp_dir = get_output_filepath(output_dir, tstep, ".ply")
        if not check_file_sanity(output_temp_dir):
            # Convert existing uncolored .ply data to verts/tris
            smooth_verts, smooth_tris = convply2geo(get_output_filepath(uncolored_ply_dir, tstep, ".ply"))
            # Use verts to determine corresponding color at each vert
            colors = convvert2color(h5dns_path, smooth_verts, temp_min, temp_max, tstep)
            # Create .ply file with added color data
            convgeo2ply(verts=smooth_verts, tris=smooth_tris, vcolors=colors, output_path_ply=output_temp_dir)

def conv_lambda2_ply(h5dns_path, output_dir, tres, contour_level):
    """
    Creates geometry that represents lambda2 contours, given cartesian velocity data in the .h5dns file, and exports
    it to .ply files for each timestep.
    :param h5dns_path: Path to h5dns file
    :param output_dir: Directory to export colored .ply geometry to
    :param tres: Number of timesteps in .h5dns
    :param contour_level: Lambda2 contour to render in 3D (must be negative to make sense)
    """

    # Iterate through all timesteps, check if lambda2 contour .ply files already exist, and create them if not
    for tstep in range(0, tres):
        ply_path = get_output_filepath(output_dir, tstep, ".ply")
        if not check_file_sanity(ply_path):
            # Run calculations to determine lambda2 contour geometry
            verts, tris = convlambda22geo(h5dns_path, tstep, contour_level)
            # Export this geometry to .ply
            convgeo2ply(verts, tris, ply_path)

def temp_bounds(h5dns_path, ply_temp_output_dir, prc_min, prc_max):
    """
    Determines the temperature associated with a particular temperature percentile across the droplet interface on all timesteps.
    The first time this function is run for a particular .h5dns, it saves a .csv with many percentiles and the associated
    temperatures. Then, desired percentiles are interpolated to get the corresponding temperatures. This is done because
    the temperature datasets can be quite large.
    :param h5dns_path: Path to h5dns file with temperature data
    :param ply_temp_output_dir: Output dir for temperature percentile csv (ply/geometry files also go here)
    :param prc_min: Min percentile to interpolate to temperature value (nondimensional)
    :param prc_max: Max percentile to interpolate to temperature value (nondimensional)
    :return: temp_min, temp_max: Min and max temperature bounds associated with min and max percentiles.
    """
    print("Determining temperature bounds...")
    temp_prctile_file = ply_temp_output_dir + "temp_prctiles.csv"
    if os.path.isfile(temp_prctile_file):
        # Load existing temperature data from file
        print("Loading temperature percentiles from file...")
        temp_prctiles = np.genfromtxt(temp_prctile_file)
    else:
        # Calculate percentiles
        print("Determining percentiles and saving (may take a while)...")
        temp_prctiles = get_temp_prctiles(h5dns_path, temp_prctile_file)

    # Interpolate between discrete percentiles/associated temperature values
    temp_min, temp_max = np.interp([prc_min, prc_max], temp_prctiles[:,0], temp_prctiles[:,1])

    return temp_min, temp_max

