# Within Blender, this script imports OBJ frames from the VOF2OBJ Python library and renders them.
# This is the main script loaded by Blender's Python API to render a single frame containing streamlines of droplet DNS data produced by Michael or Pablo.
print("Blender python script")
import bpy
import os
import sys

# Determine current Blender directory and main render directory (one level up)
directory_blender = os.path.dirname(bpy.data.filepath) 

# Add external script directories to sys.path
sys.path.append("/" + directory_blender.strip("Blender") + "/")

# Import external scripts
from Blender.fog_cube import *
from Blender.geometry_importer import import_droplet
import load_config
from Blender.scene_config import configure_scene

# Get input arguments - paths to case config, render config
argv = os.sys.argv
argv = argv[argv.index("--") + 1:]

# Load Blender configuration settings
blender_config = load_config.get_config_params(argv[0])
tstep = int(blender_config["tstep"])
domain_res = int(blender_config["domain_res"])
num_streamlines = int(blender_config["num_streamlines"])
render_scale = float(blender_config["render_scale"])
bg_image_filepath = blender_config["bg_image_filepath"]

# Configure scene for render type/user-specified settings
configure_scene(render_scale=render_scale, view_fraction=blender_config["view_fraction"],
                bg_image_filepath=bg_image_filepath, camera_distance=15,
                camera_azimuth_angle=blender_config["camera_azimuth_angle"],
                camera_elevation_angle=blender_config["camera_elevation_angle"],
                resolution_percentage=float(blender_config["resolution_percentage"]),
                fog_enabled=blender_config["fog_enabled"]) # View fraction: amount of horizontal to be visible

# Import each streamline and then render
for stream_n in range(num_streamlines):
    
    # Get path to streamline geometry
    ply_path = blender_config["ply_input_dir"] + "tstep" + str(tstep) + "_streamline" + str(stream_n) + ".ply"

    # Import and select geometry
    ob = import_droplet(ply_path=ply_path, object_name="streamline" + str(stream_n), dim=(domain_res, domain_res, domain_res), scale=render_scale, material_name=blender_config["interface_material_name"])

# Render and save frame image
bpy.data.scenes["Scene"].render.filepath = blender_config["image_output_dir_spec"] + "frame_" + str(tstep) + ".png"
bpy.ops.render.render(write_still=True)

