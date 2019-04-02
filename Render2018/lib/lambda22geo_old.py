import lib.lambda2 as lambda2
import mcubes

# Converts lambda2 contours at specified level over all timesteps
def convlambda22geo(h5dns_path, tstep, level):
    
    # Run marching cubes for the level specified by the user
    u = lambda2.lambda2_extract(h5dns_path, tstep)
    verts, tris = mcubes.marching_cubes(u, level)
    return verts, tris

