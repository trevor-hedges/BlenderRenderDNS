import configparser
from dircheck import absolutify

def config_dirname_cfg():
    """
    Creates config file with all of the important directories used in the scripts. Saves config file to the lib directory.
    """
    dirname_config = configparser.ConfigParser()

    geometry_data_dir = "geometry_data/"
    image_output_dir = "image_output/"

    dirname_config["DIRECTORIES"] = {}
    dirname_config["DIRECTORIES"]["lib"] = absolutify(".", slash_at_end=True) # The lib dir depends on where the scripts are located. This makes the current directory into an absolute path, used in the rest of the path names
    dirname_config["DIRECTORIES"]["background_images"] = absolutify("../background_images/", slash_at_end=True)
    dirname_config["DIRECTORIES"]["geometry_data"] = geometry_data_dir
    dirname_config["DIRECTORIES"]["image_output"] = image_output_dir
    dirname_config["DIRECTORIES"]["bvox"] = geometry_data_dir + "bvox/"
    dirname_config["DIRECTORIES"]["ply"] = geometry_data_dir + "ply/"
    dirname_config["DIRECTORIES"]["ply_temp"] = geometry_data_dir + "ply_temp/"
    dirname_config["DIRECTORIES"]["ply_lambda2"] = geometry_data_dir + "ply_lambda2/"
    dirname_config["DIRECTORIES"]["ply_streamline"] = geometry_data_dir + "ply_streamline/"
    dirname_config["DIRECTORIES"]["ply_vortexline"] = geometry_data_dir + "ply_vortexline/"
    dirname_config["DIRECTORIES"]["tstep_lambda2"] = image_output_dir + "tstep_lambda2/"
    dirname_config["DIRECTORIES"]["tstep_sequence_photorealistic"] = image_output_dir + "photorealistic_tstep_sequence/"
    dirname_config["DIRECTORIES"]["tstep_sequence_surftempmap"] = image_output_dir + "surftempmap_tstep_sequence/"
    dirname_config["DIRECTORIES"]["tstep_streamline"] = image_output_dir + "tstep_streamline/"
    dirname_config["DIRECTORIES"]["tstep_vortexline"] = image_output_dir + "tstep_vortexline/"
    dirname_config["DIRECTORIES"]["animations"] = image_output_dir + "animations/" # TODO: The animations functionality hasn't been properly implemented into this version of the rendering scripts
    dirname_config["DIRECTORIES"]["RenderHome"] = absolutify(".", slash_at_end=True)
    dirname_config["DIRECTORIES"]["BlenderHome"] = absolutify("/Blender/", slash_at_end=True)
    dirname_config["DIRECTORIES"]["RenderOutput"] = absolutify("../../RenderOutput/", slash_at_end=True)
    dirname_config["DIRECTORIES"]["RenderConfig"] = absolutify("../../RenderConfig/", slash_at_end=True)
    dirname_config["DIRECTORIES"]["RenderJobscripts"] = absolutify("../../RenderJobscripts/", slash_at_end=True)

    dirname_config["NAMES"] = {}
    dirname_config["NAMES"]["frame"] = "/frame_"
    dirname_config["NAMES"]["case-config-suffix"] = "-case.cfg"
    dirname_config["NAMES"]["render-config-suffix"] = "-render.cfg"

    dirname_config["FILES"] = {}
    dirname_config["FILES"]["tbar"] = "temperature.png"

    with open("dirname.cfg","w") as dirname_config_file:
        dirname_config.write(dirname_config_file)
