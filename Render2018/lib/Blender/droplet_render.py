# This is the main script loaded by Blender's Python API to render a series of frames of droplet DNS data produced by Michael or Pablo.
import bpy
import os
import sys

# Determine current Blender directory and main render directory (one level up)
directory_blender = os.path.dirname(bpy.data.filepath) 

# Add external script directories to sys.path
sys.path.append("/" + directory_blender.strip("Blender") + "/")

# Import external scripts
from dircheck import get_output_filepath
from Blender.fog_cube import * 
from Blender.split_half import cut_mesh
from Blender.geometry_importer import import_droplet
import load_config
from Blender.scene_config import configure_scene

# Get input arguments
argv = os.sys.argv
argv = argv[argv.index("--") + 1:]

# Load Blender configuration settings
blender_config = load_config.get_config_params(argv[0])
num_frames = int(blender_config["tres"])
domain_dims = (int(blender_config["xres"]), int(blender_config["yres"]), int(blender_config["zres"]))
render_scale = float(blender_config["render_scale"])
interface_material_name=blender_config["interface_material_name"]
fog_enabled = blender_config["fog_enabled"]
bg_image_filepath = blender_config["bg_image_filepath"]
bg_color_1 = tuple(map(float, blender_config["bg_color_1"].split(",")))
bg_color_2 = tuple(map(float, blender_config["bg_color_2"].split(",")))

# Configure scene for render type/user-specified settings
configure_scene(render_scale=render_scale, view_fraction=blender_config["view_fraction"],
                bg_image_filepath=bg_image_filepath, camera_distance=15,
                camera_azimuth_angle=blender_config["camera_azimuth_angle"],
                camera_elevation_angle=blender_config["camera_elevation_angle"],
                resolution_percentage=float(blender_config["resolution_percentage"]), fog_enabled=fog_enabled,
                bg_color1=bg_color_1, bg_color2=bg_color_2) # View fraction: amount of domain to be visible - 1 is entirely within the render frame, 2 is zoomed out x2, etc.

# Import droplet geometry and render each timestep
for frame_n in range(num_frames):

    # Directory/filename of timestep-specific droplet geometry .ply file
    ply_path = get_output_filepath(blender_config["ply_input_dir"], frame_n, ".ply")
    
    # Import and select geometry
    ob = import_droplet(ply_path=ply_path, object_name="ply_frame_" + str(frame_n), dim=domain_dims, scale=render_scale, material_name=interface_material_name)
    ob.select = True

    # Split geometry in half if enabled
    if blender_config["interface_half_enabled"]:
        cut_mesh()

    # Apply 3D fog texture (.bvox voxel file) for this timestep if enabled
    if fog_enabled:
        update_fog_cube_texture(get_output_filepath(blender_config["bvox_input_dir"], frame_n, ".bvox"))

    # Render and save frame image
    bpy.data.scenes["Scene"].render.filepath = get_output_filepath(blender_config["image_output_dir_spec"], frame_n, ".png")
    bpy.ops.render.render(write_still=True)

    # Delete object
    bpy.ops.object.delete()

