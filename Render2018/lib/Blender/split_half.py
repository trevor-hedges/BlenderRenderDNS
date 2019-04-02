import bpy
import bmesh
import numpy as np

def cut_mesh(dist_from_origin = 0, normal_vector = (1,0,0)): # TODO: distance from origin doesn't fully define all possible cuts. This can be generalized
    """
    Slices the selected object in Blender at the specified cut plane. This involves deleting all geometry in front of the
    cut plane and filling it with a flat cross-sectional surface.
    :param dist_from_origin: Distance from the origin at which to perform cut - the distance is taken in the direction of the normal vector.
    :param normal_vector: Vector normal to the cut plane.
    """

    n = np.array(normal_vector, dtype=float) # Normal vector
    r0 = n*dist_from_origin # Origin point of cut plane
    
    # Change to edit mode
    bpy.ops.object.mode_set(mode="EDIT")
    
    # Make sure all selected
    bpy.ops.mesh.select_all(action="SELECT")
    
    # Cut object at normal plane
    bpy.ops.mesh.bisect(plane_co=dist_from_origin*n, plane_no=n)
    
    # Fill the interior of the cut geometry at the normal plane
    bpy.ops.mesh.fill()
    
    # Deselect all
    bpy.ops.mesh.select_all(action="TOGGLE")
    
    # Get mesh for active object
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    
    # Select all vertices on one side
    for vertex in mesh.verts:
        # nx*()
        vco = np.array(vertex.co, dtype=float)
        if np.dot(n,vco-r0) > 0.001:
        # if vertex.co[0] > 0.001:
            vertex.select = True
    
    # Delete all those vertices
    bpy.ops.mesh.delete(type="VERT")
    
    # Ensure all normals point outward
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent()
    
    # Change back to object mode
    bpy.ops.object.mode_set(mode="OBJECT")
