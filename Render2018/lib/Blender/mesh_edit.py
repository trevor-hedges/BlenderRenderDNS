#TODO: Should other functionality be moved here?
import bpy
import bmesh

def remove_doubles():
    """
    Removes doubled vertices on the currently selected object in Blender.
    """

    # Enter edit mode
    bpy.ops.object.mode_set(mode="EDIT")

    # Select all vertices
    bpy.ops.mesh.select_all(action="SELECT")

    # Remove doubles
    bpy.ops.mesh.remove_doubles()

    # Switch back to object mode
    bpy.ops.object.mode_set(mode="OBJECT")
