import bpy
import numpy as np
from os import getcwd
import Blender.fog_cube as fog_cube

# Input: fraction of volume cube length in view
def configure_scene(render_scale, view_fraction, bg_image_filepath, camera_distance=15, camera_azimuth_angle=0, camera_elevation_angle=0, resolution_percentage=100, fog_enabled=False, bg_color1=(0,0,0), bg_color2=(0,0,0)): #(0,0.002,0.027)
    """
    Performs initial configuration of a Blender file for fluid data rendering. Adds necessary materials, sets camera
    position and orientation, adds background image, etc.
    :param render_scale: Amount by which all objects are scaled, used to determine view frame width of camera
    :param view_fraction: Portion of imported objects/data to show, usually more than 1 to render entire object with some background area
    :param bg_image_filepath: Path and filename of background image
    :param camera_distance: Distance from which the camera views the imported objects (not zoom) - this can be adjusted to ensure camera is outside of all objects
    :param camera_azimuth_angle: Azimuth angle from which the camera points onto the object (positive is counterclockwise)
    :param camera_elevation_angle: Elevation angle from which the camera points onto the object (upward is positive)
    :param resolution_percentage: Percentage of 4K of rendered images
    :param fog_enabled: If rendering vapor, import the cube object within which the vapor voxel data is rendered
    :param bg_color1: If no background image, first (lower) color in the background color gradient
    :param bg_color2: If no background image, second (upper) color in the background color gradient
    :return:
    """

    # Get current working directory
    directory_cwd = getcwd()

    # Change world background colors
    bpy.data.worlds["World.001"].horizon_color = bg_color1
    bpy.data.worlds["World.001"].zenith_color = bg_color2

    # If background image specified, enable backdrop and apply background image
    if not (bg_image_filepath == ""):
        # Load backdrop object
        bpy.ops.wm.append(filename="Backdrop", filepath="material.blend",
                          directory=directory_cwd + "/Blender/material.blend/Object/")
        # Load backdrop material
        bpy.ops.wm.append(filename="BackdropMat", filepath="material.blend",
                          directory=directory_cwd + "/Blender/material.blend/Material/")
        # Apply background image filepath
        bpy.data.images["Backdrop.002"].filepath = bg_image_filepath
        # Rotate bg object such that center of texture is always behind geometry
        bpy.data.objects["Backdrop"].rotation_euler[2] = camera_azimuth_angle * np.pi / 180

    # Add all project materials to Blender workspace
    material_names = ["heatmapMaterial", "WaterMaterial5", "VoxelMaterialW2", "BodyMat"]
    for material_name in material_names:
        bpy.ops.wm.append(filename=material_name, filepath="material.blend", directory=directory_cwd+"/Blender/material.blend/Material/")

    # Set resolution percentage of output images
    bpy.data.scenes["Scene"].render.resolution_percentage = resolution_percentage

    # Set camera distance
    bpy.data.objects["MainCameraObject"].location[0] = camera_distance

    # Set field of view necessary to render the entire object (or portion of object as specified by the view fraction)
    bpy.data.cameras["MainCamera"].angle = 2*np.arctan(render_scale*view_fraction/(2*camera_distance))

    # Set camera angles
    bpy.data.objects["Empty"].rotation_euler[1] = -camera_elevation_angle*np.pi/180
    bpy.data.objects["Empty"].rotation_euler[2] = camera_azimuth_angle * np.pi / 180

    # If fog enabled, create the cube object necessary to render voxel fog
    if fog_enabled:
        fog_cube.spawn_fog_cube(render_scale/2)

