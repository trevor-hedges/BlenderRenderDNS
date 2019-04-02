import os.path
import configparser
from dircheck import get_yesno_input
import create_jobscripts
from create_dirname_config import config_dirname_cfg
from create_all_dirs import create_all
import socket
import cgns_load_data
# Script that creates the two configuration files (case and render files) necessary to run the scripts, with a data file from Abhiram's body flow simulation as input.

# Check whether scripts being run on Mox
if socket.gethostname()[0:3] == "mox":
    mox = True
    blender_dir = "/gscratch/ferrante/blender/blender-2.78c-linux-glibc219-x86_64/./"
else:
    mox = False
    blender_dir = ""

# Check if dirname.cfg, which contains directory paths used throughout the scripts, exists - otherwise, create it
if not os.path.exists("dirname.cfg"):
    config_dirname_cfg()

# Load important directories
dirname_config = configparser.ConfigParser()
dirname_config.read("dirname.cfg")

# Get case name. This corresponds to a specific .h5dns file and is specified by the user. A case config file will be created with its name.
case_name = input("Enter case name. This can be any string that refers to a particular VIZ.cgns file. ")
create_all(case_name)
case_config_path = dirname_config["DIRECTORIES"]["RenderConfig"] + case_name + "-case.cfg"

# If existing case config file exists, the user is specifying a particular .h5dns file that is already associated with
# this case name, so move on to render settings config. Otherwise, create case config file from user input.
if os.path.exists(case_config_path):
    print("Found existing case configuration: " + case_config_path)
    existing_case_config = configparser.ConfigParser()
    existing_case_config.read(case_config_path)
    print("data file: " + existing_case_config["STRING"]["h5dns_path"])
else:
    # Create new case config file
    new_case_config = configparser.ConfigParser()

    # There are different sections for each datatype (this is how the scripts know what data types to load, when they are all saved as strings)
    new_case_config["STRING"] = {}
    new_case_config["FLOAT"] = {}
    new_case_config["INT"] = {}

    # Save important strings
    new_case_config["STRING"]["case_name"] = case_name
    new_case_config["STRING"]["data_file_type"] = "bodyflow"
    h5dns_path = input("Enter absolute path to data file: ")
    new_case_config["STRING"]["h5dns_path"] = h5dns_path

    # Load data file and save important params
    params = cgns_load_data.get_important_data(h5dns_path)
    new_case_config["INT"]["tres"] = str(params["tres"])
    new_case_config["INT"]["ires"] = str(params["ires"])
    new_case_config["INT"]["jres"] = str(params["jres"])
    new_case_config["INT"]["kres"] = str(params["kres"])

    # Write case config file
    with open(case_config_path, "w") as case_config_file:
        new_case_config.write(case_config_file)

# Get render-specific config settings from user. This specifies what type of render to perform (photorealistic, surface
# temperature, ...), and other render settings (scale of droplet to render, etc.)
render_type = int(input("Select type of render to perform (enter number).\n 1  Streamline render\n 2  Vortex line render\n"))
render_name = input("Enter render profile name. This can be any string that refers to specific rendering settings for a data case. ")

# Initialize categories based on data types
new_render_config = configparser.ConfigParser()
new_render_config["STRING"] = {}
new_render_config["INT"] = {}
new_render_config["FLOAT"] = {}
new_render_config["BOOL"] = {}
new_render_config["STRING"]["render_name"] = render_name

# Determine settings from user that are specific to each type.
if (render_type == 1): # Streamline
    # Name render config file based on the type of render being performed
    render_config_path = dirname_config["DIRECTORIES"]["RenderConfig"] + render_name + "-render-streamline.cfg"
    # Get some other settings

elif (render_type == 2): # Vortex line
    render_config_path = dirname_config["DIRECTORIES"]["RenderConfig"] + render_name + "-render-vortexline.cfg"

# General inputs
new_render_config["INT"]["num_streamlines"] = input("Specify number of streamlines: ")
new_render_config["INT"]["streamline_seed"] = "777" #input("Specify random seed number to determine streamline start positions from: ")
new_render_config["FLOAT"]["view_fraction"] = input("Specify desired render frame width as multiple of domain length: ")
new_render_config["FLOAT"]["camera_azimuth_angle"] = input("Specify camera azimuth angle from the x-axis (deg): ")
new_render_config["FLOAT"]["camera_elevation_angle"] = input("Specify camera elevation angle from the horizontal (deg): ")
bg_image_enabled = get_yesno_input("Use custom background image? ")
if bg_image_enabled:
    new_render_config["STRING"]["bg_image_filepath"] = dirname_config["DIRECTORIES"]["background_images"] + input("Specify background image name (in \"Render2018/BackgroundImages\"): ")
    new_render_config["STRING"]["bg_color_1"] = ""
    new_render_config["STRING"]["bg_color_2"] = ""
else:
    new_render_config["STRING"]["bg_image_filepath"] = ""
    new_render_config["STRING"]["bg_color_1"] = input("Specify R,G,B value of lower background color (separate floats by commas, values range from 0 to 1): ")
    new_render_config["STRING"]["bg_color_2"] = input("Specify R,G,B value of upper background color (separate floats by commas, values range from 0 to 1): ")
new_render_config["FLOAT"]["resolution_percentage"] = input("Specify resolution percentage out of 100, as a percentage of 4K: ")

# Write render config file
with open(render_config_path, "w") as render_config_file:
    new_render_config.write(render_config_file)

# Create slurm jobscript to run on Mox
slurm_name = case_name + "_" + render_name + ".slurm"
create_jobscripts.create_mox_slurm(slurm_dir=dirname_config["DIRECTORIES"]["RenderJobscripts"], slurm_name=slurm_name, job_name=case_name+"_"+render_name, lib_dir=os.getcwd(), python_file_to_run="render_init.py", case_config_path=case_config_path, render_config_path=render_config_path)
local_py_name = case_name + "_" + render_name + ".py"
create_jobscripts.create_local_py(python_dir=dirname_config["DIRECTORIES"]["RenderJobscripts"], python_filename=local_py_name, lib_dir=dirname_config["DIRECTORIES"]["lib"], python_file_to_run="render_init.py", case_config_path=case_config_path, render_config_path=render_config_path)

# Run jobscript if user desires
if mox:
    if get_yesno_input("Run " + slurm_name + " to launch this rendering job?"):
        os.system("sbatch -p ferrante -A ferrante " + dirname_config["DIRECTORIES"]["RenderJobscripts"] + "/" + slurm_name)
else:
    if get_yesno_input("Run " + local_py_name + " to launch this rendering job?"):
        os.system("python3 " + dirname_config["DIRECTORIES"]["RenderJobscripts"] + local_py_name) 
