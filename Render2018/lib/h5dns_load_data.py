import h5py as h5
import numpy as np

class field4Dlow:
    """
    Provides information on an h5dns file, and data from said file, with dimensions t,z,y,x.
    Allows for easy retrieval of data.
    """
    def __init__(self, filename):
        """
        Class initializer. Loads h5dns file and some useful data.
        :param filename: Path to h5dns file
        """

        self.filename = filename

        # Open file
        self.f = h5.File(filename, 'r')

        # Extract bounds
        self.tres = len(self.f['FIELD_SEQUENCE_field3d']['times'])
        self.zres = self.f['RUNTIME_PARAMETERS'].attrs['NNK']
        self.yres = self.f['RUNTIME_PARAMETERS'].attrs['NNJ']
        self.xres = self.f['RUNTIME_PARAMETERS'].attrs['NNI']

        # Extract other data for info file
        self.lx = self.f['RUNTIME_PARAMETERS'].attrs['LX']
        self.ly = self.f['RUNTIME_PARAMETERS'].attrs['LY']
        self.lz = self.f['RUNTIME_PARAMETERS'].attrs['LZ']
        self.dt = self.f['RUNTIME_PARAMETERS'].attrs['DT']

        # Droplet diameter
        self.dropd = self.f['RUNTIME_PARAMETERS'].attrs['DROPD']

        # Gas temperature
        self.tgas = self.f['RUNTIME_PARAMETERS'].attrs['VOF_TGAS']

    def printInfo(self):
        """
        :return: A bunch of info in text format (for testing purposes)
        """
        return ("Number of timesteps: " + str(self.tres) + "\n" + "Resolution (I,J,K): (" + str(self.xres) + ", " +
                str(self.yres) + ", " + str(self.zres) + ")\n" + "Dimensions (I,J,K): (" + str(self.lx) + ", " +
                str(self.ly) + ", " + str(self.lz) + ")\n" + "dt: " + str(self.dt) + "\n" +
                "Droplet Diameter: " + str(self.dropd) + "\n" + "Gas temperature: " + str(self.tgas) + "\n\n")

    def obtain3Dtimestep(self, tstep, field):
        """
        Returns 3D data for a specific timestep on a specific scalar field in the h5dns data, indexed as [i,j,k]
        :param tstep: Timestep
        :param field: Field to take data from. Examples: "VOF", "YV", "Temperature"
        :return: 3D scalar field of data.
        """
        datafield = np.swapaxes(self.f['FIELD_SEQUENCE_field3d']['FIELD_DATA_%06d' % tstep][field][:,:,:], 0, 2) # Swaps the axes such that it is returned in [i,j,k] format instead of [k,j,i]
        return datafield

    def obtain2Dslice(self, tstep, field, slice_axis, slice_level):
        """
        Returns a 2D slice of a 3D scalar field at a specific timestep.
        :param tstep: Timestep
        :param field: Field to take data from
        :param slice_axis: Axis normal to which the slice is taken. Specify "0" for X, "1" for Y, "2" for Z
        :param slice_level: X, Y, or Z level at which to slice.
        :return: 2D scalar field - [X,Y], [X,Z], or [Y,Z] depending on axis
        """
        if slice_axis == 0: # Cut at X = slice_level, YZ plane visualized
            return np.swapaxes(self.f['FIELD_SEQUENCE_field3d']['FIELD_DATA_%06d' % tstep][field][:,:,slice_level], 0, 1)
        elif slice_axis == 1: # Cut at Y = slice_level, XZ visualized
            return np.swapaxes(self.f['FIELD_SEQUENCE_field3d']['FIELD_DATA_%06d' % tstep][field][:,slice_level,:], 0, 1)
        else: # Cut at Z
            return np.swapaxes(self.f['FIELD_SEQUENCE_field3d']['FIELD_DATA_%06d' % tstep][field][slice_level,:,:], 0, 1)

    def close(self):
        """
        Close h5dns file: should call this when done working with data.
        """
        self.f.close()

def get_important_data(h5dns_path):
    """
    Returns important parameters from an .h5dns file.
    :param h5dns_path: Path to .h5dns file
    :return: Dictionary with important parameters
    """

    data_field = field4Dlow(h5dns_path)
    param_dict = {"tres": data_field.tres, "xres": data_field.xres, "yres": data_field.yres, "zres": data_field.zres, "dropd": data_field.dropd, "tgas": data_field.tgas}
    data_field.close()

    return param_dict