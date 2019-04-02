import numpy as np
import matplotlib.pyplot as plt
import lib.h5dns_load_data as h5dns_load_data
from lib.converters import convgeo2ply

# Extracts the lambda2 field from cartesian velocity field
def lambda2_extract(h5dns_filepath, tstep):
    
    vofFieldInfo = h5dns_load_data.field4Dlow(h5dns_filepath)
    
    u = vofFieldInfo.obtain3Dtimestep(tstep, "XVelocity")
    v = vofFieldInfo.obtain3Dtimestep(tstep, "YVelocity")
    w = vofFieldInfo.obtain3Dtimestep(tstep, "ZVelocity")

    gradu = np.gradient(u) # [d/dx(u), d/dy(u), d/dz(u)]
    gradv = np.gradient(v)
    gradw = np.gradient(w)

    J = np.array([gradu, gradv, gradw])
    Jt = np.transpose(J,(1,0,2,3,4))

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

    return lambda2vals
