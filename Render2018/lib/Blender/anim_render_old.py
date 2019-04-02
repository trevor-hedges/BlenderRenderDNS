import os
import sys
import bpy
import configparser
import numpy as np
import shutil

# Determine current Blender directory
directory_blender = os.path.dirname(bpy.data.filepath)

# Add external script directories to sys.path
sys.path.append("/" + directory_blender.strip("lib/Blender") + "/")

# TODO: import all external scripts
from lib.Blender.transform_mesh import center_databox
from lib.loadfromconfig import *
from lib.dircheck import get_output_filepath, get_base_output_name
from lib.Blender.fog_cube import *
from lib.Blender.split_half import cut_mesh
from lib.Blender.mesh_edit import *
from lib.Blender.droplet import *
from lib.Blender.scene_config import configure_scene

# Get input argument which is the path of the config file
argv = os.sys.argv
argv = argv[argv.index("--") + 1:]

# Configure scene - use case config, render config as inputs
case_config, render_config, ply_dir, interface_material_name = configure_scene(case_cfgfile=argv[0], render_cfgfile=argv[1], directory_blender=directory_blender)

for frame_n in render_config.anim_frames:
    
    # Directory of specific droplet interface geometry
    ply_path = get_output_filepath(ply_dir, frame_n, ".ply")

    # Import and select geometry
    ob = import_droplet(get_output_filepath(ply_dir, frame_n, ".ply"), "ply_frame_" + str(frame_n), (case_config.xres, case_config.yres, case_config.zres), 10, interface_material_name)
    ob.select = True

    # If half enabled, split geometry in half
    if render_config.interface_half_enabled:
        cut_mesh()

    # If fog enabled, update its texture to the animation frame
    if render_config.fog_enabled:
        update_fog_cube_texture(get_output_filepath(render_config.bvox_output_dir, frame_n, ".bvox"))
 
    # Generate dir for tstep
    output_dir_tstep = render_config.anim_output_dir + "/" + str(frame_n) + "/"
    if not os.path.exists(output_dir_tstep):
        os.makedirs(output_dir_tstep)

    # Render anim
    bpy.data.scenes["Scene"].render.filepath = output_dir_tstep
    bpy.ops.render.render(animation=True)
    for anim_frame_n in range(bpy.context.scene.frame_end):
        shutil.move(output_dir_tstep + '%04d.png' % (anim_frame_n + 1), output_dir_tstep + 'frame_%d.png' % anim_frame_n)

    # Delete object
    bpy.ops.object.delete()

