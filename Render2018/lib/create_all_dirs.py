import configparser
from dircheck import check_make, absolutify

def create_all(case_name):
    """
    Creates all the directories necessary for a specific .h5dns case, that are not specific to certain rendering
    settings (these directories are created separately)
    :param case_name: User-specified name of case that corresponds to .h5dns file
    """

    # Load directory name settings
    dirname_config = configparser.ConfigParser()
    dirname_config.read("dirname.cfg")

    # Construct all directory paths and put them in an array
    case_namesl = case_name + "/"
    render_output_dir = dirname_config["DIRECTORIES"]["RenderOutput"]
    dirs = [] 
    dirs.append(dirname_config["DIRECTORIES"]["RenderConfig"])
    dirs.append(dirname_config["DIRECTORIES"]["RenderJobscripts"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["geometry_data"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["image_output"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["ply"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["bvox"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["ply_temp"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["ply_lambda2"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["ply_streamline"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["tstep_sequence_photorealistic"])
    dirs.append(render_output_dir + case_namesl + dirname_config["DIRECTORIES"]["ply_vortexline"])

    # Check if all dirs exist, and if not, make them
    check_make(dirs)

