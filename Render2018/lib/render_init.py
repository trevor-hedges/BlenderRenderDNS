import argparse
import load_config
import main_render
import bodyflow_render
# Script that launches a rendering job in Python. Launches rendering jobs for droplet data (Michael/Pablo) or axisymmetric body flow data (Abhiram)

# Parse input arguments that point to case config and render config files
parser = argparse.ArgumentParser()
parser.add_argument("-c", metavar="case config file", type=str, required=True, help="Path to case config file specific to data file. ")
parser.add_argument("-r", metavar="render config file", type=str, required=True, help="Path to config file that specifies rendering settings. ")
args = parser.parse_args()
case_config_filepath = args.c
render_config_filepath = args.r

# Load case config file
cconfd = load_config.get_config_params(case_config_filepath)

# Determine render type from case config file and render config filename, and launch the corresponding rendering function.
rcfg_filename = render_config_filepath.split(".")[-2]
if cconfd["data_file_type"] == "turbdrops":
    if rcfg_filename.endswith("photorealistic"):
        main_render.photorealistic(case_config_filepath, render_config_filepath)
    elif rcfg_filename.endswith("surf_temp"):
        main_render.surf_tempmap(case_config_filepath, render_config_filepath)
    elif rcfg_filename.endswith("lambda2"):
        main_render.lambda2(case_config_filepath, render_config_filepath)
elif cconfd["data_file_type"] == "bodyflow":
    if rcfg_filename.endswith("streamline"):
        bodyflow_render.streamline(case_config_filepath, render_config_filepath)
    elif rcfg_filename.endswith("vortexline"):
        bodyflow_render.vortexline(case_config_filepath, render_config_filepath)