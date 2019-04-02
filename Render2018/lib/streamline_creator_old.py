import numpy as np
from lib.converters import convgeo2ply
from lib.h5dns_load_data import field4Dlow
from scipy.interpolate import RegularGridInterpolator
from lib.dircheck import check_file_sanity

# generates one streamline
# not passing in all fields because this caused memory issues (?)
def gen_streamline(h5dns_file, tstep, pt, steps_per_element):

    vof = field4Dlow(h5dns_file)
    cube_res = vof.xres
    cube_bound = cube_res - 1
    xvel = vof.obtain3Dtimestep(tstep, "XVelocity")
    yvel = vof.obtain3Dtimestep(tstep, "YVelocity")
    zvel = vof.obtain3Dtimestep(tstep, "ZVelocity")
    vof.close()

    # Maximum number of iterations the streamline-finding loop can go through before aborting
    max_iter = cube_res*steps_per_element*10 # The number at the end is an arbitrary multiplier

    # Step factor (normalized distance to advance per iteration of streamline where 1 is the length of a single element
    step_factor = 1.0/steps_per_element

    # Number of points in stream tube visualization
    num_pts = 12
    circ_rad = 0.1 # elements wide

    # Generate stream tube coords in local axis (just a circle)
    theta = np.matrix(np.arange(0,2*np.pi,2*np.pi/num_pts))
    coords_loc = np.concatenate((circ_rad*np.cos(theta), circ_rad*np.sin(theta),np.matrix(np.zeros([1,num_pts]))),0)
    coords_loc4 = np.concatenate((coords_loc, np.matrix(np.ones([1,num_pts]))),0)
    coords = np.zeros([int(max_iter+1),3,num_pts])
    vel_mags = np.zeros(int(max_iter+1))

    # Starting streamline location
    vert_current = np.array(pt, dtype="float") # start at given point
    vert_prev = np.array(vert_current) # Make copy of current vert in prev vert (Will march forward current)

    valrange = np.arange(cube_res)
    valrange3 = (valrange, valrange, valrange)

    # Create interpolator
    xvel_interpolator = RegularGridInterpolator(valrange3, xvel)
    yvel_interpolator = RegularGridInterpolator(valrange3, yvel)
    zvel_interpolator = RegularGridInterpolator(valrange3, zvel)

    # Interpolate velocity at current point
    vector_current = np.array([xvel_interpolator(vert_current)[0], yvel_interpolator(vert_current)[0], zvel_interpolator(vert_current)[0]])
    vector_current = vector_current/np.linalg.norm(vector_current) # Normalize this velocity to unit vector since we only care about direction
    
    #try:
        #vector_current = np.array([xvel_interpolator(vert_current)[0], yvel_interpolator(vert_current)[0], zvel_interpolator(vert_current)[0]])
        #vector_current = vector_current/np.linalg.norm(vector_current) # Normalize this velocity to unit vector since we only care about direction
    #except:
    #    print(vert_current)

    # March forward one step
    vert_current += vector_current*step_factor

    # Check if vert now outside of domain - if so, don't export any geometry
    if np.any(vert_current < 0.0) or np.any(vert_current > 31.0):
        return(np.array([]),np.array([]))

    # Save current vector as "previous"
    vector_prev = np.array(vector_current)

    # Initial local x and y axes (in the XZ plane)
    xloc = np.array([0,0,-1]) # -Z
    yloc = np.array([0,1,0]) # 
    zloc = np.cross(xloc, yloc)

    n = 0
    while n < max_iter:

        print("Iteration: " + str(n))
        print("Vert_current: " + str(vert_current))
        
        vector_current = np.array([xvel_interpolator(vert_current)[0], yvel_interpolator(vert_current)[0], zvel_interpolator(vert_current)[0]])

        # Get velocity magnitude
        vel_mag = np.linalg.norm(vector_current)
        
        # Save magnitude
        vel_mags[n] = vel_mag

        #colors[verti,:] = (np.array(cm.inferno((temperature - lower_bound) / (upper_bound - lower_bound))[0:3])*255).astype(int)

        # Normalize velocity vector
        vector_current = vector_current/vel_mag # Normalize this velocity to unit vector since we only care about direction

        #print("vector_current: " + str(vector_current))
        #print("vector_prev: " + str(vector_prev))

        # Calculate angle and axis between vectors
        #print("dot: "+ str(np.dot(vector_current, vector_prev)))

        angle = np.arccos(np.dot(vector_current, vector_prev))
        #print("angle: " + str(angle))

        axis = np.cross(vector_prev, vector_current)
        #print("Axis: " + str(axis))
        if axis.any():
            axis = axis/np.linalg.norm(axis)
            rotation = True
        else: # axis is a 0 vector
            rotation = False

        # Use this angle and axis to rotate x and y unit vectors in planes
        if rotation:
            R = np.array([[np.cos(angle)+axis[0]**2*(1-np.cos(angle)), axis[0]*axis[1]*(1-np.cos(angle))-axis[2]*np.sin(angle), axis[0]*axis[2]*(1-np.cos(angle))+axis[1]*np.sin(angle)],
                [axis[1]*axis[0]*(1-np.cos(angle))+axis[2]*np.sin(angle), np.cos(angle)+axis[1]**2*(1-np.cos(angle)), axis[1]*axis[2]*(1-np.cos(angle))-axis[0]*np.sin(angle)],
                [axis[2]*axis[0]*(1-np.cos(angle))-axis[1]*np.sin(angle), axis[2]*axis[1]*(1-np.cos(angle))+axis[0]*np.sin(angle), np.cos(angle)+axis[2]**2*(1-np.cos(angle))]], dtype="float")
            xloc = np.dot(R,xloc)
            yloc = np.dot(R,yloc)
            zloc = np.cross(xloc,yloc)
            #print("R: " + str(R))
            #print("xloc: " + str(xloc))
            #print("yloc: " + str(yloc))
            #print("zloc: " + str(zloc))
        else:
            # Local vectors stay the same as they were before
            #print("No rotation for this pathstep. ")
            pass

        # Generate transformation matrix from local rotated coords back to absolute coords
        Tinv = np.matrix([[1,0,0,vert_current[0]],[0,1,0,vert_current[1]],[0,0,1,vert_current[2]],[0,0,0,1]])
        #Rinv = np.matrix([[xloc[0],xloc[1],xloc[2],0],[yloc[0],yloc[1],yloc[2],0],[zloc[0],zloc[1],zloc[2],0],[0,0,0,1]])
        Rinv = np.matrix([[xloc[0],yloc[0],zloc[0],0],[xloc[1],yloc[1],zloc[1],0],[xloc[2],yloc[2],zloc[2],0],[0,0,0,1]])

        #print("tinv: " + str(Tinv))
        #print("rinv: " + str(Rinv))

        # Transform circle points to absolute coords (one cross section of the stream tube being visualized
        coords_abs = Tinv*Rinv*coords_loc4
         
        #print("tinv*rinv: " + str(Tinv*Rinv))
        #print("coords_abs: " + str(coords_abs))

        # Connect stream tube coords with previous ones
        coords[n,:,:] = coords_abs[0:3,:]

        # Update "current" vert/vector to "previous" vert/vector
        vert_prev = vert_current
        vector_prev = vector_current

        # Update current location based on velocity
        vert_current += vector_current*step_factor

        vector_current = vert_current-vert_prev
        vector_current = vector_current/np.linalg.norm(vector_current) # Make it a unit vector

        # If edge of volume reached: break loop
        if np.any(vert_current > cube_bound) or np.any(vert_current < 0):
            break

        n += 1

    # Trim coords down to actual size
    coords = coords[0:n+1,:,:]

    # Generate verts/tris geometry based on coords
    triA0 = np.arange(num_pts)
    triA1 = (triA0 + 1) % num_pts
    triA2 = triA1 + num_pts
    triB0 = triA0 + num_pts
    triB1 = triA0
    triB2 = triA2

    triA = np.array([[triA0, triA1, triA2], [triB0, triB1, triB2]])
    triA = np.swapaxes(triA,1,2).reshape(2*num_pts,3)
    triA = np.tile(triA,(n,1))
    add = num_pts*np.reshape(np.swapaxes(np.swapaxes(np.tile(np.arange(n),(num_pts*2,3,1)),0,2),1,2),(num_pts*2*(n),3))
    tris = triA + add
    verts = np.swapaxes(coords,1,2).reshape((n+1)*num_pts,3)
    num_verts = np.shape(verts)[0]
    num_captris = num_pts-2
    captris = np.zeros([num_captris,3], dtype=int)
    captris[:,1] = np.arange(num_captris)+2
    captris[:,2] = np.arange(num_captris)+1
    captrisend = np.zeros(np.shape(captris), dtype=int)
    captrisend[:,0] = captris[:,0]
    captrisend[:,1] = captris[:,2]
    captrisend[:,2] = captris[:,1]
    captrisend += num_verts-num_pts
    tris = np.concatenate((tris, captris, captrisend), axis=0)

    return(verts, tris, colors)


def create_datafile(h5dns_file, num_streamlines, tstep, output_dir):
    
    # Get resolution
    vof = field4Dlow(h5dns_file)
    resolution = vof.xres
    vof.close()

    # Save data
    data = np.array([resolution, num_streamlines, tstep], dtype=int)
    np.save(output_dir + "/data", data)

def create_streamlines(h5dns_file, tstep, steps_per_element, starting_points, output_dir):

    # starting_points: Some numpy array of points: Each row is a separate point
    print("starting_points: " + str(starting_points))
    print(np.shape(starting_points))
    num_streamlines = np.shape(starting_points)[0]
    print("num_streamlines " + str(num_streamlines))


    for ptn in np.arange(num_streamlines):
        output_filename = output_dir + "tstep" + str(tstep) + "_streamline" + str(ptn) + ".ply"
        if not check_file_sanity(output_filename):
            starting_point = starting_points[ptn,:]
            
            # Run function for streamline conversion here
            verts, tris = gen_streamline(h5dns_file=h5dns_file, tstep=0, pt=starting_point, steps_per_element=steps_per_element)
            
            # Use geo2ply to export
            convgeo2ply(verts, tris, output_filename)

    # Create data files
    #create_datafile(h5dns_file, num_streamlines, tstep, output_dir)


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

    return(coords3)

