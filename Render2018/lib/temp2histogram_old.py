import numpy as np
import matplotlib.pyplot as plt
from lib.field4df import *

def create_tfield_histogram(h5dns_path, tstep):
   
    # Load h5dns file
    vof_field_info = field4Dlow(h5dns_path)

    #xvals = range(vof_field_info.xres)
    #yvals = range(vof_field_info.yres)
    #zvals = range(vof_field_info.zres)

    # Get temperature field
    t_field = vof_field_info.obtain3Dtimestep(tstep, "Temperature")

    # Make 1d array of values
    t_vals = t_field.flatten()

    vals_of_inter = []
    # Remove all values in range near 0
    for val in t_vals:
        if val > 0.001:
            vals_of_inter.append(val)

    t_vals_inter = np.array(vals_of_inter)

    # Histogram
    plt.hist(t_vals_inter, bins=50)
    plt.xlabel('normalized temperature')
    plt.ylabel('cases')
    #plt.axis([40, 160, 0, 0.03])
    plt.grid(True)

    plt.show()
