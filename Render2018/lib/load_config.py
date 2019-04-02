import configparser

def get_config_params(config_filedir):
    """
    Loads a config file and returns it as a dictionary.
    :param config_filedir: Directory and filename of config file to load
    :return: Dictionary where keys are the names of the entries in the config file. The values associated with each key
    have the data type specified by the sections in the config file ("FLOAT", "INT", etc.)
    """

    # Load config file in ConfigParser
    config_input = configparser.ConfigParser()
    config_input.read(config_filedir)

    # Initialize dictionary
    info = {}

    # Iterate through config file sections, determine which entries are which data type based on the section they are
    # found in, and load each entry into the dictionary, where each key name is the entry name in the config file
    for section in config_input.sections():
        for (key, val) in config_input.items(section):
            if (section == "FLOAT"):
                info[key] = float(val)
            elif (section == "INT"):
                info[key] = int(val)
            elif (section == "STRING"):
                info[key] = val
            elif (section == "BOOL"):
                if val == "True":
                    info[key] = True
                else:
                    info[key] = False

    return(info)

def write_config_file(config_filedir, config_dict, append_config=False):
    """
    Writes a config file, given a dictionary as input, where keys correspond to entries in the config file.
    The config file is written with sections based on datatypes, i.e. "FLOAT", "INT", etc.
    :param config_filedir: Directory and filename to write config file to
    :param config_dict: Dictionary of values to write to config file
    :param append_config: Whether or not to append to an existing config file
    :return:
    """
    config_file = configparser.ConfigParser()
    if append_config:
        # Read existing config file to add to it
        config_file.read(config_filedir)
    else:
        # Create new categories for new file
        config_file["STRING"] = {}
        config_file["FLOAT"] = {}
        config_file["INT"] = {}
        config_file["BOOL"] = {}

    # Add everything to config
    for key, value in config_dict.items():
        value_type = type(value)
        if value_type is str:
            category = "STRING"
        elif value_type is float:
            category = "FLOAT"
        elif value_type is int:
            category = "INT"
        elif value_type is bool:
            category = "BOOL"
        else:
            print("Invalid data type")
        config_file[category][key] = str(value)

    # Save config
    with open(config_filedir, "w") as config_file_towrite:
        config_file.write(config_file_towrite)