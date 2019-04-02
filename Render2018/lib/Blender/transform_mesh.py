import bpy
import bmesh
import mathutils

def center_databox(xlen, ylen, zlen, scale=1):
    """
    Centers an imported droplet object at the origin. Assumes a square domain, and that the mesh was imported such that
    one distance unit in Blender corresponds to one cartesian grid length in the data file.
    :param xlen: x-resolution of domain
    :param ylen: y-resolution of domain
    :param zlen: z-resolution of domain
    :param scale: Length of bounding box to scale domain to
    """

    # Enter edit mode
    bpy.ops.object.mode_set(mode="EDIT")
    
    # Select all
    bpy.ops.mesh.select_all(action="SELECT")
    
    # Get current mesh
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    
    correction = mathutils.Vector([1/(2*xlen), 1/(2*ylen), 1/(2*zlen)]) #TODO: not quite sure why this is necessary to ensure object centered exactly at origin - seems to be a thing with the marching cubes algorithm
    for vertex in mesh.verts:
        # Scale by y-axis desired length and center the bounding box
        vertex.co = (vertex.co - mathutils.Vector([xlen,ylen,zlen])/2)*(scale/ylen) + correction*scale
    
    # Return to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

