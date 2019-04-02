import bpy
import os.path
from Blender.mesh_edit import *
from Blender.transform_mesh import center_databox
import mathutils

def import_droplet(ply_path, object_name, dim, scale, material_name):
    """
    Imports a .ply that corresponds to droplet interface data exported from a VOF field. This is specific to droplets in
    that it applies a correction factor to the droplet position to ensure that geometry produced with the marching cubes
    algorithm is centered at the origin in Blender.
    :param ply_path: Path to the .ply of the droplet surface interface
    :param object_name: Name to give to the droplet object in Blender
    :param dim: (x,y,z) dimensions of the droplet domain
    :param scale: Scale factor to apply to imported geometry
    :param material_name: Name of material to apply to geometry
    :return: Object class of the imported geometry
    """

    # Import geometry
    bpy.ops.import_mesh.ply(filepath = ply_path)
    
    # Get name of just-imported object 
    name_starts_with = os.path.basename(ply_path)[:-4] # Base name of ply file without ".ply" extension
    print(object_name)
    print(bpy.data.objects.keys())
    for object_name_infile in bpy.data.objects.keys():
        if object_name_infile.startswith(name_starts_with):
            current_object = object_name_infile
            break
    
    # Select this object
    bpy.context.scene.objects.active = bpy.data.objects[current_object]
    
    # Get this object
    ob = bpy.context.active_object

    # Re-name current object
    ob.name = object_name

    # Remove doubled vertices
    remove_doubles()

    # Move object to center stage and rescale to appropriate size
    center_databox(dim[0], dim[1], dim[2], scale)

    # Get interface material
    mat = bpy.data.materials.get(material_name)
    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots; create new slot
        ob.data.materials.append(mat)

    # Enable smooth shading on current mesh object
    bpy.ops.object.shade_smooth()

    return ob


def import_ply_geometry(ply_path, object_name, translation, rotation, scale, material_name):
    """
    Imports a .ply file and applies translation, rotation, and scale in that order. Not specific to any particular type
    of geometry, unlike the import_droplet method.
    :param ply_path: Path to the .ply
    :param object_name: Name to give the imported object
    :param translation: (x,y,z) center position to apply to object
    :param rotation: (x,y,z) to apply to object as XYZ Euler angles
    :param scale: (x,y,z) to apply to object
    :param material_name: Name of material to apply to object
    :return: Object class of the imported geometry
    """

    # Import geometry
    bpy.ops.import_mesh.ply(filepath=ply_path)

    # Get name of just-imported object
    name_starts_with = os.path.basename(ply_path)[:-4]  # Base name of ply file without ".ply" extension
    for object_name_infile in bpy.data.objects.keys():
        if object_name_infile.startswith(name_starts_with):
            current_object = object_name_infile
            break

    # Select this object
    bpy.context.scene.objects.active = bpy.data.objects[current_object]

    # Get this object
    ob = bpy.context.active_object

    # Re-name current object
    ob.name = object_name

    # Remove doubled vertices
    remove_doubles()

    # Set translation, rotation, scale
    bpy.context.object.location = mathutils.Vector(translation)
    bpy.context.object.rotation_euler[0:3] = rotation
    bpy.context.object.scale = mathutils.Vector(scale)

    # Get interface material
    mat = bpy.data.materials.get(material_name)
    # Assign it to object
    if ob.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots; create new slot
        ob.data.materials.append(mat)

    # Enable smooth shading on current mesh object
    bpy.ops.object.shade_smooth()

    return ob