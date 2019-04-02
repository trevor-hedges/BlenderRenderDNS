import bpy
import os

# TODO: Generalize to any dimensions, not just a cubic domain (so far, no renders with vapor data have been performed on non-cubic domain)
def spawn_fog_cube(box_radius, material_name="VoxelMaterialW2"):
    """
    Spawns a cube in a Blender scene within which fog from vapor data can be rendered. Called by the scene configuration method
    :param box_radius: Radius of the box within which fog will appear
    :param material_name: Name of the material in Blender to import and apply to the box (should be a voxel material)
    """

    # Get filepaths
    filepath_current = bpy.data.filepath
    directory_current = os.path.dirname(filepath_current)

    # Spawn cube
    centroid = (0, 0, 0)
    bpy.ops.mesh.primitive_cube_add(radius=box_radius, location=centroid, view_align=True)

    # Set as active object
    ob = bpy.context.active_object

    # Append voxel fog material
    material_filepath = directory_current + "/material.blend/Material"
    bpy.ops.wm.append(filename=material_name, filepath="material.blend", directory=material_filepath)
    mat = bpy.data.materials.get(material_name)

    # Assign it to cube object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        ob.data.materials.append(mat)

    # Determine and set voxel cube scale
    bpy.data.materials[material_name].texture_slots[0].scale = (1/box_radius, 1/box_radius, 1/box_radius)

def update_fog_cube_texture(texture_path):
    """
    Updates the vapor data in a scene where a vapor data cube exists. Blender considers the voxel data to be a
    "3D texture" so this method updates the filepath to this "texture" (voxel data file)
    :param texture_path: Path to .bvox file
    """
    for texture_name in bpy.data.textures.keys():
        # Change all possible textures since multiple copies may exist
        if texture_name.startswith("VoxelMaterialWT2"):
            print("Texture name: " + texture_name)
            print("BVOX file: " + texture_path)
            bpy.data.textures[texture_name].voxel_data.filepath = texture_path
