import os
import numpy as np
import h5py as h5
import scipy.interpolate as interpolate
import cgns_load_data
import streamline_geometry
from converters import convgeo2ply
import dircheck

def get_prctiles(data, save_dir):
    """
    Returns values associated with percentiles of a list/array of input values. #TODO: There is another function like this that can be generalized
    :param data: Numpy array of values to take percentiles of (percentiles are taken for every 0.1th percentile)
    :param save_dir: Directory in which to save text file with percentiles and associated values
    :return: Percentile data: Left column contains percentiles, right column contains associated values
    """

    # Get percentile values
    prctiles = np.arange(0, 100, 0.1)
    prctile_vals = np.zeros(len(prctiles))
    for i in range(len(prctiles)):
        prctile = prctiles[i]
        prctile_vals[i] = np.percentile(data, prctile)

    # Save percentile data
    output_data = np.column_stack((prctiles, prctile_vals))
    np.savetxt(save_dir, output_data)

    # Return percentile data
    return output_data

def get_max_min_vels(data_file, output_dir, prc_min=1, prc_max=99):
    """
    Gets the min and max bounds for the magnitude coloring of the streamlines. These bounds are associated with small
    and large percentiles in the velocity field.
    :param data_file: Path to cgns/h5dns data file with velocity data
    :param output_dir: Directory at which output streamline files are saved - this is also where the percentile data is loaded from
    :param prc_min: Minimum percentile bound at which to find min velocity
    :param prc_max: Maximum percentile bound
    :return: vel_min, vel_max: Min and max velocity associated with min and max percentile bounds.
    """

    # Find percentiles
    prctile_file = output_dir + "velocity_prctiles.csv"
    if os.path.isfile(prctile_file):
        # Load existing temperature data from file
        prctiles = np.genfromtxt(prctile_file)
        print("Loaded temperature percentiles from file")
    else:
        # Calculate percentiles
        print("Determining percentiles and saving (may take a while)...")

        # Get important params
        data_params = cgns_load_data.get_important_data(data_file)

        # Allocate vels data
        data = h5.File(data_file, "r")
        num_ks = 40
        nth_ij = 3
        len_i = len(data["Base"]["Zone1"]["FlowSolution_%04d" % 0]["VelocityX"][" data"][::nth_ij, 0, 0])
        len_j = len(data["Base"]["Zone1"]["FlowSolution_%04d" % 0]["VelocityX"][" data"][0, ::nth_ij, 0])
        vel_data_all_tsteps = np.zeros([data_params["tres"], len_i, len_j, num_ks])

        # Calculate velocity magnitudes
        for tstep in range(data_params["tres"]):
            vel_data_all_tsteps[tstep,:,:,:] = np.sqrt((data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityX"][" data"][::nth_ij, ::nth_ij, 0:num_ks])**2+\
                   (data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityY"][" data"][::nth_ij, ::nth_ij, 0:num_ks])**2+\
                   (data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityZ"][" data"][::nth_ij, ::nth_ij, 0:num_ks])**2)
            print("tstep " + str(tstep) + " loaded")
        data.close()

        # Calculate percentiles
        prctiles = get_prctiles(data=np.ndarray.flatten(vel_data_all_tsteps), save_dir=prctile_file)
        print("Saved prctile file")

    # Interpolate between discrete percentiles/associated temperature values
    vel_min, vel_max = np.interp([prc_min, prc_max], prctiles[:, 0], prctiles[:, 1])
    return(vel_min, vel_max)

def draw_streamlines(data_file, output_dir, line_type, tres, num_streamlines, step_distance, max_iterations, rand_seed=777):
    """
    Generates streamlines for all timesteps using data from Abhiram's body flow simulation. The streamlines are seeded from
    random positions on/near the body surface.
    :param data_file: Directory/filename of data file which contains the velocity or vorticity data to find streamline in.
    :param output_dir: Output directory to save .ply geometry files to.
    :param line_type: "Velocity" or "Vorticity"
    :param tres: Number of timesteps to calculate streamlines on.
    :param num_streamlines: Number of streamlines to generate
    :param step_distance: Distance to advance in flow field at each step of the streamline generation.
    :param max_iterations: Maximum number of steps to take before ending streamline generation.
    :param rand_seed: Seed used to generate random locations on the body as streamline starting points.
    """

    # Load necessary data for interpolation. Makes column arrays of vertices and the corresponding velocities.
    data_loader = cgns_load_data.cgns_data(data_file)
    pts = data_loader.obtain_points()

    # Load positions of grid points near body surface (surface layer plus some layers above)
    surfx, surfy, surfz = data_loader.obtain_range_near_surface(dist_from_surf=10)

    # Determine number of points on surface
    nsurfpts = np.shape(surfx)[0]

    # Determine predictably random points on surface
    np.random.seed(seed=rand_seed)
    startns = np.random.choice(nsurfpts, num_streamlines)
    start_pts = np.swapaxes(np.array([surfx[startns], surfy[startns], surfz[startns]]),0,1)  # np.swapaxes(np.array(surfxps[seedpts], surfyps[seedpts], surfzps[seedpts]),0,1)

    # Determine low bound and high bound of velocity for streamline colorbar
    vel_min, vel_max = get_max_min_vels(data_file=data_file, output_dir=output_dir)

    # Loop over all specified timesteps
    for tstep in range(tres):

        # Check if streamlines already exported for this seed and on this timestep
        for stream_n in range(num_streamlines):
            if not dircheck.check_file_sanity(output_dir + "_streamline_seed_" + str(rand_seed) + "_tstep_" + str(tstep) + "_num_" + str(stream_n) + ".ply"):
                export_tstep = True
                break
            else:
                export_tstep = False

        if export_tstep:
            # Run streamline creator on all seed points
            if line_type=="Velocity":
                vels = data_loader.obtain_vel_timestep(tstep=tstep)
            elif line_type=="Vorticity":
                vels = data_loader.obtain_vor_timestep(tstep=tstep)
            interpolator=interpolate.NearestNDInterpolator(pts, vels)
            for stream_n in range(num_streamlines):
                seed_pt = start_pts[stream_n]

                # Determine if streamline previously generated
                streamline_path = output_dir + "_streamline_seed_" + str(rand_seed) + "_tstep_" + str(tstep) + "_num_" + str(stream_n) + ".ply"

                if not os.path.exists(streamline_path):
                    # Generate streamline
                    verts_lines, vel_mags = gen_streamline_nonuni(interpolator=interpolator, start_pt=seed_pt, step_distance=step_distance, max_iterations=max_iterations, exit_bounds=[0, 30, 0, 11, 0, 11])
                    print("Generated streamline " + str(stream_n))

                    # Convert to geometry and export
                    verts, tris, colors = streamline_geometry.create_streamline_geometry(verts_center=verts_lines, vel_mags=vel_mags, num_pts=4, vel_bound_low=vel_min, vel_bound_up=vel_max)
                    convgeo2ply(verts=verts, tris=tris, output_path_ply=streamline_path, vcolors=colors)
                    print("Saved streamline geometry " + str(stream_n))
                else:
                    print("File exists: " + str(streamline_path))

            print("Streamlines for tstep " + str(tstep) + " saved")

    data_loader.close()

def gen_streamline_nonuni(interpolator, start_pt, step_distance, max_iterations, exit_bounds):
    """
    Generates a single streamline in a velocity or vorticity field defined on a non-cartesian grid.
    :param interpolator: scipy.interpolate.NearestNDInterpolator object for the flow field.
    :param start_pt: Starting point for the streamline to generate
    :param step_distance: Distance to march forward on each step of the streamline generation
    :param max_iterations: Maximum number of steps the streamline generator can take before aborting
    :param exit_bounds: Bounds beyond which to stop drawing streamlines: [xmin, xmax, ymin, ymax, zmin, zmax]
    :return: verts, vel_mags: Vertices of the streamline, and corresponding velocity magnitude at each vertex.
    """

    # Allocate arrays
    verts = np.zeros([int(max_iterations + 1), 3])
    vel_mags = np.zeros(int(max_iterations + 1))

    # Starting streamline location
    vert_current = np.array(start_pt, dtype="float")  # start at given point

    # Streamline generation loop - takes small steps forward in the velocity field and saves position and magnitude at that point
    n = 0
    while n < max_iterations:

        # If edge of volume reached: break loop
        if (vert_current[0] <= exit_bounds[0]) or (vert_current[0] >= exit_bounds[1]) or (vert_current[1] <= exit_bounds[2])\
                or (vert_current[1] >= exit_bounds[3]) or (vert_current[2] <= exit_bounds[4]) or (vert_current[2] >= exit_bounds[5]):
            break

        # Save current vert
        verts[n, :] = vert_current

        # Interpolate velocity field to find vector at point
        vector_current = np.array(interpolator(vert_current)[0])

        # Get velocity magnitude
        vel_mag = np.linalg.norm(vector_current)
        vel_mags[n] = vel_mag

        # Normalize velocity vector #TODO: would make more sense to advance proportionally to velocity?
        vector_current = vector_current / vel_mag  # Normalize this velocity to unit vector since we only care about direction

        # Update current location based on velocity
        vert_current += vector_current * step_distance

        n += 1

    # Trim data down to actual size
    verts = verts[0:n, :]
    vel_mags = vel_mags[0:n]

    return (verts, vel_mags)