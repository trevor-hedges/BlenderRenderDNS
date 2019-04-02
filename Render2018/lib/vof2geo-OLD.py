import mcubes
from lib.h5dns_load_data import field4Dlow
import numpy as np

def convvof2geo(h5dns_path, tstep, interface_value = 0.8):

    # Load object that can easily access timestep 3D fields and info on its dimensions, etc.
    vofFieldInfo = field4Dlow(h5dns_path)

    # Get field of VOF data
    u = vofFieldInfo.obtain3Dtimestep(tstep, "VOF")
    
    # Use mcubes library on VOF field to obtain watertight isosurface geometry.
    vertices, triangles = mcubes.marching_cubes(u, interface_value)  # (u = 3D VOF field, interface_value = value at which to generate isosurface)
    return vertices, triangles
