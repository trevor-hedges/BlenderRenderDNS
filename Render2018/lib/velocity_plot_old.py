import numpy as np
import matplotlib.pyplot as plt
import h5dns_load_data 

# ASSUMES SQUARE DATA
def plot_velocity_field(h5dns_path, tstep, axis, level, output_dir, factor=1):

    vof_field_info = h5dns_load_data.field4Dlow(h5dns_path)
    factorres = vof_field_info.xres/factor
    if axis == 0:
        v0n = "YVelocity"
        v1n = "ZVelocity"
    elif axis == 1:
        v0n = "XVelocity"
        v1n = "ZVelocity"
    elif axis == 2:
        v0n = "XVelocity"
        v1n = "YVelocity"

    v0 = vof_field_info.obtain2Dslice(tstep, v0n, axis, level)
    v1 = vof_field_info.obtain2Dslice(tstep, v1n, axis, level)

    v0r = np.zeros([vof_field_info.xres/factor, vof_field_info.xres/factor])
    v1r = np.zeros([vof_field_info.xres/factor, vof_field_info.xres/factor])

    # Get every factorth element of v0, v1
    print(vof_field_info.xres/factor)
    for i in range(int(vof_field_info.xres/factor)):
        for j in range(int(vof_field_info.xres/factor)):
            v0r[i,j] = v0[i*factor, j*factor]
            v1r[i,j] = v1[i*factor, j*factor]

    
    
    # Normalize to ensure no long arrows
    #maxval = np.amax(np.sqrt(v0**2+v1**2))
    #print("maxval: " + str(maxval))
    #v0 = v0/(maxval)
    #v1 = v1/(maxval)

    X,Y = np.meshgrid(np.arange(factorres), np.arange(factorres))
    
    print(v0)
    print(v1)
    print(v0r)
    print(v1r)
    print(X)
    print(Y)

    """
    # Test stuff
    X, Y = np.meshgrid(np.arange(0, 2 * np.pi, .2), np.arange(0, 2 * np.pi, .2))
    U = np.cos(X)
    V = np.sin(Y)
    Q = plt.quiver(X,Y,U,V)
    """

    #plt.figure()
    Q = plt.quiver(X, Y, v0r, v1r, scale=8)#, scale_units="height", units="width")
    #qk = plt.quiverkey(Q, 0.9, 0.9, 2, r'$2 \frac{m}{s}$', labelpos='E',
    #                           coordinates='figure')

    plt.axis([0, factorres, 0, factorres])
    plt.show()
    plt.savefig(output_dir + "/vfield" + str(tstep), transparent=True, format="png")

def plot_all_velocity_field(h5dns_path, axis, level, output_dir, factor=1):
    vof_field_info = h5dns_load_data.field4Dlow(h5dns_path)
    for tstep in range(vof_field_info.tres):
        print(tstep)
        plot_velocity_field(h5dns_path, tstep, axis, level, output_dir, factor)

    vof_field_info.close()
