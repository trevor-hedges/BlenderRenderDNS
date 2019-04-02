import numpy as np

def convgeo2ply(verts, tris, output_path_ply, vcolors=False):

    # Determine if vcolors in use
    if not type(vcolors) == type(True):
        color_on = True
    else:
        color_on = False

    with open(output_path_ply, "w") as ply:
        ply.write("ply\n")
        ply.write("format ascii 1.0\n")
        ply.write("element vertex " + str(len(verts)) + "\n")
        ply.write("property float x\n")
        ply.write("property float y\n")
        ply.write("property float z\n")
        if color_on:
            ply.write("property uchar red\n")
            ply.write("property uchar green\n")
            ply.write("property uchar blue\n")
        ply.write("element face " + str(len(tris)) + "\n")
        ply.write("property list uchar uint vertex_indices\n")
        ply.write("end_header\n")
        for j in range(len(verts)):
            vertex = verts[j,:]
            if color_on:
                color = vcolors[j,:]
                ply.write(np.array_str(vertex).strip("[ ]") + " " + np.array_str(color).strip("[ ]") + "\n")
            else:
                ply.write(np.array_str(vertex).strip("[ ]") + "\n")
        for j in range(len(tris)):
            triangle = tris[j,:]
            ply.write("3 " + np.array_str(triangle).strip("[ ]") + "\n")

    print("Saved PLY file: " + output_path_ply)
