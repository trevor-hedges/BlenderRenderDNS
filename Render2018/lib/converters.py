import numpy as np
import mcubes
from h5dns_load_data import *
from scipy.interpolate import RegularGridInterpolator
# Import matplotlib so it works on Mox
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt, matplotlib.cm as cm
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)

def convply2geo(ply_path):
    """
    Loads geometry (vertices and triangles) from a .ply file and returns numpy arrays of vertices and triangles.
    :param ply_path: Directory and filename of .ply file.
    :return: verts, tris: Vertices and triangles.
    """

    # Open .ply file
    with open(ply_path, "r") as ply:
        linenum = 0
        verti = 0
        trii = 0

        # Iterate thru all lines in ply file
        loading_verts = False
        loading_tris = False
        for line in ply:

            # Check if line contains vertex information
            if line.startswith("element vertex "):
                num_verts = int(line.split()[-1]) # Get number of verts

                # Allocate vert array
                verts = np.zeros([num_verts, 3])
                continue

            if line.startswith("element face "):
                num_tris = int(line.split()[-1])

                # Allocate tri array
                tris = np.zeros([num_tris, 3], dtype=int)
                continue

            # Check for header end
            if line == "end_header\n":
                loading_verts = True
                continue 

            # If in verts section, load them 
            if loading_verts:
                verts[verti,:] = list(map(float,line.split()))[0:3]
                verti += 1
                if verti >= num_verts:
                    loading_verts = False
                    loading_tris = True
                    continue
                
            # If in faces/tris section, load them
            if loading_tris:
                tris[trii,:] = list(map(int,line.split()))[1:4]
                trii += 1
                if trii >= num_tris:
                    break

            linenum += 1

    return verts, tris

def convgeo2ply(verts, tris, output_path_ply, vcolors=False):
    """
    Saves geometry (vertices and triangles) in the .ply file format. This can be imported into Blender.
    :param verts: Vertices array
    :param tris: Triangles array
    :param output_path_ply: Path at which to save .ply file
    :param vcolors: (optional) vertex colors associated with each vert. Each color is in [R,G,B] format (each color is
    an int from 0 to 255), and each row corresponds to the vert in verts.
    """
        
    # Determine if vertex colors are provided - if so, include them in the .ply file
    if not type(vcolors) == type(True):
        color_on = True
        # Ensure tris is an array of ints
        vcolors = vcolors.astype(int)
    else:
        color_on = False

    # Write all lines of .ply file
    with open(output_path_ply, "w") as ply:
        ply.write("ply\n")
        ply.write("format ascii 1.0\n")
        ply.write("element vertex " + str(len(verts)) + "\n")
        ply.write("property float x\n")
        ply.write("property float y\n")
        ply.write("property float z\n")
        if color_on:
            ply.write("property uchar red\n")
            ply.write("property uchar green\n")
            ply.write("property uchar blue\n")
        ply.write("element face " + str(len(tris)) + "\n")
        ply.write("property list uchar uint vertex_indices\n")
        ply.write("end_header\n")

        # Write all verts, and colors if given
        for j in range(len(verts)):
            vertex = verts[j,:]
            if color_on:
                color = vcolors[j,:]
                ply.write(np.array_str(vertex).strip("[ ]") + " " + np.array_str(color).strip("[ ]") + "\n")
            else:
                ply.write(np.array_str(vertex).strip("[ ]") + "\n")

        # Write all tris
        for j in range(len(tris)):
            triangle = tris[j,:]
            ply.write("3 " + np.array_str(triangle).strip("[ ]") + "\n")

    print("Saved PLY file: " + output_path_ply)

def find_max_vapor(h5dns_path):
    """
    Finds the maximum YV (vapor) value across all timesteps and throughout the domain.
    :param h5dns_path: Path to .h5dns with YV data
    :return: max_val: Maximum vapor value (nondimensional)
    """

    # Load h5dns file 
    vofFieldInfo = field4Dlow(h5dns_path)
    
    # Iterate thru all tsteps to find max vapor value
    max_val = 0
    for tstep in range(vofFieldInfo.tres):
        
        # Get field of vapor (YV) data on this timestep
        u = vofFieldInfo.obtain3Dtimestep(tstep, "YV")
        
        # Get max value from field on this timestep
        tstep_max_val = np.max(u)

        # Check if greater than the previous max value
        if tstep_max_val > max_val:
            max_val = tstep_max_val
    
    # Close h5dns
    vofFieldInfo.close()
    
    return max_val

def convyv2bvox(h5dns_path, output_path, tstep, vapor_min, vapor_max, fog_halved=False):
    """
    Performs calculations to convert vapor (YV) data to voxel data (.bvox) readable by Blender, for a specific timestep
    :param h5dns_path: h5dns file within which to find YV data
    :param output_path: path to .bvox file to save
    :param tstep: Timestep to load data from
    :param vapor_min: Minimum vapor value to render (point at which fog becomes visible)
    :param vapor_max: Maximum vapor value to render (maximum visual density in Blender)
    :param fog_halved: Export only half of the fog domain. In some cases renders of half of the domain are preferred, but Blender is bad at rendering only half of data when entire domain is given in the .bvox file
    """

    # Load h5dns file 
    vofFieldInfo = field4Dlow(h5dns_path)

    # Header of the BVOX file. This is how Blender knows data dimensions.
    header = np.array([vofFieldInfo.xres, vofFieldInfo.yres, vofFieldInfo.zres, 1])

    # Get field of vapor (YV) data, normalized by max vapor value
    u = vofFieldInfo.obtain3Dtimestep(tstep, "YV")/vapor_max

    # Make all negative values in the field 0 - don't want to take a logarithm of a negative - will get -inf values, which will later be set to 0 again
    u[u < 0] = 0 
    
    # Perform fog intensity calculation
    u = 1 - np.log10(u)/np.log10(vapor_min/vapor_max) # TODO: find computationally fastest way to perform this operation. or just re-write it in C++...
    
    # Remove all <0 values including -inf
    u[u < 0] = 0

    # Perform halving if enabled
    if fog_halved:
        u[int(vofFieldInfo.xres/2):vofFieldInfo.xres,:,:] = 0

    # Flatten data into 1D array with Fortran-style ordering, which is readable by Blender
    vdata = np.reshape(u, -1, order="F")

    # Save as BVOX file (binary)
    binfile = open(output_path, "wb")
    header.astype("<i4").tofile(binfile)
    vdata.astype("<f4").tofile(binfile)
    binfile.close()
    print("Saved fog file: " + output_path)

    # Close h5dns
    vofFieldInfo.close()

def convvof2geo(h5dns_path, tstep, interface_value = 0.8):
    """
    Finds fluid interface in VOF data and exports as geometry, for a specific timestep. The Marching Cubes algorithm
    is used to extract interface geometry from the VOF field.
    :param h5dns_path: h5dns file within which to find VOF data
    :param tstep: Timestep from which to export interface geometry
    :param interface_value: VOF value between 0 and 1 at which to draw surface. 0.8 seems to work well to minimize blockiness
    :return: vertices, triangles: Numpy arrays of geometry (vertices and triangles)
    """

    # Load h5dns file
    vofFieldInfo = field4Dlow(h5dns_path)

    # Get field of VOF data
    u = vofFieldInfo.obtain3Dtimestep(tstep, "VOF")
    
    # Use Marching Cubes on VOF field to obtain interface geometry.
    vertices, triangles = mcubes.marching_cubes(u, interface_value)  # (u = 3D VOF field, interface_value = value at which to generate isosurface)
    return vertices, triangles

def get_temp_prctiles(h5dns_path, save_dir):
    """
    Determines the temperature values associated with many percentile values of temperature, across all timesteps, on the VOF interface (droplet surface)
    :param h5dns_path: h5dns file that contains temperature data
    :param save_dir: Directory in which to save text file with percentiles and associated values
    :return: Percentile data: Left column contains percentiles, right column contains associated values
    """

    # Get temperature values at VOF interface
    data_field = field4Dlow(h5dns_path)
    tsteps = data_field.tres

    vals = []
    # Iterate through each timestep to retrieve all temperature data points on fluid interface
    for tstep in range(tsteps):
        print("Tstep: " + str(tstep))
        vof_field = data_field.obtain3Dtimestep(tstep, "VOF")
        t_field = data_field.obtain3Dtimestep(tstep, "Temperature")
    
        # Remove all non-interface points from the percentile calculations since these points don't matter for surface temperature maps
        vof_field[vof_field > 0] = 1
        t_field_vals = np.multiply(t_field, vof_field).flatten()
        for val in t_field_vals:
            if val > 0.01:
                vals.append(val)

    # Determine percentile values
    prctiles = np.arange(0,100,0.1)
    prctile_vals = np.zeros(len(prctiles))
    for i in range(len(prctiles)):
        prctile = prctiles[i]
        prctile_val = np.percentile(vals, prctile)
        prctile_vals[i] = prctile_val

    # Save percentile data
    output_data = np.column_stack((prctiles, prctile_vals))
    np.savetxt(save_dir, output_data)

    # Return percentile data
    return output_data

def convvert2color(h5dns_path, vertices, lower_bound, upper_bound, tstep):
    """
    Given an array of vertices, determines surface tempmap colors at each vertex by interpolating temperature data.
    Colors are determined using matplotlib's Inferno colorbar, which is perceptually uniform (can be converted to grayscale).
    :param h5dns_path: h5dns file that contains temperature data
    :param vertices: vertices at which to extract temperature data
    :param lower_bound: Lowest normalized temperature on colorbar
    :param upper_bound: Highest normalized temperature on colorbar
    :param tstep: Timestep from which to use temperature data
    :return: colors: Array of colors associated with each vertex.
    """

    # Load h5dns file
    vof_field_info = field4Dlow(h5dns_path)

    # Create trilinear interpolation grid
    xvals = range(vof_field_info.xres)
    yvals = range(vof_field_info.yres)
    zvals = range(vof_field_info.zres)
 
    # Get temperature field
    t_field = vof_field_info.obtain3Dtimestep(tstep, "Temperature")
    t_field[t_field == 1.0] = 0.0
    print("Is this 0? : " + str(t_field[5,5,5]))

    # Create 3D interpolator for this timestep
    temp_interpolator = RegularGridInterpolator((xvals, yvals, zvals), t_field)

    # Allocate colors array
    colors = np.zeros([np.shape(vertices)[0], 3], dtype=int)

    # Loop through all verts
    verti = 0
    for vert in vertices:
        # Interpolate nearby temperature points on grid
        temperature = temp_interpolator(vert)[0] # temp_interpolator returns an array of length 1 for some unknown reason, so the [0] just gets this single element
        # Add color for corresponding vert to array
        colors[verti,:] = (np.array(cm.inferno((temperature - lower_bound) / (upper_bound - lower_bound))[0:3])*255).astype(int)
        verti += 1

    vof_field_info.close()

    return colors

def lambda2_extract(h5dns_filepath, tstep):
    """
    Calculates the lambda2 field from the cartesian velocity field at a specific timestep.
    :param h5dns_filepath: Path to h5dns file with velocity data
    :param tstep: Timestep to extract lambda2 from
    :return: lambda2vals: array of lambda2 vals at each point in domain
    """

    # Load h5dns data
    vofFieldInfo = field4Dlow(h5dns_filepath)
    u = vofFieldInfo.obtain3Dtimestep(tstep, "XVelocity")
    v = vofFieldInfo.obtain3Dtimestep(tstep, "YVelocity")
    w = vofFieldInfo.obtain3Dtimestep(tstep, "ZVelocity")

    # Take velocity gradients
    gradu = np.gradient(u) # [d/dx(u), d/dy(u), d/dz(u)]
    gradv = np.gradient(v)
    gradw = np.gradient(w)

    # Determine J and Jt (J transposed) for each point
    J = np.array([gradu, gradv, gradw])
    Jt = np.transpose(J,(1,0,2,3,4))

    # Determine S, Omega
    S = (J+Jt)/2
    Omega = (J-Jt)/2

    # Move axes around to get last 2 as the ones to multiply
    Sm = np.moveaxis(S,(0,1,2,3,4),(3,4,0,1,2))
    Omegam = np.moveaxis(Omega,(0,1,2,3,4),(3,4,0,1,2))

    # Square "Last 2" indices using matrix multiplication
    eigmat = np.matmul(Sm,Sm) + np.matmul(Omegam,Omegam)

    # Find eigenvalues of "Last 2" index matrices, sort ascending to descending
    eigvalmat = np.sort(np.linalg.eigvals(eigmat))

    # Separate second eigenvalue
    lambda2vals = eigvalmat[:,:,:,1]

    # Close h5dns data
    vofFieldInfo.close()

    return lambda2vals

def convlambda22geo(h5dns_path, tstep, level):
    """
    Creates geometry from lambda2 contours at specified level at a specific timestep. Finds lambda2 contours using velocity
    field, then uses marching cubes to convert it to geometry.
    :param h5dns_path: Path to h5dns file with velocity data
    :param tstep: Timestep to convert
    :param level: Lambda2 level to find contours at (must be negative)
    :return: verts, tris: Vertices and triangles of contour geometry.
    """

    # Run marching cubes for the level specified by the user
    u = lambda2_extract(h5dns_path, tstep)
    verts, tris = mcubes.marching_cubes(u, level)
    return verts, tris

