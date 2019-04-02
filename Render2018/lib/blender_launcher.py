import os
import configparser

def get_blender_dir():
    """
    Gets the Blender file directory, which requires the absolute path
    :return: Blender file directory
    """
    # Load directory name config
    dirname_config = configparser.ConfigParser()
    dirname_config.read("dirname.cfg")
    # Return path
    return os.getcwd() + "/" + dirname_config["DIRECTORIES"]["blenderhome"]

def launch_blender_new(blend_name, python_name, blender_config_filedir):
    """
    Launches Blender in terminal given a .blend file and a Blender Python API script. Passes in a config file as an
    input to the Python API script.
    :param blend_name: Blender file to load
    :param python_name: Python file to run in Blender's Python API to perform rendering
    :param blender_config_filedir: Path to the Blender config file that specifies rendering settings and stuff
    """
    blender_dir = get_blender_dir()
    blender_kicker = "blender -b " + blender_dir + "/" + blend_name + " -P " + blender_dir + "/" + python_name + " -- " + blender_config_filedir
    print("Running Blender with the following command: " + blender_kicker)
    os.system(blender_kicker)

def launch_blender_smooth(output_dir_unsmooth, output_dir_smooth):
    """
    Launches Blender in terminal to perform geometry smoothing on a series of .ply files. Used to perform smoothing on
    interface geometry that is output by the marching cubes algorithm, because after initial conversion, the geometry
    can be quite blocky.
    :param output_dir_unsmooth: Directory to .ply files that need to be smoothed
    :param output_dir_smooth: Directory to output smoothed .ply files to
    """
    blender_dir = get_blender_dir()
    blender_kicker = "blender -b " + blender_dir + "/" + "smooth_geom.blend" + " -P " + blender_dir + "/" + "smooth_geom.py" + " -- " + output_dir_unsmooth + " " + output_dir_smooth
    print("Running Blender with the following command: " + blender_kicker)
    os.system(blender_kicker)