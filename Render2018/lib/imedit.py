from PIL import Image
from dircheck import get_output_filepath
import matplotlib.pyplot as plt
import matplotlib as mpl

def add_tempmap(bound_min, bound_max, image_dir, tres, label="Temperature (K)"):
    """
    Adds colorbar legend to a series of numbered images, previously exported by rendering scripts.
    :param bound_min: Minimum colorbar value
    :param bound_max: Maximum colorbar value
    :param image_dir: Directory of numbered images
    :param tres: Number of timesteps
    :param label: Text label to add to colorbar - defaults to temperature since that is most commonly used
    """

    # Make a figure and axes with dimensions as desired.
    fig = plt.figure(figsize=(4, 12))
    ax1 = fig.add_axes([0.05, 0.05, 0.35, 0.9])
    plt.tick_params(axis='both', which='major', labelsize=40, labelcolor="white")

    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.
    cmap = mpl.cm.inferno
    norm = mpl.colors.Normalize(vmin=bound_min, vmax=bound_max)

    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='vertical')
    cb1.set_label(label, fontsize=50, color=(1,1,1))
    plt.savefig(image_dir + "/temperature.png", transparent=True)

    # Load temperature colorbar
    tbar = Image.open(image_dir + "temperature.png")

    # Get temperature colorbar size
    tbarx, tbary = tbar.size

    # Determine image size
    imxres, imyres = Image.open(get_output_filepath(base_dir=image_dir, tstep=0, extension=".png")).size

    # Resize colorbar to be smaller than the images
    tbaryn = 4/5*imyres
    tbarxn = tbaryn/tbary*tbarx
    tbar = tbar.resize((int(tbarxn), int(tbaryn)), Image.ANTIALIAS)

    for tstep in range(tres):
        # image filename specific to tstep
        image_filename_spec = get_output_filepath(base_dir=image_dir, tstep=tstep, extension=".png")
        
        # Load each image
        im = Image.open(image_filename_spec)

        # Paste tbar onto each image
        im.paste(tbar, (int(10*imxres/12), int(1*imyres/12)), tbar)

        # Save
        im.save(image_filename_spec)
