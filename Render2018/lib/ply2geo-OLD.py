import numpy as np

def convply2geo(ply_path):
    
    with open(ply_path, "r") as ply:
        linenum = 0
        verti = 0
        trii = 0

        # Iterate thru all lines in ply file
        loading_verts = False
        loading_tris = False
        for line in ply:

            # Check if line contains vertex information
            if line.startswith("element vertex "):
                num_verts = int(line.split()[-1]) # Get number of verts
                # print("Num verts: " + str(num_verts))
                
                # Allocate vert array
                verts = np.zeros([num_verts, 3])
                continue

            if line.startswith("element face "):
                num_tris = int(line.split()[-1])
                # print("Num tris: " + str(num_tris))

                # Allocate tri array
                tris = np.zeros([num_tris, 3], dtype=int)
                continue

            # Check for header end
            if line == "end_header\n":
                loading_verts = True
                continue 

            # If in verts section, load them 
            if loading_verts:
                verts[verti,:] = list(map(float,line.split()))[0:3]
                verti += 1
                if verti >= num_verts:
                    # print("First vert: " + np.array_str(verts[0,:]))
                    # print("Last vert: " + np.array_str(verts[-1,:]))
                    loading_verts = False
                    loading_tris = True
                    continue
                
            # If in faces/tris section, load them
            if loading_tris:
                tris[trii,:] = list(map(int,line.split()))[1:4]
                trii += 1
                if trii >= num_tris:
                    # print("First tri: " + np.array_str(tris[0,:]))
                    # print("Last tri: " + np.array_str(tris[-1,:]))
                    loading_tris = False
                    break

            linenum += 1

    return verts, tris
