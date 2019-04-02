import numpy as np
from scipy.interpolate import RegularGridInterpolator
# Import matplotlib so it works on Mox
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt, matplotlib.cm as cm
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)
from lib.h5dns_load_data import *

def get_temp_prctiles(h5dns_path, save_dir):
    
    # Get temperature values at VOF interface
    data_field = field4Dlow(h5dns_path)
    tsteps = data_field.tres

    vals = []
    for tstep in range(tsteps):
        print("Tstep: " + str(tstep))
        vof_field = data_field.obtain3Dtimestep(tstep, "VOF")
        t_field = data_field.obtain3Dtimestep(tstep, "Temperature")
    
        # Keep all temperature points where interface is
        vof_field[vof_field > 0] = 1
        #t_field_vals = np.trim_zeros(np.multiply(t_field, vof_field).flatten())
        t_field_vals = np.multiply(t_field, vof_field).flatten()

        for val in t_field_vals:
            if val > 0.01:
                vals.append(val)

    # Get percentile values
    prctiles = np.arange(0,100,0.1)
    prctile_vals = np.zeros(len(prctiles))
    for i in range(len(prctiles)):
        prctile = prctiles[i]
        prctile_val = np.percentile(vals, prctile)
        prctile_vals[i] = prctile_val

    # Save bounds data
    output_data = np.column_stack((prctiles, prctile_vals))
    np.savetxt(save_dir, output_data)

    # Return bounds
    return output_data

def get_bounds(h5dns_path, lower_prctile, upper_prctile):

    # Get temperature values at VOF interface
    vof_field_info = field4Dlow(h5dns_path)
    tsteps = vof_field_info.tres

    vals = []
    for tstep in range(tsteps):
        print("Tstep: " + str(tstep))
        vof_field = vof_field_info.obtain3Dtimestep(tstep, "VOF")
        t_field = vof_field_info.obtain3Dtimestep(tstep, "Temperature")
    
        # Keep all temperature points where interface is
        vof_field[vof_field > 0] = 1
        #t_field_vals = np.trim_zeros(np.multiply(t_field, vof_field).flatten())
        t_field_vals = np.multiply(t_field, vof_field).flatten()

        for val in t_field_vals:
            if val > 0.01:
                vals.append(val)

    # Plot value histogram
    # plt.hist(vals, bins=50)
    # plt.xlabel('normalized temperature')
    # plt.ylabel('cases')
    # plt.grid(True)
    # plt.show()

    # Get percentile values
    lbnd = np.percentile(vals, lower_prctile)
    ubnd = np.percentile(vals, upper_prctile)

    # Return bounds
    return lbnd, ubnd

def get_bounds_frame(h5dns_path, tstep, lower_prctile, upper_prctile):
    # Get temperature values at VOF interface
    vof_field_info = field4Dlow(h5dns_path)
    tsteps = vof_field_info.tres

    vals = []
    print("Tstep: " + str(tstep))
    vof_field = vof_field_info.obtain3Dtimestep(tstep, "VOF")
    t_field = vof_field_info.obtain3Dtimestep(tstep, "Temperature")

    # Keep all temperature points where interface is
    vof_field[vof_field > 0] = 1
    #t_field_vals = np.trim_zeros(np.multiply(t_field, vof_field).flatten())
    t_field_vals = np.multiply(t_field, vof_field).flatten()

    for val in t_field_vals:
        if val > 0.01:
            vals.append(val)
    
    # Get percentile values
    lbnd = np.percentile(vals, lower_prctile)
    ubnd = np.percentile(vals, upper_prctile)

    # Return bounds
    return lbnd, ubnd

def convvert2color(h5dns_path, vertices, lower_bound, upper_bound, tstep):
    
    # DEBUG
    print(lower_bound)
    print(upper_bound)

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
