import dircheck
import convert_data
import load_config
import blender_launcher
import imedit
import configparser

def photorealistic(case_config_filepath, render_config_filepath):
    """
    Renders photorealistic images of a droplet interface in data from Michael or Pablo's simulations, given a case config file and render config file.
    :param case_config_filepath: Path to case configuration file, which contains information on the data file to render.
    :param render_config_filepath: Path to render configuration file, which contains information on how to render the data.
    """

    # Load config file with all common directory names
    dirname_config = configparser.ConfigParser()
    dirname_config.read("dirname.cfg")

    # Get information from config files
    cconfd = load_config.get_config_params(case_config_filepath)  # Case file
    rconfd = load_config.get_config_params(render_config_filepath)  # Render file

    # Main output directory
    case_output = dirname_config["DIRECTORIES"]["RenderOutput"] + cconfd["case_name"] + "/"
    
    # Determine interface geometry output dir
    geometry_output_dir = case_output + dirname_config["DIRECTORIES"]["ply"]

    # Determine individual frame output dir
    image_output_dir_spec = dircheck.count_png_dirs(case_output + dirname_config["DIRECTORIES"]["tstep_sequence_photorealistic"])
    dircheck.check_make(image_output_dir_spec) # Make it if nonexistent
    
    # Write Blender config file
    blender_config_filedir = case_output + rconfd["render_name"] + "_blender.cfg"
    load_config.write_config_file(config_filedir=blender_config_filedir,
                                  config_dict={"image_output_dir_spec": image_output_dir_spec,
                                               "ply_input_dir": geometry_output_dir,
                                               "interface_material_name": "WaterMaterial5",
                                               "bg_image_filepath": rconfd["bg_image_filepath"],
                                               "view_fraction": cconfd["dropd"]/rconfd["droplet_scale"],
                                               "render_scale": 10,
                                               "resolution_percentage": rconfd["resolution_percentage"],
                                               "xres": cconfd["xres"], "yres": cconfd["yres"], "zres": cconfd["zres"],
                                               "tres": cconfd["tres"],
                                               "interface_half_enabled": rconfd["interface_half_enabled"],
                                               "fog_enabled": rconfd["fog_enabled"],
                                               "camera_azimuth_angle": rconfd["camera_azimuth_angle"],
                                               "camera_elevation_angle": rconfd["camera_elevation_angle"],
                                               "bg_color_1": rconfd["bg_color_1"], "bg_color_2": rconfd["bg_color_2"]})

    # Extract droplet interface geometry
    convert_data.conv_ply(h5dns_path=cconfd["h5dns_path"], output_dir=geometry_output_dir, tres=int(cconfd["tres"]))

    # Extract vapor fog (YV) if enabled
    if rconfd["fog_enabled"]:
        # Determine individual fog dir and make it if necessary
        fog_halved = rconfd["fog_half_enabled"]
        fog_dir_specifier = str(rconfd["fog_vapor_min"]) + "halved" + str(fog_halved) + "/"
        bvox_output_dir_spec = case_output + dirname_config["DIRECTORIES"]["bvox"] + fog_dir_specifier
        dircheck.check_make(bvox_output_dir_spec)
        # Convert fog data
        convert_data.conv_bvox(h5dns_path=cconfd["h5dns_path"], output_dir=bvox_output_dir_spec, tres=int(cconfd["tres"]), vapor_min=float(rconfd["fog_vapor_min"]), fog_halved=fog_halved)
        # Add fog dir to Blender config file
        load_config.write_config_file(config_filedir=blender_config_filedir, config_dict={"bvox_input_dir": bvox_output_dir_spec}, append_config=True)
 
    # Launch Blender to perform rendering
    blender_launcher.launch_blender_new(blender_config_filedir=blender_config_filedir, python_name="droplet_render.py", blend_name="droplet_render.blend")


def surf_tempmap(case_config_filepath, render_config_filepath):
    """
    Renders surface temperature images of a droplet interface in data from Michael or Pablo's simulations, given a case config file and render config file.
    :param case_config_filepath: Path to case configuration file, which contains information on the data file to render.
    :param render_config_filepath: Path to render configuration file, which contains information on how to render the data.
    """

    # Load config file with all common directory names
    dirname_config = configparser.ConfigParser()
    dirname_config.read("dirname.cfg")

    # Get information from config files
    cconfd = load_config.get_config_params(case_config_filepath)
    rconfd = load_config.get_config_params(render_config_filepath)

    # Main output directory
    case_output = dirname_config["DIRECTORIES"]["RenderOutput"] + cconfd["case_name"] + "/"
    
    # Determine surface temperature geometry output dir
    ply_temp_output_dir = case_output + dirname_config["DIRECTORIES"]["ply_temp"]

    # Get temperature bounds
    if rconfd["temp_bounds_auto"]:
        temp_min, temp_max = convert_data.temp_bounds(h5dns_path=cconfd["h5dns_path"],
                                                      ply_temp_output_dir=ply_temp_output_dir,
                                                      prc_min=rconfd["temp_min_percentile"],
                                                      prc_max=rconfd["temp_max_percentile"])
    else:
        temp_min = rconfd["temp_min"]
        temp_max = rconfd["temp_max"]

    # Determine specific output dirs and make them if necessary
    image_output_dir_spec = dircheck.count_png_dirs(case_output + dirname_config["DIRECTORIES"]["tstep_sequence_surftempmap"])
    ply_temp_output_dir_spec = ply_temp_output_dir + str(temp_min) + "to" + str(temp_max)
    dircheck.check_make([ply_temp_output_dir_spec, image_output_dir_spec])

    # Write Blender config file
    blender_config_filedir = case_output + rconfd["render_name"] + "_blender.cfg"
    load_config.write_config_file(config_filedir=blender_config_filedir,
                                  config_dict={"image_output_dir_spec": image_output_dir_spec,
                                               "ply_input_dir": ply_temp_output_dir_spec,
                                               "interface_material_name": "heatmapMaterial",
                                               "bg_image_filepath": rconfd["bg_image_filepath"],
                                               "view_fraction": cconfd["dropd"]/rconfd["droplet_scale"],
                                               "render_scale": 10,
                                               "resolution_percentage": rconfd["resolution_percentage"],
                                               "xres": cconfd["xres"], "yres": cconfd["yres"], "zres": cconfd["zres"],
                                               "tres": cconfd["tres"],
                                               "interface_half_enabled": False,
                                               "fog_enabled": False,
                                               "camera_azimuth_angle": rconfd["camera_azimuth_angle"],
                                               "camera_elevation_angle": rconfd["camera_elevation_angle"],
                                               "bg_color_1": rconfd["bg_color_1"], "bg_color_2": rconfd["bg_color_2"]})

    # Extract droplet interface geometry
    ply_output_dir_uncolored = case_output + dirname_config["DIRECTORIES"]["ply"]
    convert_data.conv_ply(h5dns_path=cconfd["h5dns_path"], output_dir=ply_output_dir_uncolored, tres=cconfd["tres"])

    # Add surface temperature color to droplet interface
    convert_data.conv_color_ply(h5dns_path=cconfd["h5dns_path"], output_dir=ply_temp_output_dir_spec, uncolored_ply_dir=ply_output_dir_uncolored, tres=cconfd["tres"], temp_min=temp_min, temp_max=temp_max)

    # Launch Blender to perform rendering
    blender_launcher.launch_blender_new(blender_config_filedir=blender_config_filedir, python_name="droplet_render.py", blend_name="droplet_render.blend")

    # Add temperature legend colorbar to images
    if rconfd["add_temp_bar"]:
        imedit.add_tempmap(bound_min=temp_min*cconfd["tgas"], bound_max=temp_max*cconfd["tgas"], image_dir=image_output_dir_spec, tres=cconfd["tres"])

def lambda2(case_config_filepath, render_config_filepath):
    """
    Renders lambda2 contours of droplet data from Michael or Pablo's simulations, given a case config file and render config file.
    :param case_config_filepath: Path to case configuration file, which contains information on the data file to render.
    :param render_config_filepath: Path to render configuration file, which contains information on how to render the data.
    """

    # Load config file with all common directory names
    dirname_config = configparser.ConfigParser()
    dirname_config.read("dirname.cfg")

    # Get information from config files
    cconfd = load_config.get_config_params(case_config_filepath)
    rconfd = load_config.get_config_params(render_config_filepath)
    
    # Main output directory
    case_output = dirname_config["DIRECTORIES"]["RenderOutput"] + cconfd["case_name"] + "/"

    # Determine lambda2 output directories and make them if necessary
    lambda2_level = rconfd["lambda2_level"]
    lambda2_specifier = "l2" + str(lambda2_level) + "/"
    geometry_output_dir = case_output + dirname_config["DIRECTORIES"]["ply"]
    ply_lambda2_output_dir = case_output + dirname_config["DIRECTORIES"]["ply_lambda2"] + lambda2_specifier
    image_lambda2_output_dir = case_output + dirname_config["DIRECTORIES"]["tstep_lambda2"] + lambda2_specifier
    image_lambda2_output_dir_spec = dircheck.count_png_dirs(image_lambda2_output_dir)
    dircheck.check_make([ply_lambda2_output_dir, image_lambda2_output_dir_spec])

    # Write Blender config file
    blender_config_filedir = case_output + rconfd["render_name"] + "_blender.cfg"
    load_config.write_config_file(config_filedir=blender_config_filedir,
                                  config_dict={"image_output_dir_spec": image_lambda2_output_dir_spec,
                                               "ply_input_dir": ply_lambda2_output_dir,
                                               "interface_material_name": "Lambda2Contour",
                                               "bg_image_filepath": rconfd["bg_image_filepath"],
                                               "view_fraction": rconfd["view_fraction"], "render_scale": 10,
                                               "resolution_percentage": rconfd["resolution_percentage"],
                                               "xres": cconfd["xres"], "yres": cconfd["yres"], "zres": cconfd["zres"],
                                               "tres": cconfd["tres"], "interface_half_enabled": False,
                                               "fog_enabled": False,
                                               "camera_azimuth_angle": rconfd["camera_azimuth_angle"],
                                               "camera_elevation_angle": rconfd["camera_elevation_angle"],
                                               "bg_color_1": rconfd["bg_color_1"], "bg_color_2": rconfd["bg_color_2"]})

    # Extract droplet geometry
    # convert_data.conv_ply(h5dns_path=cconfd["h5dns_path"], output_dir=geometry_output_dir, tres=int(cconfd["tres"]))

    # Extract lambda2 contour geometry
    convert_data.conv_lambda2_ply(h5dns_path=cconfd["h5dns_path"], output_dir=ply_lambda2_output_dir, tres=cconfd["tres"], contour_level=lambda2_level)

    # Launch Blender to perform rendering
    blender_launcher.launch_blender_new(blender_config_filedir=blender_config_filedir, python_name="droplet_render.py", blend_name="droplet_render.blend")
