import numpy as np
from lib.h5dns_load_data import *

def find_max_vapor(h5dns_path):
    
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

    # Load h5dns file 
    vofFieldInfo = field4Dlow(h5dns_path)

    # Header of the BVOX file. This is how Blender knows data dimensions.
    header = np.array([vofFieldInfo.xres, vofFieldInfo.yres, vofFieldInfo.zres, 1])

    # Get field of vapor (YV) data, normalized by max vapor value
    u = vofFieldInfo.obtain3Dtimestep(tstep, "YV")/vapor_max

    # TODO fix this comment No less-than-1 values into log - we want these to just evaluate to 0, so make them 1
    u[u < 0] = 0 
    
    # Perform fog intensity calculation
    u = 1 - np.log10(u)/np.log10(vapor_min/vapor_max) # TODO: find computationally fastest way to perform this operation. or just re-write it in C++...
    
    # Remove all <0 values including -inf
    u[u < 0] = 0

    # Perform halving if enabled
    if fog_halved:
        u[int(vofFieldInfo.xres/2):vofFieldInfo.xres,:,:] = 0

    # Put data into 1D C-like array which is readable by Blender
    vdata = np.reshape(u, -1, order="F")

    # Save a bunch of percentiles from vdata
    #with open("fog_prctile" + str(tstep) + ".txt","w") as fog_prc_file:
        #fog_prc_file.write(str(np.min(vdata)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,0.01)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,0.1)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,1)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,5)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,10)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,25)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,50)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,75)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,90)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,95)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,99)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,99.9)) + "\n")
        #fog_prc_file.write(str(np.percentile(vdata,99.99)) + "\n")
        #fog_prc_file.write(str(np.max(vdata)) + "\n")

    # Save as BVOX file (binary)
    binfile = open(output_path, "wb")
    header.astype("<i4").tofile(binfile)
    vdata.astype("<f4").tofile(binfile)
    binfile.close()
    print("Saved fog file: " + output_path)

    # Close h5dns
    vofFieldInfo.close()
