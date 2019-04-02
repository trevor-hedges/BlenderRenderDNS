import os

def count_png_dirs(png_dir):
    """
    Determines the numbered image output directory to use on a specific rendering run. On each run, this directory will
    be incremented by 1 such that it does not collide with any previous renders. This allows rendering settings to be
    tweaked and renders to be re-run without overwriting previous images.
    :param png_dir: Base directory within which to put numbered directories
    :return: Numbered directory within base directory.
    """
    #
    pngi = 0
    while True:
        png_output_dir_num = png_dir + "/" + str(pngi) + "/"
        if not os.path.exists(png_output_dir_num):
            break
        pngi += 1
    return png_output_dir_num

def check_make(dirM):
    """
    Checks to see if the given directory, or list of directories, exists, and if not, creates it.
    :param dirM: Directory, or list of directories
    :return: List of booleans corresponding to the directories - returns "True" if the directory already exists or "False" if it did not exist and was created.
    """

    # Put dirM in list to iterate (allows function to be able to handle single input or multiple inputs)
    if not isinstance(dirM, (list, tuple)):
        dirM = [dirM]
    
    output_list = []
    for dirm in dirM:
        if not os.path.exists(dirm):
            # The dir does not exist
            os.makedirs(dirm)
            output_list.append(False)
        else:
            # The dir exists
            output_list.append(True)

    return(output_list)

def check_files(base_path, extension, tsteps):
    """
    For a file that is intended to exist across many timesteps, such as .ply files or .bvox files,
    check if they all exist.
    :param base_path: Directory in which to check for files
    :param extension: File extension
    :param tsteps: Number of timesteps
    :return: True if all files exist, False if not
    """

    for tstep in range(tsteps):
        # If the file doesn't exist, return false immediately
        if not os.path.exists(base_path + get_base_output_name() + str(tstep) + extension):
            return True 

    # If loop completes entirely, all files exist, so return true
    return False 

def check_num_files(base_path, extension):
    """
    For a file that is intended to exist across many timesteps, such as .ply files or .bvox files,
    count how many timesteps of files exist, until a file does not exist.
    This is useful if a rendering job is cancelled and a certain number of files are saved, and one must check how many
    files got saved
    :param base_path: Directory in which to check for files
    :param extension: File extension
    :return: First tstep file that does not exist
    """

    tstep = 0
    while os.path.exists(base_path + get_base_output_name() + str(tstep) + extension):
        tstep += 1

    return tstep


def get_output_filepath(base_dir, tstep, extension):
    """
    Determines the path (directory + filename) of a numbered output file, given a directory, timestep number, and extension.
    :param base_dir: Output directory
    :param tstep: Timestep number
    :param extension: File extension, including dot
    :return: Path to numbered file
    """
    return base_dir + get_base_output_name() + str(tstep) + extension

def absolutify(path, slash_at_end=False):
    """
    Converts a relative path into an absolute path. Can specify whether to add a slash at the end
    :param path: Relative path
    :param slash_at_end: Adds slash at end of output path
    :return: Absolute path that corresponds to the provided relative path
    """
    # Get absolute path if relative path provided
    if path[0] != "/":
        path = os.path.abspath(path)
        # Add slash at end if not already present
        if path[-1] != "/" and slash_at_end:
            path += "/"
    return path

def get_yesno_input(text):
    """
    Gets a yes/no input from the user. The user can type "y" for yes or "n" for no.
    :param text: Text to ask user (the yes-no question)
    :return: True for yes and False for no
    """
    while True:
        user_input = input(text + " [y/n] ")
        if user_input[0] == 'y':
            return True
        elif user_input[0] == 'n':
            return False
        
        # If not returned, user input is invalid => try again
        print("Retry.")

def get_base_output_name():
    """
    Returns the base output name for any output file. All output files have the same base name but can vary in extension
    :return: base output name
    """
    #TODO: Add this to dirname.cfg?
    return "/frame_"

def check_file_sanity(filepath):
    """
    Checks if a .ply file exists and is large enough to actually contain data. Does not check validity (could implement this at a later time?)
    :param filepath: Directory + filename of file to check
    :return: True if file exists and is large enough, False if not
    """
    if os.path.exists(filepath):
        if os.stat(filepath).st_size > 10: # If less than 10 bytes, TODO: make this value make more sense - right now it's just a "Very small" filesize limit.
            return True
    else:
        return False