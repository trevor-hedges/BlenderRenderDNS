import socket

def import_matplotlib():
    if socket.gethostname()[0:3] == "mox":
        # Do the special thing

    else:
        # Just import normally
        from matplotlib import pyplot as plt, cm
