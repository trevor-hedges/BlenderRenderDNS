import h5py as h5
import numpy as np

def get_important_data(cgns_path):
    """
    Returns important parameters from a .cgns file used in Abhiram's simulations
    :param cgns_path: Path to .cgns file
    :return: Dictionary with important parameters
    """

    # Open data file
    data = h5.File(cgns_path, "r")

    # Get # of timesteps
    tres = len(data["Base"]["TimeIterValues"]["TimeValues"][" data"])

    # Get resolution in each dimension (noncartesian)
    kres, jres, ires = data["Base"]["Zone1"][" data"][0]

    # Close data file
    data.close()

    # Return dictionary of important values
    return {"tres": tres, "ires": ires, "jres": jres, "kres": kres}

class cgns_data:
    """
    Provides information on a cgns dataset from Abhiram's simulation. Allows for easy retrieval of data.
    """
    def __init__(self, filepath):
        """
        Class initializer
        :param filepath: Path to .cgns file
        """
        self.filepath = filepath

        # Open file
        self.data = h5.File(self.filepath, "r")

        # Get important info
        cgns_params = get_important_data(self.filepath)
        self.ires = cgns_params["ires"]
        self.jres = cgns_params["jres"]
        self.kres = cgns_params["kres"]
        self.tres = cgns_params["tres"]

    def obtain_range_near_surface(self, dist_from_surf=10):
        """
        Gets a 3D array with a range of points near the surface at k=1.
        :param dist_from_surf: Top k-layer to return - will return all layers between 1 and this number, inclusive.
        :return: 3D arrays of X, Y, and Z (cartesian locations) of points near surface
        """
        return np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][1:dist_from_surf, :, :]),\
               np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][1:dist_from_surf, :, :]),\
               np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][1:dist_from_surf, :, :])

    def obtain_points(self):
        """
        Gets the X, Y, and Z arrays of grid coordinate positions. Each is a 3D array where [i,j,k] refers to the position
        in the simulation coordinate system, and the values in the array are the cartesian positions.
        :return: 3D arrays for the X, Y, and Z cartesian locations of points
        """
        # Swapaxes makes the output a column rather than a row
        return np.swapaxes(np.array([np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateX"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateY"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["GridCoordinates"]["CoordinateZ"][" data"][:, :, :])]), 0, 1)

    def obtain_vel_timestep(self, tstep):
        """
        Gets the arrays containing cartesian components of velocity (Vx,Vy,Vz) corresponding to [i,j,k] points
        :param tstep: Timestep of velocity field
        :return: 3D arrays for Vx, Vy, and Vz
        """
        return np.swapaxes(np.array([np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityX"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityY"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VelocityZ"][" data"][:, :, :])]), 0, 1)

    def obtain_vor_timestep(self, tstep):
        """
        Same as obtain_vel_timestep but with vorticity vector components.
        :param tstep: Timestep of vorticity field
        :return: 3D arrays for Wx, Wy, and Wz
        """
        return np.swapaxes(np.array([np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VorticityX"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VorticityY"][" data"][:, :, :]),
                                     np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep]["VorticityZ"][" data"][:, :, :])]), 0, 1)

    def obtain_field_timestep(self, field_name, tstep):
        """
        Obtain values on a scalar field...
        :param tstep: Timestep of field
        :return: 3d array for the extracted field
        """
        return np.ndarray.flatten(self.data["Base"]["Zone1"]["FlowSolution_%04d" % tstep][field_name][" data"][:,:,:])

    def close(self):
        """
        Close out the .cgns data file - frees up the memory it uses when done extracting data.
        """
        self.data.close()
