# This script, loaded by Blender's Python API, applies the mesh smoothing modifier to .ply files of droplet geometry across a series of timesteps.
import bpy
import os
import sys

# Determine blender directory
directory_blender = os.path.dirname(bpy.data.filepath)

# Add external script directories to sys.path
sys.path.append("/" + directory_blender.strip("lib/Blender") + "/")

# Import external scripts
from lib.dircheck import get_output_filepath, get_base_output_name, check_file_sanity

# Get input arguments: input dir (unsmooth) and output dir (smooth)
argv = os.sys.argv[os.sys.argv.index("--") + 1:]
input_ply_dir = argv[0]
output_ply_dir = argv[1]

print("Loading plys from " + input_ply_dir)

# Iterate through all files
tstep = 0
while os.path.exists(input_ply_dir + get_base_output_name() + str(tstep) + ".ply"):
    
    ply_smooth_output_dir = get_output_filepath(output_ply_dir, tstep, ".ply")

    # Check if file already exists
    if not check_file_sanity(ply_smooth_output_dir):

        # Import geometry
        bpy.ops.import_mesh.ply(filepath=get_output_filepath(input_ply_dir, tstep, ".ply"))
    
        # Select just-imported object
        for object_name in bpy.data.objects.keys():
            if object_name.startswith(get_base_output_name().strip("/")):
                current_object = object_name
                break

        # Select this object
        bpy.context.scene.objects.active = bpy.data.objects[current_object]

        # Get the object class
        ob = bpy.context.active_object
    
        # Apply smooth modifier
        bpy.ops.object.modifier_add(type='SMOOTH')
        ob.modifiers["Smooth"].factor = 1
        ob.modifiers["Smooth"].iterations = 10
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Smooth')
    
        # Export smooth PLY
        bpy.ops.export_mesh.ply(filepath=ply_smooth_output_dir)

        # Delete current object
        bpy.ops.object.delete()

    tstep += 1
