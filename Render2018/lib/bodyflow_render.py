import configparser
import load_config
import extract_isosurf_mesh
import streamline_creator_noncartesian
import dircheck
import blender_launcher

def streamline(case_config_filepath, render_config_filepath):
    """
    Renders streamlines for flow around Abhiram's axisymmetric body, given a case config file and rendering config file.
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

    # Determine interface geometry output dir
    ply_output_dir = case_output + dirname_config["DIRECTORIES"]["ply_streamline"]

    # Determine individual frame output dir
    image_output_dir_spec = dircheck.count_png_dirs(case_output + dirname_config["DIRECTORIES"]["tstep_streamline"])
    dircheck.check_make(image_output_dir_spec) # Make it if nonexistent

    # Extract geometry of the simulated body
    extract_isosurf_mesh.extract_geometry_general(data_file=cconfd["h5dns_path"], output_dir=ply_output_dir, nth_coord=5, axis="K", level=1)

    # Draw streamlines on each tstep
    streamline_creator_noncartesian.draw_streamlines(data_file=cconfd["h5dns_path"], output_dir=ply_output_dir, line_type="Velocity", tres=cconfd["tres"], num_streamlines=rconfd["num_streamlines"], step_distance=0.05, max_iterations=1E5, rand_seed=rconfd["streamline_seed"])

    # Write Blender config file
    blender_config_filedir = case_output + rconfd["render_name"] + "_blender.cfg"
    load_config.write_config_file(config_filedir=blender_config_filedir,
                                  config_dict={"image_output_dir_spec": image_output_dir_spec,
                                               "ply_input_dir": ply_output_dir,
                                               "interface_material_name": "heatmapMaterial",
                                               "bg_image_filepath": rconfd["bg_image_filepath"],
                                               "view_fraction": rconfd["view_fraction"], "render_scale": 10,
                                               "resolution_percentage": rconfd["resolution_percentage"],
                                               "domain_res": 30, "tres": cconfd["tres"],
                                               "interface_half_enabled": False, "fog_enabled": False,
                                               "camera_azimuth_angle": rconfd["camera_azimuth_angle"],
                                               "camera_elevation_angle": rconfd["camera_elevation_angle"],
                                               "num_streamlines": rconfd["num_streamlines"],
                                               "streamline_seed": rconfd["streamline_seed"],
                                               "bg_color_1": rconfd["bg_color_1"], "bg_color_2": rconfd["bg_color_2"]})

    # Launch Blender to render each timestep
    for tstep in range(cconfd["tres"]):
        load_config.write_config_file(config_filedir=blender_config_filedir, config_dict={"tstep": tstep},
                                      append_config=True)
        blender_launcher.launch_blender_new(blender_config_filedir=blender_config_filedir,
                                            python_name="streamline_body_render.py", blend_name="droplet_render.blend")

def vortexline(case_config_filepath, render_config_filepath):
    """
    Renders vortex lines for flow around Abhiram's axisymmetric body, given a case config file and rendering config file.
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

    # Interface geometry output dir
    ply_output_dir = case_output + dirname_config["DIRECTORIES"]["ply_vortexline"]

    # Determine individual frame output dir
    image_output_dir_spec = dircheck.count_png_dirs(case_output + dirname_config["DIRECTORIES"]["tstep_vortexline"])
    dircheck.check_make(image_output_dir_spec)  # Make it if nonexistent

    # Extract geometry of the simulated body
    extract_isosurf_mesh.extract_geometry_general(data_file=cconfd["h5dns_path"], output_dir=ply_output_dir, nth_coord=5, axis="K", level=1)
    print("Extracted isosurf geometry")

    # Draw vortexlines on each tstep
    streamline_creator_noncartesian.draw_streamlines(data_file=cconfd["h5dns_path"], output_dir=ply_output_dir, line_type="Vorticity", tres=cconfd["tres"],
                      num_streamlines=rconfd["num_streamlines"], step_distance=0.05, max_iterations=1E5)

    # Write Blender config file
    blender_config_filedir = case_output + rconfd["render_name"] + "_blender.cfg"
    load_config.write_config_file(config_filedir=blender_config_filedir,
                                  config_dict={"image_output_dir_spec": image_output_dir_spec,
                                               "ply_input_dir": ply_output_dir,
                                               "interface_material_name": "heatmapMaterial",
                                               "bg_image_filepath": rconfd["bg_image_filepath"],
                                               "view_fraction": rconfd["view_fraction"], "render_scale": 10,
                                               "resolution_percentage": rconfd["resolution_percentage"],
                                               "domain_res": 30, "tres": cconfd["tres"],
                                               "interface_half_enabled": False, "fog_enabled": False,
                                               "camera_azimuth_angle": rconfd["camera_azimuth_angle"],
                                               "camera_elevation_angle": rconfd["camera_elevation_angle"],
                                               "num_streamlines": rconfd["num_streamlines"],
                                               "streamline_seed": rconfd["streamline_seed"],
                                               "bg_color_1": rconfd["bg_color_1"], "bg_color_2": rconfd["bg_color_2"]})

    # Launch Blender to render each timestep
    for tstep in range(cconfd["tres"]):
        load_config.write_config_file(config_filedir=blender_config_filedir, config_dict={"tstep": tstep},
                                      append_config=True)
        blender_launcher.launch_blender_new(blender_config_filedir=blender_config_filedir,
                                            python_name="streamline_body_render.py", blend_name="droplet_render.blend")