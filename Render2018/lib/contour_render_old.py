import numpy as np
from lib.field4df import field4Dlow 
import matplotlib.pyplot as plt
# Import matplotlib so it works on Mox
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt, matplotlib.cm as cm
plt.ioff() #http://matplotlib.org/faq/usage_faq.html (interactive mode)
from lib.dircheck import *

def render_field(h5dns_path, output_dir, slice_axis, slice_level, vmin, vmax):
    
    # Load object that can easily access timestep 3D fields and info on its dimensions, etc.
    data_field = field4Dlow(h5dns_path)

    for tstep in range(data_field.tres):
        plt.axis("off")
        
        plt.axis("equal")
        
        plt.contourf(data_field.obtain2Dslice(tstep, "Temperature", slice_axis, slice_level), 500, cmap=cm.inferno, vmin=vmin, vmax=vmax)
       
        plt.savefig(output_dir + get_base_output_name() + str(tstep) + ".png", bbox_inches="tight", pad_inches=0, dpi=600)
        plt.close()

    data_field.close()
