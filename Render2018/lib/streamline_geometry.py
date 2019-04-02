import numpy as np
import matplotlib.cm as cm

def create_streamline_geometry(verts_center, vel_mags, num_pts, vel_bound_low, vel_bound_up, thickness=0.02):
    """
    Given the centerline of a streamline and the corresponding magnitudes at each point on the streamline, converts this
    information into solid geometry (a cylindrical extrusion) to be rendered in Blender.
    :param verts_center: Centerline vertices of the streamline
    :param vel_mags: Velocity (or vorticity) magnitudes corresponding to each centerline vertex
    :param num_pts: Number of vertices in the extruded polygon
    :param vel_bound_low: Lower bound on the magnitude values to render as the lowest color
    :param vel_bound_up: Upper bound on the magnitude values to render as the highest color
    :param thickness: Radius of the extrusion
    :return: verts, tris, colors: Vertices, triangles, and colors to be exported in a .ply file.
    """

    num_verts = np.shape(verts_center)[0] - 2 # Remove beginning and end verts (not useful in extrusion)
    if num_verts < 0:
        num_verts = 0  # Can't have negative dimension numbers - if not enough verts, just export blank
    num_geom_verts = num_verts * num_pts  # Total number of vertices in the exported geometry

    theta = np.matrix(np.arange(0, 2 * np.pi, 2 * np.pi / num_pts)) # Angles of each vert in the cross-sections
    coords_loc = np.concatenate((thickness * np.cos(theta), thickness * np.sin(theta), np.matrix(np.zeros([1, num_pts]))),
                                0)  # Position of each cross-sectional coord in the local frame (origin is at the center of the polygon)
    coords_loc4 = np.concatenate((coords_loc, np.matrix(np.ones([1, num_pts]))), 0) # Add a 0 onto the end (useful for transformation)

    # Allocate vert arrays
    coords = np.zeros([int(num_verts), 3, num_pts])
    colors = np.zeros([int(num_verts) * num_pts, 3])

    # Initial local x and y axes in the extrusion cross-section frame
    xloc = np.array([0, 0, -1])
    yloc = np.array([0, 1, 0])
    zloc = np.cross(xloc, yloc)

    # Export blank file if there aren't enough verts
    if num_verts == 0:
        verts = np.array([])
        tris = np.array([])
        colors = np.array([])
        return (verts, tris, colors)
    else:

        # Go through and determine all vectors, and use them to calculate rotations and stuff to figure out how to connect circular cross-sections
        n = 0
        while n < num_verts:

            vert_current = verts_center[n + 1]
            vector_current = verts_center[n + 2, :] - verts_center[n + 1, :]
            vector_current = vector_current / np.linalg.norm(vector_current)
            vector_prev = verts_center[n + 1, :] - verts_center[n, :]
            vector_prev = vector_prev / np.linalg.norm(vector_prev)
            vel_mag = vel_mags[n + 1]
            colors[(n) * num_pts:(n + 1) * num_pts, :] = np.tile(
                (np.array(cm.inferno((vel_mag - vel_bound_low) / (vel_bound_up - vel_bound_low))[0:3]) * 255).astype(
                    int), (num_pts, 1))

            angle = np.arccos(np.dot(vector_current, vector_prev))
            axis = np.cross(vector_prev, vector_current)

            if axis.any():
                axis = axis / np.linalg.norm(axis)
                rotation = True
            else:  # axis is a 0 vector
                rotation = False

            # Use this angle and axis to rotate x and y unit vectors in planes
            if rotation:
                R = np.array([[np.cos(angle) + axis[0] ** 2 * (1 - np.cos(angle)),
                               axis[0] * axis[1] * (1 - np.cos(angle)) - axis[2] * np.sin(angle),
                               axis[0] * axis[2] * (1 - np.cos(angle)) + axis[1] * np.sin(angle)],
                              [axis[1] * axis[0] * (1 - np.cos(angle)) + axis[2] * np.sin(angle),
                               np.cos(angle) + axis[1] ** 2 * (1 - np.cos(angle)),
                               axis[1] * axis[2] * (1 - np.cos(angle)) - axis[0] * np.sin(angle)],
                              [axis[2] * axis[0] * (1 - np.cos(angle)) - axis[1] * np.sin(angle),
                               axis[2] * axis[1] * (1 - np.cos(angle)) + axis[0] * np.sin(angle),
                               np.cos(angle) + axis[2] ** 2 * (1 - np.cos(angle))]], dtype="float")
                xloc = np.dot(R, xloc)
                yloc = np.dot(R, yloc)
                zloc = np.cross(xloc, yloc)

            # Generate transformation matrix from local rotated coords back to absolute coords
            Tinv = np.matrix(
                [[1, 0, 0, vert_current[0]], [0, 1, 0, vert_current[1]], [0, 0, 1, vert_current[2]], [0, 0, 0, 1]])
            Rinv = np.matrix(
                [[xloc[0], yloc[0], zloc[0], 0], [xloc[1], yloc[1], zloc[1], 0], [xloc[2], yloc[2], zloc[2], 0],
                 [0, 0, 0, 1]])

            # Transform circle points to absolute coords (one cross section of the stream tube being visualized
            coords_abs = Tinv * Rinv * coords_loc4

            # Connect stream tube coords with previous ones
            coords[n, :, :] = coords_abs[0:3, :]

            n += 1

        # Create triangle matrices #TODO: this should be a separate function
        triA0 = np.arange(num_pts)
        triA1 = (triA0 + 1) % num_pts
        triA2 = triA1 + num_pts
        triB0 = triA0 + num_pts
        triB1 = triA0
        triB2 = triA2

        triA = np.array([[triA0, triA1, triA2], [triB0, triB1, triB2]])
        triA = np.swapaxes(triA, 1, 2).reshape(2 * num_pts, 3)
        triA = np.tile(triA, (n - 1, 1))
        add = num_pts * np.reshape(np.swapaxes(np.swapaxes(np.tile(np.arange(n - 1), (num_pts * 2, 3, 1)), 0, 2), 1, 2),
                                   (num_pts * 2 * (n - 1), 3))
        tris = triA + add

        verts = np.swapaxes(coords, 1, 2).reshape((n) * num_pts, 3)

        # Determine the central point of the ring at either end, which defines caps of streamline cylinders
        vert_avg_beg = np.mean(verts[num_pts * 0:num_pts * 1, :], axis=0)
        vert_avg_end = np.mean(verts[num_geom_verts - 2 * num_pts:num_geom_verts - num_pts, :], axis=0)

        verts[0:num_pts, :] = np.tile(vert_avg_beg, (num_pts, 1))
        verts[num_geom_verts - num_pts:num_geom_verts, :] = np.tile(vert_avg_end, (num_pts, 1))

    return (verts, tris, colors)