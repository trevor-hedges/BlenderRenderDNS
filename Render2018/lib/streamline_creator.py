import numpy as np
from converters import convgeo2ply
from h5dns_load_data import field4Dlow
from scipy.interpolate import RegularGridInterpolator
from dircheck import check_file_sanity
import streamline_geometry

# not passing in all velocity fields because this caused memory issues (?)
# Generates one streamline as a list of points (does not assign solid geometry to it)
def gen_streamline(h5dns_file, tstep, pt, steps_per_element):
    """
    Generates a streamline in a cartesian velocity field. Written for Michael/Pablo's h5dns data but not useful for droplet simulations
    :param h5dns_file: Directory/filename of data file with velocity data
    :param tstep:
    :param pt:
    :param steps_per_element:
    :return:
    """

    vof = field4Dlow(h5dns_file)
    xres = vof.xres
    xbound = xres - 1
    xvel = vof.obtain3Dtimestep(tstep, "XVelocity")
    yvel = vof.obtain3Dtimestep(tstep, "YVelocity")
    zvel = vof.obtain3Dtimestep(tstep, "ZVelocity")
    vof.close()

    # Maximum number of iterations the streamline-finding loop can go through before aborting
    max_iter = xres*steps_per_element*10 # The number at the end is an arbitrary multiplier

    # Step factor (normalized distance to advance per iteration of streamline where 1 is the length of a single element
    step_factor = 1.0/steps_per_element

    # Allocate arrays
    verts = np.zeros([int(max_iter+1),3])
    vel_mags = np.zeros(int(max_iter+1))

    # Starting streamline location
    vert_current = np.array(pt, dtype="float") # start at given point

    valrange = np.arange(xres)
    valrange3 = (valrange, valrange, valrange)

    # Create interpolator
    xvel_interpolator = RegularGridInterpolator(valrange3, xvel)
    yvel_interpolator = RegularGridInterpolator(valrange3, yvel)
    zvel_interpolator = RegularGridInterpolator(valrange3, zvel)


    # New loop that only finds centerpts - will also want velocity magnitudes at center points
    n = 0
    while n < max_iter:
        
        # If edge of volume reached: break loop before doing any interpolation, otherwise the interpolation will fail
        if np.any(vert_current > xbound) or np.any(vert_current < 0):
            break
        
        # Save current vert
        verts[n,:] = vert_current

        # Interpolate velocity field to find vector at point
        vector_current = np.array([xvel_interpolator(vert_current)[0], yvel_interpolator(vert_current)[0], zvel_interpolator(vert_current)[0]])
        
        # Get velocity magnitude
        vel_mag = np.linalg.norm(vector_current)

        # Save velocity magnitude
        vel_mags[n] = vel_mag

        # Normalize velocity vector
        vector_current = vector_current/vel_mag # Normalize this velocity to unit vector since we only care about direction

        # Update current location based on velocity
        vert_current += vector_current*step_factor
        
        n += 1


    # Trim data down to actual size
    verts = verts[0:n,:]
    vel_mags = vel_mags[0:n]
    
    return(verts, vel_mags)

def create_streamlines(h5dns_file, tstep, steps_per_element, starting_points, output_dir):

    # starting_points: Some numpy array of points: Each row is a separate point
    print("starting_points: " + str(starting_points))
    print(np.shape(starting_points))
    num_streamlines = np.shape(starting_points)[0]
    print("num_streamlines " + str(num_streamlines))

    streamlines_verts = []
    streamlines_vel_mags = []

    for ptn in np.arange(num_streamlines):
        starting_point = starting_points[ptn,:]

        # Get centerline of streamline and velocity magnitude at each point
        verts, vel_mags = gen_streamline(h5dns_file=h5dns_file, tstep=tstep, pt=starting_point, steps_per_element=10)
        streamlines_verts.append(verts)
        streamlines_vel_mags.append(vel_mags)

        min_vel_st = np.min(vel_mags)
        max_vel_st = np.max(vel_mags)
        if ptn == 0:
            min_vel = min_vel_st
            max_vel = max_vel_st
        else:
            if min_vel_st < min_vel:
                min_vel = min_vel_st
            if max_vel_st > max_vel:
                max_vel = max_vel_st

    for ptn in np.arange(num_streamlines):
        output_filename = output_dir + "tstep" + str(tstep) + "_streamline" + str(ptn) + ".ply"
        if not check_file_sanity(output_filename):
            verts, tris, colors = streamline_geometry.create_streamline_geometry(verts_center=streamlines_verts[ptn], vel_mags=streamlines_vel_mags[ptn], num_pts=8, vel_bound_low=min_vel, vel_bound_up=max_vel)
            convgeo2ply(verts=verts, tris=tris, output_path_ply=output_filename, vcolors=colors)

    # Returns min and max vels which are used for colorbar
    return(min_vel, max_vel)

def create_starting_points(dist, xres, starting_face):

    xend = xres-1 # Minus 1 because we want to go from 0 to xres-1 in the volume (0-indexed)

    row_short = np.linspace(dist, xend-dist, xend/dist)
    row_long = np.linspace(dist/2, xend-dist/2, xend/dist+1)
    yvals = np.linspace(dist/2, xend-dist/2, xend/dist)
    
    short_xrow_len = len(row_short)
    long_xrow_len = len(row_long)
    ylen = len(yvals)

    short_xrow = True
    cv = 0
    coords = np.zeros([int(np.ceil(ylen/2)*short_xrow_len+np.floor(ylen/2)*long_xrow_len), 2])
    # Repeat rows 1 and 2 in the second dimension
    for yvaln in range(len(yvals)):
        if short_xrow:
            xrow_len = short_xrow_len
            coords[cv:cv+xrow_len,0] = row_short #np.transpose([row_short])
        else:
            xrow_len = long_xrow_len
            coords[cv:cv+xrow_len,0] = row_long #np.transpose([row_short])

        coords[cv:cv+xrow_len,1] = yvals[yvaln]*np.ones(xrow_len)
        cv += xrow_len
        short_xrow = not short_xrow

    num_coords = np.shape(coords)[0]
    coords3 = np.zeros([num_coords,3])
    if (starting_face == "YZ-") or (starting_face == "YZ+"):
        coords3[:,1] = coords[:,0]
        coords3[:,2] = coords[:,1]
    elif (starting_face == "XZ-") or (starting_face == "XZ+"):
        coords3[:,0] = coords[:,0]
        coords3[:,2] = coords[:,1]
    elif (starting_face == "XY-") or (starting_face == "XY+"):
        coords3[:,0] = coords[:,0]
        coords3[:,1] = coords[:,1]
    if (starting_face == "YZ+"):
        coords3[:,0] = (xres-1)*np.ones(num_coords)
    elif (starting_face == "XZ+"):
        coords3[:,1] = (xres-1)*np.ones(num_coords)
    elif (starting_face == "XY+"):
        coords3[:,2] = (xres-1)*np.ones(num_coords)

    print(coords3)
    return(coords3)

