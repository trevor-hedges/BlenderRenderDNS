# This is the main script loaded by Blender's Python API to render streamlines around data from Abhiram's axisymmetric body on a single timestep.
import bpy
import os
import sys
import numpy as np

# Determine current Blender directory and main render directory (one level up)
directory_blender = os.path.dirname(bpy.data.filepath) 

# Add external script directories to sys.path
sys.path.append("/" + directory_blender.strip("Blender") + "/")

# Import external scripts
from Blender.fog_cube import *
from Blender.geometry_importer import import_ply_geometry
import load_config 
from Blender.scene_config import configure_scene

# Get input arguments
argv = os.sys.argv
argv = argv[argv.index("--") + 1:]

# Load Blender configuration settings
blender_config = load_config.get_config_params(argv[0])
tstep = int(blender_config["tstep"])
domain_res = int(blender_config["domain_res"])
num_streamlines = int(blender_config["num_streamlines"])
render_scale = float(blender_config["render_scale"])
bg_image_filepath = blender_config["bg_image_filepath"]
bg_color_1 = tuple(map(float, blender_config["bg_color_1"].split(",")))
bg_color_2 = tuple(map(float, blender_config["bg_color_2"].split(",")))

# Configure scene for render type/user-specified settings
configure_scene(render_scale=render_scale, view_fraction=blender_config["view_fraction"],
                bg_image_filepath=bg_image_filepath, camera_distance=15,
                camera_elevation_angle=blender_config["camera_elevation_angle"],
                resolution_percentage=float(blender_config["resolution_percentage"]),
                fog_enabled=blender_config["fog_enabled"], bg_color1=bg_color_1, bg_color2=bg_color_2) # works well: bg_color1=(0,0.316,0.458), bg_color2=(0,0.004,0.102)

# Set translation, rotation, and scale of input objects that is specific to this rendering case
translation=[0,7.25,0]
rotation=[0,0,np.pi/2]
scale=0.5*np.array([1.0,1.0,1.0])

# Import body geometry
import_ply_geometry(ply_path=blender_config["ply_input_dir"] + "body_axisKlevel1.ply", object_name="body", translation=translation, rotation=rotation, scale=scale, material_name="BodyMat")

# Import each streamline and then render
for stream_n in range(num_streamlines):
    
    # Get path to streamline geometry
    ply_path = blender_config["ply_input_dir"] + "_streamline_seed_" + str(blender_config["streamline_seed"]) + "_tstep_" + str(tstep) + "_num_" + str(stream_n) + ".ply"

    # Import and select geometry
    ob = import_ply_geometry(ply_path=ply_path, object_name="streamline" + str(stream_n), translation=translation, rotation=rotation, scale=scale, material_name=blender_config["interface_material_name"])

# Render and save frame image
bpy.data.scenes["Scene"].render.filepath = blender_config["image_output_dir_spec"] + "frame_" + str(tstep) + ".png"
bpy.ops.render.render(write_still=True)

